"""Sums hook process starts (and an estimated wall/CPU) over many session transcripts with hook_count_invocations.py's rules: from a list of main transcripts (argv: paths) to a JSON of starts per registration and totals.

usage: hook_starts_per_wave.py [--out FILE] [--ms-wall X --ms-cpu Y] main1.jsonl main2.jsonl ...  (each main's subagents are read from <id>/subagents/)
Runs hook_count_invocations.py once per transcript with `python3 -I`, adds up `starts` (main and workers) and `totals`; with --ms-wall/--ms-cpu prints starts x price.
"""
import json, subprocess, sys, os, collections
argv = sys.argv[1:]
out = None; mw = mc = None
while argv and argv[0].startswith("--"):
    if argv[0] == "--out": out = argv[1]
    elif argv[0] == "--ms-wall": mw = float(argv[1])
    elif argv[0] == "--ms-cpu": mc = float(argv[1])
    argv = argv[2:]
here = os.path.dirname(os.path.abspath(__file__))
tot = collections.Counter(); reg = collections.Counter(); tc = collections.Counter(); bad = 0
for p in argv:
    r = subprocess.run([sys.executable, "-I", os.path.join(here, "hook_count_invocations.py"), p], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except ValueError:
        bad += 1; continue
    for cls in ("main", "workers"):
        for k, v in d["starts"].get(cls, {}).items():
            reg[k] += v
    for k, v in d["totals"].items():
        tc[k] += v
res = {"transcripts": len(argv), "unparsed": bad, "totals": dict(tc), "starts_by_registration": dict(reg),
       "all_starts": sum(reg.values())}
if mw: res["est_wall_s_if_serial"] = round(res["all_starts"] * mw / 1000, 1)
if mc: res["est_cpu_s"] = round(res["all_starts"] * mc / 1000, 1)
print(json.dumps(res, indent=1))
if out: open(out, "w").write(json.dumps(res, indent=1))
