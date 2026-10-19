"""ESTIMATE: can the missing subagent output tokens be reconstructed from the CONTENT of the records?
Calibrate tokens-per-character on main-thread messages (final usage, complete) of one session, apply to the
subagent files (usage truncated), compare with Claude Code's own `cost-state` per-model output total.
Read-only on ~/.claude/projects.   usage: python3 -I estimate_out.py <main-session.jsonl> [...]"""
import json, sys, os, glob, collections

def blocks_chars(content):
    c = collections.Counter()
    for b in content if isinstance(content, list) else []:
        t = b.get("type")
        if t == "thinking": c["think"] += len(b.get("thinking", ""))
        elif t == "text": c["text"] += len(b.get("text", ""))
        elif t == "tool_use": c["tool"] += len(json.dumps(b.get("input", {}), ensure_ascii=False)) + len(b.get("name", ""))
    return c

def per_request(path):
    """request -> (model, chars Counter, last-record output_tokens)"""
    reqs = collections.OrderedDict(); cs = None
    for l in open(path, errors="replace"):
        try: d = json.loads(l)
        except Exception: continue
        if d.get("type") == "cost-state": cs = d
        if d.get("type") != "assistant": continue
        m = d["message"]; k = d.get("requestId") or m.get("id")
        r = reqs.setdefault(k, [m.get("model"), collections.Counter(), 0])
        r[1].update(blocks_chars(m.get("content")))
        r[2] = (m.get("usage") or {}).get("output_tokens", 0)
    return reqs, cs

for main in sys.argv[1:]:
    mreq, cs = per_request(main)
    # calibration on main thread: least squares of output tokens on [think, text, tool] chars (no intercept)
    import itertools
    rows = [(r[1]["think"], r[1]["text"], r[1]["tool"], r[2]) for r in mreq.values() if r[0] and "opus" in r[0]]
    # simple pooled ratio per kind via normal equations
    def solve(rows):
        import fractions
        A = [[sum(r[i] * r[j] for r in rows) for j in range(3)] for i in range(3)]
        b = [sum(r[i] * r[3] for r in rows) for i in range(3)]
        n = 3
        M = [A[i] + [b[i]] for i in range(n)]
        for i in range(n):
            p = max(range(i, n), key=lambda r: abs(M[r][i])); M[i], M[p] = M[p], M[i]
            for j in range(i + 1, n):
                f = M[j][i] / M[i][i]; M[j] = [M[j][k] - f * M[i][k] for k in range(n + 1)]
        x = [0] * n
        for i in reversed(range(n)):
            x[i] = (M[i][n] - sum(M[i][k] * x[k] for k in range(i + 1, n))) / M[i][i]
        return x
    coef = solve(rows) if len(rows) > 5 else [0.25, 0.25, 0.3]
    sub = collections.defaultdict(lambda: [0, 0, 0, 0])  # model -> [requests, trunc_out, est_out, chars]
    for p in sorted(glob.glob(main[:-6] + "/subagents/agent-*.jsonl")):
        reqs, _ = per_request(p)
        for k, (model, ch, out) in reqs.items():
            s = sub[model]; s[0] += 1; s[1] += out
            s[2] += coef[0] * ch["think"] + coef[1] * ch["text"] + coef[2] * ch["tool"]; s[3] += sum(ch.values())
    print(os.path.basename(main), "calibration rows (Opus main requests):", len(rows), "tokens/char think,text,tool =", [round(c, 3) for c in coef])
    mu = (cs or {}).get("modelUsage") or (cs or {}).get("costState", {}).get("modelUsage") or {}
    if not mu and cs:
        for v in cs.values():
            if isinstance(v, dict) and any("claude" in k for k in v): mu = v
    for model, (n, trunc, est, chars) in sub.items():
        truth = None
        for k, v in mu.items():
            if k == model or (model and k.split("[")[0] == model): truth = v.get("outputTokens")
        print("  %-22s requests %5d  transcript_out %8d  est_from_content %9.0f  cost-state_out(all agents of model) %s" % (model, n, trunc, est, truth))
