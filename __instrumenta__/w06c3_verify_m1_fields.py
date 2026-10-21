# w06-c3 verifier: compares, field by field, what the resident server recorded (server.jsonl args) with the platform's own stdin (truth.jsonl) for each hook call in given truth-run directories; independent of the author's analyzer; inputs: run dirs; output: counts per event and any mismatch to stdout
import json, sys, collections
def load(p):
    return [json.loads(l) for l in open(p) if l.strip()]
tot = collections.Counter(); bad = collections.Counter(); empty = collections.defaultdict(collections.Counter)
for d in sys.argv[1:]:
    truth = load(d + "/truth.jsonl"); srv = load(d + "/server.jsonl")
    for s in srv:
        a = s["args"]; ev = a["event"]; hn = a.get("hook_event_name") or ev.split(":")[0]
        # candidate truth records: same hook event, same agent, same tool_use id/tool where known
        c = [t for t in truth if t.get("hook_event_name") == hn and (t.get("agent_id") or "") == (a.get("agent_id") or "")
             and (not a.get("tool_name") or t.get("tool_name") == a["tool_name"])
             and (not a.get("tool_use_id") or t.get("tool_use_id") == a["tool_use_id"])]
        if hn in ("PostToolUse", "PreToolUse") and ev.startswith(hn):
            tn = a.get("tool_name"); 
        ok = False
        for t in c:
            good = True
            for k, v in a.items():
                if k in ("event",): continue
                if k.startswith("tool_input_"):
                    tv = (t.get("tool_input") or {}).get(k[len("tool_input_"):], "")
                elif k == "tool_calls":
                    tv = t.get("tool_calls"); v = json.loads(v) if v else v
                    tv = [{"tool_name": x["tool_name"], "tool_use_id": x["tool_use_id"]} for x in tv] if tv else tv
                    v = [{"tool_name": x["tool_name"], "tool_use_id": x["tool_use_id"]} for x in v] if v else v
                else:
                    tv = t.get(k, "")
                    if tv is None: tv = ""
                if (tv if tv is not None else "") != v: good = False; break
            if good: ok = True; break
        tot[ev] += 1
        if not ok: bad[ev] += 1; print("MISMATCH", d, ev, json.dumps(a)[:200])
        for k, v in a.items():
            if v in ("", None): empty[ev][k] += 1
for ev in tot: print(ev, "calls", tot[ev], "no matching truth record with all equal fields", bad[ev], "always-empty/had-empty fields", dict(empty[ev]))
print("TOTAL", sum(tot.values()), "mismatch", sum(bad.values()))
