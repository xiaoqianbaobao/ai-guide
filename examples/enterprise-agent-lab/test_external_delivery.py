"""Integration tests against a loopback-only mock service and isolated databases."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import tempfile
from threading import Thread
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'cross-service-recovery'))
from http_downstream import HttpDownstream, make_server
from external_delivery import dispatch, reconcile
from service import ConflictError, IDENTITIES, Service


class ExternalDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.now = 1000
        self.service = Service(str(root / 'local.sqlite3'), clock=lambda: self.now)
        self.server = make_server(str(root / 'remote.sqlite3'))
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.remote = HttpDownstream(self.server.server_port)
        self.op = IDENTITIES['demo-support']
        self.reviewer = IDENTITIES['demo-support-reviewer']
        self.draft = self.service.create_draft(self.op, '请核实退款')['draft_id']
        version = self.service.get_draft(self.reviewer, self.draft)['version']
        self.service.approve(self.reviewer, self.draft, version)
        self.service.prepare_external_submission(self.op, self.draft, 'op-1')

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def count_external(self):
        with closing(sqlite3.connect(self.server.downstream.path)) as db:
            return db.execute('SELECT count(*) FROM tickets').fetchone()[0]

    def test_response_lost_then_restart_and_reconcile_without_duplicate(self):
        self.assertEqual(dispatch(self.service, self.op, 'op-1', self.remote, lose_response=True)['state'], 'unknown')
        self.assertEqual(self.count_external(), 1)
        restarted = Service(self.service.path, clock=lambda: self.now)
        self.assertEqual(dispatch(restarted, self.op, 'op-1', self.remote)['state'], 'unknown')
        self.assertEqual(reconcile(restarted, self.op, 'op-1', self.remote), {'state': 'confirmed', 'receipt': 'op-1'})
        self.assertEqual(dispatch(restarted, self.op, 'op-1', self.remote)['state'], 'confirmed')
        self.assertEqual(self.count_external(), 1)

    def test_expiry_prevents_first_send_but_allows_cancellation(self):
        self.now += 300
        with self.assertRaises(PermissionError):
            dispatch(self.service, self.op, 'op-1', self.remote)
        self.assertEqual(self.count_external(), 0)
        self.assertEqual(self.service.cancel_external_submission(self.reviewer, 'op-1')['state'], 'cancelled')

    def test_crash_after_claim_is_unknown_and_does_not_resend(self):
        self.assertTrue(self.service.claim_external_submission(self.op, 'op-1')['claimed'])
        self.assertEqual(dispatch(self.service, self.op, 'op-1', self.remote)['state'], 'unknown')
        self.assertEqual(reconcile(self.service, self.op, 'op-1', self.remote)['state'], 'unknown')
        self.assertEqual(self.count_external(), 0)
        with self.assertRaises(ConflictError):
            self.service.cancel_external_submission(self.reviewer, 'op-1')

    def test_claim_and_cancel_are_mutually_exclusive(self):
        def claim():
            try:
                return self.service.claim_external_submission(self.op, 'op-1')['state']
            except LookupError:
                return 'cancelled-first'
        def cancel():
            try:
                return self.service.cancel_external_submission(self.reviewer, 'op-1')['state']
            except ConflictError:
                return 'claimed-first'
        with ThreadPoolExecutor(max_workers=2) as pool:
            a, b = pool.submit(claim), pool.submit(cancel)
            self.assertIn((a.result(), b.result()), [('unknown', 'claimed-first'), ('cancelled-first', 'cancelled')])
        self.assertEqual(self.count_external(), 0)

    def test_different_remote_payload_cannot_confirm(self):
        self.service.claim_external_submission(self.op, 'op-1')
        self.remote.create('op-1', 'different content')
        with self.assertRaises(ConflictError):
            reconcile(self.service, self.op, 'op-1', self.remote)
        self.assertEqual(self.service.get_external_submission(self.op, 'op-1')['state'], 'unknown')

    def test_concurrent_dispatch_sends_at_most_once(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: dispatch(self.service, self.op, 'op-1', self.remote), range(4)))
        self.assertTrue(all(item['state'] in ('unknown', 'confirmed') for item in results))
        self.assertEqual(self.service.get_external_submission(self.op, 'op-1')['state'], 'confirmed')
        self.assertEqual(self.count_external(), 1)


if __name__ == '__main__':
    unittest.main()
