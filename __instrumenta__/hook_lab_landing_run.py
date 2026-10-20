"""Headless end-to-end check of where the prompt hook writes: from a scripts folder (user_words.py, resume_brief.py, lab_status.py) to a table of which lab folder received each prompt, one row per prompt.

usage: hook_lab_landing_run.py <scratch dir outside the repo> <scripts dir> <arm name>. Builds (once) a scratch repo `main` with a lab and a linked worktree `wtA` with the lab, plus a second repo `other` with a lab;
exports the scripts as a plugin (--plugin-dir) whose hooks run them with CLAUDE_PROJECT_DIR=<main> (the Desktop's presumed value; the platform ignores a launch-time CLAUDE_PROJECT_DIR and sets it to the start directory, so the hook command sets it);
runs `claude -p` (haiku, USD 0.40 cap, `--add-dir <other>` so that the shell may `cd` there: without it the Bash tool resets the shell to the project and the payload cwd never moves; the Desktop passes `--add-dir` too) started in `wtA` for three turns: (1) a marker prompt, (2) a marker prompt that asks for `cd <other> && pwd`, (3) a marker prompt. Prints, per prompt, the payload cwd, whether the transcript file existed, and the labs holding the marker; hook payload dumps go to <scratch>/<arm>.payload.jsonl. Cost about USD 0.10.
"""
import json, os, shutil, subprocess, sys, time

S, SCRIPTS, ARM = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
main, wt, other = (os.path.join(S, d) for d in ("main", "wtA", "other"))


def git(cwd, *a):
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=a", *a], cwd=cwd, check=True, capture_output=True)


if not os.path.exists(main):
    for repo in (main, other):
        os.makedirs(os.path.join(repo, "__statera__"))
        open(os.path.join(repo, "__statera__", "wave-01.md"), "w").write("# Wave 01\n\nopened: 2026-01-01\n")
        subprocess.run(["git", "init", "-q", repo], check=True)
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "lab")
    git(main, "worktree", "add", "-q", wt, "-b", "wtA")
plug = os.path.join(S, "plugin-" + ARM)
shutil.rmtree(plug, ignore_errors=True)
os.makedirs(os.path.join(plug, ".claude-plugin")); os.makedirs(os.path.join(plug, "hooks")); os.makedirs(os.path.join(plug, "scripts"))
json.dump({"name": "landing-probe", "version": "0.0.1", "description": "probe"}, open(os.path.join(plug, ".claude-plugin", "plugin.json"), "w"))
for f in ("user_words.py", "resume_brief.py", "lab_status.py"):
    shutil.copy(os.path.join(SCRIPTS, f), os.path.join(plug, "scripts", f))
cmd = lambda f: 'CLAUDE_PROJECT_DIR="%s" python3 "${CLAUDE_PLUGIN_ROOT}/scripts/%s"' % (main, f)
dump = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hook_payload_dump.py")
log = os.path.join(S, ARM + ".payload.jsonl")
os.path.exists(log) and os.remove(log)
json.dump({"hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": cmd("user_words.py"), "timeout": 10},
                                                     {"type": "command", "command": 'python3 -I "%s" "%s"' % (dump, log), "timeout": 10}]}],
                     "SessionStart": [{"matcher": "resume|compact", "hooks": [{"type": "command", "command": cmd("resume_brief.py"), "timeout": 10}]}]}},
          open(os.path.join(plug, "hooks", "hooks.json"), "w"))

markers = ["MARK-%s-1 first prompt" % ARM, "MARK-%s-2 Run the shell command: cd %s && pwd . Reply with its output only." % (ARM, other), "MARK-%s-3 third prompt, shell is elsewhere" % ARM]
out = os.path.join(S, ARM + ".out.jsonl")
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
p = subprocess.Popen(["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose", "--model", "haiku",
                      "--setting-sources", "project", "--plugin-dir", plug, "--add-dir", other, "--permission-mode", "bypassPermissions", "--max-budget-usd", "0.40"],
                     cwd=wt, env=env, stdin=subprocess.PIPE, stdout=open(out, "w"), stderr=subprocess.DEVNULL, text=True)
n = lambda: sum(1 for l in open(out) if '"type":"result"' in l.replace(" ", ""))
for i, m in enumerate(markers):
    p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": m}]}}) + "\n"); p.stdin.flush()
    t = time.time()
    while n() < i + 1 and time.time() - t < 120:
        time.sleep(0.5)
p.stdin.close(); p.wait(timeout=60)
for i, m in enumerate(markers, 1):
    where = [d for d in ("main", "wtA", "other") if os.path.exists(os.path.join(S, d, "__statera__", "user_words.md"))
             and ("MARK-%s-%d" % (ARM, i)) in open(os.path.join(S, d, "__statera__", "user_words.md")).read()]
    rows = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
    pc = os.path.basename(rows[i - 1]["payload_cwd"]) if len(rows) >= i else "?"
    print("%s prompt %d: payload cwd %s, transcript on disk %s -> lab %s" % (ARM, i, pc, rows[i - 1]["transcript_exists"] if len(rows) >= i else "?", where or "nowhere"))
