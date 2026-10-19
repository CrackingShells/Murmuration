import json, glob, re
D = "/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/"
THIS = "/Users/hacker/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl"
for f in sorted(glob.glob(D + "*.jsonl")) + [THIS]:
    n = lead = inreminder = 0
    for l in open(f):
        if "side-sessions-event" not in l: continue
        r = json.loads(l); n += 1
        if r.get("type") == "user":
            c = r["message"]["content"]
            t = c if isinstance(c, str) else "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
            if re.match(r"\s*(<system-reminder>\n.*?\n</system-reminder>\s*)*<side-sessions-event>", t, re.S): lead += 1
        print(f[-14:-6], r.get("type"), "leading-in-user-text" if lead else "", end=" | ")
    print("\n", f[-14:-6], "records mentioning:", n, "as leading block of a user text:", lead)
