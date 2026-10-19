import json, re
f = "/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/566fa912-7009-421a-9d79-11145e2b8db9.jsonl"
for l in open(f):
    if "side-sessions-event" not in l: continue
    r = json.loads(l)
    if r.get("type") != "user": continue
    c = r["message"]["content"]; t = c if isinstance(c, str) else "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    m = re.match(r"\s*(<system-reminder>\n.*?\n</system-reminder>\s*)*<side-sessions-event>", t, re.S)
    print(r["uuid"][:8], "origin", r.get("origin"), r.get("turnOrigin"), "lead" if m else "-", "starts:", t[:25].replace("\n", " "), "len", len(t))
