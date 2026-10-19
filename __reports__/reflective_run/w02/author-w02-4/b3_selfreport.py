#!/usr/bin/env python3 -I
"""w02-c10: the B3 author's self-reported spend against the harness `end` line and the cost-state record.
usage: python3 -I b3_selfreport.py <B3 arm folder>   (reads only; the folder holds lab/, stdout.jsonl)
Reads: lab/__statera__/handbacks/*.md (a line 'about USD x'), lab/__statera__/harness.jsonl (`end` lines),
and the main transcript's last `cost-state` record, found by the session id of stdout.jsonl's result event."""
import glob, json, os, re, sys
arm = sys.argv[1]
H = os.path.join(arm, "lab", "__statera__")
ends = [json.loads(l) for l in open(os.path.join(H, "harness.jsonl")) if '"event": "end"' in l]
claimed = {}
for f in glob.glob(os.path.join(H, "handbacks", "*.md")):
    n = os.path.basename(f)[len("wave-01-"):-3]
    m = re.search(r"about USD ([0-9.]+)", open(f).read())
    if m: claimed[n] = float(m.group(1))
sid = [json.loads(l) for l in open(os.path.join(arm, "stdout.jsonl")) if '"type":"result"' in l.replace(" ", "")][-1]["session_id"]
main = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sid))[0]
cs = [json.loads(l) for l in open(main) if '"cost-state"' in l][-1]
mu = cs["modelUsage"]
sonnet = sum(v["costUSD"] for k, v in mu.items() if "sonnet" in k)
print("| worker | brief B | self-report USD | harness used USD | harness frac of B |\n|:--|--:|--:|--:|--:|")
for e in sorted(ends, key=lambda e: e["name"]):
    print("| %s | %.2f | %s | %.3f | %.3f |" % (e["name"], e["B"], claimed.get(e["name"], "-"), e["used"], e["frac"]))
tot = sum(e["used"] for e in ends)
print("\nworkers (harness `end` lines): %d, sum used %.3f USD (estimate: output = max(recorded, chars/1.3))" % (len(ends), tot))
print("cost-state, all Sonnet (exact, workers only): %.4f USD; total session %.4f USD" % (sonnet, cs["totalCostUSD"]))
c = max(claimed.values()) if claimed else None
if c:
    print("largest self-report %.2f USD = %.1f x the exact cost of ALL workers together, %.1f x the harness figure for that worker"
          % (c, c / sonnet, c / [e["used"] for e in ends if claimed.get(e["name"]) == c][0]))
