"""Classifies how each lab subagent transcript ended (live, turn limit, budget stop, interrupted, final text, other) and whether its parent session shows the hand-back as delivered; reads ~/.claude/projects/*urmuration*/*/subagents/agent-*.jsonl and their parent <session>.jsonl (read only); writes a TSV to stdout (args: pop = f | wide)."""
import json, glob, os, sys, time
root = os.path.expanduser("~/.claude/projects")
pop = sys.argv[1] if len(sys.argv) > 1 else "f"
def files():
    out = []
    for f in sorted(glob.glob(root + "/*/*/subagents/agent-*.jsonl")):
        p = f.split("/")[-4]
        if "urmuration" not in p: continue
        inf = ("Murmuration-murmuration-" in p) and ("---reports" not in p)
        if pop == "f" and not inf: continue
        if pop == "wide" and inf: continue
        out.append(f)
    return out
def short(x, n=200): return " ".join(str(x).split())[:n]
def analyse(f):
    recs = []
    for l in open(f, errors="replace"):
        try: recs.append(json.loads(l))
        except Exception: pass
    meta = {}
    try: meta = json.load(open(f[:-6] + ".meta.json"))
    except Exception: pass
    last_tool = None; hb = 0; tu = 0; hsc = 0; intr = 0
    for r in recs:
        if r.get("type") == "assistant":
            bl = r["message"].get("content") or []
            if any(isinstance(b, dict) and b.get("type") == "tool_use" for b in bl): tu += 1
            for b in bl:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    last_tool = b["name"]; hb += b["name"] == "SubagentHandback"
        if r.get("type") == "attachment" and (r.get("attachment") or {}).get("type") == "hook_stopped_continuation": hsc += 1
        if r.get("type") == "user" and "Request interrupted by user" in json.dumps(r.get("message")): intr += 1
    sig = [r for r in recs if r.get("type") in ("assistant", "user")]
    l = sig[-1]; c = l["message"]["content"]
    if l["type"] == "assistant":
        kinds = [b.get("type") for b in c if isinstance(b, dict)]
        fin = "A:%s:%s" % (l["message"].get("stop_reason"), ",".join(kinds))
    else:
        fin = "U:" + (c[0].get("type", "?") if isinstance(c, list) and c and isinstance(c[0], dict) else "str")
    ts = [r["timestamp"] for r in recs if r.get("timestamp")]
    age_min = (time.time() - os.path.getmtime(f)) / 60
    # parent evidence
    parent = os.path.dirname(os.path.dirname(f)) + ".jsonl"; ev = "no-parent-file"
    aid = os.path.basename(f)[6:-6]; tid = meta.get("toolUseId") or "@@"
    if os.path.exists(parent):
        ev = "no-trace"
        for l2 in open(parent, errors="replace"):
            if not (aid in l2 or tid in l2): continue
            try: r2 = json.loads(l2)
            except Exception: continue
            if r2.get("type") != "user": continue   # the parent's tool results and notifications, not its own prose
            body = json.dumps(r2.get("message"))
            if tid in body or aid in body:
                if "without delivering" in body: ev = "undelivered:platform-says-no-report"; break
                if "[Subagent hand-back]" in body: ev = "delivered:[Subagent hand-back]"; break
                if "task-notification" in body and "completed" in body: ev = "notified:completed"
                elif ev == "no-trace" and "Async agent launched" in body: ev = "async-launch-only"
    # result of the last SubagentHandback call, as the subagent's own transcript records it
    hbres = ""
    for k, r in enumerate(recs):
        if r.get("type") == "assistant":
            for b in r["message"].get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b["name"] == "SubagentHandback":
                    hid = b["id"]; hbres = "no-result"
                    for r2 in recs[k + 1:]:
                        for b2 in (r2.get("message") or {}).get("content") or []:
                            if isinstance(b2, dict) and b2.get("type") == "tool_result" and b2.get("tool_use_id") == hid:
                                t = json.dumps(b2.get("content")); hbres = "delivered" if "delivered to your caller" in t else ("denied-by-hook" if "hook error" in t else short(t, 60))
    # class
    if age_min < 10 and last_tool != "SubagentHandback": cl = "live"   # file written within the last 10 minutes of the run
    elif last_tool == "SubagentHandback" and l["type"] == "user": cl = "ended_on_handback_result"
    elif tu >= 150 and l["type"] == "user": cl = "turn_limit"   # 150 = maxTurns of agents/*.md; counted over the whole file, so a resumed agent can exceed it without being stopped
    elif hsc and l["type"] == "user": cl = "budget_stop"
    elif intr: cl = "interrupted"
    elif fin.startswith("A:end_turn") and hb: cl = "final_text_after_handback"
    elif fin.startswith("A:end_turn"): cl = "final_text"
    else: cl = "other"
    return dict(proj=f.split("/")[-4][-46:], sess=f.split("/")[-3][:8], agent=aid[:8], atype=meta.get("agentType", ""), name=meta.get("name", ""), last_tool=last_tool, hb=hb, tool_msgs=tu, n=len(recs), fin=fin, hsc=hsc, intr=intr, hbres=hbres, end=ts[-1] if ts else "", parent=ev, cls=cl)
if __name__ == "__main__":
    rows = [analyse(f) for f in files()]
    keys = list(rows[0].keys()); print("\t".join(keys))
    for r in rows:
        if r["last_tool"] != "SubagentHandback" or r["cls"] == "turn_limit" or "all" in sys.argv: print("\t".join(str(r[k]) for k in keys))
