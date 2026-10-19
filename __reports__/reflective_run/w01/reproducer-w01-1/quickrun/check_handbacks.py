#!/usr/bin/env python3
"""Check one probe run of run_probe.sh: is every hand-back in the lab file, byte for byte?
Usage: check_handbacks.py <scratch/run dir> [<work dir if not <run>/work>]   Output: one JSON line.
Compares the file (sliced by the header's bytes=N) with (a) the raw hook payloads in RAWLOG and (b) the
subagent transcripts the platform wrote. Read-only. Python stdlib: it only joins and compares strings."""
import glob, json, os, re, sys

run = sys.argv[1]
work = sys.argv[2] if len(sys.argv) > 2 else os.path.join(run, "work")
HEAD = re.compile(rb"^## hand-back (\d+) \| (\S+) \| agent_id=(\S+) type=(\S+) event=(\S+) bytes=(\d+) sha256=(\w+)\n\n", re.M)

def sections(path):
    data, out, pos = open(path, "rb").read(), [], 0
    while True:
        m = HEAD.search(data, pos)
        if not m: return out
        n = int(m.group(6)); body = data[m.end():m.end() + n]
        assert data[m.end() + n:m.end() + n + 1] == b"\n", "body not followed by newline: bytes=N is wrong"
        out.append(dict(n=int(m.group(1)), agent_id=m.group(3).decode(), event=m.group(5).decode(), sha=m.group(7).decode(), text=body.decode("utf-8")))
        pos = m.end() + n

files = sorted(glob.glob(os.path.join(work, "__statera__", "handbacks", "*.md")))
got = {os.path.basename(f): sections(f) for f in files}

raw = []
if os.path.exists(os.path.join(run, "RAWLOG")):
    for line in open(os.path.join(run, "RAWLOG")):
        e = json.loads(line)["input"]
        t = e.get("last_assistant_message") if e.get("hook_event_name") == "SubagentStop" else (e.get("tool_input") or {}).get("message") if e.get("tool_name") == "SubagentHandback" else None
        if e.get("agent_id") and isinstance(t, str) and t.strip() and (not raw or raw[-1] != (e["agent_id"], t)):
            raw.append((e["agent_id"], t))
flat = [(s["agent_id"], s["text"]) for secs in got.values() for s in secs if s["sha"] != "MISSING"]

# the platform's own record: per subagent transcript, the SubagentHandback inputs (auto) or the last assistant text (default)
tr = []
for p in glob.glob(os.path.expanduser("~/.claude/projects/*/*/subagents/agent-*.jsonl")):
    pass
roots = set()
if os.path.exists(os.path.join(run, "RAWLOG")):
    for line in open(os.path.join(run, "RAWLOG")):
        e = json.loads(line)["input"]
        if e.get("agent_transcript_path"): roots.add(e["agent_transcript_path"])
for p in sorted(roots):
    aid = os.path.basename(p)[6:-6]; hb, last = [], None
    for line in open(p, encoding="utf-8"):
        r = json.loads(line); m = r.get("message")
        if not isinstance(m, dict) or m.get("role") != "assistant" or not isinstance(m.get("content"), list): continue
        for b in m["content"]:
            if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback": hb.append(b["input"]["message"])
            if b.get("type") == "text": last = b["text"]
    tr.append((aid, hb[-len(hb):] if hb else ([last] if last else [])))
tr_flat = [(a, t) for a, ts in tr for t in ts]
# in default mode only the last text of each agent is checkable (earlier ones are not marked in the transcript)
tr_ok = all(any(s == (a, t) for s in flat) for a, t in tr_flat)
print(json.dumps(dict(run=os.path.basename(run.rstrip("/")), files=list(got), sections=sum(len(v) for v in got.values()),
    missing=sum(1 for v in got.values() for s in v if s["sha"] == "MISSING"),
    expected_from_hook_payloads=len(raw), file_equals_payloads=(flat == raw),
    transcript_texts=len(tr_flat), transcript_texts_found_in_file=tr_ok), ensure_ascii=False))
