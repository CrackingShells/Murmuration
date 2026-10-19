import json
f = "/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl"
for l in open(f):
    r = json.loads(l)
    if r.get("uuid", "").startswith("78493c89"):
        a = r["attachment"]; print({k: (v if k != "prompt" else v[:50]) for k, v in a.items() if k != "usage"})
