#!/usr/bin/env python3
"""Claim w01-c3, checks C1-C3: what the human sees from scripts/lab_status.py (v6) and from lab_spend.py on
(i) this run, from the worktree and from the main checkout, (ii) the combinatorics project.

This run's transcripts keep growing, so the project folders are first copied to a temporary configuration
directory and both programs read that copy (CLAUDE_CONFIG_DIR): same bytes, no drift between the two readings.
Imports scripts/lab_status.py read-only. Writes compare.csv and compare.txt. Run: python3 -I compare.py [--quick]
--quick: only the combinatorics case."""
import collections, csv, datetime, os, shutil, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(REPO, "scripts"))
import lab_spend as L
import lab_status as V6

MAIN = "/Users/hacker/Documents/src/CrackingShells/Murmuration"
COMB = "/Users/hacker/Documents/explore/combinatorics_on_binary"
cases = [("(i-a) this run, from the worktree", REPO), ("(i-b) this run, from the main checkout", MAIN),
         ("(ii) combinatorics project", COMB)]
if "--quick" in sys.argv:
    cases = cases[2:]

real = os.path.join(os.path.expanduser("~"), ".claude", "projects")
snap = tempfile.mkdtemp(prefix="w01c3-")
prefixes = tuple(L.encode(p) for p in (REPO, MAIN, COMB))
t0 = datetime.datetime.now()
n = 0
for e in sorted(os.listdir(real)):
    if e.startswith(prefixes):
        shutil.copytree(os.path.join(real, e), os.path.join(snap, "projects", e)); n += 1
os.environ["CLAUDE_CONFIG_DIR"] = snap
txt = ["compare.py: %d project folders frozen at %s into a temporary configuration directory\n" % (n, t0.strftime("%Y-%m-%d %H:%M:%S"))]
rows = []
for name, root in cases:
    txt.append("=" * 100 + "\n%s   root=%s\n" % (name, root))
    v6_rows, v6_folders, v6_warn = V6.spend(root)
    v6 = collections.Counter()
    for r in v6_rows:
        for k in ("messages", "input", "cache_write", "cache_read", "output"):
            v6[k] += r[k]
    txt.append("---- v6 (scripts/lab_status.py), Spend section verbatim:\n" + "\n".join(V6.report_spend(root)) + "\n")
    text, summ = L.report(root)
    txt.append("---- lab_spend.py (prototype), Spend section verbatim:\n" + text + "\n")
    sessions, stats, warns = L.load(L.find_scan(root))
    def tot(sel):
        c = collections.Counter()
        for s in sel:
            for r in s["rows"].values():
                for k, kk in (("msgs", "messages"), ("in", "input"), ("cw", "cache_write"), ("cr", "cache_read"), ("out", "output")):
                    c[kk] += r[k]
        return c
    mine_all = tot(sessions)
    same = [s for s in sessions if os.path.dirname(s["path"]) in v6_folders]   # the sessions v6 could see
    mine_same = tot(same)
    ratio = lambda a, b, k: round(a[k] / b[k], 3) if b[k] else ""
    rows.append({"case": name, "v6_folders": len(v6_folders), "v6_sessions_seen": len(same),
                 "mine_sessions": len(sessions),
                 "v6_messages": v6["messages"], "v6_input": v6["input"], "v6_cache_write": v6["cache_write"],
                 "v6_cache_read": v6["cache_read"], "v6_output": v6["output"],
                 "mine_same_messages": mine_same["messages"], "mine_same_input": mine_same["input"],
                 "mine_same_cache_write": mine_same["cache_write"], "mine_same_cache_read": mine_same["cache_read"],
                 "mine_same_output": mine_same["output"],
                 "v6_over_mine_same_cache_write": ratio(v6, mine_same, "cache_write"),
                 "v6_over_mine_same_cache_read": ratio(v6, mine_same, "cache_read"),
                 "v6_over_mine_same_output": ratio(v6, mine_same, "output"),
                 "mine_all_messages": mine_all["messages"], "mine_all_cache_write": mine_all["cache_write"],
                 "mine_usd_low": round(summ.get("low", 0), 2), "mine_usd_high": round(summ.get("high", 0), 2),
                 "mine_usd_exact_part": round(summ.get("exact", 0), 2)})
shutil.rmtree(snap)
suffix = "_quick" if "--quick" in sys.argv else ""
with open(os.path.join(HERE, "compare%s.txt" % suffix), "w") as fh:
    fh.write("\n".join(txt))
with open(os.path.join(HERE, "compare%s.csv" % suffix), "w", newline="") as fh:
    w = csv.DictWriter(fh, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows:
    print(r["case"]); [print("   ", k, v) for k, v in r.items() if k != "case"]
