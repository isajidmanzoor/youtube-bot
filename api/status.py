import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse


DASHBOARD_HTML = b"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Studio Dashboard</title>
  <style>
    body{margin:0;background:#0a0d10;color:#edf2f7;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif}
    main{max-width:1120px;margin:auto;padding:28px 18px 44px}
    header{display:flex;justify-content:space-between;gap:16px;align-items:flex-end;border-bottom:1px solid #2b3643;padding-bottom:18px}
    h1{margin:0 0 8px;font-size:clamp(28px,4vw,44px);line-height:1.05}.muted,#topic{color:#9aa8b6}
    #status{border:1px solid #2b3643;background:#121820;color:#41d39b;padding:10px 14px;text-transform:uppercase;letter-spacing:.08em;font-size:12px}
    .grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px;margin-top:18px}
    section{background:#121820;border:1px solid #2b3643;border-radius:8px;padding:16px}.wide{grid-column:span 8}.side{grid-column:span 4}.full{grid-column:1/-1}
    h2{margin:0 0 14px;color:#9aa8b6;font-size:15px;text-transform:uppercase;letter-spacing:.05em}
    .metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.metric{background:#17202a;border:1px solid #2b3643;border-radius:6px;padding:12px;min-height:78px}
    .metric strong{display:block;font-size:26px;margin-bottom:4px}.pipeline{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px}
    .step{border:1px solid #2b3643;border-left:3px solid #5fb3ff;border-radius:6px;padding:10px;background:#17202a;min-height:58px}
    .score{display:grid;grid-template-columns:92px 1fr 44px;gap:10px;align-items:center;margin-bottom:8px}.bar{height:8px;background:#26313c;border-radius:99px;overflow:hidden}.fill{height:100%;background:#41d39b}
    #errors{color:#ff6b6b;white-space:pre-wrap}@media(max-width:820px){header{display:block}#status{margin-top:14px}.wide,.side{grid-column:1/-1}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
  </style>
</head>
<body>
<main>
  <header><div><h1>AI Studio Dashboard</h1><div id="topic">Loading studio state...</div></div><div id="status">Loading</div></header>
  <div class="grid">
    <section class="wide"><h2>Analytics AI</h2><div class="metrics" id="metrics"></div></section>
    <section class="side"><h2>Quality Gate</h2><div id="scores"></div></section>
    <section class="full"><h2>AI Operating Pipeline</h2><div class="pipeline" id="pipeline"></div></section>
    <section class="wide"><h2>Research Swarm</h2><p id="research" class="muted"></p></section>
    <section class="side"><h2>Errors</h2><div id="errors" class="muted">No errors</div></section>
  </div>
</main>
<script>
const labels={viral_probability:"Viral %",expected_views:"Views",ctr:"CTR %",retention:"Retention %",rpm:"RPM",subscribers:"Subs",shares:"Shares",comments:"Comments"};
async function loadStatus(){
  const data=await fetch("/api/status",{cache:"no-store"}).then(r=>r.json());
  document.getElementById("status").textContent=data.status||"waiting";
  document.getElementById("topic").textContent=data.active_topic||"No active topic yet";
  const analytics=data.analytics||{};
  document.getElementById("metrics").innerHTML=Object.entries(labels).map(([k,l])=>`<div class="metric"><strong>${analytics[k]??"-"}</strong><span class="muted">${l}</span></div>`).join("");
  const scores=(data.quality_gate&&data.quality_gate.scores)||{};
  document.getElementById("scores").innerHTML=Object.entries(scores).map(([k,v])=>`<div class="score"><span>${k}</span><div class="bar"><div class="fill" style="width:${Math.min(v,100)}%"></div></div><span>${v}</span></div>`).join("")||"<span class='muted'>No quality gate yet</span>";
  document.getElementById("pipeline").innerHTML=(data.pipeline||[]).map(s=>`<div class="step"><strong>${s.name}</strong><div class="muted">${s.status||"ready"}</div></div>`).join("")||"<span class='muted'>Pipeline waiting for first run</span>";
  const research=data.research||{};document.getElementById("research").textContent=`${research.agents||0} agents | ${research.consensus||"No consensus yet"}`;
  const errors=data.errors||[];document.getElementById("errors").textContent=errors.length?errors.map(e=>`${e.at||""} ${e.message||e}`).join("\\n"):"No errors";
}
loadStatus();setInterval(loadStatus,10000);
</script>
</body>
</html>"""


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
            body = DASHBOARD_HTML
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
