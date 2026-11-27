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

    def test_correct_citation_does_not_make_wrong_answer_pass(self):
        result = {"answer": "所有订单都可以退款。", "sources": ["refund-v1"]}
        graded = grade(CASES[0], result)
        self.assertFalse(graded["task_pass"])
        self.assertTrue(graded["citation_pass"])
        self.assertFalse(graded["answer_pass"])

    def test_same_meaning_different_words_can_fail_exact_match(self):
        result = {"answer": "退款前应检查订单及付款状态。", "sources": ["refund-v1"]}
        graded = grade(CASES[0], result)
        self.assertFalse(graded["answer_pass"])


if __name__ == "__main__":
    unittest.main()
