# w06-c3: runs one headless `claude -p --agent wt:lead --model haiku` scenario against a built test plugin; inputs: scenario name, plugin dir, WT_OUT dir (server log lives there), cwd dir, mode (live|quiet), permission mode; outputs: <WT_OUT>/run.json (claude's JSON result), <WT_OUT>/dbg.log (debug file)
import json, os, subprocess, sys, time

scen, plug, out, cwd, mode, perm = sys.argv[1:7]
out, cwd = os.path.abspath(out), os.path.abspath(cwd)
os.makedirs(out, exist_ok=True); os.makedirs(cwd, exist_ok=True)
open(os.path.join(out, "mode"), "w").write(mode)

W_FULL = ("Your name is worker-{n}. Step 1: write one line quoting exactly the line of your context that begins with WT-CANARY, or the word none. "
          "Step 2: in ONE message make two parallel Bash calls: `echo p1-{n}` and `echo p2-{n}`. Step 3: run Bash `echo BLOCKME-{n}`. "
          "Step 4: hand back with a short report that gives the canary line and, word for word, any hook message you saw after step 3, or none.")
W_LEAN = "Your name is worker-{n}. Run Bash `echo a-{n}`, then Bash `echo b-{n}`, then hand back with the word done."


def lead(workers, extra=""):
    steps = ["Step 1: run Bash `echo main-1`, then Bash `echo main-2`."]
    for n, tpl in workers:
        steps.append("Step %d: call the Agent tool with subagent_type `wt:worker`, name `worker-%s` and this exact prompt (between the markers, markers excluded) and wait: <<<%s>>>" % (len(steps) + 1, n, tpl.format(n=n)))
    return " ".join(steps) + extra + " Last step: reply with one line per worker giving its report text."


S = {
    "full": lead([("A", W_FULL)], " Then call the Agent tool once with subagent_type `wt:worker`, name `worker-D` and prompt `DENYME just say hi`; report whether it was refused and any message you saw."),
    "full2": lead([("A", W_FULL), ("B", W_FULL)], " Then call the Agent tool once with subagent_type `wt:worker`, name `worker-D` and prompt `DENYME just say hi`; report whether it was refused and any message you saw."),
    "lean5": lead([(str(i), W_LEAN) for i in range(5)]),
    "lean2": lead([(str(i), W_LEAN) for i in range(2)]),
    "outage": ("Step 1: run Bash `echo before-outage`. Step 2: run Bash `%s kill $(cat %s/server.pid); sleep 2`. Step 3: run Bash `echo after-outage-1`, then Bash `echo BLOCKME-after`. "
               "Step 4: call the Agent tool with subagent_type `wt:worker`, name `worker-D` and prompt `DENYME just say hi`. Step 5: call the Agent tool with subagent_type `wt:worker`, name `worker-Z` and prompt `Your name is worker-Z. Run Bash echo z then hand back with done.` "
               "Last step: reply with one line: for each of steps 3, 4 and 5, did anything stop or warn you, quoting any hook message." % (os.environ.get("WT_REFUSE", ""), out)),
}
cmd = ["claude", "-p", S[scen], "--model", "haiku", "--agent", "wt:lead", "--plugin-dir", plug, "--permission-mode", perm,
       "--debug-file", os.path.join(out, "dbg.log"), "--output-format", "json"]
t0 = time.time()
r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=int(os.environ.get("WT_TIMEOUT", "260")),
                   env=dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash"))
open(os.path.join(out, "run.json"), "w").write(r.stdout)
open(os.path.join(out, "run.err"), "w").write(r.stderr)
print("rc", r.returncode, "wall_s", round(time.time() - t0, 1), "out", len(r.stdout))
