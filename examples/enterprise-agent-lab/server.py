"""Loopback-only HTTP wrapper for the offline teaching service."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from service import ConflictError, IDENTITIES, Service


class Handler(BaseHTTPRequestHandler):
    server_version = "AgentTeachingLab"

    def log_message(self, *args):
        pass  # Avoid logging demo request content or tokens.

    def respond(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def identity(self):
        identity = IDENTITIES.get(self.headers.get("X-Demo-Token", ""))
        if not identity:
            raise PermissionError("demo identity required")
        return identity

    def handle_request(self):
        identity = self.identity()
        service = self.server.service
        if self.command == "GET" and self.path.startswith("/api/drafts/"):
            return service.get_draft(identity, self.path.rsplit("/", 1)[-1])
        if self.command != "POST":
            raise LookupError("route not found")
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 4096:
            raise ValueError("body must be 1–4096 bytes")
        data = json.loads(self.rfile.read(length))
        if not isinstance(data, dict):
            raise ValueError("JSON object required")
        if self.path == "/api/ask":
            return service.ask(identity, data.get("question"))
        if self.path == "/api/drafts":
            return service.create_draft(identity, data.get("text"))
        if self.path == "/api/approve":
            return service.approve(identity, data.get("draft_id"), data.get("reviewed_version"))
        if self.path == "/api/submit":
            return service.submit(identity, data.get("draft_id"), data.get("operation_id"))
        raise LookupError("route not found")

    def dispatch(self):
        try:
            self.respond(200, self.handle_request())
        except PermissionError:
            self.respond(403, {"error": "forbidden"})
        except LookupError:
            self.respond(404, {"error": "not found"})
        except ConflictError:
            self.respond(409, {"error": "draft changed; review again"})
        except (ValueError, TypeError, json.JSONDecodeError):
            self.respond(400, {"error": "invalid request"})

    do_GET = dispatch
    do_POST = dispatch


def make_server(path: str, port: int = 8765):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.service = Service(path)
    return server


if __name__ == "__main__":
    db_path = Path(__file__).resolve().parent / "lab.sqlite3"
    print("教学服务仅监听 http://127.0.0.1:8765；不要用于真实数据。", flush=True)
    make_server(str(db_path)).serve_forever()
