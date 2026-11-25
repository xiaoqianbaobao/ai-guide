"""Loopback-only mock downstream and HTTP client for failure-injection exercises."""
from http.client import RemoteDisconnected
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote
from urllib.request import Request, urlopen
from recovery import MockDownstream


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/tickets":
            self.respond(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                raise ValueError("invalid body length")
            payload = json.loads(self.rfile.read(length))
            operation_id, text = payload["operation_id"], payload["text"]
            if not isinstance(operation_id, str) or not operation_id.strip() or not isinstance(text, str) or not text.strip():
                raise ValueError("invalid payload")
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            self.respond(400, {"error": "invalid request"})
            return
        try:
            receipt = self.server.downstream.create(operation_id, text)
        except ValueError:
            self.respond(409, {"error": "operation conflict"})
            return
        if self.headers.get("X-Demo-Drop-Response") == "1":
            # The database transaction has committed; deliberately terminate the connection.
            self.close_connection = True
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.connection.close()
            return
        self.respond(200, {"receipt": receipt})

    def do_GET(self):
        if not self.path.startswith("/tickets/"):
            self.respond(404, {"error": "not found"})
            return
        result = self.server.downstream.lookup(unquote(self.path[len("/tickets/"):]))
        self.respond(200 if result else 404, result or {"error": "not found"})


def make_server(path, port=0):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.downstream = MockDownstream(path)
    return server


class HttpDownstream:
    def __init__(self, port, timeout=2):
        self.base = f"http://127.0.0.1:{port}"
        self.timeout = timeout

    def create(self, operation_id, text, lose_response=False):
        body = json.dumps({"operation_id": operation_id, "text": text}, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if lose_response:
            headers["X-Demo-Drop-Response"] = "1"
        request = Request(self.base + "/tickets", data=body, headers=headers)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.load(response)["receipt"]
        except HTTPError as error:
            if error.code in (400, 409):
                raise ValueError("downstream rejected request") from error
            raise TimeoutError("downstream outcome unknown") from error
        except (URLError, TimeoutError, RemoteDisconnected, ConnectionResetError) as error:
            raise TimeoutError("downstream outcome unknown") from error

    def lookup(self, operation_id):
        try:
            with urlopen(self.base + "/tickets/" + quote(operation_id, safe=""), timeout=self.timeout) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 404:
                return None
            raise TimeoutError("lookup unavailable") from error
        except (URLError, TimeoutError, RemoteDisconnected, ConnectionResetError) as error:
            raise TimeoutError("lookup unavailable") from error
