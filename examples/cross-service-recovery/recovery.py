"""Offline, single-worker teaching demo with separate local and mock downstream databases."""
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import sqlite3


def fingerprint(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class MockDownstream:
    """Simulates a downstream supporting durable idempotency and consistent lookup."""
    def __init__(self, path):
        self.path = path
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS tickets (operation_id TEXT PRIMARY KEY, digest TEXT NOT NULL, text TEXT NOT NULL)")

    def create(self, operation_id, text, lose_response=False):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("INSERT OR IGNORE INTO tickets VALUES (?, ?, ?)", (operation_id, fingerprint(text), text))
            stored = db.execute("SELECT digest FROM tickets WHERE operation_id = ?", (operation_id,)).fetchone()
            if stored[0] != fingerprint(text):
                raise ValueError("operation ID already used with different content")
        if lose_response:
            raise TimeoutError("response lost after downstream commit")
        return operation_id

    def lookup(self, operation_id):
        with closing(sqlite3.connect(self.path)) as db:
            row = db.execute("SELECT operation_id, digest FROM tickets WHERE operation_id = ?", (operation_id,)).fetchone()
        return None if row is None else {"receipt": row[0], "digest": row[1]}


class Coordinator:
    """Persists intent before a write; one worker only, no real network or authentication."""
    def __init__(self, path, downstream):
        self.path, self.downstream = path, downstream
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS operations (operation_id TEXT PRIMARY KEY, text TEXT NOT NULL, state TEXT NOT NULL, receipt TEXT)")

    def prepare(self, operation_id, text):
        if not isinstance(operation_id, str) or not operation_id.strip() or not isinstance(text, str) or not text.strip():
            raise ValueError("operation ID and text are required")
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("INSERT OR IGNORE INTO operations VALUES (?, ?, 'pending', NULL)", (operation_id, text))
            stored = db.execute("SELECT text FROM operations WHERE operation_id = ?", (operation_id,)).fetchone()
            if stored[0] != text:
                raise ValueError("operation ID reused with different content")

    def state(self, operation_id):
        with closing(sqlite3.connect(self.path)) as db:
            row = db.execute("SELECT text, state, receipt FROM operations WHERE operation_id = ?", (operation_id,)).fetchone()
        if row is None:
            raise LookupError("operation not found")
        return {"text": row[0], "state": row[1], "receipt": row[2]}

    def mark(self, operation_id, state, receipt=None):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE operations SET state = ?, receipt = ? WHERE operation_id = ?", (state, receipt, operation_id))

    def dispatch(self, operation_id, lose_response=False, crash_after_write=False):
        operation = self.state(operation_id)
        if operation["state"] == "confirmed":
            return operation
        try:
            receipt = self.downstream.create(operation_id, operation["text"], lose_response=lose_response)
        except TimeoutError:
            self.mark(operation_id, "unknown")
            return self.state(operation_id)
        if crash_after_write:
            raise RuntimeError("simulated crash after downstream commit")
        self.mark(operation_id, "confirmed", receipt)
        return self.state(operation_id)

    def reconcile(self, operation_id):
        operation = self.state(operation_id)
        try:
            found = self.downstream.lookup(operation_id)
        except TimeoutError:
            self.mark(operation_id, "unknown")
            return self.state(operation_id)
        if found is None:
            # A missing lookup result is not proof that an external write failed.
            self.mark(operation_id, "unknown")
        elif found["digest"] != fingerprint(operation["text"]):
            raise ValueError("downstream content does not match local intent")
        else:
            self.mark(operation_id, "confirmed", found["receipt"])
        return self.state(operation_id)


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        root = Path(directory)
        downstream = MockDownstream(str(root / "downstream.sqlite3"))
        coordinator = Coordinator(str(root / "local.sqlite3"), downstream)
        coordinator.prepare("demo-operation-1", "请人工核实退款。")
        print("响应丢失后:", coordinator.dispatch("demo-operation-1", lose_response=True)["state"])
        restarted = Coordinator(str(root / "local.sqlite3"), downstream)
        print("重启并对账后:", restarted.reconcile("demo-operation-1")["state"])
