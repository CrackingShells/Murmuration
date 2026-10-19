#!/usr/bin/env python3
"""End-to-end run of the budget hook: a haiku parent dispatches one explorer in the background with `Budget: USD 0.30` and `Time: min 20` and a
task longer than the budget; waits for its hand-back; resumes it with a raise (SendMessage with `Budget:` and `Time:` lines); waits again.
usage: e2e_drive.py <scratch> <cell> [--files N] [--budget USD] [--time MIN] [--raise-usd X] [--raise-min T] [--cap USD] [--type explorer|author] [--no-resume] [--extra TEXT] [--midrun] [--sleep SECONDS]
Everything is written under <scratch>/runs/<cell>/ (outside the worktree). Stdlib only; one `claude -p` call; seed 20261019 for the task files."""
import argparse, json, os, random, shutil, subprocess, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("scratch"); ap.add_argument("cell")
ap.add_argument("--files", type=int, default=200); ap.add_argument("--budget", default="0.30"); ap.add_argument("--time", default="20")
ap.add_argument("--raise-usd", default="0.30"); ap.add_argument("--raise-min", default="10"); ap.add_argument("--cap", default="2.5"); ap.add_argument("--type", default="explorer")
ap.add_argument("--plugin", default="plugin_e2e"); ap.add_argument("--no-resume", action="store_true"); ap.add_argument("--extra", default=""); ap.add_argument("--midrun", action="store_true"); ap.add_argument("--sleep", type=int, default=0)
a = ap.parse_args()
S = os.path.abspath(a.scratch); plugin = os.path.join(S, a.plugin)
base = os.path.join(S, "runs", a.cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab)
subprocess.run([sys.executable, os.path.join(plugin, "scripts", "lab_init.py"), "--project", lab], input="What is the founding year of each station?", text=True, capture_output=True, check=True)
rnd = random.Random(20261019)
first = "Quill Marsh Fen Cairn Wren Slate Briar Hollow Tarn Vale Heath Moor".split(); second = "moor reach ford gate wick stead haven mere".split()
for i in range(1, a.files + 1):
    st = "%s%s" % (rnd.choice(first), rnd.choice(second))
    open(os.path.join(lab, "f%03d.txt" % i), "w").write(
        "The %s station was founded in %d by %s %s and stands %d metres above the valley floor. Its population is about %d people, most of whom work in %s. "
        "A local saying holds that the dry wind arrives every %d days.\n" % (st, rnd.randint(1800, 1950), rnd.choice("Ada Bram Cora Dov Elin Faro".split()), rnd.choice("Verrin Holt Maro Ashby Pell".split()),
        rnd.randint(20, 900), rnd.randint(1000, 90000), rnd.choice(["salt harvesting", "peat cutting", "weaving", "ferry work"]), rnd.randint(3, 30)))
name = "%s-w03-%s" % (a.type, a.cell.replace("_", "").replace("-", ""))
brief = ("Your name is %s.\nBudget: USD %s\nTime: min %s\n"
         "Read the %d files f001.txt to f%03d.txt in the current directory, one file per Bash call (`%s`), one call at a time, in order. "
         "Your deliverable is the complete list, one line per file: the file name, the station name, the founding year, and the founder. Write it in your hand-back." % (name, a.budget, a.time, a.files, a.files, ("sleep %d; " % a.sleep if a.sleep else "") + "cat fNNN.txt")) + (("\n" + a.extra) if a.extra else "")
resume = ("Budget: USD %s\nTime: min %s\nThe principal investigator reads your hand-back and grants this much more. Continue with the files you have not read, "
          "and hand back the complete list when you finish or when you reach the new budget." % (a.raise_usd, a.raise_min))
steps = ["Step 1: call the Agent tool once with subagent_type 'murmuration:%s', name '%s', run_in_background true, with exactly the text between the lines ==== as its prompt (keep every line, change nothing).\n====\n%s\n====\n" % (a.type, name, brief),
         "Step 2: wait for the worker's completion notification (while waiting, run `sleep 20` with Bash, one call at a time, at most 60 times). Do not end your turn before it arrives. Do not read the worker's files and do not do its work.\n"]
if a.midrun:   # the raise goes to a worker that is still running
    steps = [steps[0], "Step 2: at once, without waiting, load SendMessage with ToolSearch (query select:SendMessage) if needed and call SendMessage with to '%s' and, as message, exactly the text between the lines ++++ (keep every line).\n++++\n%s\n++++\n" % (name, resume),
             "Step 3: wait for the worker's completion notification (run `sleep 20` with Bash, one call at a time, at most 60 times). Do not end your turn before it arrives. Then say DONE."]
elif not a.no_resume:
    steps.append("Step 3: when it has arrived, run `sleep 20` once (the idle gap is part of the test), then resume the same worker: load SendMessage with ToolSearch (query select:SendMessage) if needed, and call SendMessage with to '%s' and, as message, exactly the text between the lines ++++ (keep every line).\n++++\n%s\n++++\n" % (name, resume))
    steps.append("Step 4: wait for its second completion notification the same way (sleep 20, at most 80 times). Then say DONE.")
else:
    steps.append("Then say DONE.")
prompt = "".join(steps)
cmd = ["claude", "-p", "--model", "haiku", "--plugin-dir", plugin, "--setting-sources", "project", "--strict-mcp-config", "--permission-mode", "auto",
       "--max-budget-usd", a.cap, "--output-format", "stream-json", "--verbose", "--include-hook-events", prompt]
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}; env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, cwd=lab, env=env, timeout=2400)
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout); open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
res = None
for l in p.stdout.splitlines():
    try:
        r = json.loads(l)
    except ValueError:
        continue
    if r.get("type") == "result":
        res = r
json.dump(dict(cell=a.cell, name=name, B=a.budget, T=a.time, raise_usd=a.raise_usd, raise_min=a.raise_min, files=a.files, wall_s=round(time.time() - t0, 1), rc=p.returncode,
               usd=res and res.get("total_cost_usd"), turns=res and res.get("num_turns"), session=res and res.get("session_id"),
               model_usd={k: v.get("costUSD") for k, v in ((res or {}).get("modelUsage") or {}).items()}), open(os.path.join(base, "meta.json"), "w"))
print(open(os.path.join(base, "meta.json")).read())
