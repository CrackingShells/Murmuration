# Starts one headless haiku session with `--settings FILE` holding autoCompactWindow 1000000, changes FILE to 150000 between two turns of the same process, and prints the effectiveWindow of every autocompact check in the debug log (does a running session pick up a settings change without restart?).
"""usage: w08_c3_settings_live.py S   (S = scratch folder; writes S/live/{win.json,debug.log,stream.jsonl}). Two turns of 'Say ok' on haiku: about USD 0.02. FILE is outside any `.claude/` folder (the lab's guard refuses writes to settings files there)."""
import json, os, re, subprocess, sys, time
S = os.path.abspath(sys.argv[1]); D = os.path.join(S, "live"); os.makedirs(D, exist_ok=True)
W = os.path.join(D, "win.json"); json.dump({"autoCompactWindow": 1000000}, open(W, "w"))
env = dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash")
for k in list(env):
    if k.startswith("CLAUDE_AUTOCOMPACT") or k.startswith("CLAUDE_CODE_AUTO_COMPACT"): env.pop(k)
p = subprocess.Popen(["claude", "-p", "--model", "haiku", "--settings", W, "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
                      "--debug-file", os.path.join(D, "debug.log")], cwd=D, env=env, stdin=subprocess.PIPE, stdout=open(os.path.join(D, "stream.jsonl"), "w"), text=True)
def turn(n):
    p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": "Say ok"}]}}) + "\n"); p.stdin.flush()
    t = time.time()
    while time.time() - t < 60:
        time.sleep(1)
        if sum('"type":"result"' in l.replace(' ', '') for l in open(os.path.join(D, "stream.jsonl"))) >= n: return
turn(1)
json.dump({"autoCompactWindow": 150000}, open(W, "w")); time.sleep(3)
turn(2)
p.stdin.close(); p.wait(timeout=30)
dbg = open(os.path.join(D, "debug.log"), errors="replace").read()
print("effectiveWindow per autocompact check:", re.findall(r"effectiveWindow=(\d+)", dbg))
print("settings change lines:", [l[24:140] for l in dbg.splitlines() if re.search(r"Settings changed|setting files changed|Watching for changes", l)][:6])
