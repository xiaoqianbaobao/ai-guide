import sqlite3
import unittest
from workflow import Approval, Draft, MockTicketService, execute, fingerprint


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.service = MockTicketService(self.db)
        self.draft = Draft("support", "manual-review", "请人工核实退款")
        self.approval = Approval("operation-1", fingerprint(self.draft))

    def count(self):
        return self.db.execute("SELECT count(*) FROM tickets").fetchone()[0]

    def test_response_lost_after_commit_retries_without_duplicate(self):
        with self.assertRaises(TimeoutError):
            execute(self.service, self.draft, self.approval, lose_response=True)
        self.assertEqual(execute(self.service, self.draft, self.approval), "operation-1")
        self.assertEqual(self.count(), 1)

    def test_changed_draft_requires_new_approval(self):
        changed = Draft("support", "external", self.draft.text)
        with self.assertRaises(PermissionError):
            execute(self.service, changed, self.approval)
        self.assertEqual(self.count(), 0)

    def test_operation_id_cannot_be_reused_for_different_draft(self):
        execute(self.service, self.draft, self.approval)
        changed = Draft("support", "manual-review", "另一件事")
        with self.assertRaises(ValueError):
            execute(self.service, changed, Approval("operation-1", fingerprint(changed)))
        self.assertEqual(self.count(), 1)

    def test_two_operations_can_create_two_tickets(self):
        execute(self.service, self.draft, self.approval)
        execute(self.service, self.draft, Approval("operation-2", fingerprint(self.draft)))
        self.assertEqual(self.count(), 2)


if __name__ == "__main__":
    unittest.main()
