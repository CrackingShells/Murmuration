# Runs the 16 fixed headless haiku sessions of explorer-w07-g (permission mode x colgrep hook x lab plugin; context length; four ways to read four files), one after another, and writes per session a run JSON, a --debug-file log and a load-average line; inputs: the claude CLI, the scratch dir with work/ files and plugin/ export, outputs: <S>/runs/<label>.json, <S>/dbg/<label>.log, <S>/runs/loadavg.tsv.
# usage: w07g_run.py S [--only label,label]   (labels listed in PLAN; order is fixed: B0 first to verify the colgrep switch, the rest shuffled with seed 7)
import json, os, random, subprocess, sys, time

S = os.path.abspath(sys.argv[1])
only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
WORK = os.path.join(S, "work")
PLUG = os.path.join(S, "plugin")
BASIC = "Call the Bash tool once per command, one call per turn, in this order, each command exactly as written, then stop. Write no other text. Commands: " + "; ".join("`%s`" % c for c in ["ls", "cat a.txt", "head -n 2 b.txt", "pwd", "wc -l a.txt", "date", "echo hi", "ls -la"])
ALLOW = ",".join("Bash(%s *)" % c for c in ["ls", "cat", "head", "wc", "echo"]) + ",Bash(pwd),Bash(date),Bash(ls),Bash(date -u),Bash(pwd -P)"
OFF = json.dumps({"enabledPlugins": {"colgrep-mcp@cracking-shells": False}})
LEN = ("Do these steps in order, one tool call per turn, each exactly as written, then reply done. Write no other text. "
       "1 Bash `pwd`; 2 Bash `date`; 3 Bash `echo hi`; 4 Bash `ls`; 5 Bash `echo go`; "
       "6 Read /private/tmp/murmuration-w07/explorer-w07-g/work/big1.txt; 7 Read /private/tmp/murmuration-w07/explorer-w07-g/work/big2.txt; 8 Read /private/tmp/murmuration-w07/explorer-w07-g/work/big3.txt; "
       "9 Bash `pwd -P`; 10 Bash `date -u`; 11 Bash `echo ok`; 12 Bash `ls -a`; 13 Bash `echo end`.")
D = "/private/tmp/murmuration-w07/explorer-w07-g/work/"
WAYS = {
    "W1": "Make exactly one Bash call with this command: `cat a.txt; cat b.txt; cat c.txt; cat d.txt`. Then reply done. Write no other text.",
    "W2": "Make four Bash calls in one single message (all four tool calls together, not one per turn): `cat a.txt`, `cat b.txt`, `cat c.txt`, `cat d.txt`. Then reply done. Write no other text.",
    "W3": "Make four Read calls in one single message (all four tool calls together, not one per turn) for %sa.txt, %sb.txt, %sc.txt, %sd.txt. Then reply done. Write no other text." % (D, D, D, D),
    "W4": "Make four Read calls, one per turn, in this order: %sa.txt, %sb.txt, %sc.txt, %sd.txt. Then reply done. Write no other text." % (D, D, D, D),
}
# label: (prompt, permission mode, colgrep hook on, lab plugin on)
PLAN = {}
for rep in (0, 1):
    PLAN["A%d" % rep] = (BASIC, "auto", True, False)
    PLAN["B%d" % rep] = (BASIC, "auto", False, False)
    PLAN["C%d" % rep] = (BASIC, "auto", True, True)
    PLAN["D%d" % rep] = (BASIC, "auto", False, True)
    PLAN["F%d" % rep] = (BASIC, "default", False, False)
for k, v in WAYS.items():
    PLAN[k] = (v, "auto", False, False)
for rep in (0, 1):
    PLAN["L%d" % rep] = (LEN, "auto", False, False)
PLAN.pop("A0")  # A0 is the trial run, already done with the same command line (label trial)
labels = list(PLAN)
rng = random.Random(7)
first = "B0"
rest = [l for l in labels if l != first]
rng.shuffle(rest)
order = [first] + rest
if only:
    order = [l for l in order if l in only]
os.makedirs(os.path.join(S, "runs"), exist_ok=True)
os.makedirs(os.path.join(S, "dbg"), exist_ok=True)
for label in order:
    prompt, mode, colgrep, plug = PLAN[label]
    dbg = os.path.join(S, "dbg", label + ".log")
    cmd = ["claude", "-p", prompt, "--model", "haiku", "--permission-mode", mode, "--output-format", "json", "--debug-file", dbg, "--strict-mcp-config"]
    if mode == "default":
        cmd += ["--allowedTools", ALLOW]
    if not colgrep:
        cmd += ["--settings", OFF]
    if plug:
        cmd += ["--plugin-dir", PLUG]
    env = dict(os.environ)
    env["CLAUDE_CODE_SHELL"] = "/bin/bash"
    la0 = os.getloadavg()
    t0 = time.time()
    r = subprocess.run(cmd, cwd=WORK, capture_output=True, text=True, timeout=240, env=env)
    t1 = time.time()
    la1 = os.getloadavg()
    open(os.path.join(S, "runs", label + ".json"), "w").write(r.stdout)
    open(os.path.join(S, "runs", label + ".err"), "w").write(r.stderr[-2000:])
    with open(os.path.join(S, "runs", "loadavg.tsv"), "a") as f:
        f.write("%s\t%.0f\t%.2f\t%.2f\t%.2f\t%.2f\t%.1f\n" % (label, t0, la0[0], la0[1], la1[0], la1[1], t1 - t0))
    print(label, "rc", r.returncode, "%.1fs" % (t1 - t0), "load1 %.2f -> %.2f" % (la0[0], la1[0]), flush=True)
