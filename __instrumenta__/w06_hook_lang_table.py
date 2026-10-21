"""Tabulates the rows of w06_hook_lang_probe.py (JSONL: one platform hook record each, joined with the script's own clock) into markdown: per cell and language the platform durationMs (n, median, p10, p90, min, max), and where the script stamped its own clock the lag from the platform's clock start to the script's first instruction (start lag) and from its last instruction to the record (record lag).

usage: w06_hook_lang_table.py rows.jsonl [rows2.jsonl ...] > table.md   Only records of the cell's own event and of the w06 hooks (lang sh|shs|py|rs) are tabulated, siblings ("other") get one summary line per cell.
"""
import json, sys, statistics as st
rows = [json.loads(l) for f in sys.argv[1:] for l in open(f)]
EV = {"ups": "UserPromptSubmit", "ptu": "PreToolUse"}
def q(v, p): v = sorted(v); return v[int(p * (len(v) - 1))]
print("| cell | lang | n | runs | durationMs median | p10 | p90 | min | max | start lag median | record lag median | load1 median |\n|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
cells = sorted({r["cell"] for r in rows})
for c in cells:
    ev = EV[c.split("-")[0]]
    for lang in ("sh", "shs", "py", "rs", "other"):
        rs = [r for r in rows if r["cell"] == c and r["lang"] == lang and r["event"] == ev]
        if not rs: continue
        d = [r["dur_ms"] for r in rs]
        sl = [r["body_t0"] - r["t0_start"] for r in rs if "body_t0" in r]; rl = [r["ts"] - r["body_t1"] for r in rs if "body_t0" in r]
        print("| %s | %s | %d | %d | %.0f | %.0f | %.0f | %.0f | %.0f | %s | %s | %.1f |" % (c, lang, len(d), len({r["rep"] for r in rs}), st.median(d), q(d, .1), q(d, .9), min(d), max(d), "%.0f" % st.median(sl) if sl else "-", "%.0f" % st.median(rl) if rl else "-", st.median(r["load1"] for r in rs)))
# second table: PreToolUse cells, first Bash call of a run against calls 2-4 (same hook, same run)
print("\n| PreToolUse cell | lang | first call: n, median ms | calls 2-4: n, median ms, p90 |\n|:--|:--|:--|:--|")
for c in cells:
    if not c.startswith("ptu-"): continue
    for lang in ("sh", "shs", "py", "rs"):
        first, rest = [], []
        for rep in sorted({r["rep"] for r in rows if r["cell"] == c}):
            rs = [r for r in rows if r["cell"] == c and r["rep"] == rep and r["lang"] == lang and r["event"] == "PreToolUse"]
            rs.sort(key=lambda r: r["ts"])
            k = len(rs) // 4 if rs else 0
            # records are grouped by call: with m hooks of this lang per call, the first m are call 1
            m = len(rs) // 4 if len(rs) >= 4 else 1
            first += [r["dur_ms"] for r in rs[:m]]; rest += [r["dur_ms"] for r in rs[m:]]
        if first: print("| %s | %s | %d, %.0f | %d, %.0f, %.0f |" % (c, lang, len(first), st.median(first), len(rest), st.median(rest) if rest else float("nan"), q(rest, .9) if rest else float("nan")))
