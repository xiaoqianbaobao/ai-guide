"""Offline training service. Demo identities are NOT real authentication."""
from dataclasses import dataclass
from contextlib import closing
import hashlib
import sqlite3
import time
import uuid


@dataclass(frozen=True)
class Identity:
    user: str
    tenant: str
    role: str


IDENTITIES = {
    "demo-support": Identity("alice", "support", "operator"),
    "demo-support-reviewer": Identity("bob", "support", "reviewer"),
    "demo-hr": Identity("chen", "hr", "operator"),
}


class ConflictError(Exception):
    """The draft changed after the reviewer fetched it."""


def digest(tenant: str, text: str) -> str:
    return hashlib.sha256((tenant + "\0" + text).encode()).hexdigest()


class Service:
    def __init__(self, path: str, clock=time.time, approval_ttl=300):
        self.path = path
        self.clock = clock
        self.approval_ttl = approval_ttl
        with closing(self.connect()) as db, db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, tenant TEXT NOT NULL, text TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS drafts(id TEXT PRIMARY KEY, tenant TEXT NOT NULL, creator TEXT NOT NULL,
                text TEXT NOT NULL, digest TEXT NOT NULL, approved_digest TEXT, approved_by TEXT);
            CREATE TABLE IF NOT EXISTS tickets(operation_id TEXT PRIMARY KEY, draft_id TEXT NOT NULL UNIQUE,
                tenant TEXT NOT NULL, text TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, tenant TEXT NOT NULL,
                actor TEXT NOT NULL, action TEXT NOT NULL, object_id TEXT NOT NULL);
            """)
            columns = {row["name"] for row in db.execute("PRAGMA table_info(drafts)")}
            if "approved_until" not in columns:
                # Existing demo approvals have no expiry and must be re-approved.
                db.execute("ALTER TABLE drafts ADD COLUMN approved_until REAL")
            db.executemany("INSERT OR IGNORE INTO documents VALUES (?, ?, ?)", [
                ("refund-v1", "support", "退款申请需要核对订单和付款状态。"),
                ("payroll-v1", "hr", "薪酬调整需要人事负责人审批。"),
            ])

    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def audit(db, identity: Identity, action: str, object_id: str):
        db.execute("INSERT INTO audit(tenant, actor, action, object_id) VALUES (?, ?, ?, ?)",
                   (identity.tenant, identity.user, action, object_id))

    def ask(self, identity: Identity, question: str) -> dict:
        if not isinstance(question, str) or not question.strip() or len(question) > 500:
            raise ValueError("question must be 1–500 characters")
        with closing(self.connect()) as db, db:
            rows = db.execute("SELECT id, text FROM documents WHERE tenant = ?", (identity.tenant,)).fetchall()
            matches = [row for row in rows if question.strip() in row["text"]]
            self.audit(db, identity, "ask", "knowledge")
        if not matches:
            return {"status": "insufficient_evidence", "answer": "现有授权资料不足，无法确认。", "sources": []}
        return {"status": "answered", "answer": matches[0]["text"], "sources": [matches[0]["id"]]}

    def create_draft(self, identity: Identity, text: str) -> dict:
        if identity.role != "operator":
            raise PermissionError("operator required")
        if not isinstance(text, str) or not text.strip() or len(text) > 1000:
            raise ValueError("text must be 1–1000 characters")
        draft_id = uuid.uuid4().hex
        with closing(self.connect()) as db, db:
            db.execute("INSERT INTO drafts(id, tenant, creator, text, digest) VALUES (?, ?, ?, ?, ?)",
                       (draft_id, identity.tenant, identity.user, text, digest(identity.tenant, text)))
            self.audit(db, identity, "draft_created", draft_id)
        return {"draft_id": draft_id, "status": "awaiting_approval"}

    def get_draft(self, identity: Identity, draft_id: str) -> dict:
        with closing(self.connect()) as db:
            row = db.execute("SELECT id, tenant, text, creator, approved_by, approved_until FROM drafts WHERE id = ? AND tenant = ?",
                             (draft_id, identity.tenant)).fetchone()
        if not row:
            raise LookupError("draft not found")
        return {"id": row["id"], "text": row["text"], "creator": row["creator"],
                "approved_by": row["approved_by"], "approved_until": row["approved_until"],
                "version": digest(row["tenant"], row["text"])}

    def approve(self, identity: Identity, draft_id: str, reviewed_version: str) -> dict:
        if identity.role != "reviewer":
            raise PermissionError("reviewer required")
        if not isinstance(reviewed_version, str) or len(reviewed_version) != 64:
            raise ValueError("reviewed version required")
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM drafts WHERE id = ? AND tenant = ?", (draft_id, identity.tenant)).fetchone()
            if not row:
                raise LookupError("draft not found")
            if db.execute("SELECT 1 FROM tickets WHERE draft_id = ?", (draft_id,)).fetchone():
                raise ConflictError("ticket already submitted")
            current = digest(row["tenant"], row["text"])
            if reviewed_version != current:
                raise ConflictError("draft changed after review")
            expires = self.clock() + self.approval_ttl
            db.execute("UPDATE drafts SET approved_digest = ?, approved_by = ?, approved_until = ? WHERE id = ?",
                       (current, identity.user, expires, draft_id))
            self.audit(db, identity, "draft_approved", draft_id)
        return {"draft_id": draft_id, "status": "approved", "approved_until": expires}

    def revoke(self, identity: Identity, draft_id: str) -> dict:
        if identity.role != "reviewer":
            raise PermissionError("reviewer required")
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT approved_digest FROM drafts WHERE id = ? AND tenant = ?",
                             (draft_id, identity.tenant)).fetchone()
            if not row:
                raise LookupError("draft not found")
            if db.execute("SELECT 1 FROM tickets WHERE draft_id = ?", (draft_id,)).fetchone():
                raise ConflictError("ticket already submitted")
            if row["approved_digest"]:
                db.execute("UPDATE drafts SET approved_digest = NULL, approved_by = NULL, approved_until = NULL WHERE id = ?", (draft_id,))
                self.audit(db, identity, "approval_revoked", draft_id)
        return {"draft_id": draft_id, "status": "revoked"}

    def submit(self, identity: Identity, draft_id: str, operation_id: str) -> dict:
        if identity.role != "operator":
            raise PermissionError("operator required")
        if not isinstance(operation_id, str) or not operation_id.strip() or len(operation_id) > 128:
            raise ValueError("operation_id must be 1–128 characters")
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM drafts WHERE id = ? AND tenant = ?", (draft_id, identity.tenant)).fetchone()
            if not row:
                raise LookupError("draft not found")
            existing = db.execute("SELECT * FROM tickets WHERE operation_id = ? OR draft_id = ?", (operation_id, draft_id)).fetchone()
            if existing:
                if existing["operation_id"] != operation_id or existing["draft_id"] != draft_id or existing["tenant"] != identity.tenant:
                    raise ValueError("operation ID or draft already used")
                return {"ticket_id": existing["operation_id"], "status": "submitted", "replayed": True}
            if (not row["approved_digest"] or row["approved_digest"] != digest(row["tenant"], row["text"])
                    or row["approved_until"] is None or self.clock() >= row["approved_until"]):
                raise PermissionError("current draft requires unexpired approval")
            db.execute("INSERT INTO tickets VALUES (?, ?, ?, ?)", (operation_id, draft_id, identity.tenant, row["text"]))
            self.audit(db, identity, "ticket_submitted", operation_id)
            return {"ticket_id": operation_id, "status": "submitted", "replayed": False}
