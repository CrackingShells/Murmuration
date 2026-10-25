"""Lists every parent-session record that says a subagent stopped at its turn limit or ended without delivering its report (platform notices), with the agent id, time, whether the agent's own file shows a delivered SubagentHandback after it; reads ~/.claude/projects/*urmuration*/*.jsonl and their subagents/agent-*.jsonl (read only); writes a TSV to stdout."""
import json, glob, os, re
root = os.path.expanduser("~/.claude/projects")
print("\t".join("proj sess agent name atype notice_ts turn_limit no_report text_at_stop later_handback_delivered later_handback_ts file_end".split()))
seen = set()
for parent in sorted(glob.glob(root + "/*urmuration*/*.jsonl")):
    sess = os.path.basename(parent)[:-6]
    for l in open(parent, errors="replace"):
        if "without delivering" not in l and "-turn limit" not in l: continue
        try: r = json.loads(l)
        except Exception: continue
        if r.get("type") not in ("user", "queue-operation"): continue
        body = json.dumps(r.get("message") or r.get("content") or r)
        m = re.search(r"<task-id>([0-9a-z]+)</task-id>", body) or re.search(r"agentId: ([0-9a-z]+)", body)
        if not m: continue
        aid = m.group(1)
        key = (parent, aid, r.get("timestamp"), body[:60])
        if key in seen: continue
        seen.add(key)
        tl = bool(re.search(r"stopped at its \d+-turn limit", body)); nr = "without delivering" in body
        if not (tl or nr): continue
        pat = os.path.dirname(parent) + "/" + sess + "/subagents/agent-" + aid + "*.jsonl"
        fs = glob.glob(pat); later = ""; lts = ""; name = atype = ""; fend = ""
        if fs:
            try: mt = json.load(open(fs[0][:-6] + ".meta.json")); name = mt.get("name", ""); atype = mt.get("agentType", "")
            except Exception: pass
            recs = []
            for l2 in open(fs[0], errors="replace"):
                try: recs.append(json.loads(l2))
                except Exception: pass
            fend = [x["timestamp"] for x in recs if x.get("timestamp")][-1]
            for k, x in enumerate(recs):
                if x.get("type") == "assistant" and (x.get("timestamp") or "") > (r.get("timestamp") or "~"):
                    for b in x["message"].get("content") or []:
                        if isinstance(b, dict) and b.get("type") == "tool_use" and b["name"] == "SubagentHandback":
                            later = "yes"; lts = x["timestamp"]
        mm = re.search(r"stopped at its (\d+)-turn limit", body)
        print("\t".join([os.path.basename(os.path.dirname(parent))[-40:], sess[:8], aid[:8], name, atype, r.get("timestamp") or "", mm.group(1) if mm else "", "1" if nr else "0", "", later or "no", lts, fend]))
