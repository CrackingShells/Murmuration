"""Checks of the patched scripts/lab_status.py spend section against Claude Code's own cost-state (claim w02-c1).

    python3 -I check.py [--quick]

Read-only; standard library; no model calls; no randomness. The reader under test is imported from the
shipped script; every comparison value comes from `cost-state` records read here, or from a second
reader written here (the detector by requestId, as defined by the w01-c2 claim)."""
import collections
import glob
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts", "lab_status.py"))
WT = os.path.dirname(os.path.dirname(SCRIPT))
MAIN = "/Users/hacker/Documents/src/CrackingShells/Murmuration"
COMB = "/Users/hacker/Documents/explore/combinatorics_on_binary"
QUICK = "--quick" in sys.argv

spec = importlib.util.spec_from_file_location("lab_status", SCRIPT)
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)


def sessions_of(root):
    return ls.find_sessions(ls.lab_roots(root))


def cost_state_of(path):
    last = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"cost-state"' in line:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("type") == "cost-state":
                    last = rec
    return last


# ---- 1. combinatorics: the four sessions' cost-state totals against the script's TOTAL
comb = sessions_of(COMB)
cs_total = sum(cost_state_of(p)["totalCostUSD"] for p in comb)
text = "\n".join(ls.report_spend(COMB))
m = re.search(r"TOTAL  USD ([0-9.]+)", text)
print("1. combinatorics: %d sessions; sum of cost-state totalCostUSD %.4f; script TOTAL %s; equal to the cent: %s"
      % (len(comb), cs_total, m.group(1), abs(float(m.group(1)) - cs_total) < 0.005))

# ---- 2. the same, for every ended session found for this lab (worktree and main checkout give the same set)
lab_a, lab_b = sessions_of(WT), sessions_of(MAIN)
print("2. discovery: from the worktree %d sessions, from the main checkout %d, same set: %s"
      % (len(lab_a), len(lab_b), sorted(lab_a) == sorted(lab_b)))
ended = [p for p in lab_a if cost_state_of(p)]
if QUICK:
    ended = ended[:40]
print("   ended sessions (with a cost-state record): %d of %d%s" % (len(ended), len(lab_a), " (quick: first 40)" if QUICK else ""))

# ---- 3. cell by cell (session x model): list-price USD and output tokens against cost-state's own numbers,
#         split by the detector (does the cell hold a subagent request whose last record has no stop_reason?)
warns = []
sess, copies = ls.load_sessions(comb + ended, warns)
by_path = {s["path"]: s for s in sess}
cells = []  # (detector_says_exact, usd_ratio, output_equal, cost_state_output, tr_output, helper_only)
for p in comb + ended:
    cs = cost_state_of(p)
    s = by_path[p]
    per_model = collections.defaultdict(collections.Counter)
    for (label, model), r in s["rows"].items():
        per_model[model].update(r)
    for model, mu in (cs.get("modelUsage") or {}).items():
        r = per_model.get(model, collections.Counter())
        cells.append({"exact": r["lower"] == 0, "msgs": r["msgs"], "usd": r["usd"], "cs_usd": mu["costUSD"],
                      "out": r["output"], "cs_out": mu["outputTokens"], "model": model, "cs_in": mu["inputTokens"]})
priced = [c for c in cells if c["msgs"] > 0 and c["cs_usd"] > 0.0005]
tab = collections.Counter()
for c in priced:
    ratio_ok = abs(c["usd"] / c["cs_usd"] - 1) <= 0.0005
    out_ok = c["out"] == c["cs_out"]
    tab[(c["exact"], ratio_ok, out_ok)] += 1
print("3. %d cells (session x model) with a transcript message and cost-state USD above 0.0005 (of %d cells in cost-state)"
      % (len(priced), len(cells)))
print("   detector says exact (no `+`) / USD within 0.05% of cost-state / output tokens equal  -> cells")
for k in sorted(tab, reverse=True):
    print("   %-5s / %-5s / %-5s -> %d" % (k + (tab[k],)))
