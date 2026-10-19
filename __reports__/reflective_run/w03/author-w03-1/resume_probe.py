#!/usr/bin/env python3
"""Resume probe: a haiku parent dispatches a worker in the background, waits for its hand-back, then resumes it with SendMessage
(the message carries `Budget:` and `Time:` lines), and waits again. The logging plugin records every event (SubagentStart included) and
what the worker's transcript holds at that moment.
usage: resume_probe.py <scratch> <cell> [--mode log|blockuse]     Stdlib only; one `claude -p` call, cap USD 0.8."""
import argparse, json, os, shutil, subprocess, time
ap = argparse.ArgumentParser(); ap.add_argument("scratch"); ap.add_argument("cell"); ap.add_argument("--mode", default="log"); ap.add_argument("--cap", default="0.8")
a = ap.parse_args()
S = os.path.abspath(a.scratch); base = os.path.join(S, "runs", a.cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab)
for n in ("s1", "s2"):
    open(os.path.join(lab, n + ".txt"), "w").write("file %s: ok\n" % n)
name = "author-w03-%s" % a.cell
brief = "Your name is %s.\nBudget: USD 0.50\nTime: min 4\nRun `cat s1.txt` with Bash, then hand back with the file's content." % name
resume = "Budget: USD 1.25\nTime: min 7\nPlease run `cat s2.txt` with Bash, then hand back with the file's content."
prompt = ("Step 1: call the Agent tool once with subagent_type 'murmuration:author', name '%s', run_in_background true, with exactly the text between the lines ==== as its prompt.\n====\n%s\n====\n"
          "Step 2: wait for the worker's completion notification (while waiting, run `sleep 10` with Bash, one call at a time, at most 12 times). Do not end your turn before it arrives.\n"
          "Step 3: when it has arrived, wait 20 seconds more with `sleep 20` (this idle gap is part of the test), then resume the same worker: load SendMessage with ToolSearch (query select:SendMessage) if needed, "
          "and call SendMessage with to '%s' and, as message, exactly the text between the lines ++++ (keep every line).\n++++\n%s\n++++\n"
          "Step 4: wait for its second completion notification the same way (sleep 10, at most 12 times). Then say DONE." % (name, brief, name, resume))
cmd = ["claude", "-p", "--model", "haiku", "--plugin-dir", os.path.join(S, "plugin_probe"), "--setting-sources", "project", "--strict-mcp-config",
       "--permission-mode", "auto", "--max-budget-usd", a.cap, "--output-format", "stream-json", "--verbose", "--include-hook-events", prompt]
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
env.update(PROBE_LOG=os.path.join(base, "events.jsonl"), PROBE_MODE=a.mode, PROBE_FULL="1", CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS="0")
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, cwd=lab, env=env, timeout=900)
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout); open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
res = None
for line in p.stdout.splitlines():
    try:
        r = json.loads(line)
    except ValueError:
        continue
    if r.get("type") == "result":
        res = r
json.dump(dict(cell=a.cell, name=name, mode=a.mode, wall_s=round(time.time() - t0, 1), rc=p.returncode, usd=res and res.get("total_cost_usd"), turns=res and res.get("num_turns"),
               session=res and res.get("session_id")), open(os.path.join(base, "meta.json"), "w"))
print(open(os.path.join(base, "meta.json")).read())
