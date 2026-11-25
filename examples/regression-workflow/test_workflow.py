import unittest
from workflow import Task


class StateMachineTests(unittest.TestCase):
    def test_review_cannot_be_skipped(self):
        task = Task("example")
        with self.assertRaises(ValueError):
            task.apply("1", "deployment_finished")
        self.assertEqual(task.state, "investigating")
        self.assertNotIn("1", task.seen_events)

    def test_repeated_event_is_ignored(self):
        task = Task("example")
        self.assertTrue(task.apply("1", "diagnosis_ready"))
        self.assertFalse(task.apply("1", "diagnosis_ready"))
        self.assertEqual(task.state, "awaiting_review")

    def test_failed_recovery_returns_to_investigation(self):
        task = Task("example")
        for event_id, event in [("1", "diagnosis_ready"), ("2", "review_approved"),
                                ("3", "deployment_finished"), ("4", "still_regressed")]:
            task.apply(event_id, event)
        self.assertEqual(task.state, "investigating")

    def test_conflicting_duplicate_event_is_rejected(self):
        task = Task("example")
        task.apply("1", "diagnosis_ready")
        with self.assertRaises(ValueError):
            task.apply("1", "review_approved")
        self.assertEqual(task.state, "awaiting_review")

    def test_resolution_requires_recovery_check(self):
        task = Task("example")
        for event_id, event in [("1", "diagnosis_ready"), ("2", "review_approved"),
                                ("3", "deployment_finished"), ("4", "recovered")]:
            task.apply(event_id, event)
        self.assertEqual(task.state, "resolved")


if __name__ == "__main__":
    unittest.main()
