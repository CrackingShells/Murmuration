# Lists, in one PI main-thread transcript, the records of type user/queue-operation/attachment (not assistant) whose text names a given agent, with timestamp, type, origin kind and the first 200 characters; inputs: transcript path, agent name; output on stdout. Used to locate the wake of an escalation that w09d_turns.parse did not attribute to the verifier.
# usage: python3 -I w09h_find_mentions.py <transcript.jsonl> <agent-name>
import sys, json
path, name = sys.argv[1], sys.argv[2]
for i, line in enumerate(open(path, encoding="utf-8", errors="replace")):
    if name not in line or line.startswith('{"type":"api-request'): continue
    try: r = json.loads(line)
    except ValueError: continue
    t = r.get("type")
    if t == "assistant": continue
    m = r.get("message") or {}
    c = m.get("content") if isinstance(m, dict) else None
    if isinstance(c, list):
        s = " ".join(b.get("text", "") if isinstance(b, dict) and b.get("type") == "text" else (str(b.get("content"))[:300] if isinstance(b, dict) else str(b)) for b in c)
    elif isinstance(c, str): s = c
    else: s = json.dumps(r.get("attachment") or r.get("content") or r)[:600]
    o = r.get("origin"); k = o.get("kind") if isinstance(o, dict) else o
    j = s.find(name)
    print(i, r.get("timestamp"), t, k, len(s), repr(s[max(0, j - 60):j + 140]))
