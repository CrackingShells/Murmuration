"""Runs the headless probes for w04-c1: builds a scratch repo with a linked worktree under argv[1] (outside the repository), runs `claude -p` in it with hook dumpers, and writes the hook logs to argv[1]/<case>.jsonl.

Inputs: argv[1] = scratch folder (empty or new), argv[2] = absolute path of hook_payload_dump.py. Output: <case>.jsonl logs and <case>.out.jsonl session streams.
Cases: A = one prompt started in the worktree; B = three turns (say OK; shell cd into the main checkout; say OK) started in the worktree.
CLAUDE_PROJECT_DIR is set to the main checkout in the launch environment to imitate the Desktop. Cost about USD 0.05 per case with haiku.
"""
import json, os, subprocess, sys, time

S, DUMP = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(S, exist_ok=True)
main, wt = os.path.join(S, "main"), os.path.join(S, "wtA")
if not os.path.exists(main):
    git = lambda *a, cwd=main: subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=a", *a], cwd=cwd, check=True, capture_output=True)
    os.makedirs(os.path.join(main, "__statera__"))
    open(os.path.join(main, "__statera__", "wave-01.md"), "w").write("# Wave 01\n\nopened: 2026-01-01\n")
    subprocess.run(["git", "init", "-q", main], check=True)
    git("add", "-A"); git("commit", "-qm", "lab")
    git("worktree", "add", "-q", wt, "-b", "wtA")


def settings(case):
    log = os.path.join(S, case + ".jsonl")
    hook = [{"hooks": [{"type": "command", "command": "python3 -I %s %s" % (DUMP, log), "timeout": 10}]}]
    path = os.path.join(S, case + ".settings.json")
    json.dump({"hooks": {"UserPromptSubmit": hook, "SessionStart": hook}}, open(path, "w"))
    return path


def drive(case, cwd, msgs):
    out = os.path.join(S, case + ".out.jsonl")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=main)
    p = subprocess.Popen(["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
                          "--model", "haiku", "--setting-sources", "project", "--settings", settings(case),
                          "--permission-mode", "bypassPermissions", "--max-budget-usd", "0.40"],
                         cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=open(out, "w"), stderr=subprocess.DEVNULL, text=True)
    n = lambda: sum(1 for l in open(out) if '"type":"result"' in l.replace(" ", ""))
    for i, m in enumerate(msgs):
        p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": m}]}}) + "\n")
        p.stdin.flush()
        t = time.time()
        while n() < i + 1 and time.time() - t < 120:
            time.sleep(0.5)
    p.stdin.close(); p.wait(timeout=60)


drive("A", wt, ["Reply OK."])
drive("B", wt, ["Reply OK.", "Run the shell command: cd %s && pwd . Reply with its output only." % main, "Reply OK."])
