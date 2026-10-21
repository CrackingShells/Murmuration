"""Distribution of the size of what a PostToolUse / PostToolBatch hook payload would carry, estimated from transcripts: the JSON length of each tool_result (per call) and the sum per user record (per batch).

Inputs: transcript .jsonl paths as arguments (main-thread session and/or worker agent-*.jsonl). Output: count, percentiles (p50, p90, p99, max) in KB, mean, and the fraction above 30, 100, 200 KB, for calls and for batches, separately for main files (no 'agent-' prefix) and worker files.
Estimate only: the platform may truncate a tool_response differently from what the transcript stores (a 148 KB Bash output gave a 31 KB payload in a headless probe).
"""
import json, os, sys, statistics as st
def sizes(path):
    calls, batches = [], []
    for line in open(path, errors="replace"):
        if '"tool_result"' not in line: continue
        try: r = json.loads(line)
        except Exception: continue
        c = (r.get("message") or {}).get("content")
        if not isinstance(c, list): continue
        tot = 0; n = 0
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                L = len(json.dumps(b.get("content"))); calls.append(L); tot += L; n += 1
        if n: batches.append(tot)
    return calls, batches
G = {"main": ([], []), "worker": ([], [])}
for p in sys.argv[1:]:
    k = "worker" if os.path.basename(p).startswith("agent-") else "main"
    c, b = sizes(p); G[k][0].extend(c); G[k][1].extend(b)
for k, (c, b) in G.items():
    for nm, xs in (("call", c), ("batch", b)):
        if not xs: continue
        xs = sorted(xs); q = lambda f: xs[min(len(xs) - 1, int(f * len(xs)))] / 1024
        fr = lambda t: sum(x > t * 1024 for x in xs) / len(xs)
        print("%-6s %-5s n=%5d  p50 %6.1f  p90 %6.1f  p99 %6.1f  max %8.1f KB  mean %6.1f KB  >30KB %.3f  >100KB %.3f  >200KB %.3f" % (k, nm, len(xs), q(.5), q(.9), q(.99), xs[-1] / 1024, st.mean(xs) / 1024, fr(30), fr(100), fr(200)))
