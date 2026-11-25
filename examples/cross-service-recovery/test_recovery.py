from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from recovery import Coordinator, MockDownstream


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.external = MockDownstream(str(self.root / "external.sqlite3"))
        self.local = Coordinator(str(self.root / "local.sqlite3"), self.external)
        self.local.prepare("operation-1", "请人工核实退款")

    def count_external(self):
        with closing(sqlite3.connect(self.external.path)) as db:
            return db.execute("SELECT count(*) FROM tickets").fetchone()[0]

    def test_lost_response_recovers_after_restart(self):
        self.assertEqual(self.local.dispatch("operation-1", lose_response=True)["state"], "unknown")
        restarted = Coordinator(self.local.path, self.external)
        self.assertEqual(restarted.reconcile("operation-1")["state"], "confirmed")
        self.assertEqual(restarted.dispatch("operation-1")["receipt"], "operation-1")
        self.assertEqual(self.count_external(), 1)

    def test_crash_after_external_write_recovers_pending_operation(self):
        with self.assertRaises(RuntimeError):
            self.local.dispatch("operation-1", crash_after_write=True)
        self.assertEqual(self.local.state("operation-1")["state"], "pending")
        self.assertEqual(Coordinator(self.local.path, self.external).reconcile("operation-1")["state"], "confirmed")
        self.assertEqual(self.count_external(), 1)

    def test_missing_lookup_does_not_claim_failure(self):
        self.assertEqual(self.local.reconcile("operation-1")["state"], "unknown")
        self.assertEqual(self.count_external(), 0)

    def test_retry_with_same_id_does_not_duplicate(self):
        self.local.dispatch("operation-1", lose_response=True)
        self.assertEqual(self.local.dispatch("operation-1")["state"], "confirmed")
        self.assertEqual(self.count_external(), 1)

    def test_operation_id_reuse_with_changed_content_is_rejected(self):
        with self.assertRaises(ValueError):
            self.local.prepare("operation-1", "另一张工单")
        self.external.create("operation-1", "冲突内容")
        with self.assertRaises(ValueError):
            self.local.reconcile("operation-1")


if __name__ == "__main__":
    unittest.main()
