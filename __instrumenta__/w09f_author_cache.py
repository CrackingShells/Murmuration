"""For every author subagent transcript of the lab's worktrees (read only) counts requests that came after a pause over 300 s, how many of them re-wrote at least half of the earlier context (a cold request), the USD those re-writes cost at list price, and the 1-hour share of cache writes, split before and after the 1-hour cache merge (3b0448b, 2026-10-21T17:38Z); input: ~/.claude/projects, threads.tsv from w09f_threads.py; output: markdown on stdout."""
import csv, glob, json, os, datetime, statistics as st
H = os.path.dirname(os.path.abspath(__file__)) + "/../__reports__/wave-09/explorer-w09-f/"
root = os.path.expanduser("~/.claude/projects")
CUT = "2026-10-21T17:38"
def T(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
ERAS = ["a: before w05-c1 (waiting paragraph merged 2026-10-21T08:08Z)", "b: between w05-c1 and w07-c7 (1-hour cache merged 17:38Z)", "c: after w07-c7"]
agg = {0: dict(n=0, req=0, gaps=0, cold=0, coldusd=0.0, w1=0, w5=0, usd_total=0.0, reqs_gap=0, avoid=0.0), 1: dict(n=0, req=0, gaps=0, cold=0, coldusd=0.0, w1=0, w5=0, usd_total=0.0, reqs_gap=0, avoid=0.0), 2: dict(n=0, req=0, gaps=0, cold=0, coldusd=0.0, w1=0, w5=0, usd_total=0.0, reqs_gap=0, avoid=0.0)}
rows = [r for r in csv.DictReader(open(H + "threads.tsv"), delimiter="\t") if r["kind"] == "sub" and r["agent_type"] == "murmuration:author" and r["proj"].startswith("wt:")]
for r in rows:
    fs = [f for f in glob.glob(root + "/*" + r["proj"][3:] + "/*/subagents/agent-" + "*" + ".jsonl") if os.path.basename(f)[6:14] == r["file"] and "---reports" not in f]
    if not fs: continue
    last = {}; order = []
    for l in open(fs[0], errors="replace"):
        try: x = json.loads(l)
        except Exception: continue
        if x.get("type") == "assistant":
            m = x["message"]; rid = x.get("requestId") or m.get("id")
            if rid not in last: order.append(rid)
            last[rid] = (x["timestamp"], m.get("usage") or {})
    after = 0 if r["start"] < "2026-10-21T08:08" else (1 if r["start"] < CUT else 2); a = agg[after]; a["n"] += 1
    prev_t = prev_ctx = None
    for rid in order:
        ts, u = last[rid]; cc = u.get("cache_creation") or {}
        w1 = cc.get("ephemeral_1h_input_tokens", 0) or 0; w5 = cc.get("ephemeral_5m_input_tokens", (u.get("cache_creation_input_tokens") or 0) - w1) or 0
        cr = u.get("cache_read_input_tokens") or 0; ctx = cr + w1 + w5 + (u.get("input_tokens") or 0)
        a["req"] += 1; a["w1"] += w1; a["w5"] += w5
        a["usd_total"] += ((u.get("input_tokens") or 0) * 2 + (u.get("output_tokens") or 0) * 10 + cr * 0.1 + w5 * 2.5 + w1 * 4.0) / 1e6
        if prev_t is not None and T(ts) - prev_t > 300:
            a["gaps"] += 1; a["avoid"] += (prev_ctx or 0) * 2.4 / 1e6
            if prev_ctx and (w1 + w5) >= 0.5 * prev_ctx: a["cold"] += 1; a["coldusd"] += (w1 * 4.0 + w5 * 2.5 - w1 * 0.1 - w5 * 0.1) / 1e6
        prev_t = T(ts); prev_ctx = ctx
print("| period | authors | requests | requests after a pause >300 s | of them cold (>=50% of earlier context re-written) | extra USD of those re-writes over a read | 1-hour share of cache-write tokens | authors' USD at list |"); print("|:--|--:|--:|--:|--:|--:|--:|--:|")
for k, lab in enumerate(ERAS):
    a = agg[k]; print("| %s | %d | %d | %d | %d | %.2f | %.2f | %.2f |" % (lab, a["n"], a["req"], a["gaps"], a["cold"], a["coldusd"], a["w1"] / max(1, a["w1"] + a["w5"]), a["usd_total"]))
a = agg[2]
print("\nafter the merge: 1-hour write tokens %d x (USD 4.0 - 2.5)/M = USD %.2f premium paid; the %d pauses over 300 s, had the cache lived 5 minutes, would have re-written their earlier context: %d pauses' earlier context x (2.5 - 0.1)/M = USD %.2f avoided (counterfactual, ESTIMATE; pauses over 3600 s would not be avoided, none seen)" % (a["w1"], a["w1"] * 1.5 / 1e6, a["gaps"], a["gaps"], a["avoid"]))
