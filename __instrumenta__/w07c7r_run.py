# Runs one headless haiku session of the w07-c7 reproduction (arm A = ac07ab3, arm B = f376bef author agent file, model set to haiku): kind c2 = one author doing a 330 s bounded wait inside one Bash call, kind resume = author finishes, main thread waits 330 s, then SendMessage resumes the author; inputs: S scratch folder, lab repo, the two commits, label (A4/B4 = c2, AR/BR = resume, AC/BC = c2 wait inside the author and then the resume); outputs: S/runs/<label>.json, S/runs/times.tsv, S/work/<label>/ (cwd).
# usage: w07c7r_run.py S REPO COMMIT_A COMMIT_B label
import os, subprocess, sys, time
S, REPO, CA, CB, label = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
def export(tag, commit):
    d = os.path.join(S, "plugin_" + tag)
    if not os.path.isdir(d):
        os.makedirs(d)
        subprocess.run("git -C %s archive %s | tar -x -C %s" % (REPO, commit, d), shell=True, check=True)
        p = os.path.join(d, "agents", "author.md")
        txt = open(p).read().replace("model: sonnet\n", "model: haiku\n", 1)
        assert "model: haiku" in txt and len(txt) > 1000
        open(p, "w").write(txt)
    return d
pl = export("A", CA) if label[0] == "A" else export("B", CB)
WAIT = "`timeout 330 sh -c 'until false; do sleep 5; done'; echo waited`"
BODY = ("This is a cache test, not a research task: file no claim, write no file. Make these Bash calls, one per turn, in this order, each exactly as written. "
        "Call 1 `pwd`. Call 2: command `timeout 330 sh -c 'until false; do sleep 5; done'; echo waited`, with the Bash timeout parameter set to 360000. "
        "Call 3 `date`. Then reply 'done' and nothing else.")
if label.endswith("4"):
    P = ("Make exactly one call of the Agent tool with subagent_type `murmuration:author`, name `author-test`, and as its prompt exactly this text: \"" + BODY.replace('"', "'") +
         "\". Wait for it to finish, then reply with its answer and nothing else.")
else:
    first = BODY if label.endswith("C") else "This is a cache test, not a research task: file no claim, write no file. Make one Bash call `pwd`, then reply 'done' and nothing else."
    P = ("Step 1: make exactly one call of the Agent tool with subagent_type `murmuration:author`, name `author-test`, and as its prompt exactly this text: "
         "\"" + first.replace('"', "'") + "\" Wait for it to finish. "
         "Step 2: make one Bash call with command " + WAIT + " and the Bash timeout parameter set to 360000. "
         "Step 3: look up the SendMessage tool with ToolSearch if it is not available, then call SendMessage with to `author-test` and message \"Make one Bash call `date`, then reply 'done again' and nothing else.\" "
         "Step 4: reply with the author's answers and nothing else.")
os.makedirs(os.path.join(S, "runs"), exist_ok=True)
w = os.path.join(S, "work", label); os.makedirs(w, exist_ok=True)
cmd = ["claude", "-p", P, "--model", "haiku", "--permission-mode", "auto", "--output-format", "json", "--strict-mcp-config", "--plugin-dir", pl]
env = dict(os.environ); env["CLAUDE_CODE_SHELL"] = "/bin/bash"
t0 = time.time()
r = subprocess.run(cmd, cwd=w, capture_output=True, text=True, timeout=1200, env=env)
t1 = time.time()
open(os.path.join(S, "runs", label + ".json"), "w").write(r.stdout)
open(os.path.join(S, "runs", label + ".err"), "w").write(r.stderr[-2000:])
open(os.path.join(S, "runs", "times.tsv"), "a").write("%s\t%.0f\t%.1f\t%d\n" % (label, t0, t1 - t0, r.returncode))
print(label, "rc", r.returncode, "%.1fs" % (t1 - t0), flush=True)
