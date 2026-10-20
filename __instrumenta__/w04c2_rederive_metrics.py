"""Re-derives m1-m5 per run of the w04-c2 explorer cells from their raw folders (harness.jsonl, report file, ground.json, meta.json), independently of budget_arms_analyze.py, into a table on stdout.
usage: python3 -I w04c2_rederive_metrics.py <runs dir> <cell> [<cell> ...]
m1 denies = deny lines; m2 fraction at hand-back = frac of the last harness record before the deny (first) and of the `end` record (final), read from the log, not repriced; m3 report present at __reports__/wave-04/<name>/00-findings_v0.md and the six template headings; items = table rows naming fNNN with a year, correct = station, year and founder all match ground.json; m5 = total_cost_usd of meta.json. Stdlib only."""
import json, os, re, sys
runs = sys.argv[1]
HEADS = ["## Result", "## Table", "## Worst-fitting case", "## Not covered", "## Steering questions", "## Pointers"]
print("cell\tdenies\tfirst\tfinal\tover\treport\tfront\theads6\trows\tcorrect\tusd")
for cell in sys.argv[2:]:
    d = os.path.join(runs, cell)
    meta = json.load(open(d + "/meta.json")); gt = json.load(open(d + "/ground.json"))
    log = [json.loads(l) for l in open(d + "/lab/__statera__/harness.jsonl")]
    deny = [i for i, r in enumerate(log) if r["event"] == "deny"]
    fr = [r for r in log if "frac" in r]
    end = [r for r in log if r["event"] == "end"]
    final = end[-1]["frac"] if end else None
    first = final
    if deny:
        before = [r["frac"] for r in log[:deny[0]] if "frac" in r]
        first = before[-1] if before else None
    rep = "%s/lab/__reports__/wave-04/%s/00-findings_v0.md" % (d, meta["name"])
    t = open(rep).read() if os.path.exists(rep) else None
    rows = ok = 0
    if t:
        for line in t.splitlines():
            m = re.match(r"\|\s*(f\d{3})(?:\.txt)?\s*\|(.*)", line)
            if not m or m.group(1) not in gt: continue
            g = gt[m.group(1)]; rest = m.group(2)
            if re.search(r"\b\d{4}\b", rest):
                rows += 1
                if g["station"] in rest and str(g["year"]) in rest and g["founder"] in rest: ok += 1
    print("\t".join(str(x) for x in [cell, len(deny), first, final, "" if first is None or final is None else round(final - first, 3),
          t is not None, bool(t and t.startswith("---")), sum(h in t for h in HEADS) if t else 0, len(set()) or rows, ok, round(meta["usd"], 3)]))
