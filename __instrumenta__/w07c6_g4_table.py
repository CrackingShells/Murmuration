# Pairs the sessions of w07c6_session_pairs by pair number and reports the platform-recorded duration of the guard rows (PreToolUse:Bash of the test plugin) per session as its median over the session's Bash calls, A minus B per pair, how many pairs B wins, the median saving and its spread, medians without each session's first call, and the sessions' wall and load; input: g4_rows.jsonl; output: markdown on stdout.
# usage: python3 -I __instrumenta__/w07c6_g4_table.py g4_rows.jsonl
import json, statistics as st, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
by = {}
for r in rows: by.setdefault(r["pair"], {})[r["arm"]] = r
def q(xs, p):
    xs = sorted(xs); k = (len(xs) - 1) * p; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)
pairs = [(k, v["A"], v["B"]) for k, v in sorted(by.items()) if "A" in v and "B" in v and v["A"]["guard_ms"] and v["B"]["guard_ms"]]
print("| pair | order | A median ms | B median ms | A-B ms | A calls | B calls | A max | B max | load before A/B |")
print("|--:|:--|--:|--:|--:|--:|--:|--:|--:|:--|")
for k, a, b in pairs:
    order = "A,B" if k % 2 == 0 else "B,A"
    ma, mb = st.median(a["guard_ms"]), st.median(b["guard_ms"])
    print("| %d | %s | %.0f | %.0f | %.0f | %d | %d | %d | %d | %.2f / %.2f |" % (k, order, ma, mb, ma - mb, len(a["guard_ms"]), len(b["guard_ms"]), max(a["guard_ms"]), max(b["guard_ms"]), a["load1_before"], b["load1_before"]))
def summ(label, fa, fb):
    d = [fa(a) - fb(b) for _, a, b in pairs]
    print("\n%s: pairs %d, B lower in %d, equal in %d; median saving (A-B) %.1f ms [p10 %.1f, p90 %.1f, min %.1f, max %.1f]" % (label, len(d), sum(x > 0 for x in d), sum(x == 0 for x in d), st.median(d), q(d, .1), q(d, .9), min(d), max(d)))
summ("per-session median of all guard calls", lambda a: st.median(a["guard_ms"]), lambda b: st.median(b["guard_ms"]))
summ("per-session median without the first call", lambda a: st.median(a["guard_ms"][1:]), lambda b: st.median(b["guard_ms"][1:]))
summ("per-session mean of all guard calls", lambda a: st.mean(a["guard_ms"]), lambda b: st.mean(b["guard_ms"]))
allA = [x for _, a, _ in pairs for x in a["guard_ms"]]; allB = [x for _, _, b in pairs for x in b["guard_ms"]]
print("\nall calls pooled: A n %d median %.0f ms (p10 %.0f, p90 %.0f); B n %d median %.0f ms (p10 %.0f, p90 %.0f)" % (len(allA), st.median(allA), q(allA, .1), q(allA, .9), len(allB), st.median(allB), q(allB, .1), q(allB, .9)))
print("sessions: wall A median %.1f s, B %.1f s; load1 before, median %.2f; all statuses zero: %s; cost USD total %.3f over %d sessions" % (st.median(r["wall_s"] for r in rows if r["arm"] == "A"), st.median(r["wall_s"] for r in rows if r["arm"] == "B"), st.median(r["load1_before"] for r in rows), all(s == 0 for r in rows for s in r["guard_status"]), sum(r["cost_usd"] or 0 for r in rows), len(rows)))
