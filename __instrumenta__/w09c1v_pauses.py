"""Counts, for every murmuration:author subagent transcript of the lab's six worktrees under ~/.claude/projects (start before 2026-10-25), pauses over 300 s between consecutive assistant requests (first timestamp of each requestId) and cold re-writes (cache write >= half of the previous context), per era (before 2026-10-21T08:08Z, to 17:38Z, after); pauses per author per era and a one-sided permutation test (seed 7, 20000) to stdout; independent of w09f/w09c1 scripts."""
import json, glob, os, datetime, random, statistics as st
root = os.path.expanduser("~/.claude/projects")
LAB = ("8cff9e", "928ebd", "bc67fb", "34edd8", "1aa673", "3417be")
T = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
per = {0: [], 1: [], 2: []}; cold = {0: 0, 1: 0, 2: 0}
for d in glob.glob(root + "/*"):
    if not d.endswith(LAB) or "---reports" in d: continue
    for a in glob.glob(d + "/*/subagents/agent-*.jsonl"):
        try: meta = json.load(open(a[:-6] + ".meta.json"))
        except Exception: continue
        if meta.get("agentType") != "murmuration:author": continue
        first = {}; ctx = {}; order = []; ts0 = None
        for l in open(a, errors="replace"):
            try: r = json.loads(l)
            except Exception: continue
            if ts0 is None and r.get("timestamp"): ts0 = r["timestamp"]
            if r.get("type") != "assistant": continue
            m = r["message"]; rid = r.get("requestId") or m.get("id"); u = m.get("usage") or {}
            if rid not in first: first[rid] = r["timestamp"]; order.append(rid)
            ctx[rid] = (u.get("cache_read_input_tokens") or 0, u.get("cache_creation_input_tokens") or 0, u.get("input_tokens") or 0)
        if ts0 >= "2026-10-25": continue
        era = 0 if ts0 < "2026-10-21T08:08" else (1 if ts0 < "2026-10-21T17:38" else 2)
        n = 0
        for p, q in zip(order, order[1:]):
            if T(first[q]) - T(first[p]) > 300:
                n += 1
                pc = sum(ctx[p])
                if ctx[q][1] >= 0.5 * pc: cold[era] += 1
        per[era].append(n)
for e in per: print("era", e, "authors", len(per[e]), "pauses", sum(per[e]), "per author %.2f" % (sum(per[e]) / len(per[e])), "cold", cold[e])
random.seed(7)
def perm(x, y):
    obs = sum(x) / len(x) - sum(y) / len(y); pool = x + y; k = 0
    for _ in range(20000):
        random.shuffle(pool); k += (sum(pool[:len(x)]) / len(x) - sum(pool[len(x):]) / len(y)) >= obs
    return obs, k / 20000
print("a-b", perm(per[0], per[1]), "b-c", perm(per[1], per[2]))
