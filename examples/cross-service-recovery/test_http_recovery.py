from contextlib import closing
from io import BytesIO
from multiprocessing import Process, Queue
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from http_downstream import HttpDownstream, make_server
from recovery import Coordinator


def serve(path, queue):
    server = make_server(path)
    queue.put(server.server_port)
    server.serve_forever()


class HttpRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.queue = Queue()
        self.process = Process(target=serve, args=(str(self.root / "external.sqlite3"), self.queue))
        self.process.start()
        port = self.queue.get(timeout=10)
        self.remote = HttpDownstream(port, timeout=1)
        self.coordinator = Coordinator(str(self.root / "local.sqlite3"), self.remote)
        self.coordinator.prepare("http-operation", "请人工核实退款")

    def tearDown(self):
        if self.process.is_alive():
            self.process.terminate()
        self.process.join(timeout=5)
        self.queue.close()
        self.queue.join_thread()
        self.tmp.cleanup()

    def count_external(self):
        with closing(sqlite3.connect(self.root / "external.sqlite3")) as db:
            return db.execute("SELECT count(*) FROM tickets").fetchone()[0]

    def test_connection_dropped_after_commit_then_reconciled(self):
        self.assertEqual(self.coordinator.dispatch("http-operation", lose_response=True)["state"], "unknown")
        self.assertEqual(self.count_external(), 1)
        restarted = Coordinator(self.coordinator.path, self.remote)
        self.assertEqual(restarted.reconcile("http-operation")["state"], "confirmed")
        self.assertEqual(restarted.dispatch("http-operation")["receipt"], "http-operation")
        self.assertEqual(self.count_external(), 1)

    def test_crash_after_http_success_then_reconciled(self):
        with self.assertRaises(RuntimeError):
            self.coordinator.dispatch("http-operation", crash_after_write=True)
        self.assertEqual(self.coordinator.state("http-operation")["state"], "pending")
        self.assertEqual(self.coordinator.reconcile("http-operation")["state"], "confirmed")
        self.assertEqual(self.count_external(), 1)

    def test_server_unavailable_preserves_unknown(self):
        self.process.terminate()
        self.process.join(timeout=5)
        self.assertEqual(self.coordinator.reconcile("http-operation")["state"], "unknown")

    def test_confirmed_receipt_survives_downstream_outage(self):
        before = self.coordinator.dispatch("http-operation")
        self.assertEqual(before["state"], "confirmed")
        self.process.terminate()
        self.process.join(timeout=5)
        restarted = Coordinator(self.coordinator.path, self.remote)
        self.assertEqual(restarted.reconcile("http-operation"), before)

    def test_invalid_success_response_remains_unknown_then_recovers(self):
        # Simulate a committed downstream write followed by an unusable 200 response.
        self.remote.create("http-operation", "请人工核实退款")
        for body in (b'{broken', b'{}', b'{"receipt": null}'):
            with self.subTest(body=body), patch("http_downstream.urlopen", return_value=BytesIO(body)):
                state = self.coordinator.dispatch("http-operation")
                self.assertEqual(state["state"], "unknown")
                self.assertIsNone(state["receipt"])
        self.assertEqual(self.coordinator.reconcile("http-operation")["state"], "confirmed")
        self.assertEqual(self.count_external(), 1)

    def test_invalid_lookup_response_remains_unknown(self):
        for body in (b'{broken', b'{}', b'{"receipt": null, "digest": "bad"}'):
            with self.subTest(body=body), patch("http_downstream.urlopen", return_value=BytesIO(body)):
                self.assertEqual(self.coordinator.reconcile("http-operation")["state"], "unknown")

    def test_receipt_for_another_operation_cannot_confirm_write(self):
        body = b'{"receipt":"wrong-operation"}'
        with patch("http_downstream.urlopen", return_value=BytesIO(body)):
            state = self.coordinator.dispatch("http-operation")
        self.assertEqual(state["state"], "unknown")
        self.assertIsNone(state["receipt"])

    def test_receipt_for_another_operation_cannot_confirm_lookup(self):
        from recovery import fingerprint
        import json
        body = json.dumps({"receipt": "wrong-operation", "digest": fingerprint("请人工核实退款")}).encode()
        with patch("http_downstream.urlopen", return_value=BytesIO(body)):
            state = self.coordinator.reconcile("http-operation")
        self.assertEqual(state["state"], "unknown")
        self.assertIsNone(state["receipt"])

    def test_conflicting_payload_is_rejected(self):
        self.remote.create("http-operation", "第一份内容")
        with self.assertRaises(ValueError):
            self.remote.create("http-operation", "不同内容")
        with self.assertRaises(ValueError):
            self.coordinator.reconcile("http-operation")
        self.assertEqual(self.count_external(), 1)


if __name__ == "__main__":
    unittest.main()
