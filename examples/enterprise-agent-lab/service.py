"""Offline training service. Demo identities are NOT real authentication."""
from dataclasses import dataclass
from contextlib import closing
import hashlib
import json
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
    "demo-hr-reviewer": Identity("dana", "hr", "reviewer"),
}


class ConflictError(Exception):
    """A reviewed resource changed or was withdrawn before a write."""


def digest(tenant: str, text: str) -> str:
    return hashlib.sha256((tenant + "\0" + text).encode()).hexdigest()


def approval_version(tenant: str, draft_id: str, creator: str, text: str, revision: int) -> str:
    # A version identifies the reviewed draft and its creator, not just its text.
    payload = json.dumps([tenant, draft_id, creator, text, revision], ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


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
            CREATE TABLE IF NOT EXISTS external_operations(operation_id TEXT PRIMARY KEY,
                draft_id TEXT NOT NULL UNIQUE, tenant TEXT NOT NULL, text TEXT NOT NULL,
                approved_version TEXT NOT NULL, approved_by TEXT NOT NULL,
                approved_until REAL NOT NULL, state TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS cancelled_external_operations(operation_id TEXT PRIMARY KEY,
                draft_id TEXT NOT NULL, tenant TEXT NOT NULL, approved_version TEXT NOT NULL,
                approved_by TEXT NOT NULL, cancelled_by TEXT NOT NULL, cancelled_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, tenant TEXT NOT NULL,
                actor TEXT NOT NULL, action TEXT NOT NULL, object_id TEXT NOT NULL);
            """)
            columns = {row["name"] for row in db.execute("PRAGMA table_info(drafts)")}
            if "approved_until" not in columns:
                # Existing demo approvals have no expiry and must be re-approved.
                db.execute("ALTER TABLE drafts ADD COLUMN approved_until REAL")
            if "revision" not in columns:
                db.execute("ALTER TABLE drafts ADD COLUMN revision INTEGER NOT NULL DEFAULT 1")
            document_columns = {row["name"] for row in db.execute("PRAGMA table_info(documents)")}
            if "revision" not in document_columns:
                db.execute("ALTER TABLE documents ADD COLUMN revision INTEGER NOT NULL DEFAULT 1")
            if "active" not in document_columns:
                db.execute("ALTER TABLE documents ADD COLUMN active INTEGER NOT NULL DEFAULT 1")
            db.execute("""CREATE TABLE IF NOT EXISTS document_history(
                document_id TEXT NOT NULL, tenant TEXT NOT NULL, revision INTEGER NOT NULL,
                text TEXT NOT NULL, active INTEGER NOT NULL,
                PRIMARY KEY(document_id, revision))""")
            db.executemany("INSERT OR IGNORE INTO documents(id, tenant, text) VALUES (?, ?, ?)", [
                ("refund-v1", "support", "退款申请需要核对订单和付款状态。"),
                ("payroll-v1", "hr", "薪酬调整需要人事负责人审批。"),
            ])
            db.execute("""INSERT OR IGNORE INTO document_history
                SELECT id, tenant, revision, text, active FROM documents""")

    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def audit(db, identity: Identity, action: str, object_id: str):
        db.execute("INSERT INTO audit(tenant, actor, action, object_id) VALUES (?, ?, ?, ?)",
                   (identity.tenant, identity.user, action, object_id))

    @staticmethod
    def ensure_no_external_operation(db, draft_id):
        if db.execute("SELECT 1 FROM external_operations WHERE draft_id = ?", (draft_id,)).fetchone():
            raise ConflictError("external submission already prepared")

    def ask(self, identity: Identity, question: str) -> dict:
        if not isinstance(question, str) or not question.strip() or len(question) > 500:
            raise ValueError("question must be 1–500 characters")
        with closing(self.connect()) as db, db:
            rows = db.execute("SELECT id, text, revision FROM documents WHERE tenant = ? AND active = 1", (identity.tenant,)).fetchall()
            matches = [row for row in rows if question.strip() in row["text"]]
            self.audit(db, identity, "ask", "knowledge")
        if not matches:
            return {"status": "insufficient_evidence", "answer": "现有授权资料不足，无法确认。", "sources": []}
        return {"status": "answered", "answer": matches[0]["text"], "sources": [matches[0]["id"]],
                "source_versions": [{"id": matches[0]["id"], "revision": matches[0]["revision"]}]}

    def get_document(self, identity: Identity, document_id: str) -> dict:
        if identity.role != "reviewer":
            raise PermissionError("reviewer required")
        with closing(self.connect()) as db:
            row = db.execute("SELECT id, text, revision, active FROM documents WHERE id = ? AND tenant = ?",
                             (document_id, identity.tenant)).fetchone()
        if not row:
            raise LookupError("document not found")
        return dict(row)

    def sources_are_current(self, identity: Identity, versions) -> bool:
        """Check all retrieved versions against one database read snapshot."""
        if not versions:
            return False
        with closing(self.connect()) as db:
            db.execute("BEGIN")
            for document_id, revision in versions:
                row = db.execute("""SELECT revision, active FROM documents
                    WHERE id = ? AND tenant = ?""", (document_id, identity.tenant)).fetchone()
                if not row or not row["active"] or row["revision"] != revision:
                    return False
        return True

    def change_document(self, identity: Identity, document_id: str, expected_revision: int,
                        text: str = "", withdraw: bool = False) -> dict:
        if identity.role != "reviewer":
            raise PermissionError("reviewer required")
        if (not isinstance(document_id, str) or not document_id.strip()
                or type(expected_revision) is not int or expected_revision < 1
                or not isinstance(withdraw, bool)):
            raise ValueError("document and revision required")
        if not withdraw and (not isinstance(text, str) or not text.strip() or len(text) > 1000):
            raise ValueError("document text must be 1–1000 characters")
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM documents WHERE id = ? AND tenant = ?",
                             (document_id, identity.tenant)).fetchone()
            if not row:
                raise LookupError("document not found")
            if not row["active"] or row["revision"] != expected_revision:
                raise ConflictError("document changed or withdrawn")
            revision, active = row["revision"] + 1, 0 if withdraw else 1
            new_text = row["text"] if withdraw else text
            db.execute("UPDATE documents SET text = ?, revision = ?, active = ? WHERE id = ? AND tenant = ?",
                       (new_text, revision, active, document_id, identity.tenant))
            db.execute("INSERT INTO document_history VALUES (?, ?, ?, ?, ?)",
                       (document_id, identity.tenant, revision, new_text, active))
            self.audit(db, identity, "document_withdrawn" if withdraw else "document_updated", document_id)
        return {"id": document_id, "revision": revision, "active": bool(active)}

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
            row = db.execute("SELECT id, tenant, text, creator, revision, approved_by, approved_until FROM drafts WHERE id = ? AND tenant = ?",
                             (draft_id, identity.tenant)).fetchone()
        if not row:
            raise LookupError("draft not found")
        return {"id": row["id"], "text": row["text"], "creator": row["creator"],
                "approved_by": row["approved_by"], "approved_until": row["approved_until"],
                "revision": row["revision"],
                "version": approval_version(row["tenant"], row["id"], row["creator"], row["text"], row["revision"])}

    def update_draft(self, identity: Identity, draft_id: str, expected_version: str, text: str) -> dict:
        if identity.role != "operator":
            raise PermissionError("operator required")
        if (not isinstance(expected_version, str) or len(expected_version) != 64
                or not isinstance(text, str) or not text.strip() or len(text) > 1000):
            raise ValueError("version and text required")
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM drafts WHERE id = ? AND tenant = ?", (draft_id, identity.tenant)).fetchone()
            if not row:
                raise LookupError("draft not found")
            if row["creator"] != identity.user:
                raise PermissionError("creator required")
            self.ensure_no_external_operation(db, draft_id)
            if db.execute("SELECT 1 FROM tickets WHERE draft_id = ?", (draft_id,)).fetchone():
                raise ConflictError("ticket already submitted")
            current = approval_version(row["tenant"], row["id"], row["creator"], row["text"], row["revision"])
            if current != expected_version:
                raise ConflictError("draft changed")
            revision = row["revision"] + 1
            db.execute("""UPDATE drafts SET text = ?, digest = ?, revision = ?,
                approved_digest = NULL, approved_by = NULL, approved_until = NULL WHERE id = ?""",
                (text, digest(identity.tenant, text), revision, draft_id))
            self.audit(db, identity, "draft_updated", draft_id)
        return {"draft_id": draft_id, "revision": revision,
                "version": approval_version(identity.tenant, draft_id, identity.user, text, revision),
                "status": "awaiting_approval"}

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
            self.ensure_no_external_operation(db, draft_id)
            if db.execute("SELECT 1 FROM tickets WHERE draft_id = ?", (draft_id,)).fetchone():
                raise ConflictError("ticket already submitted")
            current = approval_version(row["tenant"], row["id"], row["creator"], row["text"], row["revision"])
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
            self.ensure_no_external_operation(db, draft_id)
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
            self.ensure_no_external_operation(db, draft_id)
            if db.execute("SELECT 1 FROM external_operations WHERE operation_id = ?", (operation_id,)).fetchone():
                raise ConflictError("operation ID already reserved")
            if db.execute("SELECT 1 FROM cancelled_external_operations WHERE operation_id = ?", (operation_id,)).fetchone():
                raise ConflictError("operation ID already cancelled")
            existing = db.execute("SELECT * FROM tickets WHERE operation_id = ? OR draft_id = ?", (operation_id, draft_id)).fetchone()
            if existing:
                if existing["operation_id"] != operation_id or existing["draft_id"] != draft_id or existing["tenant"] != identity.tenant:
                    raise ValueError("operation ID or draft already used")
                return {"ticket_id": existing["operation_id"], "status": "submitted", "replayed": True}
            if (not row["approved_digest"] or row["approved_digest"] != approval_version(row["tenant"], row["id"], row["creator"], row["text"], row["revision"])
                    or row["approved_until"] is None or self.clock() >= row["approved_until"]):
                raise PermissionError("current draft requires unexpired approval")
            db.execute("INSERT INTO tickets VALUES (?, ?, ?, ?)", (operation_id, draft_id, identity.tenant, row["text"]))
            self.audit(db, identity, "ticket_submitted", operation_id)
            return {"ticket_id": operation_id, "status": "submitted", "replayed": False}

    def prepare_external_submission(self, identity: Identity, draft_id: str, operation_id: str) -> dict:
        """Reserve an approved draft and its immutable intent; no external write occurs here."""
        if identity.role != "operator":
            raise PermissionError("operator required")
        if not isinstance(operation_id, str) or not operation_id.strip() or len(operation_id) > 128:
            raise ValueError("operation_id must be 1–128 characters")
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM drafts WHERE id = ? AND tenant = ?", (draft_id, identity.tenant)).fetchone()
            if not row:
                raise LookupError("draft not found")
            if db.execute("SELECT 1 FROM cancelled_external_operations WHERE operation_id = ?", (operation_id,)).fetchone():
                raise ConflictError("operation ID already cancelled")
            existing = db.execute("SELECT * FROM external_operations WHERE operation_id = ? OR draft_id = ?", (operation_id, draft_id)).fetchone()
            if existing:
                if (existing["operation_id"] != operation_id or existing["draft_id"] != draft_id
                        or existing["tenant"] != identity.tenant):
                    raise ConflictError("operation ID or draft already reserved")
                return {"operation_id": operation_id, "state": existing["state"], "replayed": True}
            if db.execute("SELECT 1 FROM tickets WHERE draft_id = ? OR operation_id = ?", (draft_id, operation_id)).fetchone():
                raise ConflictError("operation ID or draft already submitted")
            version = approval_version(row["tenant"], row["id"], row["creator"], row["text"], row["revision"])
            if (not row["approved_by"] or row["approved_digest"] != version
                    or row["approved_until"] is None or self.clock() >= row["approved_until"]):
                raise PermissionError("current draft requires unexpired approval")
            db.execute("INSERT INTO external_operations VALUES (?, ?, ?, ?, ?, ?, ?, 'prepared')",
                       (operation_id, draft_id, identity.tenant, row["text"], version,
                        row["approved_by"], row["approved_until"]))
            self.audit(db, identity, "external_submission_prepared", operation_id)
            return {"operation_id": operation_id, "state": "prepared", "replayed": False}

    def cancel_external_submission(self, identity: Identity, operation_id: str) -> dict:
        """Cancel an unsent reservation; retain the ID and require a fresh approval."""
        if identity.role != "reviewer":
            raise PermissionError("reviewer required")
        if not isinstance(operation_id, str) or not operation_id.strip() or len(operation_id) > 128:
            raise ValueError("operation_id must be 1–128 characters")
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            previous = db.execute("SELECT 1 FROM cancelled_external_operations WHERE operation_id = ? AND tenant = ?",
                                  (operation_id, identity.tenant)).fetchone()
            if previous:
                return {"operation_id": operation_id, "state": "cancelled", "replayed": True}
            row = db.execute("SELECT * FROM external_operations WHERE operation_id = ? AND tenant = ?",
                             (operation_id, identity.tenant)).fetchone()
            if not row:
                raise LookupError("operation not found")
            if row["state"] != "prepared":
                raise ConflictError("operation may have been sent; reconcile before any cancellation")
            db.execute("INSERT INTO cancelled_external_operations VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (operation_id, row["draft_id"], row["tenant"], row["approved_version"],
                        row["approved_by"], identity.user, self.clock()))
            db.execute("DELETE FROM external_operations WHERE operation_id = ?", (operation_id,))
            db.execute("UPDATE drafts SET approved_digest = NULL, approved_by = NULL, approved_until = NULL WHERE id = ? AND tenant = ?",
                       (row["draft_id"], identity.tenant))
            self.audit(db, identity, "external_submission_cancelled", operation_id)
            return {"operation_id": operation_id, "state": "cancelled", "replayed": False}
