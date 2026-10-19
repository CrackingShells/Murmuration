import json, re, sys, datetime, statistics
H = "/Users/hacker/.claude/projects/"
SESS = {
 "this": H+"-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl",
 "genesis": H+"-Users-hacker-Documents-explore-combinatorics-on-binary/566fa912-7009-421a-9d79-11145e2b8db9.jsonl",
 "design": H+"-Users-hacker-Documents-explore-combinatorics-on-binary/82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl",
 "3ccc": H+"-Users-hacker-Documents-explore-combinatorics-on-binary/3ccc590f-0187-4f79-b7af-4955944f1374.jsonl",
}
UNTIL = sys.argv[1] if len(sys.argv) > 1 else "2026-10-19T02:24:30Z"
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
U = ts(UNTIL)
NOTE = re.compile(r"<task-notification>.*?</task-notification>", re.S)
GLOBAL=set()
for name, f in SESS.items():
    recs = []
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        t = d.get("timestamp")
        if not t: continue
        recs.append((ts(t), d))
    recs.sort(key=lambda x: x[0])
    # tool_use ids of Agent launches, main thread only
    agent_ids = set(); asst = []
    for t, d in recs:
        if d.get("isSidechain"): continue
        if d.get("type") == "assistant":
            asst.append(t)
            c = d.get("message", {}).get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Agent", "Task"):
                        agent_ids.add(b["id"])
    aid = set()
    for t, d in recs:
        if d.get("isSidechain") or d.get("type") != "user": continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in agent_ids:
                    x = b.get("content")
                    x = x if isinstance(x, str) else " ".join(i.get("text", "") for i in x if isinstance(i, dict))
                    aid.update(re.findall(r"agentId: (\w+)", x))
    seen = {}
    for t, d in recs:
        if d.get("isSidechain") or t > U: continue
        s = json.dumps(d, ensure_ascii=False)
        s = s.encode().decode("unicode_escape", "ignore") if False else json.dumps(d)
        raw = json.dumps(d, ensure_ascii=False)
        if "task-notification>" not in raw: continue
        # extract from any string in record
        txts = []
        def walk(o):
            if isinstance(o, str): txts.append(o)
            elif isinstance(o, dict): [walk(v) for v in o.values()]
            elif isinstance(o, list): [walk(v) for v in o]
        walk(d)
        for x in txts:
            for m in NOTE.findall(x):
                if m not in seen: seen[m] = t
    rows = []
    for m, t in seen.items():
        tu = re.search(r"<tool-use-id>(.*?)</tool-use-id>", m)
        tid = re.search(r"<task-id>(.*?)</task-id>", m)
        is_agent = bool((tu and tu.group(1) in agent_ids) or (tid and tid.group(1) in aid))
        nxt = [a for a in asst if t < a <= U]
        lat = (nxt[0] - t) if nxt else None
        rows.append((t, tid.group(1) if tid else None, is_agent, lat))
    w = [r for r in rows if r[2] and (r[1], round(r[0],1)) not in GLOBAL]
    GLOBAL.update((r[1], round(r[0],1)) for r in rows if r[2])  # fork dedupe: count an inherited notice only in the earliest session
    lats = sorted(r[3] for r in w if r[3] is not None)
    nolat = sum(1 for r in w if r[3] is None)
    print(name, "all notices", len(rows), "worker", len(w), "no reaction in snapshot", nolat,
          "median %.1f" % statistics.median(lats) if lats else "", "max %.1f" % max(lats) if lats else "",
          "over300", sum(1 for x in lats if x > 300), "over60", sum(1 for x in lats if x > 60))
    if "-v" in sys.argv: [print("  ", datetime.datetime.fromtimestamp(r[0], datetime.timezone.utc).isoformat(), r[1], r[2], r[3]) for r in sorted(rows)]
