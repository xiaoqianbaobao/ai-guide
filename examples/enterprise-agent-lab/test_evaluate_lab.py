from pathlib import Path
from contextlib import closing
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from evaluate_lab import evaluate_service
from evaluate import DOCUMENTS
from service import Service


class LabEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.service = Service(str(Path(self.tmp.name) / 'eval.sqlite3'))

    def test_real_service_has_documented_baseline(self):
        results = evaluate_service(self.service)
        self.assertEqual([r['task_pass'] for r in results], [True, True, True, False])
        self.assertFalse(any(r['unauthorized'] for r in results))

    def test_service_seed_and_grading_fixtures_match(self):
        with closing(self.service.connect()) as db:
            actual = {(r['id'], r['tenant'], r['text']) for r in db.execute('SELECT id, tenant, text FROM documents')}
        expected = {(d.id, d.tenant, d.text) for d in DOCUMENTS}
        self.assertEqual(actual, expected)

    def test_harness_flags_injected_unauthorized_service_response(self):
        ask = self.service.ask
        def leaky(identity, question):
            if question == '薪酬':
                return {'answer': '薪酬调整需要人事负责人审批。', 'sources': ['payroll-v1']}
            return ask(identity, question)
        with patch.object(self.service, 'ask', side_effect=leaky):
            results = evaluate_service(self.service)
        self.assertTrue(results[2]['unauthorized'])
        self.assertFalse(results[2]['task_pass'])


if __name__ == '__main__':
    unittest.main()
