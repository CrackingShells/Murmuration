# Counts, for every subagent transcript of the lab's sessions (waves 1-8), how many workers and requests have a context above 150k, 250k, 400k tokens and what one compaction at that size would save or cost them, from ~/.claude/projects/*Murmuration*/*/subagents/*.jsonl to a table on stdout.
"""usage: w08_c3_worker_ceilings.py [PROJECTS_DIR]   (default ~/.claude/projects; folders with 'scratch', 'probes-out' or 'explore' in the name are skipped; transcripts are read, never printed)
Context of a request = input + cache read + cache write of the assistant message (distinct message ids). Model per transcript: first assistant message's model; prices lab_status.PRICES.
Compaction model (explorer-w08-e): at the first request k whose context exceeds T: cost = prev context x read + 11,800 x input + 6,000 x output + 41,000 x 1-hour write; afterwards every request's context is lower by (C_k - P) with P = 67,000 + R (R = 10,000), saving (C_k - P) x read price per request. One compaction per worker; later re-crossings are ignored (a lower bound on cost and on saving)."""
import glob, json, os, sys
HOME = os.path.expanduser("~/.claude/projects")
ROOT = sys.argv[1] if len(sys.argv) > 1 else HOME
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status
workers = []
for proj in glob.glob(os.path.join(ROOT, "*Murmuration*")):
    b = os.path.basename(proj)
    if any(x in b for x in ("scratch", "probes-out", "explore")): continue
    for f in glob.glob(os.path.join(proj, "*", "subagents", "*.jsonl")):
        seen, ctx, model = {}, [], None
        for l in open(f, errors="replace"):
            if '"type":"assistant"' not in l.replace(" ", "")[:400] and '"assistant"' not in l[:300]: continue
            try: d = json.loads(l)
            except ValueError: continue
            if d.get("type") != "assistant": continue
            m = d.get("message") or {}; u = m.get("usage") or {}
            c = (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
            if m.get("id") not in seen: ctx.append(c); model = model or m.get("model")
            seen[m.get("id")] = c
            ctx[-1] = max(ctx[-1], c) if len(ctx) else c
        if ctx: workers.append((f, model, ctx))
if os.environ.get("MODEL_FILTER"): workers = [w for w in workers if os.environ["MODEL_FILTER"] in (w[1] or "")]  # e.g. MODEL_FILTER=sonnet
print("workers", len(workers), "requests", sum(len(c) for _, _, c in workers), "max context per worker: median %d, p90 %d, max %d" % (
    sorted(max(c) for _, _, c in workers)[len(workers) // 2], sorted(max(c) for _, _, c in workers)[int(len(workers) * .9)], max(max(c) for _, _, c in workers)))
print("models", {m: sum(1 for w in workers if w[1] == m) for m in {w[1] for w in workers}})
print("T\tworkers_over\tshare_workers\trequests_over\tshare_requests\tcompactions\tsaving_usd\tcost_usd\tnet_usd\tworker_usd_total")
P = 67000 + 10000
tot = 0.0
for _, model, ctx in workers:
    p = lab_status.PRICES.get((model or "").rsplit("-20", 1)[0]) or lab_status.PRICES["claude-sonnet-5-5"]
    for k, c in enumerate(ctx): tot += c * p[2] / 1e6  # reads only: a rough scale of the context bill
for T in (150000, 250000, 400000):
    wo = ro = n = 0; save = cost = 0.0
    for _, model, ctx in workers:
        p = lab_status.PRICES.get((model or "").rsplit("-20", 1)[0]) or lab_status.PRICES["claude-sonnet-5-5"]
        over = [i for i, c in enumerate(ctx) if c > T]; ro += len(over)
        if over:
            wo += 1; k = over[0]; n += 1
            cost += (ctx[k - 1] * p[2] + 11800 * p[0] + 6000 * p[1] + 41000 * p[4]) / 1e6 if k > 0 else 0
            save += (len(ctx) - 1 - k) * max(ctx[k] - P, 0) * p[2] / 1e6
    R = sum(len(c) for _, _, c in workers)
    print("%d\t%d\t%.1f%%\t%d\t%.2f%%\t%d\t%.2f\t%.2f\t%.2f\t%.2f" % (T, wo, 100 * wo / len(workers), ro, 100 * ro / R, n, save, cost, save - cost, tot))
