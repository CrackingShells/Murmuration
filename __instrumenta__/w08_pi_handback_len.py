# w08_pi_handback_len.py: characters of each SubagentHandback message per worker of one PI session, and whether its brief asked for a length; inputs: the session's subagents/*.jsonl and their .meta.json; output: TSV on stdout (name, brief_asks_length, handbacks, chars of each).
import json, sys, glob, os, re
sess = sys.argv[1]
rows = []
for f in sorted(glob.glob(os.path.join(sess, "subagents", "*.jsonl"))):
    brief, name, msgs = None, None, []
    for line in open(f, errors="replace"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        m = r.get("message") or {}
        c = m.get("content")
        if brief is None and r.get("type") == "user":
            brief = c if isinstance(c, str) else " ".join(b.get("text", "") for b in c or [] if isinstance(b, dict))
            g = re.search(r"Your name is ([a-z0-9-]+)", brief or "")
            name = g.group(1) if g else os.path.basename(f)
        if r.get("type") == "assistant" and isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                    msgs.append(len(str((b.get("input") or {}).get("message", ""))))
    if msgs:
        asks = bool(re.search(r"at most about [0-9,]+ characters", brief or ""))
        rows.append((name, asks, msgs))
print("name\tbrief_asks_length\thandbacks\tchars")
for n, a, m in rows:
    print("%s\t%s\t%d\t%s" % (n, a, len(m), ",".join(map(str, m))))
