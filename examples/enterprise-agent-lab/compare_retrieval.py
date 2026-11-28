"""Offline counterexample: a hand-written alias improves one case but creates another failure."""
from pathlib import Path
from tempfile import TemporaryDirectory

from evaluate_lab import CASES, DEMO_IDENTITY_BY_TENANT, evaluate_service, grade
from service import Service


CHALLENGE = {
    'id': 'keyword-is-not-intent', 'tenant': 'support',
    'question': '“退钱”这两个字的英文怎么拼写？', 'source': None,
    'expected_answer': '现有授权资料不足，无法确认。',
}


class AliasCandidate:
    """Intentionally simplistic candidate used only to demonstrate a false positive."""
    def __init__(self, service):
        self.service = service

    def ask(self, identity, question):
        return self.service.ask(identity, '退款' if '退钱' in question else question)


def compare(service):
    candidate = AliasCandidate(service)
    identity = DEMO_IDENTITY_BY_TENANT[CHALLENGE['tenant']]
    return {
        'baseline': {'development': evaluate_service(service),
                     'challenge': grade(CHALLENGE, service.ask(identity, CHALLENGE['question']))},
        'candidate': {'development': evaluate_service(candidate),
                      'challenge': grade(CHALLENGE, candidate.ask(identity, CHALLENGE['question']))},
    }


def main():
    with TemporaryDirectory() as tmp:
        results = compare(Service(str(Path(tmp) / 'comparison.sqlite3')))
    for label, result in results.items():
        passed = sum(row['task_pass'] for row in result['development'])
        print(f"{label}: 开发任务 {passed}/{len(CASES)}；反例{'通过' if result['challenge']['task_pass'] else '失败'}")


if __name__ == '__main__':
    main()
