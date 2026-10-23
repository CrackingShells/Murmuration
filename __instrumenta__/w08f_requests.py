# Extracts, per API request, usage and content sizes from a w08f stream-json run (message_start/message_delta usage, thinking_tokens, assistant blocks, tool results); from <run>.jsonl files to a TSV of requests and a growth table on stdout.
# usage: w08f_requests.py RUN.jsonl [more.jsonl ...]  -> prints per request: k, ctx (input+cache_read+cache_write), out, thinking_tokens (platform-reported in message_delta), text chars, tool_use input chars, thinking signature chars, USD at list price (Sonnet 5.5: 2 / 0.10 / 2.5 / 4 / 10 per MTok), growth to next request.
import sys, json
P = dict(i=2.0, r=0.10, w5=2.5, w1=4.0, o=10.0)
def parse(path):
    reqs = {}; order = []; results = []; pending = None
    for l in open(path):
        try: d = json.loads(l)
        except Exception: continue
        t = d.get("type"); e = d.get("event") or {}
        if t == "stream_event" and e.get("type") == "message_start":
            m = e["message"]; mid = m["id"]; u = m["usage"]
            if mid not in reqs:
                reqs[mid] = dict(id=mid, u0=u, out=None, think=None, text=0, tool=0, sig=0, ntool=0, stop=None); order.append(mid)
            pending = mid
        elif t == "stream_event" and e.get("type") == "message_delta" and pending:
            u = e.get("usage") or {}
            reqs[pending]["out"] = u.get("output_tokens"); reqs[pending]["think"] = (u.get("output_tokens_details") or {}).get("thinking_tokens")
            reqs[pending]["stop"] = (e.get("delta") or {}).get("stop_reason")
            if u.get("cache_creation_input_tokens") is not None: reqs[pending]["u1"] = u
        elif t == "assistant":
            m = d["message"]; r = reqs.get(m["id"])
            if r is None: continue
            for b in m["content"]:
                if b["type"] == "text": r["text"] = max(r["text"], len(b["text"]))
                elif b["type"] == "thinking": r["sig"] = max(r["sig"], len(b.get("signature", "")))
                elif b["type"] == "tool_use": r["tool"] = max(r["tool"], len(json.dumps(b["input"]))); r["ntool"] += 0
        elif t == "user":
            c = d["message"]["content"]
            if isinstance(c, list):
                for b in c:
                    if b.get("type") == "tool_result":
                        x = b.get("content"); x = x if isinstance(x, str) else json.dumps(x)
                        results.append(len(x))
    rows = []
    for k, mid in enumerate(order):
        r = reqs[mid]; u = r.get("u1") or r["u0"]
        cc = u.get("cache_creation") or {}
        w5 = cc.get("ephemeral_5m_input_tokens", 0); w1 = cc.get("ephemeral_1h_input_tokens", u.get("cache_creation_input_tokens", 0) - w5)
        ctx = u["input_tokens"] + u["cache_read_input_tokens"] + u["cache_creation_input_tokens"]
        usd = (u["input_tokens"] * P["i"] + u["cache_read_input_tokens"] * P["r"] + w5 * P["w5"] + w1 * P["w1"] + (r["out"] or 0) * P["o"]) / 1e6
        rows.append(dict(k=k, ctx=ctx, cr=u["cache_read_input_tokens"], cw=u["cache_creation_input_tokens"], inp=u["input_tokens"], out=r["out"], think=r["think"], text=r["text"], tool=r["tool"], sig=r["sig"], usd=usd, stop=r["stop"]))
    return rows, results
if __name__ == "__main__":
    for p in sys.argv[1:]:
        rows, res = parse(p)
        print("#", p, "requests", len(rows), "tool results chars", res)
        print("k\tctx\tcr\tcw\tout\tthink\ttext_ch\ttool_ch\tsig_ch\tusd\tgrowth_to_next\tstop")
        for i, r in enumerate(rows):
            g = rows[i + 1]["ctx"] - r["ctx"] if i + 1 < len(rows) else ""
            print("%d\t%d\t%d\t%d\t%s\t%s\t%d\t%d\t%d\t%.4f\t%s\t%s" % (r["k"], r["ctx"], r["cr"], r["cw"], r["out"], r["think"], r["text"], r["tool"], r["sig"], r["usd"], g, r["stop"]))
