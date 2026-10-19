#!/usr/bin/env python3
"""Claim w01-c3, checks F1-F4: the cases in which the claim would be false, run on purpose.
F1 no cross-file deduplication (what v6 does): USD of the combinatorics project vs the sum of the four cost-state totals.
F2 a wrong price table (Opus 5 list price, $5/$25, instead of Opus 5.5, $4/$20): the cell ratios must leave 1.000.
F3 no git: the scan from the main checkout cannot reach the worktree's sessions.
F4 the output-token uplift for subagents, calibrated on one ended session and tested on the other (leave-one-out).
Writes falsify.txt. Run: python3 -I falsify.py"""
import collections, glob, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import lab_spend as L
COMB = os.path.expanduser("~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary")
MAIN = "/Users/hacker/Documents/src/CrackingShells/Murmuration"
out = []
def say(s=""):
    out.append(s); print(s)

mains = sorted(glob.glob(COMB + "/*.jsonl"))
sessions, stats, _ = L.load(mains)
cs_total = sum(s["cost_state"]["totalCostUSD"] for s in sessions)
mine = sum(sum(r["usd"] for r in s["rows"].values()) for s in sessions)
# F1: every file on its own, as v6 does (last record per id per file, no ownership, no cross-file dedup)
naive = 0.0
w = []
for m in mains:
    for f in [m] + L.agent_files(m):
        msgs, *_ = L.read_file(f, w)
        naive += sum(L.message_usd(d["model"], d["usage"]) or 0 for d in msgs.values())
say("F1 combinatorics, four sessions: cost-state total USD %.2f; lab_spend (dedup, owned) %.2f (the %.2f short of cost-state is the Haiku helper calls, which are in no transcript, "
    "and subagent output); per-file counting without cross-file dedup %.2f = %.3fx cost-state" % (cs_total, mine, cs_total - mine, naive, naive / cs_total))
say("   (per-file counting is v6's rule; v6 itself prints tokens only, the x1.32-1.44 factors are in compare.csv)")

# F2: wrong table
orig = dict(L.PRICES)
L.PRICES["claude-opus-5-5"] = (5.0, 25.0, 0.50, 6.25, 10.0)  # the Opus 5 / 4.x row of the same page
s2, _, _ = L.load(mains)
for s in s2:
    cell = sum(r["usd"] for (lab, k, m), r in s["rows"].items() if m == "claude-opus-5-5")
    ref = s["cost_state"]["modelUsage"].get("claude-opus-5-5", {}).get("costUSD")
    if ref and not any(r["lower_bound_msgs"] for (lab, k, m), r in s["rows"].items() if m == "claude-opus-5-5"):
        say("F2 session %s Opus 5.5 cell with the Opus 5 price row: %.2f / cost-state %.2f = %.3f (the right table gives 1.000)" % (s["sid"][:8], cell, ref, cell / ref))
L.PRICES.update(orig)

# F3: no git
real = L.git_worktrees
L.git_worktrees = lambda root: []
nogit = L.find_scan(MAIN)
L.git_worktrees = real
withgit = L.find_scan(MAIN)
wt = [f for f in withgit if "optimization-8cff9e" in f]
say("F3 scan from the main checkout: with git %d sessions of which %d are the worktree's; without git %d sessions, %d of the worktree's" %
    (len(withgit), len(wt), len(nogit), len([f for f in nogit if "optimization-8cff9e" in f])))

# F4: leave-one-out of the subagent output uplift
by = {}
for s in sessions:
    cs = s["cost_state"]
    for model in ("claude-sonnet-5-5", "claude-fable-5-1"):
        mu = cs["modelUsage"].get(model)
        if not mu: continue
        tr = sum(r["usd"] for (lab, k, m), r in s["rows"].items() if m == model)
        by.setdefault(model, {})[s["sid"][:8]] = (mu["costUSD"], tr)
for model, d in by.items():
    ks = sorted(d)
    for a, b in ((ks[0], ks[1]), (ks[1], ks[0])):
        up = d[a][0] / d[a][1]
        pred = d[b][1] * up
        say("F4 %s: uplift %.3f from session %s predicts session %s at USD %.2f; cost-state says %.2f (%+.1f%%)" %
            (model, up, a, b, pred, d[b][0], 100 * (pred / d[b][0] - 1)))
open(os.path.join(HERE, "falsify.txt"), "w").write("\n".join(out) + "\n")
