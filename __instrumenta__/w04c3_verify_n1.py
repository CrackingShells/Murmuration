#!/usr/bin/env python3
"""Recomputes n1 (fraction of the USD 0.30 budget at the first SubagentHandback request) per run from the worker transcript with its own price arithmetic (list-price rows from the lab table, output = max(recorded, chars/1.3)), and compares with the hook log's `used` at the same request count and with the platform's sonnet cost in meta.json; prints a TSV.
usage: w04c3_verify_n1.py <scratch> <cell> [<cell> ...]
Inputs: <scratch>/runs/<cell>/{meta.json,lab/__statera__/harness.jsonl}, worker transcript in ~/.claude/projects. Stdlib only."""
import glob, json, os, sys
P = (2.0, 10.0, 0.10, 2.5, 4.0)  # sonnet: in, out, cache read, cache write 5m, 1h per Mtok (the lab's table)
scratch = sys.argv[1]
print("cell\tn1_mine\tn1_end_all_reqs\tsonnet_usd_platform_over_B\thook_used_over_B_at_nearest_req\thb_req\tn_req")
for cell in sys.argv[2:]:
    R = scratch + "/runs/" + cell
    meta = json.load(open(R + "/meta.json")); B = float(meta["B"])
    f = sorted(glob.glob(os.path.expanduser("~/.claude/projects/*runs-%s-lab/*/subagents/agent-*.jsonl" % cell)), key=os.path.getsize)[-1]
    reqs, order, hbreq = {}, [], None
    for l in open(f):
        d = json.loads(l)
        if d.get("type") != "assistant" or not isinstance(d["message"].get("usage"), dict): continue
        u = d["message"]["usage"]; key = d.get("requestId") or d["message"].get("id")
        if key not in reqs:
            reqs[key] = dict(i=0, o=0, cr=0, cw=0, cw5=0, cw1=0, blocks={}); order.append(key)
        r = reqs[key]; cc = u.get("cache_creation") or {}
        r["i"] = max(r["i"], u.get("input_tokens") or 0); r["o"] = max(r["o"], u.get("output_tokens") or 0)
        r["cr"] = max(r["cr"], u.get("cache_read_input_tokens") or 0); r["cw"] = max(r["cw"], u.get("cache_creation_input_tokens") or 0)
        r["cw5"] = max(r["cw5"], cc.get("ephemeral_5m_input_tokens") or 0); r["cw1"] = max(r["cw1"], cc.get("ephemeral_1h_input_tokens") or 0)
        for k, b in enumerate(d["message"].get("content") or []):
            if isinstance(b, dict):
                t = b.get("text") or b.get("thinking") or json.dumps(b.get("input") or {}, sort_keys=True)
                r["blocks"][(b.get("type"), b.get("id") or k)] = len(t)
                if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback" and hbreq is None: hbreq = len(order)
    cum, cums = 0.0, []
    for key in order:
        r = reqs[key]; out = max(r["o"], sum(r["blocks"].values()) / 1.3)
        cw5 = r["cw5"] if (r["cw5"] or r["cw1"]) else r["cw"]
        cum += (r["i"] * P[0] + out * P[1] + r["cr"] * P[2] + cw5 * P[3] + r["cw1"] * P[4]) / 1e6; cums.append(cum)
    logs = [json.loads(x) for x in open(R + "/lab/__statera__/harness.jsonl")]
    hk = [(x["requests"], x["used"]) for x in logs if x.get("used") is not None and x.get("requests")]
    near = min(hk, key=lambda t: abs(t[0] - (hbreq or len(order))))
    n1 = cums[hbreq - 1] / B if hbreq else None
    print("\t".join(str(x) for x in [cell, round(n1, 3) if n1 else None, round(cums[-1] / B, 3), round(meta["model_usd"].get("claude-sonnet-5-5", 0) / B, 3), "%s@%s" % (round(near[1] / B, 3), near[0]), hbreq, len(order)]))
