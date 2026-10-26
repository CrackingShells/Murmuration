# w09-c6: compares a small re-run of the judges (w09c_judge.py output on a private subset of cases) with the committed rows of explorer-w09-c: per judge, verdicts equal / different and p50 latency of both. Prints aggregates only. Usage: python3 -I w09c6_spotcheck.py RESULTS_DIR NEW_JSONL=OLD_NAME ... (e.g. spot_granite.res.jsonl=granite_short.jsonl)
import sys, json, statistics, collections
rdir = sys.argv[1]
for a in sys.argv[2:]:
    nf, of = a.split("=")
    new = [r for r in map(json.loads, open(nf)) if "cid" in r]
    old = {r["cid"]: r for r in map(json.loads, open(rdir + "/" + of)) if "cid" in r}
    both = [r for r in new if r["cid"] in old]
    flips = collections.Counter((r["group"], old[r["cid"]]["verdict"] + "->" + r["verdict"]) for r in both if r["verdict"] != old[r["cid"]]["verdict"])
    ms = [r["ms"] for r in new[1:]]; oms = [old[r["cid"]]["ms"] for r in both[1:] if r["cid"] in old]
    print(f"{of}: new rows {len(new)}, also in committed rows {len(both)}, same verdict {sum(r['verdict']==old[r['cid']]['verdict'] for r in both)}, flips {dict(flips)}; new p50 {statistics.median(ms):.0f} ms (first call {new[0]['ms']:.0f}, max {max(ms):.0f}); committed p50 on the same cases {statistics.median(oms):.0f} ms")
    nr = [r for r in new if r["group"] == "refusal"]; na = [r for r in new if r["group"] == "allow"]
    print(f"  new run: refusals blocked {sum(r['verdict']=='block' for r in nr)} of {len(nr)}; allows blocked {sum(r['verdict']=='block' for r in na)} of {len(na)}")
