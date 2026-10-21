#!/usr/bin/env python3
# Finds, in a PI transcript (.jsonl), the turns where a skill_listing attachment (isInitial) re-enters the context, estimates the extra tokens (delta_ctx minus the median delta of peer turns without it), the requests each copy is carried, and its carry cost as a share of the list-price total; writes <outdir>/<label>_listing_reinjection.tsv. Usage: w05b_listing_reinjection.py TRANSCRIPT LABEL OUTDIR
import json, sys, os, statistics as st, datetime
P = {"claude-opus-5-5": (4.0, 20.0, 0.20, 5.0, 8.0)}
F, label, out = sys.argv[1:4]
recs = [json.loads(l) for l in open(F, errors="replace")]
order, seen = [], {}
for i, d in enumerate(recs):
    if d["type"] == "assistant":
        m = d["message"]["id"]
        if m not in seen:
            seen[m] = dict(first=i, last=i, u=d["message"]["usage"], ts=d["timestamp"], model=d["message"].get("model")); order.append(m)
        seen[m]["last"] = i
        if d["message"]["usage"].get("output_tokens", 0) >= seen[m]["u"].get("output_tokens", 0):
            seen[m]["u"] = d["message"]["usage"]
g = lambda u, k: int(u.get(k) or 0)
ctx = lambda u: g(u, "input_tokens") + g(u, "cache_read_input_tokens") + g(u, "cache_creation_input_tokens")
T = 0.0
for m in order:
    u = seen[m]["u"]; p = P.get(seen[m]["model"], P["claude-opus-5-5"]); cc = u.get("cache_creation") or {}
    w1 = int(cc.get("ephemeral_1h_input_tokens") or 0); w5 = g(u, "cache_creation_input_tokens") - w1
    T += (g(u, "input_tokens") * p[0] + g(u, "output_tokens") * p[1] + g(u, "cache_read_input_tokens") * p[2] + w1 * p[4] + w5 * p[3]) / 1e6
resets = [k for k in range(1, len(order)) if ctx(seen[order[k]]["u"]) < 0.6 * ctx(seen[order[k - 1]]["u"])] + [len(order)]
withl, without, ev = [], [], []
for k in range(1, len(order)):
    a, b = seen[order[k - 1]], seen[order[k]]
    seg = recs[a["last"] + 1:b["first"]]
    peer = any(r["type"] == "user" and (r.get("origin") or {}).get("kind") == "peer" for r in seg)
    sl = [r for r in seg if r["type"] == "attachment" and r["attachment"]["type"] == "skill_listing"]
    dl = ctx(b["u"]) - ctx(a["u"])
    t1 = datetime.datetime.fromisoformat(b["ts"].replace("Z", "+00:00")).timestamp(); t0 = datetime.datetime.fromisoformat(a["ts"].replace("Z", "+00:00")).timestamp()
    if peer and not sl:
        without.append(dl)
    if sl:
        if g(b["u"], "cache_read_input_tokens") > 0.5 * ctx(a["u"]):  # skip cache-miss rewrites: their delta is the whole context
            ev.append((k, b["ts"], t1 - t0, dl, peer, len(sl[0]["attachment"]["content"])))
base = st.median(without) if without else 0
tot_tok = tot_usd = 0
with open(os.path.join(out, label + "_listing_reinjection.tsv"), "w") as f:
    f.write("request\tts_utc\tgap_s\tdelta_ctx\tpeer_turn\tlisting_chars\textra_tokens\tcarried_requests\tcarry_usd_list\n")
    for k, ts_, gap, dl, peer, ch in ev:
        if k == 0 or dl <= 0 or k in resets:
            continue
        extra = max(dl - base, 0)
        end = min(x for x in resets if x > k)
        reads = sum(g(seen[order[m]]["u"], "cache_read_input_tokens") > 0 for m in range(k + 1, end))
        usd = extra * (P["claude-opus-5-5"][4] + reads * P["claude-opus-5-5"][2]) / 1e6
        tot_tok += extra; tot_usd += usd
        f.write("%d\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%.3f\n" % (k, ts_, gap, dl, peer, ch, extra, end - k - 1, usd))
print("%s: %d skill_listing re-entries after request 0; median delta of peer turns without listing %d; extra tokens %d; carry cost at list price = %.3f of the list-price total (%d requests)" % (label, len(ev), base, tot_tok, tot_usd / T, len(order)))
