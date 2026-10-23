# Per run folder (stream.jsonl + debug.log): the compaction request's usage and USD (from debug.log 'Forked agent ... totalUsage'), the first assistant request after compact_boundary (cache write split 5m/1h, cache read) and the context before/after; own code, Opus list price per million: in 5, out 25? read PRICE below. Inputs: RUNS_DIR NAME...; output: one line per run.
import json, os, re, sys
P = dict(i=4.0, o=20.0, r=0.20, w5=5.0, w1=8.0)  # as in scripts/lab_status.py PRICES for the Opus 5.5 row; checked below against the script by the caller
RD = sys.argv[1]
for n in sys.argv[2:]:
    D = os.path.join(RD, n); dbg = open(os.path.join(D, "debug.log"), errors="replace").read()
    fa = re.findall(r"Forked agent \[([\w-]+)\] finished.*?totalUsage: input=(\d+) output=(\d+) cacheRead=(\d+) cacheCreate=(\d+)", dbg)
    rows = []
    for l in open(os.path.join(D, "stream.jsonl")):
        try: rows.append(json.loads(l))
        except ValueError: pass
    b = [i for i, d in enumerate(rows) if d.get("type") == "system" and d.get("subtype") == "compact_boundary"]
    comp = [(int(a), int(o), int(r), int(c)) for _, a, o, r, c in fa]
    usd = sum((a * P["i"] + o * P["o"] + r * P["r"] + c * P["w1"]) / 1e6 for a, o, r, c in comp)
    nxt = None; pre = post = None
    if b:
        cm = rows[b[0]]["compact_metadata"]; pre, post = cm["pre_tokens"], cm["post_tokens"]
        for d in rows[b[0]:]:
            if d.get("type") == "assistant":
                u = d["message"]["usage"]; cc = u.get("cache_creation") or {}
                nxt = (u.get("input_tokens"), u.get("cache_read_input_tokens"), u.get("cache_creation_input_tokens"), cc.get("ephemeral_5m_input_tokens"), cc.get("ephemeral_1h_input_tokens")); break
    print(n, "pre", pre, "post", post, "compactions", len(comp), "comp_usage(in,out,read,write)", comp, "comp_usd %.3f" % usd, "| next request (in,read,write,w5m,w1h)", nxt,
          "| write usd 5m %.3f 1h %.3f" % ((nxt[2] or 0) * P["w5"] / 1e6, (nxt[2] or 0) * P["w1"] / 1e6) if nxt else "")
