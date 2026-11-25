from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from server import make_server


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "test.sqlite3")
        self.server = make_server(self.db_path, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def request(self, path, token, data=None):
        body = None if data is None else json.dumps(data, ensure_ascii=False).encode()
        req = Request(self.base + path, data=body, headers={"X-Demo-Token": token, "Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=3) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)

    def approve(self, draft_id):
        _, draft = self.request("/api/drafts/" + draft_id, "demo-support-reviewer")
        return self.request("/api/approve", "demo-support-reviewer",
                            {"draft_id": draft_id, "reviewed_version": draft["version"]})

    def test_knowledge_is_filtered_by_tenant(self):
        status, answer = self.request("/api/ask", "demo-support", {"question": "退款"})
        self.assertEqual((status, answer["sources"]), (200, ["refund-v1"]))
        _, denied = self.request("/api/ask", "demo-support", {"question": "薪酬"})
        self.assertEqual(denied["status"], "insufficient_evidence")
        self.assertNotIn("薪酬调整", json.dumps(denied, ensure_ascii=False))

    def test_approval_and_replay_do_not_duplicate_ticket(self):
        _, draft = self.request("/api/drafts", "demo-support", {"text": "请核实退款"})
        draft_id = draft["draft_id"]
        self.assertEqual(self.request("/api/drafts/" + draft_id, "demo-hr")[0], 404)
        self.assertEqual(self.request("/api/submit", "demo-support", {"draft_id": draft_id, "operation_id": "op-1"})[0], 403)
        self.assertEqual(self.request("/api/approve", "demo-support", {"draft_id": draft_id})[0], 403)
        self.assertEqual(self.request("/api/drafts/" + draft_id, "demo-support-reviewer")[1]["text"], "请核实退款")
        self.assertEqual(self.approve(draft_id)[0], 200)
        payload = {"draft_id": draft_id, "operation_id": "op-1"}
        self.assertFalse(self.request("/api/submit", "demo-support", payload)[1]["replayed"])
        self.assertTrue(self.request("/api/submit", "demo-support", payload)[1]["replayed"])
        self.assertEqual(self.request("/api/submit", "demo-support", {"draft_id": draft_id, "operation_id": "op-2"})[0], 400)
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM tickets").fetchone()[0], 1)

    def test_modified_draft_cannot_use_old_approval(self):
        _, draft = self.request("/api/drafts", "demo-support", {"text": "原始草稿"})
        draft_id = draft["draft_id"]
        self.approve(draft_id)
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("UPDATE drafts SET text = ? WHERE id = ?", ("被修改的草稿", draft_id))
        self.assertEqual(self.request("/api/submit", "demo-support", {"draft_id": draft_id, "operation_id": "op-1"})[0], 403)

    def test_concurrent_retries_create_one_ticket(self):
        _, draft = self.request("/api/drafts", "demo-support", {"text": "并发重试样例"})
        draft_id = draft["draft_id"]
        self.approve(draft_id)
        payload = {"draft_id": draft_id, "operation_id": "same-operation"}
        with ThreadPoolExecutor(max_workers=4) as pool:
            responses = list(pool.map(lambda _: self.request("/api/submit", "demo-support", payload), range(4)))
        self.assertTrue(all(status == 200 for status, _ in responses))
        self.assertEqual(sum(not result["replayed"] for _, result in responses), 1)
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM tickets").fetchone()[0], 1)

    def test_reviewed_version_cannot_approve_changed_draft(self):
        _, draft = self.request("/api/drafts", "demo-support", {"text": "审核看到的内容"})
        draft_id = draft["draft_id"]
        _, reviewed = self.request("/api/drafts/" + draft_id, "demo-support-reviewer")
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("UPDATE drafts SET text = ? WHERE id = ?", ("后来修改的内容", draft_id))
        status, _ = self.request("/api/approve", "demo-support-reviewer",
                                 {"draft_id": draft_id, "reviewed_version": reviewed["version"]})
        self.assertEqual(status, 409)
        self.assertEqual(self.request("/api/submit", "demo-support", {"draft_id": draft_id, "operation_id": "op"})[0], 403)
        self.assertEqual(self.approve(draft_id)[0], 200)

    def test_unknown_identity_and_empty_question_are_rejected(self):
        self.assertEqual(self.request("/api/ask", "unknown", {"question": "退款"})[0], 403)
        self.assertEqual(self.request("/api/ask", "demo-support", {"question": ""})[0], 400)


if __name__ == "__main__":
    unittest.main()
