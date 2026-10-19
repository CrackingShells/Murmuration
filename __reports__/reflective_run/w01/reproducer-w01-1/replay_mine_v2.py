"""Own replay: for each subagent transcript with SubagentHandback tool calls, send the hook a synthetic PostToolUse event; compare file sections with the tool_use input. Hook is run as a subprocess (python3 -I); nothing imported from the author."""
import json, glob, os, re, subprocess, sys, shutil
HOOK = sys.argv[1]; LAB = sys.argv[2]; SESS = sys.argv[3]   # SESS = session jsonl path
shutil.rmtree(LAB, ignore_errors=True); os.makedirs(os.path.join(LAB, "__statera__"))
sub = SESS[:-6] + "/subagents"
H = re.compile(rb"^## hand-back (\d+) \| (\S+) \| agent_id=(\S+) type=(\S+) event=(\S+) status=(\S+) bytes=(\d+) sha256=(\w+)\n\[model output[^\n]*\]\n\n", re.M)
def secs(path):
    b = open(path, "rb").read(); pos = 0; out = []
    while True:
        m = H.search(b, pos)
        if not m: return out
        n = int(m.group(7)); out.append(b[m.end():m.end()+n]); pos = m.end()+n
rows = []
for f in sorted(glob.glob(sub + "/agent-*.jsonl")):
    aid = os.path.basename(f)[6:-6]
    msgs = []
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        c = (d.get("message") or {}).get("content")
        if d.get("type") == "assistant" and isinstance(c, list):
            for b in c:
                if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback": msgs.append(b["input"].get("message"))
    meta = json.load(open(f[:-6] + ".meta.json"))
    for m in msgs:
        ev = dict(hook_event_name="PostToolUse", tool_name="SubagentHandback", agent_id=aid, agent_type=meta.get("agentType"), cwd=LAB, transcript_path=SESS, tool_input=dict(message=m), session_id="x", permission_mode="auto")
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        p = subprocess.run([sys.executable, "-I", HOOK], input=json.dumps(ev), capture_output=True, text=True, env=env)
        assert p.returncode == 0 and p.stdout == ""
    rows.append((aid, meta.get("name"), len(msgs), [m for m in msgs]))
for aid, name, n, msgs in rows:
    if not n: continue
    fn = glob.glob(os.path.join(LAB, "__statera__", "handbacks", "*%s*.md" % (name or "")))
    got = secs(fn[0]) if fn else []
    print(aid, name, "handbacks_in_transcript=%d" % n, "file=%s" % (os.path.basename(fn[0]) if fn else None), "sections=%d" % len(got), "equal=%s" % (got == [m.encode() for m in msgs]), "bytes=%s" % [len(m.encode()) for m in msgs])
