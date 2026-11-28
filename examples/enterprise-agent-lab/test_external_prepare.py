"""Reservation tests: no HTTP endpoint or external side effect is implemented."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from service import ConflictError, IDENTITIES, Service


class ExternalPreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.now = 1000
        self.service = Service(str(Path(self.tmp.name) / "lab.sqlite3"), clock=lambda: self.now)
        self.operator = IDENTITIES["demo-support"]
        self.reviewer = IDENTITIES["demo-support-reviewer"]
        self.draft = self.service.create_draft(self.operator, "请核实退款")['draft_id']

    def approve(self):
        draft = self.service.get_draft(self.reviewer, self.draft)
        self.service.approve(self.reviewer, self.draft, draft['version'])
        return draft

    def test_reservation_requires_current_approval_and_tenant(self):
        with self.assertRaises(PermissionError):
            self.service.prepare_external_submission(self.operator, self.draft, "op")
        self.approve()
        with self.assertRaises(LookupError):
            self.service.prepare_external_submission(IDENTITIES['demo-hr'], self.draft, "op")
        self.now += 300
        with self.assertRaises(PermissionError):
            self.service.prepare_external_submission(self.operator, self.draft, "op")
        with closing(sqlite3.connect(self.service.path)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM external_operations").fetchone()[0], 0)

    def test_reservation_is_durable_and_locks_competing_actions(self):
        draft = self.approve()
        self.assertFalse(self.service.prepare_external_submission(self.operator, self.draft, "op")['replayed'])
        restarted = Service(self.service.path, clock=lambda: self.now)
        self.assertTrue(restarted.prepare_external_submission(self.operator, self.draft, "op")['replayed'])
        with closing(sqlite3.connect(self.service.path)) as db:
            snapshot = db.execute("SELECT tenant, text, approved_version, approved_by, state FROM external_operations").fetchone()
        self.assertEqual(snapshot, ('support', '请核实退款', draft['version'], 'bob', 'prepared'))
        for action in (
            lambda: restarted.update_draft(self.operator, self.draft, draft['version'], '修改'),
            lambda: restarted.revoke(self.reviewer, self.draft),
            lambda: restarted.approve(self.reviewer, self.draft, draft['version']),
            lambda: restarted.submit(self.operator, self.draft, 'other'),
            lambda: restarted.prepare_external_submission(self.operator, self.draft, 'other'),
        ):
            with self.assertRaises(ConflictError):
                action()

    def test_operation_id_cannot_cross_local_and_external_flows(self):
        self.approve()
        self.service.prepare_external_submission(self.operator, self.draft, 'shared')
        other = self.service.create_draft(self.operator, '第二份草稿')['draft_id']
        version = self.service.get_draft(self.reviewer, other)['version']
        self.service.approve(self.reviewer, other, version)
        with self.assertRaises(ConflictError):
            self.service.submit(self.operator, other, 'shared')
        with self.assertRaises(ConflictError):
            self.service.prepare_external_submission(self.operator, other, 'shared')

    def test_local_ticket_id_cannot_be_reserved_by_another_draft(self):
        self.approve()
        self.service.submit(self.operator, self.draft, 'shared')
        other = self.service.create_draft(self.operator, '第二份草稿')['draft_id']
        version = self.service.get_draft(self.reviewer, other)['version']
        self.service.approve(self.reviewer, other, version)
        with self.assertRaises(ConflictError):
            self.service.prepare_external_submission(self.operator, other, 'shared')

    def test_concurrent_same_reservation_creates_one_record(self):
        self.approve()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.service.prepare_external_submission(self.operator, self.draft, 'same'), range(4)))
        self.assertEqual(sum(not result['replayed'] for result in results), 1)
        with closing(sqlite3.connect(self.service.path)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM external_operations").fetchone()[0], 1)

    def test_reservation_and_revoke_have_one_winner(self):
        self.approve()
        def reserve():
            try:
                self.service.prepare_external_submission(self.operator, self.draft, 'op')
                return 'reserved'
            except PermissionError:
                return 'not-approved'
        def revoke():
            try:
                self.service.revoke(self.reviewer, self.draft)
                return 'revoked'
            except ConflictError:
                return 'already-reserved'
        with ThreadPoolExecutor(max_workers=2) as pool:
            a, b = pool.submit(reserve), pool.submit(revoke)
            self.assertIn((a.result(), b.result()),
                          [('reserved', 'already-reserved'), ('not-approved', 'revoked')])

    def test_replay_after_expiry_does_not_extend_approval(self):
        self.approve()
        self.service.prepare_external_submission(self.operator, self.draft, 'op')
        self.now += 301
        self.assertTrue(self.service.prepare_external_submission(self.operator, self.draft, 'op')['replayed'])
        with closing(sqlite3.connect(self.service.path)) as db:
            self.assertEqual(db.execute('SELECT approved_until, state FROM external_operations').fetchone(), (1300, 'prepared'))

    def test_cancel_unlocks_draft_but_requires_new_approval_and_id(self):
        self.approve()
        self.service.prepare_external_submission(self.operator, self.draft, 'old')
        result = self.service.cancel_external_submission(self.reviewer, 'old')
        self.assertFalse(result['replayed'])
        self.assertTrue(self.service.cancel_external_submission(self.reviewer, 'old')['replayed'])
        with self.assertRaises(PermissionError):
            self.service.prepare_external_submission(self.operator, self.draft, 'new')
        self.approve()
        with self.assertRaises(ConflictError):
            self.service.prepare_external_submission(self.operator, self.draft, 'old')
        with self.assertRaises(ConflictError):
            self.service.submit(self.operator, self.draft, 'old')
        self.assertEqual(self.service.prepare_external_submission(self.operator, self.draft, 'new')['state'], 'prepared')
        self.assertTrue(self.service.cancel_external_submission(self.reviewer, 'old')['replayed'])
        with closing(sqlite3.connect(self.service.path)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM audit WHERE action = 'external_submission_cancelled'").fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT operation_id, cancelled_by FROM cancelled_external_operations').fetchone(), ('old', 'bob'))
            self.assertEqual(db.execute('SELECT operation_id FROM external_operations').fetchone()[0], 'new')

    def test_cancel_requires_reviewer_same_tenant_and_unsent_state(self):
        self.approve()
        self.service.prepare_external_submission(self.operator, self.draft, 'op')
        with self.assertRaises(PermissionError):
            self.service.cancel_external_submission(self.operator, 'op')
        with self.assertRaises(LookupError):
            self.service.cancel_external_submission(IDENTITIES['demo-hr-reviewer'], 'op')
        with closing(sqlite3.connect(self.service.path)) as db, db:
            db.execute("UPDATE external_operations SET state = 'unknown' WHERE operation_id = 'op'")
        with self.assertRaises(ConflictError):
            self.service.cancel_external_submission(self.reviewer, 'op')
        with closing(sqlite3.connect(self.service.path)) as db:
            self.assertEqual(db.execute('SELECT state FROM external_operations').fetchone()[0], 'unknown')
            self.assertEqual(db.execute('SELECT count(*) FROM cancelled_external_operations').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
