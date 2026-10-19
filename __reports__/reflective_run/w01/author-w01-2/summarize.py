"""Summaries over results.jsonl (last record per cell wins).  usage: python3 -I summarize.py [--rows]"""
import json, sys, collections
rows = {}
for l in open("results.jsonl"):
    o = json.loads(l); rows[o["cell"]] = o
def pm(o): return o.get("permmode") or ("auto" if o.get("auto") == "1" else "bypassPermissions")
out = []
for c, o in rows.items():
    sub = list(o["sub"].values())
    hv = [x for x in o["hook_view"] if x["event"] == "SubagentStop" and x["field"].startswith("agent")]
    fin_sub_last = sum(s["sums"]["last"]["output_tokens"] for s in sub)
    hook_last = hv[0]["out_last"] if hv else None
    d = o["diff_last"]
    out.append(dict(cell=c, ver=o["version"], pm=pm(o), bg=o["started_in_background"], think=o["think"], length=o["length"], io=o["io"],
                    tag=(c.rsplit("-",1)[1] if c.endswith(("-hr","-pk","-bc")) else ""), nsub=len(sub), reqs=sum(s["requests"] for s in sub),
                    truth_out=o["truth"]["output_tokens"], tot_out_last=o["tot_last"]["output_tokens"],
                    d_out=d["output_tokens"], d_in=d["input_tokens"], d_cr=d["cache_read_input_tokens"], d_cw=d["cache_creation_input_tokens"],
                    sub_out_final=fin_sub_last, sub_out_hook=hook_last, sub_null=sum(s["null_stop_last"] for s in sub),
                    think_truth=o["think_truth"], usd=o["cost_usd"], n_results=o["n_results"]))
if "--rows" in sys.argv:
    for r in sorted(out, key=lambda r: (r["ver"], r["pm"], str(r["bg"]), r["think"], r["length"], r["cell"])): print(json.dumps(r))
    sys.exit()
def grp(keyf, label, rs):
    g = collections.defaultdict(list)
    for r in rs: g[keyf(r)].append(r)
    print("\n##", label)
    print("%-44s %4s %12s %12s %12s %10s" % ("group", "n", "out_exact", "in/cache_exact", "sub_out_trunc", "hook!=final"))
    for k in sorted(g, key=str):
        v = g[k]
        print("%-44s %4d %12d %12d %12d %10d" % (k, len(v), sum(r["d_out"] == 0 for r in v), sum(r["d_in"] == r["d_cr"] == r["d_cw"] == 0 for r in v),
              sum(r["sub_null"] > 0 for r in v), sum(r["sub_out_hook"] != r["sub_out_final"] for r in v)))
main = [r for r in out if not r["tag"]]
grp(lambda r: (r["ver"], r["pm"]), "by version x permission mode (all non-hookrace cells)", main)
na = [r for r in main if r["pm"] != "auto"]
au = [r for r in main if r["pm"] == "auto"]
grp(lambda r: (r["ver"], "bg=%s" % r["bg"], "think=%s" % r["think"], "len=%s" % r["length"]), "NON-auto cells by version x bg x thinking x length", na)
grp(lambda r: (r["ver"], "bg=%s" % r["bg"], "think=%s" % r["think"], "len=%s" % r["length"]), "AUTO cells by version x bg x thinking x length", au)
grp(lambda r: (r["ver"], r["pm"], r["tag"]), "hook-race set (non-auto, fg, long)", [r for r in out if r["tag"]])
print("\ntotal cells", len(out), " total USD %.4f" % sum(r["usd"] for r in out))
