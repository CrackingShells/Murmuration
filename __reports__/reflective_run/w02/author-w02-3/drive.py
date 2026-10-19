#!/usr/bin/env python3
"""One headless cell: a scratch lab, a haiku parent that dispatches one murmuration worker (sonnet by its agent file).

usage: drive.py <scratch> <cell> --plugin head|wt|nohooks --type explorer|author|reproducer --budget USD|none [--files N] [--cap USD] [--name NAME]
Everything is written under <scratch>/runs/<cell>/ (outside the worktree). Prints one JSON summary line.
Stdlib only. `claude` is called once per cell with --max-budget-usd (default 0.7)."""
import argparse, json, os, random, shutil, subprocess, sys, time

ap = argparse.ArgumentParser()
ap.add_argument("scratch"); ap.add_argument("cell")
ap.add_argument("--plugin", default="head"); ap.add_argument("--type", default="explorer")
ap.add_argument("--budget", default="0.15"); ap.add_argument("--files", type=int, default=40)
ap.add_argument("--cap", default="0.7"); ap.add_argument("--name", default="")
ap.add_argument("--mode", default="auto"); ap.add_argument("--extra", default=""); ap.add_argument("--B", default="")  # the budget the cell is judged against when the brief has no line
a = ap.parse_args()
S = os.path.abspath(a.scratch)
plugin = os.path.join(S, "plugin_" + a.plugin)
base = os.path.join(S, "runs", a.cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab)
name = a.name or "%s-w02-%s" % (a.type, a.cell.replace("_", "").replace("-", ""))

# a lab made by the plugin's own script
subprocess.run([sys.executable, os.path.join(plugin, "scripts", "lab_init.py"), "--project", lab],
               input="What is the founding year of each station?", text=True, capture_output=True, check=True)

# the task: N short files, content fixed by the seed
rnd = random.Random(20261019)
first = "Quill Marsh Fen Cairn Wren Slate Briar Hollow Tarn Vale Heath Moor".split()
second = "moor reach ford gate wick stead haven mere".split()
for i in range(1, a.files + 1):
    st = "%s%s" % (rnd.choice(first), rnd.choice(second))
    open(os.path.join(lab, "f%02d.txt" % i), "w").write(
        "The %s station was founded in %d by %s %s and stands %d metres above the valley floor. Its population is about %d people, "
        "most of whom work in %s. A local saying holds that the dry wind arrives every %d days.\n" % (
            st, rnd.randint(1800, 1950), rnd.choice("Ada Bram Cora Dov Elin Faro".split()), rnd.choice("Verrin Holt Maro Ashby Pell".split()),
            rnd.randint(20, 900), rnd.randint(1000, 90000), rnd.choice(["salt harvesting", "peat cutting", "weaving", "ferry work"]), rnd.randint(3, 30)))
brief = ("Your name is %s.\n" % name) + ("Budget: USD %s\n" % a.budget if a.budget != "none" else "") + (
    "Read the %d files f01.txt to f%02d.txt in the current directory, one file per Bash call (cat fNN.txt), one call at a time, in order. "
    "Then hand back a report with one line per file: the file name, the station name, the founding year, and the founder." % (a.files, a.files)) + (("\n" + a.extra) if a.extra else "")
prompt = ("Call the Agent tool exactly once with subagent_type 'murmuration:%s', name '%s', in the foreground, with exactly the text between "
          "the lines ==== as its prompt (keep every line, change nothing).\n====\n%s\n====\nWhen the Agent call is finished, say DONE." % (a.type, name, brief))
cmd = ["claude", "-p", "--model", "haiku", "--plugin-dir", plugin, "--setting-sources", "project", "--strict-mcp-config",
       "--permission-mode", a.mode, "--max-budget-usd", a.cap, "--output-format", "stream-json", "--verbose", "--include-hook-events", prompt]
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, cwd=lab, env=env, timeout=900)
wall = time.time() - t0
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout); open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
res = None
for line in p.stdout.splitlines():
    try:
        r = json.loads(line)
    except ValueError:
        continue
    if r.get("type") == "result":
        res = r
json.dump(dict(cell=a.cell, name=name, B=a.B or a.budget, type=a.type, plugin=a.plugin, budget=a.budget, files=a.files, wall_s=round(wall, 1), rc=p.returncode,
               usd=res and res.get("total_cost_usd"), turns=res and res.get("num_turns"),
               model_usd={k: v.get("costUSD") for k, v in ((res or {}).get("modelUsage") or {}).items()}), open(os.path.join(base, "meta.json"), "w"))
print(open(os.path.join(base, "meta.json")).read())
