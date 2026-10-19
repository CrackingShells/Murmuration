import json, os, subprocess, sys, shutil, re
HOOK = sys.argv[1]; LAB = os.path.abspath("edge_lab"); shutil.rmtree(LAB, ignore_errors=True); os.makedirs(LAB + "/__statera__")
def fire(**kw):
    ev = dict(cwd=LAB, hook_event_name="PostToolUse", tool_name="SubagentHandback", agent_id="aX", agent_type="t:t", session_id="s", transcript_path=LAB + "/s.jsonl"); ev.update(kw)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    p = subprocess.run([sys.executable, "-I", HOOK], input=json.dumps(ev), capture_output=True, text=True, env=env); return p.returncode, p.stdout, p.stderr
# 1 header-lookalike quoting an earlier file section for the same agent id and a sha equal to the next message's sha
nxt = "second message"
import hashlib
sha = hashlib.sha256(nxt.encode()).hexdigest()[:12]
fake = "quoted from a file:\n## hand-back 7 | 2026-10-19T11:00:00+09:00 | agent_id=aX type=t:t event=SubagentStop bytes=14 sha256=%s\n\nsecond message\n" % sha
fire(tool_input=dict(message=fake), agent_type="t:t")
fire(tool_input=dict(message=nxt))
t = open(LAB + "/__statera__/handbacks/t-t-aX.md".replace("t-t-aX", "t-t-aX")).read() if os.path.exists(LAB + "/__statera__/handbacks/t-t-aX.md") else None
print("file", os.listdir(LAB + "/__statera__/handbacks"))
t = open(LAB + "/__statera__/handbacks/" + os.listdir(LAB + "/__statera__/handbacks")[0]).read()
print([m for m in re.findall(r"^## hand-back (\d+) .*? bytes=(\d+) sha256=(\w+)$", t, re.M)])
print("legit second message written?", t.count("\nsecond message\n"), "(1 inside the quote, +1 if written)")
# 2 lone surrogate
shutil.rmtree(LAB + "/__statera__/handbacks")
print("surrogate:", fire(tool_input=dict(message="bad \ud800 text"), agent_id="aS")[:1], os.path.exists(LAB + "/__statera__/handbacks") and os.listdir(LAB + "/__statera__/handbacks"))
