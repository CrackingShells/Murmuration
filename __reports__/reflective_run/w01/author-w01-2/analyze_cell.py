"""Analyse one cell under runs/<cell>/ : transcript sums (by dedup method) against result.modelUsage.
usage: python3 -I analyze_cell.py <cell> [<cell> ...]    -> prints one JSON line per cell, appends results.jsonl
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sumtx
K = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
MU = dict(input_tokens="inputTokens", output_tokens="outputTokens",
          cache_read_input_tokens="cacheReadInputTokens", cache_creation_input_tokens="cacheCreationInputTokens")


def analyze(cell):
    base = os.path.join(HERE, "runs", cell)
    cj = json.load(open(os.path.join(base, "cell.json")))
    res = []
    init = None
    for l in open(os.path.join(base, "stdout.jsonl")):
        try:
            d = json.loads(l)
        except Exception:
            continue
        if d.get("type") == "result":
            res.append(d)
        if d.get("type") == "system" and d.get("subtype") == "init":
            init = d
    hooks = [json.loads(l) for l in open(os.path.join(base, "hooks", "hooks.jsonl"))]
    tp = [h["input"]["transcript_path"] for h in hooks if h["event"] == "SessionStart"][0]
    ses = sumtx.session(tp)
    last = res[-1]
    mu = last["modelUsage"]
    truth = {k: sum(v[MU[k]] for v in mu.values()) for k in K}
    think_truth = sum(v.get("thinkingTokens", 0) for v in mu.values())
    out = dict(cell=cell, **{k: cj.get(k) for k in ("bin", "mode", "think", "length", "env", "io", "partial", "thinkdisp", "effort", "auto", "permmode", "poll")},
               version=(init or {}).get("claude_code_version"), n_results=len(res),
               cost_usd=last.get("total_cost_usd"), models=list(mu), truth=truth, think_truth=think_truth,
               started_in_background=(last.get("subagent_stats") or {}).get("started_in_background"),
               spawned=(last.get("subagent_stats") or {}).get("spawned"))
    subs = ses["subagents"]
    out["n_subagent_files"] = len(subs)
    for method in ("first", "last", "max"):
        tot = {k: ses["main"]["sums"][method][k] + sum(s["sums"][method][k] for s in subs.values()) for k in K}
        out["tot_" + method] = tot
        out["diff_" + method] = {k: tot[k] - truth[k] for k in K}
    out["main_sums_last"] = ses["main"]["sums"]["last"]
    out["sub"] = {a: dict(requests=s["requests"], records=s["records"], null_stop_last=s["n_null_stop_last"],
                          sums=s["sums"], stops=[r["last_stop"] for r in s["per_request"]],
                          outs_first=[r["first_out"] for r in s["per_request"]],
                          outs_last=[r["last_out"] for r in s["per_request"]],
                          kinds=[r["kinds"] for r in s["per_request"]],
                          think=[r["think_tokens"] for r in s["per_request"]]) for a, s in subs.items()}
    out["main_per_request"] = [(r["first_out"], r["last_out"], r["last_stop"]) for r in ses["main"]["per_request"]]
    out["cost_state"] = ses["main"]["cost_state"]
    hk = []
    for h in hooks:
        for f in ("agent_transcript_path_at_hook", "transcript_path_at_hook"):
            if f in h:
                x = h[f]
                sums = x.get("sums") or {}
                hk.append(dict(event=h["event"], agent=h["input"].get("agent_id"), field=f, exists=x.get("exists"),
                               requests=x.get("requests"), size=x.get("size"),
                               out_first=sums.get("first", {}).get("output_tokens"),
                               out_last=sums.get("last", {}).get("output_tokens"),
                               out_max=sums.get("max", {}).get("output_tokens"),
                               null_stop_last=x.get("n_null_stop_last"), t=h["t"], poll=h.get("poll")))
    out["hook_view"] = hk
    return out


if __name__ == "__main__":
    for c in sys.argv[1:]:
        o = analyze(c)
        open(os.path.join(HERE, "results.jsonl"), "a").write(json.dumps(o, default=list) + "\n")
        print(json.dumps(o, default=list))
