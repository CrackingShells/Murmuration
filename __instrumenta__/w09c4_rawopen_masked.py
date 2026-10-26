# Counts raw-artifact opens per hand-back wake (waves 5-8, by sender role; waves 1-8 with/without the platform banner), twice: with w09d_turns.py as coded, and with the "lab_status" substring masked in Bash commands so that call_info keeps the paths of a compound command; hand-backs exclude the peer messages that open "Another Claude session sent a message" without "[Subagent hand-back]"; reads <label>=<transcript> pairs, prints a text table.
# usage: python3 -I w09c4_rawopen_masked.py <label>=<transcript.jsonl> [...]   (the six pairs of w09-c2's method)
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w09d_turns as W
orig = W.call_info
def masked(name, inp):
    if name == "Bash" and "lab_status" in (inp.get("command") or ""):
        inp = dict(inp); inp["command"] = inp["command"].replace("lab_status", "lab_stat_us")
    return orig(name, inp)
from math import comb
def fisher(a, n1, b, n2):
    N = n1 + n2; K = a + b; tot = comb(N, K); p0 = comb(n1, a) * comb(n2, b) / tot
    return sum(comb(n1, x) * comb(n2, K - x) / tot for x in range(max(0, K - n2), min(n1, K) + 1) if comb(n1, x) * comb(n2, K - x) / tot <= p0 * (1 + 1e-9))
BANNER = "[harness: subagent output matched"
def run(pairs, mask):
    W.call_info = masked if mask else orig
    res = collections.defaultdict(lambda: [0, 0]); ban = collections.defaultdict(lambda: [0, 0]); peer = collections.defaultdict(lambda: [0, 0])
    for label, path in pairs:
        turns = W.parse(label, path)[0]
        W.analyse(turns)
        for t in turns:
            g = t["triggers"][0]
            if g["kind"] != "B" or t["n_steps"] == 0:
                continue
            nm = g.get("agent") or ""
            role = nm.split("-")[0] if re.match(r"(explorer|author|reproducer|proof-adversary)-w\d\d", nm) else "other"
            head = g.get("head") or ""
            ispeer = head.startswith("Another Claude session sent a message")
            if label in ("w5", "w6", "w7", "w8"):
                k = peer if ispeer else res
                k[role][0] += 1; k[role][1] += t["raw_here"]
            if not ispeer:
                b = BANNER in head
                ban[b][0] += 1; ban[b][1] += t["raw_here"]
    return res, ban, peer
pairs = [a.split("=", 1) for a in sys.argv[1:]]
for mask in (False, True):
    res, ban, peer = run(pairs, mask)
    print("== lab_status substring masked: %s" % mask)
    tot = [sum(v[0] for v in res.values()), sum(v[1] for v in res.values())]
    print("  waves 5-8 hand-backs (peer messages excluded), raw open in the same turn:", "; ".join("%s %d/%d" % (r, v[1], v[0]) for r, v in sorted(res.items())), "; all %d/%d" % (tot[1], tot[0]))
    print("  the peer messages left out:", "; ".join("%s %d/%d" % (r, v[1], v[0]) for r, v in sorted(peer.items())))
    print("  waves 1-8 hand-backs, banner: %d/%d, no banner: %d/%d" % (ban[True][1], ban[True][0], ban[False][1], ban[False][0]) + "; two-sided Fisher exact p = %.2f" % fisher(ban[True][1], ban[True][0], ban[False][1], ban[False][0]))
