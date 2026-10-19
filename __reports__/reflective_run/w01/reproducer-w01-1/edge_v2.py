import json, os, subprocess, sys, shutil, hashlib, glob
HOOK = sys.argv[1]; LAB = os.path.abspath("edge_lab_v2"); shutil.rmtree(LAB, ignore_errors=True); os.makedirs(LAB + "/__statera__")
exec(open("cmp_mine_v2.py").read().split("def payloads")[0].split("import sys")[1].join(["import sys",""]) if False else "")
import re
H = re.compile(rb"^## hand-back (\d+) \| (\S+) \| agent_id=(\S+) type=(\S+) event=(\S+) status=(\S+) bytes=(\d+) sha256=(\w+)\n\[model output[^\n]*\]\n\n", re.M)
def secs(path):
    b = open(path, "rb").read(); pos = 0; out = []
    while True:
        m = H.search(b, pos)
        if not m: return out
        n = int(m.group(7)); out.append((int(m.group(1)), m.group(6).decode(), b[m.end():m.end()+n])); pos = m.end()+n
def fire(**kw):
    ev = dict(cwd=LAB, hook_event_name="PostToolUse", tool_name="SubagentHandback", agent_id="aX", agent_type="t:t", session_id="s", transcript_path=LAB + "/s.jsonl", permission_mode="auto"); ev.update(kw)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    p = subprocess.run([sys.executable, "-I", HOOK], input=json.dumps(ev), capture_output=True, text=True, env=env); return p.returncode, p.stdout, p.stderr
def files(): return glob.glob(LAB + "/__statera__/handbacks/*.md")
nxt = "second message"; sha = hashlib.sha256(nxt.encode()).hexdigest()[:12]
fake = "quoted:\n## hand-back 7 | 2026-10-19T11:00:00+09:00 | agent_id=aX type=t:t event=PostToolUse status=delivered bytes=14 sha256=%s\n[model output: x]\n\nsecond message\n" % sha
fire(tool_input=dict(message=fake)); fire(tool_input=dict(message=nxt))
print("quoted header:", [(a, b, c[:20]) for a, b, c in secs(files()[0])])
shutil.rmtree(LAB + "/__statera__/handbacks")
print("surrogate:", fire(tool_input=dict(message="bad \ud800 text"), agent_id="aS")[0], [(a, b, c) for f in files() for a, b, c in secs(f)])
# draft then no delivery then a stop without text: gap guard
shutil.rmtree(LAB + "/__statera__/handbacks")
fire(hook_event_name="SubagentStop", tool_name=None, last_assistant_message="draft text", agent_id="aD")
fire(hook_event_name="SubagentStop", tool_name=None, agent_id="aD")
print("draft then empty stop:", [(a, b, c[:30]) for f in files() for a, b, c in secs(f)])
# same in default mode: a SubagentStop with text is delivered
shutil.rmtree(LAB + "/__statera__/handbacks")
fire(hook_event_name="SubagentStop", tool_name=None, last_assistant_message="default text", agent_id="aE", permission_mode="default")
print("default stop:", [(a, b, c[:30]) for f in files() for a, b, c in secs(f)])
# permission_mode missing (older/other binaries) -> counted as delivered?
shutil.rmtree(LAB + "/__statera__/handbacks")
ev = dict(hook_event_name="SubagentStop", last_assistant_message="no mode", agent_id="aF", agent_type="t:t", cwd=LAB)
subprocess.run([sys.executable, "-I", HOOK], input=json.dumps(ev), capture_output=True, text=True)
print("no permission_mode:", [(a, b, c[:30]) for f in files() for a, b, c in secs(f)])
# read-only folder
os.makedirs(LAB + "/__statera__/handbacks", exist_ok=True); os.chmod(LAB + "/__statera__/handbacks", 0o500)
r = fire(tool_input=dict(message="ro"), agent_id="aR"); os.chmod(LAB + "/__statera__/handbacks", 0o700)
print("read-only dir:", r[0], repr(r[1]), "files", [os.path.basename(f) for f in files()])
