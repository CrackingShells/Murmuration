# w06-c9: runs one headless `claude -p` scenario (a haiku PI that dispatches two haiku explorers) against an export of the Murmuration plugin at a given commit, in a fresh lab folder under /private/tmp/murmuration-w06/author-w06-6/; inputs: run name, commit, optional scenario (base); outputs: <S>/runs/<name>/{run.json,run.err,dbg.log,lab/}; the session transcripts stay in ~/.claude/projects (session_id in run.json)
"""usage: w06c9_run.py NAME COMMIT [base]    (env REPO = the repository to `git archive` from, default the working directory; PERM = permission mode, default auto; W4_TIMEOUT = seconds, default 280)
One export per commit (S/export_<commit>), shared by the runs of that commit; the agents' `model:` lines are set to haiku in every export (cost), nothing else is changed.
Run the two arms of a pair at the same time (two processes): they share no state (own lab folder, own debug file), so the machine's load falls on both. `claude` is started with CLAUDE_CODE_SHELL=/bin/bash,
--permission-mode auto, --debug-file, an export passed with --plugin-dir, no --max-budget-usd.
"""
import json, os, shutil, subprocess, sys, time

S = "/private/tmp/murmuration-w06/author-w06-6"
name, commit = sys.argv[1:3]
scen = sys.argv[3] if len(sys.argv) > 3 else "base"
R = "%s/runs/%s" % (S, name)
lab = R + "/lab"
if os.path.exists(R):
    raise SystemExit("run exists: " + R)
os.makedirs(lab + "/__statera__"); os.makedirs(lab + "/__reports__")
plug = "%s/export_%s" % (S, commit)
if not os.path.isdir(plug):
    tmp = plug + ".tmp%d" % os.getpid()
    os.makedirs(tmp)
    subprocess.run("git -C %s archive %s | tar -x -C %s" % (os.environ.get("REPO", os.getcwd()), commit, tmp), shell=True, check=True)
    for a in os.listdir(tmp + "/agents"):
        t = open(tmp + "/agents/" + a).read()
        open(tmp + "/agents/" + a, "w").write("".join("model: haiku\n" if l.startswith("model:") else l for l in t.splitlines(True)))
    try:
        os.rename(tmp, plug)   # two arms starting at once with one commit: the first rename wins
    except OSError:
        pass


def worker(n, extra="", T="5"):
    return "Your name is explorer-w99-%s.\nBudget: USD 0.50\nTime: min %s\n%sThen call SubagentHandback with message `done`." % (n, T, extra)


def lead(workers, tail=""):
    steps = ["Step 1: run Bash `echo main-1`."]
    for n, prompt in workers:
        steps.append("Step %d: call the Agent tool with subagent_type `murmuration:explorer`, name `explorer-w99-%s` and this exact prompt (between the markers, markers excluded) and wait for it: <<<%s>>>" % (len(steps) + 1, n, prompt))
    return " ".join(steps) + tail + " Last step: reply with one line per worker giving its report text."


B = "Run Bash `echo a-%s`, then Bash `echo b-%s`. "
SC = {"base": lead([(str(i), worker(i, B % (i, i))) for i in range(2)])}
cmd = ["claude", "-p", SC[scen], "--model", "haiku", "--agent", "murmuration:research-pi", "--plugin-dir", plug, "--permission-mode", os.environ.get("PERM", "auto"),
       "--debug-file", R + "/dbg.log", "--output-format", "json"]
t0 = time.time()
r = subprocess.run(cmd, cwd=lab, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=int(os.environ.get("W4_TIMEOUT", "280")),
                   env=dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash"))
open(R + "/run.json", "w").write(r.stdout)
open(R + "/run.err", "w").write(r.stderr)
print(name, "rc", r.returncode, "wall_s", round(time.time() - t0, 1), "out", len(r.stdout))
