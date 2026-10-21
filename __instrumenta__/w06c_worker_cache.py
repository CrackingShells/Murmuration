#!/usr/bin/env python3
# Computes, from a session's subagent transcripts (agent-*.jsonl), the cache-write split (5-minute vs 1-hour) and every request that follows a gap over 300 s with its cache read against the previous context (hit, partial or miss) and the extra USD of the misses over a read; writes <outdir>/<label>_worker_cache.tsv and prints a summary. Usage: w06c_worker_cache.py SUBAGENT_DIR LABEL OUTDIR
import json, sys, os, glob, datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L
sub, label, out = sys.argv[1:4]
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
tot = {"cw5": 0, "cw1": 0, "cr": 0}
rows = []
for f in sorted(glob.glob(os.path.join(sub, "agent-*.jsonl"))):
    try: name = json.load(open(f[:-6] + ".meta.json")).get("name", "?")
    except Exception: name = "?"
    msgs, order = {}, []
    for l in open(f, errors="replace"):
        if '"assistant"' not in l: continue
        try: d = json.loads(l)
        except Exception: continue
        if d.get("type") != "assistant": continue
        m = d["message"]; mid = m.get("id"); u = m.get("usage") or {}
        if mid not in msgs:
            msgs[mid] = dict(t=ts(d["timestamp"]), model=m.get("model"), usage={}); order.append(mid)
        L.merge_usage(msgs[mid]["usage"], u)
    prev_t, prev_ctx = None, 0
    for mid in order:
        m = msgs[mid]; u = m["usage"]; cc = u.get("cache_creation") or {}
        cw1, cw5 = int(cc.get("ephemeral_1h_input_tokens") or 0), int(cc.get("ephemeral_5m_input_tokens") or 0)
        cw5 += max(0, int(u.get("cache_creation_input_tokens") or 0) - cw1 - cw5)
        cr = int(u.get("cache_read_input_tokens") or 0)
        tot["cw5"] += cw5; tot["cw1"] += cw1; tot["cr"] += cr
        ctx = cr + cw1 + cw5 + int(u.get("input_tokens") or 0)
        if prev_t is not None and m["t"] - prev_t > 300:
            p = L.PRICES.get((m["model"] or "").rsplit("-20", 1)[0], L.PRICES["claude-sonnet-5-5"])
            lost = max(0, prev_ctx - cr)
            rows.append((name, m["model"], "%.0f" % (m["t"] - prev_t), prev_ctx, cr, lost, "%.4f" % (lost * ((p[3] if cw5 >= cw1 else p[4]) - p[2]) / 1e6)))
        prev_t, prev_ctx = m["t"], ctx
with open(os.path.join(out, label + "_worker_cache.tsv"), "w") as fh:
    fh.write("agent\tmodel\tgap_s\tprev_ctx\tcache_read\ttokens_not_read\textra_usd_over_read\n")
    for r in rows: fh.write("\t".join(map(str, r)) + "\n")
miss = [r for r in rows if r[5] > 0.5 * r[3]]
print(label, "cache writes: 5m %d, 1h %d tokens; reads %d; requests after a gap >300 s: %d; misses (read < half of previous ctx): %d, tokens not read %d, extra USD %.2f; gaps >300 s by max: %s" % (
    tot["cw5"], tot["cw1"], tot["cr"], len(rows), len(miss), sum(r[5] for r in miss), sum(float(r[6]) for r in miss), max([int(r[2]) for r in rows] or [0])))
