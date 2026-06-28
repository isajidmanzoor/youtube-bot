import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self._handle_request(include_body=False)

    def do_GET(self):
        self._handle_request(include_body=True)

    def _handle_request(self, include_body=True):
        request_path = urlparse(self.path).path
        if request_path in ("", "/"):
            return self._send_dashboard(include_body)
        return self._send_status(include_body)

    def _send_dashboard(self, include_body=True):
        path = os.path.join(os.getcwd(), "public", "index.html")
        if os.path.exists(path):
            with open(path, "rb") as f:
                body = f.read()
            status = 200
        else:
            body = b"AI Studio Dashboard"
            status = 200

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "public, max-age=0, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def _send_status(self, include_body=True):
        path = os.path.join(os.getcwd(), "logs", "studio_dashboard.json")
        if os.path.exists(path):
            with open(path) as f:
                payload = json.load(f)
        else:
            payload = {
                "status": "waiting",
                "active_topic": None,
                "pipeline": [],
                "research": {"agents": 0, "consensus": "No run yet"},
                "rendering": {"status": "waiting"},
                "errors": [],
                "analytics": {},
                "quality_gate": {},
            }

        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if include_body:
            self.wfile.write(body)
