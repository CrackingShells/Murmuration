"""print a transcript compactly: record type, role, block kinds, and text snippets; flag CANARY / BUDGET marks"""
import json, sys, glob, os
pat = sys.argv[2] if len(sys.argv) > 2 else "CANARY"
def show(path):
    print("=====", path.split("/projects/")[-1][-90:])
    for i, l in enumerate(open(path)):
        try: r = json.loads(l)
        except Exception: continue
        t = r.get("type"); m = r.get("message") or {}
        c = m.get("content") if isinstance(m, dict) else None
        att = r.get("attachment")
        desc = []
        if att: desc.append("ATTACH:" + json.dumps(att)[:300])
        if isinstance(c, str): desc.append("str:" + c[:200].replace("\n", "\\n"))
        elif isinstance(c, list):
            for b in c:
                k = b.get("type")
                if k == "text": desc.append("text:" + b["text"][:200].replace("\n", "\\n"))
                elif k == "tool_use": desc.append("tool_use:" + json.dumps(b.get("input"))[:100])
                elif k == "tool_result": desc.append("tool_result:" + json.dumps(b.get("content"))[:200])
                else: desc.append(k)
        flag = "***" if pat in l else "   "
        print(flag, i, t, m.get("role") if isinstance(m, dict) else None, r.get("isSidechain"), " | ".join(desc)[:420])
proj = os.path.expanduser("~/.claude/projects")
d = [x for x in glob.glob(proj + "/*") if sys.argv[1] in x][0]
for f in sorted(glob.glob(d + "/*.jsonl")) + sorted(glob.glob(d + "/*/subagents/*.jsonl")): show(f)
