# Prints, from one PI main-thread transcript, the hand-back or queued record at a given line and then the PI's assistant text blocks and tool-call heads (first 160 characters of each command or path) over the next N lines; inputs: transcript path, start line (0-based, as printed by w09h_find_mentions.py), N; output on stdout.
# usage: python3 -I w09h_pi_after.py <transcript.jsonl> <start-line> <N> [maxchars-of-record]
import sys, json
path, start, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 6000
for i, line in enumerate(open(path, encoding="utf-8", errors="replace")):
    if i < start: continue
    if i >= start + n: break
    if line.startswith('{"type":"api-request'): continue
    try: r = json.loads(line)
    except ValueError: continue
    t = r.get("type")
    if i == start:
        print("== RECORD", i, t, r.get("timestamp")); print(line[:mx]); continue
    if t == "assistant":
        for b in (r.get("message") or {}).get("content") or []:
            if b.get("type") == "text": print("[%d %s PI text] %s" % (i, r.get("timestamp"), b["text"][:1500]))
            elif b.get("type") == "tool_use":
                inp = b.get("input") or {}
                print("[%d tool %s] %s" % (i, b["name"], (inp.get("command") or inp.get("file_path") or inp.get("to") or inp.get("description") or "")[:160].replace("\n", " ")))
    elif t == "user" and isinstance((r.get("message") or {}).get("content"), str):
        print("[%d user-str %s] %s" % (i, r.get("timestamp"), r["message"]["content"][:200].replace("\n", " ")))
