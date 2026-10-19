import json, sys, glob
D = "/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/"
for f in sorted(glob.glob(D + "*.jsonl")):
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("turnOrigin") == "scheduled" or (r.get("type") == "attachment" and "schedul" in json.dumps(r.get("attachment", {}).get("origin", ""))):
            print(f[-14:-6], r.get("type"), r.get("uuid", "")[:8], "isMeta", r.get("isMeta"), "side", r.get("isSidechain"), "origin", json.dumps(r.get("origin"))[:40], "keys-tool", "toolUseResult" in r, "sourceTool", "sourceToolUseID" in r)
