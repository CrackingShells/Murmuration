"""Headless check of where the changed prompt hook writes when the session's lab changes under it: from a scripts dir and a scenario (enter | resume) to a table, one row per prompt, of the payload cwd, the transcript head cwd and the lab folder that received the marker.

usage: hook_enter_worktree_resume_run.py <scratch dir outside the repo> <scripts dir> <scenario> [pd=main|unset]
scenario `enter`: start in repo `main` (with a lab), prompt 1 marker, prompt 2 asks the agent to call the EnterWorktree tool (name enterwt) and print pwd, prompt 3 marker.
scenario `resume`: start in linked worktree `wtA`, prompt 1 marker; then a second `claude -p --resume <session id>` process started in `main` with a marker prompt.
The hook command (user_words.py + hook_payload_dump.py) is prefixed CLAUDE_PROJECT_DIR=<main> when pd=main (the Desktop's presumed value), else the variable is unset. Cost about USD 0.10 per scenario (haiku, cap 0.40).
Reuses/creates in <scratch>: main, wtA (linked worktree of main), with a __statera__ committed in main.
"""
import json, os, shutil, subprocess, sys, time

S, SCRIPTS, SCEN = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
PD = sys.argv[4] if len(sys.argv) > 4 else "main"
main, wt = os.path.join(S, "main"), os.path.join(S, "wtA")
tag = SCEN + "-" + PD
dump = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hook_payload_dump.py")


def git(cwd, *a):
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=a", *a], cwd=cwd, check=True, capture_output=True)


if not os.path.exists(main):
    os.makedirs(os.path.join(main, "__statera__"))
    open(os.path.join(main, "__statera__", "wave-01.md"), "w").write("# Wave 01\n\nopened: 2026-01-01\n")
    subprocess.run(["git", "init", "-q", main], check=True)
    git(main, "add", "-A"); git(main, "commit", "-qm", "lab")
    git(main, "worktree", "add", "-q", wt, "-b", "wtA")
plug = os.path.join(S, "plugin-" + tag)
shutil.rmtree(plug, ignore_errors=True)
for d in (".claude-plugin", "hooks", "scripts"):
    os.makedirs(os.path.join(plug, d))
json.dump({"name": "ewt-probe", "version": "0.0.1", "description": "probe"}, open(os.path.join(plug, ".claude-plugin", "plugin.json"), "w"))
for f in ("user_words.py", "resume_brief.py", "lab_status.py"):
    shutil.copy(os.path.join(SCRIPTS, f), os.path.join(plug, "scripts", f))
pre = 'CLAUDE_PROJECT_DIR="%s" ' % main if PD == "main" else ""
log = os.path.join(S, tag + ".payload.jsonl")
os.path.exists(log) and os.remove(log)
json.dump({"hooks": {"UserPromptSubmit": [{"hooks": [
    {"type": "command", "command": pre + 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/user_words.py"', "timeout": 10},
    {"type": "command", "command": pre + 'python3 -I "%s" "%s"' % (dump, log), "timeout": 10}]}]}},
    open(os.path.join(plug, "hooks", "hooks.json"), "w"))
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
base = ["claude", "--model", "haiku", "--setting-sources", "project", "--plugin-dir", plug, "--permission-mode", "bypassPermissions", "--max-budget-usd", "0.40"]
M = lambda i: "MARK-%s-%d" % (tag, i)
sid = None
if SCEN == "enter":
    out = os.path.join(S, tag + ".out.jsonl")
    p = subprocess.Popen(base + ["-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose"],
                         cwd=main, env=env, stdin=subprocess.PIPE, stdout=open(out, "w"), stderr=subprocess.DEVNULL, text=True)
    msgs = [M(1) + " first prompt", M(2) + " Call the EnterWorktree tool with name enterwt, then run the shell command pwd and reply with its output only.", M(3) + " third prompt"]
    n = lambda: sum(1 for l in open(out) if '"type":"result"' in l.replace(" ", ""))
    for i, m in enumerate(msgs):
        p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": m}]}}) + "\n"); p.stdin.flush()
        t = time.time()
        while n() < i + 1 and time.time() - t < 150:
            time.sleep(0.5)
    p.stdin.close(); p.wait(timeout=60)
    nm = 3
else:
    out = os.path.join(S, tag + ".out1.jsonl")
    subprocess.run(base + ["-p", "--output-format", "stream-json", "--verbose", M(1) + " first prompt, reply OK"], cwd=wt, env=env, stdout=open(out, "w"), stderr=subprocess.DEVNULL, timeout=180)
    for l in open(out):
        try:
            sid = json.loads(l).get("session_id") or sid
        except ValueError:
            pass
    out2 = os.path.join(S, tag + ".out2.jsonl")
    r = subprocess.run(base + ["-p", "--resume", sid, "--output-format", "stream-json", "--verbose", M(2) + " second prompt after resume, reply OK"], cwd=main, env=env, stdout=open(out2, "w"), stderr=subprocess.PIPE, text=True, timeout=180)
    print("resume exit", r.returncode, (r.stderr or "")[:200])
    nm = 2
rows = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
labs = [d for d in ("main", "wtA") if os.path.exists(os.path.join(S, d, "__statera__", "user_words.md"))]
for d in os.listdir(os.path.join(main, ".claude", "worktrees")) if os.path.isdir(os.path.join(main, ".claude", "worktrees")) else []:
    labs.append(".claude/worktrees/" + d)
for i in range(1, nm + 1):
    where = []
    for d in labs:
        f = os.path.join(S, "main" if d.startswith(".") else d, d if d.startswith(".") else "", "__statera__", "user_words.md")
        if os.path.exists(f) and M(i) in open(f).read():
            where.append(d)
    r = rows[i - 1] if len(rows) >= i else {}
    hc = [h.get("cwd") for h in r.get("head", []) if h.get("cwd")]
    print("%s prompt %d: payload cwd %s, env PD %s, transcript on disk %s, first head cwd %s -> lab %s" % (
        tag, i, os.path.basename(r.get("payload_cwd") or "?"), os.path.basename(r.get("env_CLAUDE_PROJECT_DIR") or "-"), r.get("transcript_exists"), os.path.basename(hc[0]) if hc else None, where or "nowhere"))
