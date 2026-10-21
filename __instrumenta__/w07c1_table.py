#!/usr/bin/env python3
"""Tabulates the w07c1 cells: reads <scratch>/runs/*/summary.json and each cell's session transcript (~/.claude/projects/*/<session>.jsonl) and prints markdown tables (request 0 tokens, deferred-name count, skill_listing presence, model requests, Reads and failed Reads, answer check for p2) plus the p1 pair differences; input: scratch dir [and an output dir to copy the cell summaries to]; output: stdout.
Read-only on transcripts; prints no credentials."""
import glob, json, os, re, shutil, sys
S = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else None
rows = {}
for d in sorted(glob.glob(os.path.join(S, "runs", "*"))):
    try: sm = json.load(open(os.path.join(d, "summary.json")))
    except Exception: continue
    fs = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sm["session_id"]))
    dn = 0; dch = 0; sl = 0; slc = 0
    if fs:
        for l in open(fs[0]):
            r = json.loads(l)
            if r.get("type") == "attachment":
                a = r["attachment"]
                if a.get("type") == "deferred_tools_delta": dn += len(a.get("addedNames", [])); dch += sum(len(n) + 1 for n in a.get("addedNames", []))
                if a.get("type") == "skill_listing": sl = a.get("skillCount"); slc = len(a.get("content", ""))
            if r.get("type") == "assistant": break
    f = sm["final"]
    ok = ("USD 3" in f and "Wave NN" in f) if sm["prompt"] == "p2" else None
    rd = [os.path.relpath(p, os.path.join(S, "runs", sm["cell"], "plugin")) if p and p.startswith(S) else p for p, _ in sm["reads"]]
    rows[sm["cell"]] = dict(sm=sm, dn=dn, dch=dch, sl=sl, slc=slc, ok=ok, rd=rd)
    if out:
        os.makedirs(os.path.join(out, "cells", sm["cell"]), exist_ok=True)
        shutil.copy(os.path.join(d, "summary.json"), os.path.join(out, "cells", sm["cell"], "summary.json"))
print("| cell | prompt | req0 tokens | deferred names | deferred chars | listing skills | listing chars | model requests | Reads (failed) | final answer (first 90 chars) |")
print("|:--|:--|--:|--:|--:|--:|--:|--:|:--|:--|")
for c, v in rows.items():
    sm = v["sm"]
    print("| %s | %s | %d | %d | %d | %s | %s | %d | %s (%d) | %s |" % (c, sm["prompt"], sm["req0_total"], v["dn"], v["dch"], v["sl"], v["slc"], sm["n_requests"], "; ".join(v["rd"]).replace("|", "/"), sm["reads_failed"], sm["final"][:90].replace("\n", " ").replace("|", "/")))
print("\nPairs (p1): A request 0 - B request 0 (rule: >= 9000 in each pair)")
for n in (1, 2, 3):
    if "A%d" % n not in rows or "B%d" % n not in rows: continue
    A = rows["A%d" % n]; B = rows["B%d" % n]
    print("- pair %d: A%d %d (deferred %d), B%d %d (deferred %d), drop %d" % (n, n, A["sm"]["req0_total"], A["dn"], n, B["sm"]["req0_total"], B["dn"], A["sm"]["req0_total"] - B["sm"]["req0_total"]))
print("\nExtra cells, outside the v0 rule:")
for b in ("V1_1", "V1_2", "V1_3"):
    for a_ in ("A4",):
        if a_ in rows and b in rows: print("- %s %d (deferred %d) vs %s %d (deferred %d): drop %d" % (a_, rows[a_]["sm"]["req0_total"], rows[a_]["dn"], b, rows[b]["sm"]["req0_total"], rows[b]["dn"], rows[a_]["sm"]["req0_total"] - rows[b]["sm"]["req0_total"]))
print("\np2 correct (budget and heading):", {c: v["ok"] for c, v in rows.items() if v["ok"] is not None})
