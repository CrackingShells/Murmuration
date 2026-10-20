#!/usr/bin/env python3
"""Runs one headless cell of wave-4 E1/E2: a haiku parent dispatches one sonnet explorer (Budget/Time lines, report deliverable, N generated station files) and waits; writes the run folder, ground truth and meta.json.
usage: headless_explorer_cell.py <scratch> <cell> <plugin dir> --seed S [--files N] [--budget USD] [--time MIN] [--cap USD; default none] [--brief report|list]
Derived from __reports__/reflective_run/w03/author-w03-1/e2e_drive.py (no resume step; ground truth kept outside the lab; the report path as the deliverable).
Output under <scratch>/runs/<cell>/: lab/ (the explorer's project), ground.json (never in the lab), stdout.jsonl, meta.json. Stdlib only; the model has no seed."""
import argparse, json, os, random, shutil, subprocess, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("scratch"); ap.add_argument("cell"); ap.add_argument("plugin")
ap.add_argument("--seed", type=int, required=True); ap.add_argument("--files", type=int, default=90); ap.add_argument("--budget", default="0.30"); ap.add_argument("--time", default="20")
ap.add_argument("--cap", default=""); ap.add_argument("--brief", default="report")   # cap "" = no --max-budget-usd flag: with the flag the platform shows every request a `budget_usd` attachment (used, total, remaining) of the whole session
a = ap.parse_args()
S = os.path.abspath(a.scratch); plugin = os.path.abspath(a.plugin)
base = os.path.join(S, "runs", a.cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab)
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"; env["COLGREP_DATA_DIR"] = os.path.join(base, "colgrep"); os.makedirs(env["COLGREP_DATA_DIR"])
subprocess.run([sys.executable, os.path.join(plugin, "scripts", "lab_init.py"), "--project", lab], input="What is the founding year of each station?", text=True, capture_output=True, check=True, env=env)
rnd = random.Random(a.seed)
first = "Quill Marsh Fen Cairn Wren Slate Briar Hollow Tarn Vale Heath Moor".split(); second = "moor reach ford gate wick stead haven mere".split()
ground = {}
for i in range(1, a.files + 1):
    st = "%s%s" % (rnd.choice(first), rnd.choice(second)); yr = rnd.randint(1800, 1950); fa, fb = rnd.choice("Ada Bram Cora Dov Elin Faro".split()), rnd.choice("Verrin Holt Maro Ashby Pell".split())
    open(os.path.join(lab, "f%03d.txt" % i), "w").write(
        "The %s station was founded in %d by %s %s and stands %d metres above the valley floor. Its population is about %d people, most of whom work in %s. "
        "A local saying holds that the dry wind arrives every %d days.\n" % (st, yr, fa, fb, rnd.randint(20, 900), rnd.randint(1000, 90000), rnd.choice(["salt harvesting", "peat cutting", "weaving", "ferry work"]), rnd.randint(3, 30)))
    ground["f%03d" % i] = dict(station=st, year=yr, founder="%s %s" % (fa, fb))
json.dump(ground, open(os.path.join(base, "ground.json"), "w"), indent=0)
name = "explorer-w04-%s" % a.cell.replace("_", "").replace("-", "")
rpath = "__reports__/wave-04/%s/00-findings_v0.md" % name
if a.brief == "report":
    task = ("Read the %d files f001.txt to f%03d.txt in the current directory, one file per Bash call (`cat fNNN.txt`), one call at a time, in order. "
            "Your deliverable is the findings report at %s, from the findings template of the research-loop skill: its Table holds one row per file, with the file name, "
            "the station name, the founding year and the founder. Hand back with a short message that points to the report." % (a.files, a.files, rpath))
else:   # the wave-3 shape: the list goes into the hand-back message
    task = ("Read the %d files f001.txt to f%03d.txt in the current directory, one file per Bash call (`cat fNNN.txt`), one call at a time, in order. "
            "Your deliverable is the complete list, one line per file: the file name, the station name, the founding year, and the founder. Write it in your hand-back." % (a.files, a.files))
brief = "Your name is %s.\nBudget: USD %s\nTime: min %s\n%s" % (name, a.budget, a.time, task)
prompt = ("Step 1: call the Agent tool once with subagent_type 'murmuration:explorer', name '%s', run_in_background true, with exactly the text between the lines ==== as its prompt (keep every line, change nothing).\n====\n%s\n====\n"
          "Step 2: wait for the worker's completion notification (while waiting, run `sleep 20` with Bash, one call at a time, at most 60 times). Do not end your turn before it arrives. "
          "Do not read the worker's files and do not do its work. Then say DONE.\n" % (name, brief))
cmd = ["claude", "-p", "--model", "haiku", "--plugin-dir", plugin, "--setting-sources", "project", "--strict-mcp-config", "--permission-mode", "auto",
       "--output-format", "stream-json", "--verbose", "--include-hook-events", prompt]
if a.cap:
    cmd[cmd.index("--output-format"):cmd.index("--output-format")] = ["--max-budget-usd", a.cap]
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
json.dump(dict(cell=a.cell, name=name, plugin=os.path.basename(plugin), seed=a.seed, cap=a.cap, B=a.budget, T=a.time, files=a.files, brief=a.brief, wall_s=round(time.time() - t0, 1), rc=p.returncode,
               usd=res and res.get("total_cost_usd"), turns=res and res.get("num_turns"), session=res and res.get("session_id"),
               model_usd={k: v.get("costUSD") for k, v in ((res or {}).get("modelUsage") or {}).items()}), open(os.path.join(base, "meta.json"), "w"))
print(open(os.path.join(base, "meta.json")).read())
