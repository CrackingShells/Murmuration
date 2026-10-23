# w08-c10: compares two decision files of w08j_replay.py (before, after) on the frozen set of explorer-w08-j; inputs: the frozen set JSON, before.jsonl, after.jsonl; output: markdown on stdout: per implementation the cases whose decision changed (id, label, source, before, after, the command's first 150 characters), counts of newly denied by label, newly allowed (must be 0), and python-equals-rust on both files.
# usage: python3 -I w08_c10_compare_frozen.py SET.json BEFORE.jsonl AFTER.jsonl [--show N]
import json, sys

cases = {c["id"]: c for c in json.load(open(sys.argv[1]))["cases"]}
load = lambda p: {json.loads(l)["id"]: json.loads(l) for l in open(p) if l.strip()}
before, after = load(sys.argv[2]), load(sys.argv[3])
for impl in ("py", "rs"):
    newly_denied = [i for i in cases if not before[i][impl] and after[i][impl]]
    newly_allowed = [i for i in cases if before[i][impl] and not after[i][impl]]
    regroup = [i for i in cases if before[i][impl] and after[i][impl] and before[i][impl] != after[i][impl]]
    by = {}
    for i in newly_denied:
        by[cases[i]["label"]] = by.get(cases[i]["label"], 0) + 1
    print("## %s: newly denied %d (by label %s), newly allowed %d, denied by another rule group %d" % (impl, len(newly_denied), by, len(newly_allowed), len(regroup)))
    for i in newly_denied + newly_allowed + regroup:
        c = cases[i]
        cmd = c["input"].get("command") or c["input"].get("file_path") or ""
        print("- %s label=%s indirect=%s source=%s %s -> %s | %s" % (i, c["label"], c["indirect"], c["source"], before[i][impl], after[i][impl], cmd[:150].replace("\n", "\\n")))
for name, d in (("before", before), ("after", after)):
    print("%s: python and rust agree on %d of %d" % (name, sum(1 for r in d.values() if r["py"] == r["rs"]), len(d)))
true_allowed = lambda d, impl: sum(1 for i, c in cases.items() if c["label"] == "true" and not d[i][impl])
false_denied = lambda d, impl: sum(1 for i, c in cases.items() if c["label"] == "false" and d[i][impl])
for impl in ("py", "rs"):
    print("%s: true cases allowed %d -> %d; false cases denied %d -> %d" % (impl, true_allowed(before, impl), true_allowed(after, impl), false_denied(before, impl), false_denied(after, impl)))
