import json, glob, os, collections
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pre = collections.Counter(); post = collections.Counter(); dts = []
tot = []
for d in sorted(glob.glob(S + "/runs/anx-*/")):
    H = [json.loads(l) for l in open(d + "hooks.jsonl")]
    n_pre = n_post = 0
    for h in H:
        i = h["input"]
        if not i.get("agent_id") or "spend" not in h: continue
        if h["event"] == "PreToolUse":
            n_pre += 1; pre[h["spend"]["requests"] - n_pre] += 1
        if h["event"] == "PostToolUse":
            n_post += 1; post[h["spend"]["requests"] - n_post] += 1
        dts.append(h["dt_ms"])
    # final vs truth
    res = None
    for l in open(d + "stdout.jsonl"):
        r = json.loads(l)
        if r.get("type") == "result": res = r
    sub = [h for h in H if h["event"] == "SubagentStop"][-1]["spend"]
    # main transcript sum
    mt = [h for h in H if h["event"] == "SessionStart"][0]["input"]["transcript_path"]
    last = {}
    for l in open(mt):
        r = json.loads(l)
        if r.get("type") == "assistant" and (r.get("message") or {}).get("usage"):
            last[r.get("requestId")] = r["message"]["usage"]
    m = dict(i=0, cr=0, cw=0, o=0)
    for u in last.values():
        m["i"] += u["input_tokens"]; m["cr"] += u["cache_read_input_tokens"]; m["cw"] += u["cache_creation_input_tokens"]; m["o"] += u["output_tokens"]
    mu = list(res["modelUsage"].values())[0]
    tot.append((os.path.basename(d.rstrip("/")), mu["inputTokens"] - m["i"] - sub["in"], mu["cacheReadInputTokens"] - m["cr"] - sub["cr"], mu["cacheCreationInputTokens"] - m["cw"] - sub["cw"], mu["outputTokens"] - m["o"] - sub["out"], sub["out"], mu["outputTokens"]))
print("request-count minus true tool-call index, PreToolUse (0 = current, -1 = stale by one):", dict(pre))
print("same, PostToolUse:", dict(post))
dts.sort(); print("hook wall ms: n=%d median=%.1f p95=%.1f max=%.1f" % (len(dts), dts[len(dts)//2], dts[int(len(dts)*.95)], dts[-1]))
print("modelUsage minus (main transcript + subagent hook-final): d_in d_cr d_cw d_out ; sub_out_at_hook ; total out")
for t in tot[:6]: print(t)
bad = [t for t in tot if t[1] or t[2] or t[3]]
print("runs where input/cache differ from truth:", len(bad), "of", len(tot))
