# Re-derives, from a w05-c1 run folder's run.jsonl and the worker's subagent transcript (~/.claude/projects), per-request context/cache read/cache write (5m vs 1h), gaps, tool-call durations over 60 s, Bash timeout parameters and the worker's own list-price cost; prints text. Independent of w05c1_wait_arms.py (stdlib only).
# usage: python3 -I w05c1_rederive_requests.py RUNDIR [RUNDIR ...]   (RUNDIR = .../runs/A1, holds run.jsonl)
import glob, json, os, sys
from datetime import datetime
SONNET = dict(i=2.0, o=10.0, cr=0.10, cw5=2.5, cw1=4.0)
def ts(s): return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
for rd in sys.argv[1:]:
    sess = None; total = None; nres = 0
    for l in open(os.path.join(rd, "run.jsonl")):
        try: d = json.loads(l)
        except Exception: continue
        sess = d.get("session_id", sess)
        if d.get("type") == "result": total = d.get("total_cost_usd"); nres += 1
    subs = glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents/agent-*.jsonl" % sess))
    print("=== %s session %s subagent transcripts %d result records %d total_cost_usd %s" % (os.path.basename(rd), sess, len(subs), nres, total))
    tp = max(subs, key=os.path.getsize)
    reqs = {}; order = []; calls = {}
    for l in open(tp):
        d = json.loads(l); m = d.get("message")
        if not isinstance(m, dict) or "timestamp" not in d: continue
        t = ts(d["timestamp"])
        if d["type"] == "assistant":
            u = m.get("usage", {}); mid = m.get("id")
            if mid not in reqs: reqs[mid] = {"t": t}; order.append(mid)
            cc = u.get("cache_creation") or {}
            reqs[mid].update(model=m.get("model"), i=u.get("input_tokens", 0), o=u.get("output_tokens", 0), cr=u.get("cache_read_input_tokens", 0),
                             cw=u.get("cache_creation_input_tokens", 0), cw1=cc.get("ephemeral_1h_input_tokens", 0), cw5=cc.get("ephemeral_5m_input_tokens", 0))
            for c in m.get("content", []):
                if c.get("type") == "tool_use": calls[c["id"]] = dict(t=t, n=c["name"], inp=c.get("input"), dur=None)
        elif d["type"] == "user" and isinstance(m.get("content"), list):
            for c in m["content"]:
                if c.get("type") == "tool_result" and c.get("tool_use_id") in calls: calls[c["tool_use_id"]]["dur"] = t - calls[c["tool_use_id"]]["t"]
    cost = 0; t0 = reqs[order[0]]["t"]; prev = None; ncold = 0
    print("req  t_s   gap_s  ctx     cache_read cache_write(5m/1h)  cold(gap>300 & cr<50%ctx)")
    for k, mid in enumerate(order):
        r = reqs[mid]; ctx = r["i"] + r["cr"] + r["cw"]; gap = None if prev is None else r["t"] - reqs[prev]["t"]
        cold = gap is not None and gap > 300 and r["cr"] < 0.5 * ctx; ncold += cold
        c = (r["i"] * SONNET["i"] + r["o"] * SONNET["o"] + r["cr"] * SONNET["cr"] + r["cw5"] * SONNET["cw5"] + r["cw1"] * SONNET["cw1"]) / 1e6
        cost += c
        print("%3d %6.1f %6s %7d %8d %7d (%d/%d) %s %s" % (k, r["t"] - t0, "-" if gap is None else "%.1f" % gap, ctx, r["cr"], r["cw"], r["cw5"], r["cw1"], "COLD" if cold else "", r["model"]))
        prev = mid
    print("worker requests %d cold %d; worker list-price cost (sonnet prices) USD %.3f" % (len(order), ncold, cost))
    for c in sorted(calls.values(), key=lambda c: -(c["dur"] or 0))[:4]:
        print("  longest calls: %7.1f s  %s %s" % (c["dur"] or 0, c["n"], json.dumps(c["inp"])[:200]))
