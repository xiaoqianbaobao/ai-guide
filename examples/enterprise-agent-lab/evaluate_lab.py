"""Run the teaching evaluation set against a fresh local Service, without a model or network."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys

# Reuse the fictional cases and grading rules from the preceding course module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'knowledge-assistant-eval'))
from evaluate import CASES, grade  # noqa: E402
from service import IDENTITIES, Service

DEMO_IDENTITY_BY_TENANT = {'support': IDENTITIES['demo-support'], 'hr': IDENTITIES['demo-hr']}


def evaluate_service(service):
    """Collect results from the actual service; identity is chosen by the harness."""
    results = []
    for case in CASES:
        identity = DEMO_IDENTITY_BY_TENANT[case['tenant']]
        result = service.ask(identity, case['question'])
        results.append(grade(case, result))
    return results


def main():
    # Never evaluate or modify an existing lab database by accident.
    with TemporaryDirectory() as tmp:
        service = Service(str(Path(tmp) / 'eval.sqlite3'))
        results = evaluate_service(service)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"任务通过：{sum(row['task_pass'] for row in results)}/{len(results)}")
    print(f"检测到越权：{sum(row['unauthorized'] for row in results)}")


if __name__ == '__main__':
    main()
