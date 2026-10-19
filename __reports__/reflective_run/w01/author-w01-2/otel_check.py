"""Compare, for a cell made by otel_cell.py: OTel api_request sums, forwarded-stream sums, transcript sums, result.modelUsage.
usage: python3 -I otel_check.py <cell> ..."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sumtx
K = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
for cell in sys.argv[1:]:
    base = os.path.join(HERE, "runs", cell)
    ev = json.load(open(os.path.join(base, "otel_events.json")))
    api = [e for e in ev if e["event.name"] == "api_request"]
    ot = dict(input_tokens=0, output_tokens=0, cache_read_input_tokens=0, cache_creation_input_tokens=0)
    for e in api:
        ot["input_tokens"] += int(e["input_tokens"]); ot["output_tokens"] += int(e["output_tokens"])
        ot["cache_read_input_tokens"] += int(e["cache_read_tokens"]); ot["cache_creation_input_tokens"] += int(e["cache_creation_tokens"])
    res = []; fw = {}
    for l in open(os.path.join(base, "stdout.jsonl")):
        d = json.loads(l)
        if d.get("type") == "result": res.append(d)
        if d.get("type") == "assistant" and d.get("request_id"):
            fw[d["request_id"]] = d["message"]["usage"]["output_tokens"]   # last forwarded record per request
    mu = res[-1]["modelUsage"]; MU = dict(input_tokens="inputTokens", output_tokens="outputTokens", cache_read_input_tokens="cacheReadInputTokens", cache_creation_input_tokens="cacheCreationInputTokens")
    truth = {k: sum(v[MU[k]] for v in mu.values()) for k in K}
    hk = [json.loads(l) for l in open(os.path.join(base, "hooks", "hooks.jsonl"))]
    ses = sumtx.session(hk[0]["input"]["transcript_path"])
    tr = {k: ses["main"]["sums"]["last"][k] + sum(s["sums"]["last"][k] for s in ses["subagents"].values()) for k in K}
    sub_ids = {r["key"] for s in ses["subagents"].values() for r in s["per_request"]}
    otel_sub = sum(int(e["output_tokens"]) for e in api if e.get("query_source", "").startswith("agent"))
    print(json.dumps(dict(cell=cell, permmode=json.load(open(os.path.join(base, "cell.json")))["permmode"], truth=truth, otel=ot, transcript_last=tr,
                          otel_equals_truth=ot == truth, transcript_equals_truth=tr == truth,
                          otel_subagent_output=otel_sub, transcript_subagent_output=sum(s["sums"]["last"]["output_tokens"] for s in ses["subagents"].values()),
                          stream_forwarded_output_total=sum(fw.values()), n_forwarded_requests=len(fw), cost_usd=res[-1]["total_cost_usd"],
                          otel_cost=sum(float(e["cost_usd"]) for e in api))))