bad = [c for c in priced if c["exact"] and abs(c["usd"] / c["cs_usd"] - 1) > 0.0005]
print("   cells the detector calls exact whose USD is off by more than 0.05%%: %d" % len(bad))
for c in bad[:8]:
    print("     %s transcript %.4f cost-state %.4f (msgs %d, out %d vs %d, cost-state input %d)"
          % (c["model"], c["usd"], c["cs_usd"], c["msgs"], c["out"], c["cs_out"], c["cs_in"]))
flagged = [c for c in priced if not c["exact"]]
print("   cells with `+`: %d; their transcript USD / cost-state USD: min %.3f max %.3f; any above 1.0: %d"
      % (len(flagged), min(c["usd"] / c["cs_usd"] for c in flagged), max(c["usd"] / c["cs_usd"] for c in flagged),
         sum(c["usd"] > c["cs_usd"] * 1.0005 for c in flagged)))

# ---- 4. the detector, a second implementation: group records of each subagent file by requestId, take the last
#         record of each, call the file exact when all have a stop_reason. Against the script's per-agent `+`.
def detector_by_request(path):
    last = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"assistant"' not in line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            m = rec.get("message") if isinstance(rec, dict) else None
            if rec.get("type") == "assistant" and isinstance(m, dict) and isinstance(m.get("usage"), dict) \
                    and m.get("model") != "<synthetic>":
                last[rec.get("requestId") or m.get("id")] = bool(m.get("stop_reason"))
    return all(last.values()) if last else None


agree = collections.Counter()
files = []
for p in comb + ended:
    files += sorted(glob.glob(os.path.join(p[:-len(".jsonl")], "subagents", "**", "agent-*.jsonl"), recursive=True))
if QUICK:
    files = files[:150]
for f in files:
    mine = ls.read_transcript(f, [])[0]
    mine_exact = all(m["final"] for m in mine.values()) if mine else None
    agree[(detector_by_request(f), mine_exact)] += 1
print("4. %d subagent files: (exact by requestId, exact by message id) -> files: %s" % (len(files), dict(agree)))
print("   disagreements: %d" % sum(n for (a, b), n in agree.items() if a != b))

# ---- 5. falsifiers
# F1: counting each file alone (no ownership by sessionId) double counts copies
per_file = 0.0
for p in comb:
    fs = [p] + sorted(glob.glob(os.path.join(p[:-len(".jsonl")], "subagents", "**", "agent-*.jsonl"), recursive=True))
    for f in fs:
        for m in ls.read_transcript(f, [])[0].values():
            per_file += ls.message_usd(m["model"], m["usage"]) or 0.0
owned = sum(r["usd"] for s in ls.load_sessions(comb, [])[0] for r in s["rows"].values())
print("5. F1 combinatorics list-price USD: per-file counting %.2f, owned by sessionId %.2f, cost-state %.2f"
      % (per_file, owned, cs_total))
# F2: a price table other than cost-state's moves the ratios off 1.000
saved = dict(ls.PRICES)
ls.PRICES["claude-opus-5-5"] = (5.0, 25.0, 0.50, 6.25, 10.0)  # the Opus 5 row (assumed): $5/$25
sessions_alt, _ = ls.load_sessions(comb[:1], [])
alt = sum(r["usd"] for s in sessions_alt for (l, mod), r in s["rows"].items() if "opus" in mod and "main" in l)
ls.PRICES.update(saved)
base_sessions, _ = ls.load_sessions(comb[:1], [])
base = sum(r["usd"] for s in base_sessions for (l, mod), r in s["rows"].items() if "opus" in mod and "main" in l)
print("   F2 first combinatorics session, Opus main-thread cell: table %.2f, with an Opus row of $5/$25 %.2f (x%.2f)"
      % (base, alt, alt / base if base else 0))
