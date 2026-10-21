# Runs the headless haiku sessions of P6 (author agent file A against B = A + experimental.cacheTtl 1h): exports A and B plugins from git with the author's model set to haiku, then runs one main thread that dispatches one murmuration:author doing fixed tool calls (c1: 4 short Bash calls; c2: one 6-7 minute bounded wait inside one Bash call); inputs: git repo with commits A and B, the claude CLI; outputs: <S>/runs/<label>.json (run output), <S>/runs/times.tsv (label, start epoch, wall s), <S>/work/<label>/ (cwd, so the transcript project folder is per label).
# usage: w07c7_run.py S REPO COMMIT_A COMMIT_B label[,label...]   labels: A1 A2 B1 B2 (c1) A3 B3 (c2); run c2 labels in parallel from separate processes
import os, subprocess, sys, time, shutil
S, REPO, CA, CB, labels = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].split(",")
def export(tag, commit):
    d = os.path.join(S, "plugin_" + tag)
    if not os.path.isdir(d):
        os.makedirs(d)
        subprocess.run("git -C %s archive %s | tar -x -C %s" % (REPO, commit, d), shell=True, check=True)
        p = os.path.join(d, "agents", "author.md")
        s = open(p).read().replace("model: sonnet\n", "model: haiku\n", 1)
        open(p, "w").write(s)
    return d
PL = {"A": export("A", CA), "B": export("B", CB)}
C1 = ("This is a cache test, not a research task: file no claim, write no file. Make these Bash calls, one per turn, in this order, each exactly as written, "
      "then reply 'done' and nothing else: `pwd`; `ls`; `date`; `echo hi`.")
C2 = ("This is a cache test, not a research task: file no claim, write no file. Make these Bash calls, one per turn, in this order, each exactly as written. "
      "Call 1 `pwd`. Call 2: command `timeout 420 sh -c 'until false; do sleep 5; done'; echo waited`, with the Bash timeout parameter set to 450000. "
      "Call 3 `date`. Then reply 'done' and nothing else.")
def prompt(label):
    body = C2 if label in ("A3", "B3") else C1
    return ("Make exactly one call of the Agent tool with subagent_type `murmuration:author`, name `author-test`, and as its prompt exactly this text: \"" + body.replace('"', "'") +
            "\". Wait for it to finish, then reply with its answer and nothing else.")
os.makedirs(os.path.join(S, "runs"), exist_ok=True)
for label in labels:
    w = os.path.join(S, "work", label); os.makedirs(w, exist_ok=True)
    cmd = ["claude", "-p", prompt(label), "--model", "haiku", "--permission-mode", "auto", "--output-format", "json", "--strict-mcp-config", "--plugin-dir", PL[label[0]]]
    env = dict(os.environ); env["CLAUDE_CODE_SHELL"] = "/bin/bash"
    t0 = time.time()
    r = subprocess.run(cmd, cwd=w, capture_output=True, text=True, timeout=1500, env=env)
    t1 = time.time()
    open(os.path.join(S, "runs", label + ".json"), "w").write(r.stdout)
    open(os.path.join(S, "runs", label + ".err"), "w").write(r.stderr[-2000:])
    with open(os.path.join(S, "runs", "times.tsv"), "a") as f:
        f.write("%s\t%.0f\t%.1f\t%d\n" % (label, t0, t1 - t0, r.returncode))
    print(label, "rc", r.returncode, "%.1fs" % (t1 - t0), flush=True)
