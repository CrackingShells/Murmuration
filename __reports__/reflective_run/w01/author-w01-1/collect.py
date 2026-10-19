#!/usr/bin/env python3
"""Collect the results of run_all.sh into results/: hand-back checks, Write-refusal tables, total cost.
Usage: collect.py   (run from anywhere; reads scratch/*, ~/.claude/projects/* transcripts of those runs; writes results/)
Python stdlib: it joins JSON files and shells out to check_handbacks.py / write_attempts.py."""
import glob, json, os, re, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__)); res = os.path.join(here, "results"); os.makedirs(res, exist_ok=True)
py = [sys.executable, "-I"]
def proj(tag):   # Claude Code's project folder for a run's cwd: every non-alphanumeric character becomes '-'
    return os.path.expanduser("~/.claude/projects/" + re.sub(r"[^A-Za-z0-9]", "-", os.path.join(here, "scratch", tag, "work")))
checks = []
for d in sorted(glob.glob(os.path.join(here, "scratch", "p[0-9]*"))):
    tag = os.path.basename(d)
    if os.path.exists(os.path.join(d, "RAWLOG")):
        work = d + "/work" if tag != "p7_nolab_auto" else os.path.join(here, "scratch", "NOLAB-not-in-lab")
        out = subprocess.run(py + [os.path.join(here, "check_handbacks.py"), d, d + "/work"], capture_output=True, text=True).stdout.strip()
        if out: checks.append(out)
open(os.path.join(res, "check_handbacks.jsonl"), "w").write("\n".join(checks) + "\n")
def attempts(path):
    return subprocess.run(py + [os.path.join(here, "write_attempts.py"), path], capture_output=True, text=True).stdout
for tag, name in (("w1_sub_302", "write_sub_2.1.302"), ("w3_sub_299", "write_sub_2.1.299"), ("w2_main_302", "write_main_2.1.302")):
    p = proj(tag); subs = glob.glob(p + "/*/subagents"); mains = glob.glob(p + "/*.jsonl")
    txt = attempts(subs[0] if subs else mains[0]) if (subs or mains) else "no transcript\n"
    txt = re.sub(r"/Users/[^\t]*/scratch/[a-z0-9_]+/work/", "", txt)
    open(os.path.join(res, name + ".tsv"), "w").write("\n".join(l[:160] for l in txt.split("\n")))
nolab = glob.glob(os.path.join(here, "scratch", "p7_nolab_auto", "**", "__statera__"), recursive=True)
cost = {os.path.basename(os.path.dirname(f)): json.load(open(f))["total_cost_usd"] for f in sorted(glob.glob(os.path.join(here, "scratch", "*", "out.json")))}
json.dump(dict(total_cost_usd=round(sum(cost.values()), 4), runs=len(cost), per_run=cost, nolab_statera_dirs_created=nolab), open(os.path.join(res, "summary.json"), "w"), indent=1)
print(open(os.path.join(res, "check_handbacks.jsonl")).read()); print(json.dumps(dict(total_cost_usd=round(sum(cost.values()), 4), runs=len(cost), nolab_statera_dirs_created=nolab)))
