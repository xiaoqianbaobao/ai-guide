"""Run against the loopback demo server started separately with server.py."""
import json
from urllib.request import Request, urlopen


BASE = "http://127.0.0.1:8765"


def call(path, token, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode()
    request = Request(BASE + path, data=data, headers={"X-Demo-Token": token, "Content-Type": "application/json"})
    with urlopen(request, timeout=3) as response:
        return json.load(response)


if __name__ == "__main__":
    print("知识查询:", call("/api/ask", "demo-support", {"question": "退款"}))
    draft = call("/api/drafts", "demo-support", {"text": "客户询问退款进度，请人工核实。"})
    draft_id = draft["draft_id"]
    reviewed = call("/api/drafts/" + draft_id, "demo-support-reviewer")
    print("待审草稿:", reviewed)
    print("审批结果:", call("/api/approve", "demo-support-reviewer",
                        {"draft_id": draft_id, "reviewed_version": reviewed["version"]}))
    # A fresh ID must be generated once and persisted by a real client before sending.
    import uuid
    payload = {"draft_id": draft_id, "operation_id": uuid.uuid4().hex}
    print("首次提交:", call("/api/submit", "demo-support", payload))
    print("重复提交:", call("/api/submit", "demo-support", payload))
