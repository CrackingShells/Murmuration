# Independent per-request cache usage of the dispatched (subagent) transcripts of headless sessions, one row per requestId (last record wins): cache read, 5m and 1h write, uncached input, timestamp gap, tools; inputs: one or more project folders under ~/.claude/projects (read-only); outputs: markdown rows on stdout and a per-session sum of write tokens by TTL.
# usage: w07c7r_usage.py PROJECT_DIR_NAME [...]
import json, glob, os, sys, datetime
H = os.path.expanduser("~/.claude/projects")
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
for pd in sys.argv[1:]:
    for f in sorted(glob.glob(os.path.join(H, pd, "*", "subagents", "agent-*.jsonl"))):
        reqs = {}; order = []
        for l in open(f):
            try: d = json.loads(l)
            except Exception: continue
            if d.get("type") != "assistant": continue
            m = d["message"]; u = m.get("usage") or {}; cc = u.get("cache_creation") or {}
            rid = d.get("requestId") or m.get("id")
            if rid not in reqs: order.append(rid); reqs[rid] = {"tools": []}
            r = reqs[rid]
            r.update(t=ts(d["timestamp"]), inp=u.get("input_tokens", 0), rd=u.get("cache_read_input_tokens", 0), w5=cc.get("ephemeral_5m_input_tokens", 0), w1=cc.get("ephemeral_1h_input_tokens", 0), wt=u.get("cache_creation_input_tokens", 0))
            for b in m.get("content") or []:
                if b.get("type") == "tool_use" and b["name"] not in r["tools"]: r["tools"].append(b["name"])
        print("\n##", pd, os.path.basename(f), "requests", len(order))
        print("| i | gap s | in | read | w5m | w1h | wtot | ctx | read/prevctx | tools |\n|--:|--:|--:|--:|--:|--:|--:|--:|--:|:--|")
        prev = None; s5 = s1 = 0
        for i, rid in enumerate(order):
            r = reqs[rid]; ctx = r["inp"] + r["rd"] + r["wt"]; s5 += r["w5"]; s1 += r["w1"]
            print("| %d | %s | %d | %d | %d | %d | %d | %d | %s | %s |" % (i, "" if prev is None else "%.1f" % (r["t"] - prev["t"]), r["inp"], r["rd"], r["w5"], r["w1"], r["wt"], ctx,
                  "" if prev is None else "%.3f" % (r["rd"] / prev["ctx"]), ",".join(r["tools"])))
            r["ctx"] = ctx; prev = r
        print("sum write 5m %d, 1h %d; requests that wrote: %d of %d" % (s5, s1, sum(1 for r in reqs.values() if r["wt"] > 0), len(order)))
