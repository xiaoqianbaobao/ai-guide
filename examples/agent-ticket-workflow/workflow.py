"""Offline teaching example: approved draft and idempotent mock ticket writes."""
from dataclasses import asdict, dataclass
import hashlib
import json
import sqlite3


@dataclass(frozen=True)
class Draft:
    tenant: str
    destination: str
    text: str


def fingerprint(draft: Draft) -> str:
    payload = json.dumps(asdict(draft), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Approval:
    operation_id: str
    draft_fingerprint: str


class MockTicketService:
    """Simulates a downstream system that supports persistent idempotency keys."""

    def __init__(self, connection: sqlite3.Connection):
        self.db = connection
        self.db.execute("CREATE TABLE IF NOT EXISTS tickets (operation_id TEXT PRIMARY KEY, digest TEXT NOT NULL, payload TEXT NOT NULL)")

    def create(self, operation_id: str, draft: Draft, *, lose_response: bool = False) -> str:
        digest = fingerprint(draft)
        payload = json.dumps(asdict(draft), ensure_ascii=False, sort_keys=True)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO tickets VALUES (?, ?, ?)", (operation_id, digest, payload))
            existing = self.db.execute("SELECT digest FROM tickets WHERE operation_id = ?", (operation_id,)).fetchone()
            if existing is None or existing[0] != digest:
                raise ValueError("operation ID already used for different content")
        # Deliberately fail *after* the database transaction committed.
        if lose_response:
            raise TimeoutError("response lost after commit")
        return operation_id


def execute(service: MockTicketService, draft: Draft, approval: Approval, *, lose_response: bool = False) -> str:
    if not approval.operation_id or approval.draft_fingerprint != fingerprint(draft):
        raise PermissionError("draft does not match approval")
    return service.create(approval.operation_id, draft, lose_response=lose_response)


def main() -> None:
    db = sqlite3.connect(":memory:")
    service = MockTicketService(db)
    draft = Draft("demo-support", "manual-review", "客户询问退款进度，请人工核实。")
    approval = Approval("example-operation-001", fingerprint(draft))
    try:
        execute(service, draft, approval, lose_response=True)
    except TimeoutError:
        print("响应丢失：结果未知；使用相同操作 ID 重试模拟服务。")
    print("工单 ID：", execute(service, draft, approval))
    print("工单数量：", db.execute("SELECT count(*) FROM tickets").fetchone()[0])


if __name__ == "__main__":
    main()
