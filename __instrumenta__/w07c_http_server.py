"""Tiny hook server for the w07-c probes: serves Claude Code `http` hooks on 127.0.0.1 (stdlib only), checks a per-session token header, logs every request; inputs: --port-file PATH, --log PATH, env W7C_TOKEN; output: JSONL log (ts_ns, path, token_ok, event, tool, body keys, body size, reply kind) and the chosen port in the port file.
Routes (by URL path): /ok (200, empty JSON object), /ctx (200, additionalContext nonce for the event), /deny (PreToolUse deny, else decision block with continueOnBlock), /block (decision block, reason), /blockonce (SubagentStop: block the first call per agent_id, then allow), /hang (sleep 60 s, no reply), /garbage (200, text/plain 'this is not json'), /array (200, JSON array), /s500 (HTTP 500), /slow?ms=N (sleep N ms then {}). A request with a wrong or missing token gets 403 whatever the path. Dump bodies: /ok and the rest also append the full body to <log>.bodies.jsonl.
"""
import argparse, json, os, sys, time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ap = argparse.ArgumentParser(); ap.add_argument("--port-file", required=True); ap.add_argument("--log", required=True)
a = ap.parse_args()
TOKEN = os.environ.get("W7C_TOKEN", "")
LOCK = threading.Lock(); SEEN = set()

def w(path, rec):
    with LOCK, open(path, "a") as f: f.write(json.dumps(rec) + "\n")

class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *x): pass
    def do_POST(self):
        t0 = time.time_ns()
        n = int(self.headers.get("Content-Length", 0)); raw = self.rfile.read(n) if n else b""
        u = urlparse(self.path); q = parse_qs(u.query); ok = TOKEN != "" and self.headers.get("X-W7C-Token") == TOKEN
        try: body = json.loads(raw) if raw else {}
        except Exception: body = {}
        ev = body.get("hook_event_name", ""); tool = body.get("tool_name", "")
        rec = {"ts_ns": t0, "path": u.path, "token_ok": ok, "event": ev, "tool": tool, "keys": sorted(body), "size": n,
               "ctype": self.headers.get("Content-Type"), "ua": self.headers.get("User-Agent"), "tool_use_id": body.get("tool_use_id"), "agent_id": body.get("agent_id")}
        w(a.log + ".bodies.jsonl", {"ts_ns": t0, "path": u.path, "body": body})
        kind, code, ctype, out = "empty", 200, "application/json", b"{}"
        if not ok: kind, code, out = "403", 403, b'{"error":"bad token"}'
        elif u.path == "/ctx":
            kind = "ctx"; out = json.dumps({"hookSpecificOutput": {"hookEventName": ev, "additionalContext": "HTTPCTX-NONCE-%s-%s" % (ev, (body.get("tool_use_id") or body.get("agent_id") or "x")[-6:])}}).encode()
        elif u.path == "/deny":
            kind = "deny"
            if ev == "PreToolUse": out = json.dumps({"hookSpecificOutput": {"hookEventName": ev, "permissionDecision": "deny", "permissionDecisionReason": "HTTPDENY-NONCE-1"}}).encode()
            else: out = json.dumps({"decision": "block", "reason": "HTTPDENY-NONCE-1", "continueOnBlock": True}).encode()
        elif u.path == "/block":
            kind = "block"; out = json.dumps({"decision": "block", "reason": "HTTPBLOCK-NONCE-1"}).encode()
        elif u.path == "/blockonce":
            kind = "blockonce"; key = body.get("agent_id") or body.get("session_id")
            if key in SEEN: kind = "blockonce-allow"
            else: SEEN.add(key); out = json.dumps({"decision": "block", "reason": "HTTPBLOCK-NONCE-ONCE"}).encode()
        elif u.path == "/garbage": kind, ctype, out = "garbage", "text/plain", b"this is not json"
        elif u.path == "/array": kind, out = "array", b"[1,2,3]"
        elif u.path == "/s500": kind, code, out = "500", 500, b'{"error":"boom"}'
        elif u.path == "/hang":
            w(a.log, dict(rec, reply="hang-start")); time.sleep(60); kind = "hang-end"
        elif u.path == "/slow": time.sleep(int(q.get("ms", ["100"])[0]) / 1000); kind = "slow"
        w(a.log, dict(rec, reply=kind, t_reply_ns=time.time_ns()))
        try:
            self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)
        except Exception: pass

srv = ThreadingHTTPServer(("127.0.0.1", 0), H); srv.daemon_threads = True
open(a.port_file, "w").write(str(srv.server_address[1]))
srv.serve_forever()
