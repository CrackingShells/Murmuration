# Tables the live pairs of w08c1_session_pairs.py: per hook event, the median per session of the platform's recorded hook duration (ms), A minus B per pair, and the number of pairs in which B (the Rust rows) is lower, with the calls pooled per arm.
# usage: python3 -I w08c1_e4_table.py S/runs/rows.jsonl [--out FILE]
import json, statistics as st, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
by = {}
for r in rows:
    if r["rc"] == 0 and not r["is_error"]:
        by.setdefault(r["pair"], {})[r["arm"]] = r
pairs = {p: v for p, v in by.items() if "A" in v and "B" in v}
out = ["| hook event (status 0 only) | pairs | A session-median ms (med) | B session-median ms (med) | A-B per pair med [min, max] | B lower in | pooled calls A med / B med |", "|:--|--:|--:|--:|:--|--:|--:|"]
for ev in ("PostToolUse:Bash", "PostToolBatch", "PreToolUse:Bash", "SessionStart:startup"):
    d, a, b, pa, pb = [], [], [], [], []
    for p, v in sorted(pairs.items()):
        ma, mb = v["A"]["ms"].get(ev), v["B"]["ms"].get(ev)
        if ma and mb:
            a.append(st.median(ma)); b.append(st.median(mb)); d.append(a[-1] - b[-1]); pa += ma; pb += mb
    if d:
        out.append("| %s | %d | %.1f | %.1f | %.1f [%.1f, %.1f] | %d of %d | %.0f / %.0f |" % (ev, len(d), st.median(a), st.median(b), st.median(d), min(d), max(d), sum(x > 0 for x in d), len(d), st.median(pa), st.median(pb)))
out.append("")
out.append("sessions: %d ok of %d; load1 before, median %.2f; cost per session median USD %.4f" % (len(rows) and sum(r["rc"] == 0 for r in rows), len(rows), st.median(r["load1_before"] for r in rows), st.median(r["cost_usd"] or 0 for r in rows)))
t = "\n".join(out)
if "--out" in sys.argv:
    open(sys.argv[sys.argv.index("--out") + 1], "w").write(t + "\n")
print(t)
