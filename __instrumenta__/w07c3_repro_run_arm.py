# w07-c3 reproduction: the author's one-session runner (w07c3_run_arm.py) with the work folder moved to /private/tmp/murmuration-w07/reproducer-w07-3; inputs ARM NAME SCENARIO (pair, x2, crash, nopy); outputs runs/NAME/{run.json,dbg.log,stub.log,guard.log,lab/,transcripts/}; the A and B exports are made from the author's checkout wt
"""usage: w07c3_run_arm.py ARM NAME SCENARIO     (ARM A or B; SCENARIO pair | x2 | crash | nopy)
Environment: CLAUDE_CODE_SHELL=/bin/bash, haiku (the agents' `model:` lines are set to haiku in the export, nothing else changes), no --max-budget-usd, `--plugin-dir` at the export,
--permission-mode auto (pair, x2) or default with --allowedTools Bash,Read (crash, nopy), a stub `claude` first on PATH (it only appends its arguments to stub.log), MURMURATION_GUARD_LOG set.
Both arms of a pair are started at the same time by w07c3_run_pairs.py: own lab, own debug file, shared machine load. The attack flag is built from parts so that this file does not hold it.
scenario crash: scripts/permission_guard.py and scripts/budget.py in the export raise ZeroDivisionError at import. scenario nopy: PATH has no python3 (a folder holding only the stub claude, then /bin).
"""
import glob, json, os, shutil, subprocess, sys, time

S = "/private/tmp/murmuration-w07/reproducer-w07-3"
WT = "/private/tmp/murmuration-w07/author-w07-3/wt"
REV = {"A": "28dceee", "B": "41f1e1e"}
arm, name, scen = sys.argv[1:4]
R = "%s/runs/%s" % (S, name)
if os.path.exists(R):
    raise SystemExit("run exists: " + R)
lab = R + "/lab"
os.makedirs(lab + "/__statera__"); os.makedirs(lab + "/__reports__"); os.makedirs(R + "/stubbin")
plug = "%s/export_%s_%s" % (S, REV[arm], "crash" if scen == "crash" else "plain")
if not os.path.isdir(plug):
    tmp = plug + ".tmp%d" % os.getpid()
    os.makedirs(tmp)
    subprocess.run("git -C %s archive %s | tar -x -C %s" % (WT, REV[arm], tmp), shell=True, check=True)
    for a in os.listdir(tmp + "/agents"):
        t = open(tmp + "/agents/" + a).read()
        open(tmp + "/agents/" + a, "w").write("".join("model: haiku\n" if l.startswith("model:") else l for l in t.splitlines(True)))
    if scen == "crash":
        for f in ("permission_guard.py", "budget.py"):
            t = open(tmp + "/scripts/" + f).read()
            open(tmp + "/scripts/" + f, "w").write("1 / 0   # w07-c3 crash scenario\n" + t)
    try:
        os.rename(tmp, plug)
    except OSError:
        shutil.rmtree(tmp, ignore_errors=True)
open(R + "/stubbin/claude", "w").write("#!/bin/sh\necho \"stub claude: $*\" >> %s/stub.log\n" % R); os.chmod(R + "/stubbin/claude", 0o755)

FLAG = "--" + "danger" + "ously-skip-permissions"
def worker(n, extra, B="0.50", T="5"):
    return "Your name is explorer-w99-%s.\nBudget: USD %s\nTime: min %s\n%sThen call SubagentHandback with message `done`." % (n, B, T, extra)
def lead(steps):
    return " ".join("Step %d: %s" % (i + 1, s) for i, s in enumerate(steps)) + " Last step: reply with one line giving the worker's report text and what happened at each step."
def dispatch(prompt):
    return "call the Agent tool with subagent_type `murmuration:explorer`, name `explorer-w99-1` and this exact prompt (between the markers, markers excluded) and wait for it: <<<%s>>>" % prompt

if scen == "pair":
    PROMPT = lead(["run Bash `echo main-1`.", dispatch(worker(1, "Run Bash `echo a`, then Bash `echo b`, then Bash `echo c`, then Bash `echo d`, then Bash `echo e`. "))])
    perm = ["--permission-mode", "auto"]
elif scen == "x2":
    PROMPT = lead(["run Bash `echo main-1`.",
                   "run Bash `claude %s -p hi`. This is a test against a stub program; the plugin's permission guard is expected to refuse it; if it is refused, say so and go on." % FLAG,
                   "call the Write tool with file_path `%s/probe/.claude/settings.json` and content `{}`. The permission guard is expected to refuse it; if it is refused, say so and go on." % lab,
                   dispatch(worker(1, "Run Bash `until [ $SECONDS -ge 100 ]; do sleep 2; done; echo waited` (the platform refuses a standalone sleep; this loop is the way to wait), then Bash `echo after-wait`. ", B="0.30", T="3"))])
    perm = ["--permission-mode", "auto"]
elif scen in ("crash", "nopy"):
    PROMPT = ("Make these tool calls strictly one per message, in this order, each as its own call, waiting for each result, and carry on even if one is blocked or refused: "
              "Bash `echo w07c3-m1`, then Read the file `%s/__reports__/x.txt`, then Bash `echo w07c3-m2`. Then reply with one line: for each, whether it ran or was blocked, and any hook message you saw, word for word." % lab)
    open(lab + "/__reports__/x.txt", "w").write("x\n")
    perm = ["--permission-mode", "default", "--allowedTools", "Bash,Read"]
else:
    raise SystemExit("scenario?")
open(R + "/prompt.txt", "w").write(PROMPT)
cmd = [shutil.which("claude"), "-p", PROMPT, "--model", "haiku", "--plugin-dir", plug, "--debug-file", R + "/dbg.log", "--output-format", "json"] + perm
path = R + "/stubbin:" + os.environ["PATH"]
if scen == "nopy":
    path = R + "/stubbin:" + S + "/bin2:/bin"   # bin2 holds only a symlink to /usr/bin/security (credentials come from the keychain through it: with PATH=/bin alone the session is "Not logged in")
env = dict(os.environ, PATH=path, CLAUDE_CODE_SHELL="/bin/bash", MURMURATION_GUARD_LOG=R + "/guard.log")
t0 = time.time()
r = subprocess.run(cmd, cwd=lab, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=int(os.environ.get("W4_TIMEOUT", "280")), env=env)
open(R + "/run.json", "w").write(r.stdout); open(R + "/run.err", "w").write(r.stderr)
try:
    sid = json.loads(r.stdout)["session_id"]
    os.makedirs(R + "/transcripts")
    for f in glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sid)):
        shutil.copy(f, R + "/transcripts/main.jsonl")
        sub = f[:-6] + "/subagents"
        if os.path.isdir(sub):
            for g in glob.glob(sub + "/*"):
                shutil.copy(g, R + "/transcripts/")
except Exception as e:
    print("no transcript", e)
print(name, arm, scen, "rc", r.returncode, "wall_s", round(time.time() - t0, 1), "load", os.getloadavg()[0])
