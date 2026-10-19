#!/usr/bin/env python3
"""Claim w01-c3, checks V1-V3: the price table and the deduplication against Claude Code's own cost-state.

For every ended session (a `cost-state` record) among the lab's sessions and the four combinatorics
sessions, and every model in it, compare per (session, model) cell:
  cs_usd        costUSD that Claude Code wrote
  table_on_cs   our price table applied to the token counts in the same cost-state record   (V1: is the table right?)
  table_on_tr   our price table applied to the deduplicated transcripts                      (V2: is the reading right?)
and the token counts of the transcripts against the record, field by field.
Writes validate_cells.csv. Run: python3 -I validate.py [--quick]"""
import csv, glob, json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lab_spend as L

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
COMB = os.path.expanduser("~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary")
quick = "--quick" in sys.argv

mains = L.find_scan(ROOT)
comb = sorted(glob.glob(COMB + "/*.jsonl"))
if quick:
    mains = [m for m in mains if "ab96c5ed" not in m][:5]
    comb = comb[:2]
sessions, stats, warns = L.load(mains + comb)

def table_usd(model, i, o, cr, cw5, cw1):
    p = L.price_of(model)
    if p is None: return None
    return (i*p[0] + o*p[1] + cr*p[2] + cw5*p[3] + cw1*p[4]) / 1e6

rows = []
for s in sessions:
    cs = s["cost_state"]
    if not cs:
        continue
    for model, mu in cs["modelUsage"].items():
        tr = collections.Counter()
        for (label, kind, m), r in s["rows"].items():
            if m == model:
                for k in ("msgs", "in", "out", "cr", "cw", "usd", "lower_bound_msgs"):
                    tr[k] += r[k]
        # cache-write split by TTL of the transcript cell, to price the record's cw count
        cw = mu["cacheCreationInputTokens"]
        rows.append({
            "session": s["sid"][:8], "model": model, "cs_usd": round(mu["costUSD"], 4),
            "web_searches": mu.get("webSearchRequests", 0),
            "cs_in": mu["inputTokens"], "cs_out": mu["outputTokens"], "cs_cr": mu["cacheReadInputTokens"], "cs_cw": cw,
            "tr_in": tr["in"], "tr_out": tr["out"], "tr_cr": tr["cr"], "tr_cw": tr["cw"],
            "tr_usd": round(tr["usd"], 4), "tr_lower_bound_msgs": tr["lower_bound_msgs"], "tr_msgs": tr["msgs"],
            "_cw_tr_split": None,
        })
# V1: the table on the record's own counts. The record does not split cache writes by TTL: price the cs counts
# with the TTL mix of the same cell's transcripts (both extremes are written too).
for r in rows:
    model = r["model"]
    p = L.price_of(model)
    r["table_on_cs_5m"] = round((r["cs_in"]*p[0] + r["cs_out"]*p[1] + r["cs_cr"]*p[2] + r["cs_cw"]*p[3]) / 1e6 + 0.01*r["web_searches"], 4)
    r["table_on_cs_1h"] = round((r["cs_in"]*p[0] + r["cs_out"]*p[1] + r["cs_cr"]*p[2] + r["cs_cw"]*p[4]) / 1e6 + 0.01*r["web_searches"], 4)
    for k in ("table_on_cs_5m", "table_on_cs_1h", "tr_usd"):
        r[k + "_ratio"] = round(r[k] / r["cs_usd"], 4) if r["cs_usd"] else ""
    del r["_cw_tr_split"]
fields = list(rows[0].keys())
out = os.path.join(HERE, "validate_cells_quick.csv" if quick else "validate_cells.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fields); w.writeheader(); w.writerows(rows)
print("cells", len(rows), "->", out)
print("%-9s %-18s %8s %8s %8s %8s %6s %s" % ("session", "model", "cs_usd", "tbl5m", "tbl1h", "tr_usd", "tr/cs", "lb_msgs"))
for r in rows:
    print("%-9s %-18s %8.4f %8.4f %8.4f %8.4f %6s %s" % (r["session"], r["model"], r["cs_usd"], r["table_on_cs_5m"], r["table_on_cs_1h"], r["tr_usd"], r["tr_usd_ratio"], r["tr_lower_bound_msgs"]))

# The cut used in the claim head (R1): cells with no subagent message lacking a final record (lb_msgs == 0).
nolb = [r for r in rows if r["tr_lower_bound_msgs"] == 0]
ok = [r for r in nolb if abs(r["tr_usd"] - r["cs_usd"]) <= 0.0005 * r["cs_usd"]]
print("R1 cut: %d cells of %d have lb_msgs == 0 (no subagent message without a stop_reason); %d of them within 0.05%% of cost-state" % (len(nolb), len(rows), len(ok)))
print("R1 misses:", [(r["session"], r["model"], r["cs_in"], r["tr_in"]) for r in nolb if r not in ok])
