import unittest
from evaluate import CASES, assistant, grade


class EvaluationTests(unittest.TestCase):
    def test_expected_baseline_failure_is_visible(self):
        results = [grade(case, assistant(case["tenant"], case["question"])) for case in CASES]
        self.assertEqual([r["task_pass"] for r in results], [True, True, True, False])
        self.assertFalse(any(r["unauthorized"] for r in results))

    def test_leak_is_flagged_even_if_answer_claims_to_refuse(self):
        result = {"answer": "现有授权资料不足，无法确认。", "sources": ["payroll-v1"]}
        self.assertTrue(grade(CASES[2], result)["unauthorized"])

    def test_private_content_in_answer_is_flagged(self):
        result = {"answer": "薪酬调整需要人事负责人审批。", "sources": []}
        self.assertTrue(grade(CASES[2], result)["unauthorized"])


if __name__ == "__main__":
    unittest.main()
