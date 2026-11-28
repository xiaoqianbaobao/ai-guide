from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from compare_retrieval import compare
from service import Service


class ComparisonTests(unittest.TestCase):
    def test_alias_improves_development_case_but_fails_unrelated_question(self):
        with TemporaryDirectory() as tmp:
            results = compare(Service(str(Path(tmp) / 'test.sqlite3')))
        self.assertEqual(sum(x['task_pass'] for x in results['baseline']['development']), 3)
        self.assertEqual(sum(x['task_pass'] for x in results['candidate']['development']), 4)
        self.assertTrue(results['baseline']['challenge']['task_pass'])
        self.assertFalse(results['candidate']['challenge']['task_pass'])
        self.assertFalse(results['candidate']['challenge']['unauthorized'])


if __name__ == '__main__':
    unittest.main()
