"""Independent comparison: lab file sections (sliced by bytes=N) vs RAWLOG payloads. Usage: cmp_mine.py <run dir>..."""
import sys, os, re, json, glob, hashlib
H = re.compile(rb"^## hand-back (\d+) \| (\S+) \| agent_id=(\S+) type=(\S+) event=(\S+) status=(\S+) bytes=(\d+) sha256=(\w+)\n\[model output[^\n]*\]\n\n", re.M)
def sections(path):
    b = open(path, "rb").read(); pos = 0; out = []
    while True:
        m = H.search(b, pos)
        if not m: break
        n = int(m.group(7)); body = b[m.end():m.end()+n]
        assert b[m.end()+n:m.end()+n+1] == b"\n", "no newline after body"
        out.append(dict(i=int(m.group(1)), agent=m.group(3).decode(), event=m.group(5).decode(), status=m.group(6).decode(), n=n, sha=m.group(8).decode(), body=body))
        pos = m.end()+n+1
    return out
def payloads(raw):
    res = []
    for l in open(raw):
        d = json.loads(l)["input"]; ev = d.get("hook_event_name")
        if ev == "SubagentStop": t = d.get("last_assistant_message")
        elif ev == "PostToolUse" and d.get("tool_name") == "SubagentHandback": t = (d.get("tool_input") or {}).get("message")
        else: continue
        res.append((d.get("agent_id"), ev, t if isinstance(t, str) and t.strip() else None))
    return res
for run in sys.argv[1:]:
    files = glob.glob(os.path.join(run, "work", "__statera__", "handbacks", "*.md"))
    secs = [s for f in sorted(files) for s in sections(f)]
    pl = payloads(os.path.join(run, "RAWLOG"))
    texts = [p for p in pl if p[2] is not None]
    # expected: consecutive same text per agent collapsed
    exp = []
    for a, ev, t in texts:
        if exp and exp[-1][0] == a and exp[-1][2] == t: continue
        exp.append((a, ev, t))
    real = [s for s in secs if s["sha"] != "MISSING"]; miss = [s for s in secs if s["sha"] == "MISSING"]; drafts=[s["event"] for s in secs if s["status"].startswith("draft")]
    ok = len(real) == len(exp) and all(s["body"] == e[2].encode() and s["agent"] == e[0] and s["event"] == e[1] and s["sha"] == hashlib.sha256(e[2].encode()).hexdigest()[:12] for s, e in zip(real, exp))
    stops_no_text = sum(1 for a, ev, t in pl if ev == "SubagentStop" and t is None)
    stops_text = sum(1 for a, ev, t in pl if ev == "SubagentStop" and t is not None)
    hb = sum(1 for a, ev, t in pl if ev == "PostToolUse")
    print(json.dumps(dict(run=os.path.basename(run.rstrip("/")), files=[os.path.basename(f) for f in files], sections=len(secs), missing=len(miss), expected=len(exp), byte_equal=ok, events=[s["event"]+"/"+s["status"] for s in secs], SubagentStop_with_text=stops_text, SubagentStop_without=stops_no_text, PostToolUse_handback=hb)))
