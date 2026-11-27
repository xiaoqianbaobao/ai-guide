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
from service import IDENTITIES, Service, digest


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "test.sqlite3")
        self.now = 1000.0
        self.server = make_server(self.db_path, port=0, clock=lambda: self.now, approval_ttl=300)
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

    def test_document_update_withdrawal_and_history(self):
        document = "/api/documents/refund-v1"
        update = {"document_id": "refund-v1", "expected_revision": 1,
                  "text": "退款需要核对发票与订单。"}
        self.assertEqual(self.request(document, "demo-support")[0], 403)
        self.assertEqual(self.request(document, "demo-hr-reviewer")[0], 404)
        self.assertEqual(self.request("/api/document-update", "demo-support", update)[0], 403)
        self.assertEqual(self.request("/api/document-update", "demo-hr-reviewer", update)[0], 404)
        self.assertEqual(self.request(document, "demo-support-reviewer")[1]["revision"], 1)
        self.assertEqual(self.request("/api/document-update", "demo-support-reviewer", update)[1]["revision"], 2)
        self.assertEqual(self.request("/api/document-update", "demo-support-reviewer", update)[0], 409)
        status, result = self.request("/api/ask", "demo-support", {"question": "发票"})
        self.assertEqual((status, result["source_versions"]), (200, [{"id": "refund-v1", "revision": 2}]))
        self.assertEqual(self.request("/api/ask", "demo-support", {"question": "付款状态"})[1]["status"], "insufficient_evidence")
        withdraw = {"document_id": "refund-v1", "expected_revision": 2}
        self.assertEqual(self.request("/api/document-withdraw", "demo-support-reviewer", withdraw)[1]["revision"], 3)
        self.assertEqual(self.request("/api/ask", "demo-support", {"question": "发票"})[1]["status"], "insufficient_evidence")
        self.assertEqual(self.request("/api/document-update", "demo-support-reviewer", {**update, "expected_revision": 3})[0], 409)
        Service(self.db_path)  # Restart must not reactivate the seeded document.
        self.assertEqual(self.request("/api/ask", "demo-support", {"question": "发票"})[1]["status"], "insufficient_evidence")
        with closing(sqlite3.connect(self.db_path)) as db:
            history = db.execute("SELECT revision, text, active FROM document_history WHERE document_id = ? ORDER BY revision", ("refund-v1",)).fetchall()
            self.assertEqual(history, [(1, "退款申请需要核对订单和付款状态。", 1),
                                       (2, "退款需要核对发票与订单。", 1),
                                       (3, "退款需要核对发票与订单。", 0)])

    def test_concurrent_document_updates_reject_stale_revision(self):
        def update(text):
            return self.request("/api/document-update", "demo-support-reviewer",
                                {"document_id": "refund-v1", "expected_revision": 1, "text": text})[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(update, ["第一条更新", "第二条更新"]))
        self.assertEqual(sorted(statuses), [200, 409])
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM document_history WHERE document_id = ?", ("refund-v1",)).fetchone()[0], 2)

    def test_existing_documents_migrate_with_revision_history(self):
        legacy = str(Path(self.tmp.name) / "legacy-docs.sqlite3")
        with closing(sqlite3.connect(legacy)) as db, db:
            db.execute("CREATE TABLE documents(id TEXT PRIMARY KEY, tenant TEXT NOT NULL, text TEXT NOT NULL)")
            db.execute("INSERT INTO documents VALUES (?, ?, ?)", ("refund-v1", "support", "旧版退款规则"))
        service = Service(legacy)
        result = service.ask(IDENTITIES["demo-support"], "旧版")
        self.assertEqual(result["source_versions"], [{"id": "refund-v1", "revision": 1}])
        with closing(sqlite3.connect(legacy)) as db:
            self.assertEqual(db.execute("SELECT text FROM document_history WHERE document_id = ? AND revision = 1", ("refund-v1",)).fetchone()[0], "旧版退款规则")

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

    def test_review_of_one_draft_cannot_approve_another_with_same_text(self):
        _, first = self.request('/api/drafts', 'demo-support', {'text': '相同的工单内容'})
        _, second = self.request('/api/drafts', 'demo-support', {'text': '相同的工单内容'})
        _, reviewed = self.request('/api/drafts/' + first['draft_id'], 'demo-support-reviewer')
        status, _ = self.request('/api/approve', 'demo-support-reviewer',
                                 {'draft_id': second['draft_id'], 'reviewed_version': reviewed['version']})
        self.assertEqual(status, 409)
        self.assertEqual(self.request('/api/submit', 'demo-support',
                         {'draft_id': second['draft_id'], 'operation_id': 'different-draft'})[0], 403)

    def test_creator_change_invalidates_approval(self):
        _, draft = self.request('/api/drafts', 'demo-support', {'text': '待审批内容'})
        self.assertEqual(self.approve(draft['draft_id'])[0], 200)
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute('UPDATE drafts SET creator = ? WHERE id = ?', ('other-user', draft['draft_id']))
        self.assertEqual(self.request('/api/submit', 'demo-support',
                         {'draft_id': draft['draft_id'], 'operation_id': 'changed-creator'})[0], 403)

    def test_old_unexpired_content_only_approval_requires_reapproval(self):
        _, draft = self.request('/api/drafts', 'demo-support', {'text': '旧版本已批准'})
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute('UPDATE drafts SET approved_digest = ?, approved_by = ?, approved_until = ? WHERE id = ?',
                       (digest('support', '旧版本已批准'), 'bob', self.now + 300, draft['draft_id']))
        payload = {'draft_id': draft['draft_id'], 'operation_id': 'old-approval'}
        self.assertEqual(self.request('/api/submit', 'demo-support', payload)[0], 403)
        self.assertEqual(self.approve(draft['draft_id'])[0], 200)
        self.assertEqual(self.request('/api/submit', 'demo-support', payload)[0], 200)

    def test_expiry_rejects_new_write_but_not_replay_of_completed_write(self):
        _, first = self.request("/api/drafts", "demo-support", {"text": "已提交"})
        _, second = self.request("/api/drafts", "demo-support", {"text": "未提交"})
        self.approve(first["draft_id"])
        self.approve(second["draft_id"])
        payload = {"draft_id": first["draft_id"], "operation_id": "op-first"}
        self.assertEqual(self.request("/api/submit", "demo-support", payload)[0], 200)
        self.now += 300
        self.assertEqual(self.request("/api/submit", "demo-support", {"draft_id": second["draft_id"], "operation_id": "op-second"})[0], 403)
        status, result = self.request("/api/submit", "demo-support", payload)
        self.assertEqual(status, 200)
        self.assertTrue(result["replayed"])

    def test_revoke_blocks_submission_and_requires_reapproval(self):
        _, draft = self.request("/api/drafts", "demo-support", {"text": "待撤销"})
        draft_id = draft["draft_id"]
        self.approve(draft_id)
        self.assertEqual(self.request("/api/revoke", "demo-support", {"draft_id": draft_id})[0], 403)
        self.assertEqual(self.request("/api/revoke", "demo-support-reviewer", {"draft_id": draft_id})[0], 200)
        payload = {"draft_id": draft_id, "operation_id": "op"}
        self.assertEqual(self.request("/api/submit", "demo-support", payload)[0], 403)
        self.approve(draft_id)
        self.assertEqual(self.request("/api/submit", "demo-support", payload)[0], 200)
        self.assertEqual(self.request("/api/revoke", "demo-support-reviewer", {"draft_id": draft_id})[0], 409)

    def test_submit_and_revoke_race_has_only_one_winner(self):
        _, draft = self.request("/api/drafts", "demo-support", {"text": "竞争示例"})
        draft_id = draft["draft_id"]
        self.approve(draft_id)
        barrier = threading.Barrier(2)
        def send(path, token, payload):
            barrier.wait(timeout=3)
            return self.request(path, token, payload)[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            write = pool.submit(send, "/api/submit", "demo-support", {"draft_id": draft_id, "operation_id": "race"})
            revoke = pool.submit(send, "/api/revoke", "demo-support-reviewer", {"draft_id": draft_id})
            self.assertIn((write.result(), revoke.result()), [(200, 409), (403, 200)])

    def test_unknown_identity_and_empty_question_are_rejected(self):
        self.assertEqual(self.request("/api/ask", "unknown", {"question": "退款"})[0], 403)
        self.assertEqual(self.request("/api/ask", "demo-support", {"question": ""})[0], 400)

    def test_local_learning_interface_is_served(self):
        with urlopen(self.base + "/", timeout=3) as response:
            self.assertIn("企业知识与工单助手", response.read().decode())
        with urlopen(self.base + "/app.js", timeout=3) as response:
            self.assertIn("/api/approve", response.read().decode())

    def test_legacy_approval_without_expiry_requires_reapproval(self):
        legacy = str(Path(self.tmp.name) / "legacy.sqlite3")
        with closing(sqlite3.connect(legacy)) as db, db:
            db.execute("CREATE TABLE drafts(id TEXT PRIMARY KEY, tenant TEXT NOT NULL, creator TEXT NOT NULL, text TEXT NOT NULL, digest TEXT NOT NULL, approved_digest TEXT, approved_by TEXT)")
            fingerprint = digest("support", "旧草稿")
            db.execute("INSERT INTO drafts VALUES (?, ?, ?, ?, ?, ?, ?)",
                       ("old", "support", "alice", "旧草稿", fingerprint, fingerprint, "bob"))
        service = Service(legacy, clock=lambda: self.now)
        with self.assertRaises(PermissionError):
            service.submit(IDENTITIES["demo-support"], "old", "operation")


if __name__ == "__main__":
    unittest.main()
