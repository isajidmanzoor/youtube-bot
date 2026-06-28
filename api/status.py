import json
import os
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
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
        self.wfile.write(body)
