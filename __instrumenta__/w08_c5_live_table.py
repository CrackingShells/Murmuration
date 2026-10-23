# Summarizes the live sessions of w08_c5_live_payloads.py without printing a raw payload value: (1) the keys of each hook event; (2) for each SubagentStart field, in how many of the same session's PreToolUse(Agent) payloads its value occurs (a field that occurs in 1 of N, or whose value differs per dispatch, could tie a start to its dispatch; one that occurs in all N or in none cannot) and whether it occurs in the PostToolUse answer; (3) per run, the arrival order of the events and, with a lab harness.jsonl, each start line's name against the name the same agent's `end` line carries (read from its meta/brief, independent of the pairing), and the path in each worker's start note.
# usage: python3 -I w08_c5_live_table.py S RUN [RUN ...] > table.md      (S: the scratch folder given to w08_c5_live_payloads.py)
import glob, json, os, re, sys
S, runs = sys.argv[1], sys.argv[2:]
print("## Keys of each hook event\n\n| run | event | keys |\n|:--|:--|:--|")
tot = {}
for run in runs:
    ev = [json.loads(l) for l in open(os.path.join(S, "live", run, "events.jsonl"))]
    seen = {}
    for e in ev:
        p = e["payload"]
        seen.setdefault(p["hook_event_name"], set(p))
    for k in ("PreToolUse", "PostToolUse", "SubagentStart", "SubagentStop"):
        print("| %s | %s | %s |" % (run, k, ", ".join(sorted(seen.get(k, [])))))
    pres = [e["payload"] for e in ev if e["payload"]["hook_event_name"] == "PreToolUse"]
    posts = [e["payload"] for e in ev if e["payload"]["hook_event_name"] == "PostToolUse"]
    for e in ev:
        p = e["payload"]
        if p["hook_event_name"] != "SubagentStart":
            continue
        for f, v in p.items():
            if f == "hook_event_name":
                continue
            inpre = sum(1 for q in pres if json.dumps(v) in json.dumps(q))
            inpost = sum(1 for q in posts if json.dumps(v) in json.dumps(q))
            t = tot.setdefault(f, [0, 0, 0, 0, set()])
            t[0] += 1; t[1] += inpre; t[2] += inpost; t[3] += len(pres); t[4].add(run)
print("\n## SubagentStart fields against the dispatch payloads of the same session\n\n| field | starts | value found in PreToolUse payloads (sum over starts) | of possible | found in PostToolUse answers (sum) |\n|:--|--:|--:|--:|--:|")
for f, t in sorted(tot.items()):
    print("| %s | %d | %d | %d | %d |" % (f, t[0], t[1], t[3], t[2]))
print("\n## Runs\n\n| run | event order (P pre, A answer, S start, E stop) | start lines | start lines with name_unconfirmed | start names that differ from the end line's name | `named` lines | note path correct |\n|:--|:--|--:|--:|--:|--:|:--|")
for run in runs:
    ev = [json.loads(l) for l in open(os.path.join(S, "live", run, "events.jsonl"))]
    order = "".join({"PreToolUse": "P", "PostToolUse": "A", "SubagentStart": "S", "SubagentStop": "E"}[e["payload"]["hook_event_name"]] for e in sorted(ev, key=lambda e: e["arrive"]))
    hj = os.path.join(S, "live", run, "lab", "__statera__", "harness.jsonl")
    if not os.path.exists(hj):
        print("| %s | %s | n/a | n/a | n/a | n/a | n/a |" % (run, order)); continue
    rows = [json.loads(l) for l in open(hj)]
    starts = [r for r in rows if r["event"] == "start"]
    end = {r["agent_id"]: r["name"] for r in rows if r["event"] == "end"}
    wrong = sum(1 for r in starts if not r.get("name_unconfirmed") and r["name"] != end.get(r["agent_id"]))
    lab = os.path.join(S, "live", run, "lab")
    proj = os.path.expanduser("~/.claude/projects/") + re.sub(r"[^A-Za-z0-9]", "-", lab) + "/*/subagents/agent-*.jsonl"
    fs = glob.glob(proj)
    ok = sum(1 for f in fs if re.search(r'paths: \[[\\\\"]*%s/__instrumenta__' % re.escape(lab), open(f).read()))
    print("| %s | %s | %d | %d | %d | %d | %d of %d workers |" % (run, order, len(starts), sum(1 for r in starts if r.get("name_unconfirmed")), wrong, sum(1 for r in rows if r["event"] == "named"), ok, len(fs)))
