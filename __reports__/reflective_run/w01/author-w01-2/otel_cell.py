"""One auto-mode (or other) run with a local OTLP/HTTP-JSON receiver and --forward-subagent-text.
Question: which sources give EXACT per-request output tokens for a subagent when the subagent transcript
does not (permission mode auto)?  Sources compared: OTel `api_request` events (env set at process start),
stream-json forwarded subagent messages, result.modelUsage.
usage: python3 -I otel_cell.py <cell-name> --bin {installed|desktop} --permmode auto|bypassPermissions
"""
import argparse, json, os, subprocess, sys, threading, time, http.server, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_cell

ap = argparse.ArgumentParser()
ap.add_argument("cell"); ap.add_argument("--bin", default="installed"); ap.add_argument("--permmode", default="auto")
ap.add_argument("--mode", default="fg")
a = ap.parse_args()
ns = argparse.Namespace(bin=a.bin, mode=a.mode, think="on", length="long", env="inherit", io="p", partial="0",
                        thinkdisp="default", effort="default", auto="0", permmode=a.permmode, poll="0")
shutil.rmtree(os.path.join(HERE, "runs", a.cell), ignore_errors=True)
cmd, stdin, env, work = run_cell.build(ns, a.cell)
cmd = cmd[:-1] + ["--forward-subagent-text", cmd[-1]]   # prompt stays last
base = os.path.join(HERE, "runs", a.cell)
bodies = []

class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("content-length", 0)); b = self.rfile.read(n)
        bodies.append((self.path, b.decode(errors="replace")))
        self.send_response(200); self.send_header("content-type", "application/json"); self.end_headers(); self.wfile.write(b"{}")
    def log_message(self, *x): pass

srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
env.update({"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_LOGS_EXPORTER": "otlp", "OTEL_METRICS_EXPORTER": "none",
            "OTEL_EXPORTER_OTLP_PROTOCOL": "http/json", "OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:%d" % port,
            "OTEL_LOGS_EXPORT_INTERVAL": "500", "OTEL_LOG_TOOL_DETAILS": "1"})
json.dump(dict(vars(a), cmd=cmd, started=time.time(), bin=a.bin, mode=a.mode, think="on", length="long", env="inherit",
               io="p", partial="0", thinkdisp="default", effort="default", auto="0", permmode=a.permmode),
          open(os.path.join(base, "cell.json"), "w"), indent=1)
p = subprocess.run(cmd, input="", capture_output=True, text=True, cwd=work, env=env, timeout=420)
time.sleep(3)
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout)
open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
# parse OTLP logs
def val(v):
    for k in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if k in v: return v[k]
    return v
ev = []
for path, body in bodies:
    if "/v1/logs" not in path: continue
    try: d = json.loads(body)
    except Exception: continue
    for rl in d.get("resourceLogs", []):
        for sl in rl.get("scopeLogs", []):
            for lr in sl.get("logRecords", []):
                ev.append({kv["key"]: val(kv["value"]) for kv in lr.get("attributes", [])})
json.dump([e for e in ev if e.get("event.name") in ("api_request", "subagent_completed")],
          open(os.path.join(base, "otel_events.json"), "w"), indent=1)
print(a.cell, "exit", p.returncode, "events", len(ev))
