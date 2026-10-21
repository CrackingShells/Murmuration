# Tabulates, for each transcript JSONL given, the user records that carry a string/text prompt: (promptSource, turnOrigin, entrypoint, kind of leading text) with counts and one example start; inputs: transcript paths; output: stdout table.
import json, sys, collections, re
def kind(text):
    t = re.sub(r"\A\s*(?:<system-reminder>\n.*?\n</system-reminder>\s*)+", "", text, flags=re.S)
    for p in ("<cross-session-message", "<task-notification>", "<agent-message", "<command-name>", "<local-command", "<side-sessions-event>", "<artifact-view-context", "<pasted_content"):
        if t.startswith(p): return p
    return "text"
summary = sys.argv[1] == '--summary'
args = sys.argv[2:] if summary else sys.argv[1:]
total = collections.Counter(); first = {}
for path in args:
    cnt = collections.Counter(); ex = {}
    for line in open(path, errors="replace"):
        try: d = json.loads(line)
        except ValueError: continue
        if d.get("type") != "user" or "toolUseResult" in d or d.get("sourceToolAssistantUUID"): continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list):
            c = " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
            if not c: continue
        if not isinstance(c, str): continue
        o = d.get("origin"); ok = o.get("kind") if isinstance(o, dict) else o
        if summary:
            sk = (d.get("promptSource"), d.get("turnOrigin"), ok, d.get("isMeta"), kind(c)); total[sk] += 1; first.setdefault(sk, (path.split("/")[-1][:8], d.get("timestamp"), d.get("version"), re.sub(r"\s+", " ", c)[:70])); continue
        key = (d.get("promptSource"), d.get("turnOrigin"), d.get("entrypoint"), d.get("isMeta"), d.get("origin") and json.dumps(d.get("origin"))[:60], kind(c), (d.get("turnPosition") or {}).get("promptIndex") == 0)
        cnt[key] += 1; ex.setdefault(key, (d.get("timestamp"), re.sub(r"\s+", " ", c)[:90]))
    if not summary:
        print("==", path.split("/")[-1], sum(cnt.values()))
        for k, n in cnt.most_common(): print(n, k, ex[k])
if summary:
    print("(promptSource, turnOrigin, origin.kind, isMeta, leading kind) -> count, first example (session, time, version, text)")
    for k, n in total.most_common(): print(n, k, first[k])
