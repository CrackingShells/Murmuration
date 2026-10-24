# w09-a: for each classifier refusal in classified.jsonl, finds the next calls of the same session (by timestamp) and records their decider, writing retry_pairs.jsonl (redacted text) and printing counts of what follows a refusal. Usage: python3 -I w09a_retry_pairs.py IN_DIR
import json, os, sys, collections
d = sys.argv[1]
rows = [json.loads(l) for l in open(os.path.join(d, "classified.jsonl"))]
by = collections.defaultdict(list)
for r in rows:
    by[r["session"]].append(r)
for v in by.values():
    v.sort(key=lambda r: r["ts"])
cnt = collections.Counter(); out = open(os.path.join(d, "retry_pairs.jsonl"), "w")
def txt(r):
    i = r.get("input") or {}
    return (i.get("command") or i.get("file_path") or json.dumps(i)) if isinstance(i, dict) else ""
for s, v in by.items():
    for k, r in enumerate(v):
        if r["decider"] != "classifier_block":
            continue
        nxt = [x for x in v[k + 1:k + 6] if x["tool"] == r["tool"]][:3]
        out.write(json.dumps({"block": {"id": r["id"], "tool": r["tool"], "text": txt(r)[:1500], "reason": r.get("reason")},
                              "next_same_tool": [{"id": x["id"], "decider": x["decider"], "text": txt(x)[:1500], "dt_s": None} for x in nxt]}) + "\n")
        cnt["blocks"] += 1
        cnt["followed_by_same_tool_call"] += bool(nxt)
        cnt["next_same_tool_allowed_by_classifier"] += bool(nxt and nxt[0]["decider"] == "classifier_allow")
        cnt["next_same_tool_no_decision_record"] += bool(nxt and nxt[0]["decider"] == "no_decision_record")
        cnt["next_same_tool_blocked_again"] += bool(nxt and nxt[0]["decider"] == "classifier_block")
print(dict(cnt))
