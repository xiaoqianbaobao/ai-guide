"""A tiny, offline evaluation harness; all records below are fictional."""
from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Document:
    id: str
    tenant: str
    text: str


DOCUMENTS = (
    Document("refund-v1", "support", "退款申请需要核对订单和付款状态。"),
    Document("payroll-v1", "hr", "薪酬调整需要人事负责人审批。"),
)


def assistant(tenant: str, question: str) -> dict:
    """Exact substring retrieval provides a deliberately weak baseline."""
    matches = [d for d in DOCUMENTS if d.tenant == tenant and question in d.text]
    if not matches:
        return {"answer": "现有授权资料不足，无法确认。", "sources": []}
    return {"answer": matches[0].text, "sources": [matches[0].id]}


CASES = (
    {"id": "known", "tenant": "support", "question": "退款", "source": "refund-v1",
     "expected_answer": "退款申请需要核对订单和付款状态。"},
    {"id": "unknown", "tenant": "support", "question": "不存在的问题", "source": None,
     "expected_answer": "现有授权资料不足，无法确认。"},
    {"id": "cross-tenant", "tenant": "support", "question": "薪酬", "source": None,
     "expected_answer": "现有授权资料不足，无法确认。"},
    # This natural-language paraphrase is intentionally hard for the baseline.
    {"id": "paraphrase", "tenant": "support", "question": "怎么申请退钱", "source": "refund-v1",
     "expected_answer": "退款申请需要核对订单和付款状态。"},
)


def grade(case: dict, result: dict) -> dict:
    allowed = {d.id for d in DOCUMENTS if d.tenant == case["tenant"]}
    forbidden_text = [d.text for d in DOCUMENTS if d.tenant != case["tenant"]]
    sources = result["sources"]
    unauthorized = any(source not in allowed for source in sources) or any(
        text in result["answer"] for text in forbidden_text
    )
    citation_pass = not sources if case["source"] is None else case["source"] in sources
    # Exact match is deliberately strict and only appropriate for this fixed demo.
    answer_pass = result["answer"] == case["expected_answer"]
    return {"id": case["id"], "citation_pass": citation_pass, "answer_pass": answer_pass,
            "task_pass": citation_pass and answer_pass, "unauthorized": unauthorized}


def main() -> None:
    results = [grade(case, assistant(case["tenant"], case["question"])) for case in CASES]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"任务通过：{sum(row['task_pass'] for row in results)}/{len(results)}")
    print(f"检测到越权：{sum(row['unauthorized'] for row in results)}")


if __name__ == "__main__":
    main()
