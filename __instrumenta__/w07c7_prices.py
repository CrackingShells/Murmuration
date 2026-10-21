# Checks the write prices behind c4: for each P6 session, recomputes the session cost from every deduplicated request of the main thread and of the author (usage split 5-minute / 1-hour, lab_status.PRICES for haiku 5.5) and compares it with the total_cost_usd that the CLI itself wrote in the run JSON; a mismatch beyond 1% would mean the 1-hour rate used here is not the one billed; inputs: S (runner folder), labels, scripts/lab_status.py of the lab (arg LAB); output: markdown table on stdout.
# usage: w07c7_prices.py S LAB label[,label...]
import json, glob, os, sys
S, LAB, labels = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3].split(",")
sys.path.insert(0, os.path.join(LAB, "scripts")); import lab_status as L
home = os.path.expanduser("~/.claude/projects")
print("| session | requests (main + author) | 5m write tokens | 1h write tokens | recomputed USD | CLI total_cost_usd | ratio | ratio if 1h writes were billed at the 5m rate |\n|:--|--:|--:|--:|--:|--:|--:|--:|")
for lab in labels:
    proj = os.path.join(home, "-private-tmp-" + os.path.relpath(os.path.join(S, "work", lab), "/private/tmp").replace("/", "-"))
    seen = {}
    for f in glob.glob(proj + "/*.jsonl") + glob.glob(proj + "/*/subagents/agent-*.jsonl"):
        for l in open(f):
            if '"assistant"' not in l: continue
            try: d = json.loads(l)
            except Exception: continue
            if d.get("type") != "assistant": continue
            m = d["message"]
            if m.get("model", "").startswith("<"): continue
            seen[(f, d.get("requestId"))] = m
    usd = 0.0; w5 = w1 = 0
    for m in seen.values():
        u = m.get("usage") or {}; cc = u.get("cache_creation") or {}
        w5 += cc.get("ephemeral_5m_input_tokens", 0); w1 += cc.get("ephemeral_1h_input_tokens", 0)
        usd += L.message_usd(m["model"], u) or 0.0
    run = json.load(open(os.path.join(S, "runs", lab + ".json")))
    alt = usd - w1 * (L.PRICES["claude-haiku-5-5"][4] - L.PRICES["claude-haiku-5-5"][3]) / 1e6
    print("| %s | %d | %d | %d | %.5f | %.5f | %.3f | %.3f |" % (lab, len(seen), w5, w1, usd, run["total_cost_usd"], usd / run["total_cost_usd"], alt / run["total_cost_usd"]))
