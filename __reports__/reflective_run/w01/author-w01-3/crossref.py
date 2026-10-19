#!/usr/bin/env python3
"""Claim w01-c3, check X1: token-level agreement of lab_spend.py with (a) cost-state, cell by cell (validate_cells.csv),
(b) explorer-w01-a's independent deduplication (crosschecks.csv, columns mine_*). Run after validate.py. python3 -I crossref.py"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
cells = list(csv.DictReader(open(os.path.join(HERE, "validate_cells.csv"))))
print("(a) lab_spend.py vs cost-state, %d session x model cells" % len(cells))
for f_cs, f_tr, name in (("cs_in", "tr_in", "input"), ("cs_cr", "tr_cr", "cache read"), ("cs_cw", "tr_cw", "cache write"), ("cs_out", "tr_out", "output")):
    eq = sum(1 for c in cells if c[f_cs] == c[f_tr])
    nonzero = sum(1 for c in cells if int(c[f_cs]) > 0)
    print("   %-11s equal in %d of %d cells (cs count > 0 in %d)" % (name, eq, len(cells), nonzero))
bad = [c for c in cells if c["cs_in"] != c["tr_in"] or c["cs_cr"] != c["tr_cr"] or c["cs_cw"] != c["tr_cw"]]
print("   cells where input/cache differ:", [(c["session"], c["model"], c["cs_in"], c["tr_in"], c["cs_cr"], c["tr_cr"]) for c in bad])
print("(b) vs explorer-w01-a mine_* (crosschecks.csv)")
A = os.path.join(HERE, "..", "explorer-w01-a", "crosschecks.csv")
by = {(c["session"], c["model"]): c for c in cells}
for r in csv.DictReader(open(A)):
    if r["check"] != "cost-state vs transcripts":
        continue
    c = by.get((r["session"], r["model"]))
    if not c:
        print("   no cell", r["session"], r["model"]); continue
    same = all(str(r[a]) == str(c[b]) for a, b in (("mine_in", "tr_in"), ("mine_out", "tr_out"), ("mine_cr", "tr_cr"), ("mine_cw", "tr_cw")))
    print("   %s %-18s explorer-a == lab_spend on all four token fields: %s" % (r["session"], r["model"], same))
