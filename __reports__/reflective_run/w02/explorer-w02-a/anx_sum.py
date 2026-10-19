import json, sys, re, glob, os
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
for d in sorted(glob.glob(S + "/runs/anx-*/")):
    cell = os.path.basename(d.rstrip("/"))
    try: H = [json.loads(l) for l in open(d + "hooks.jsonl")]
    except Exception: continue
    res = None
    for l in open(d + "stdout.jsonl"):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("type") == "result": res = r
    bash = [h for h in H if h["event"] == "PostToolUse" and h["input"].get("agent_id") and h["input"].get("tool_name") == "Bash"]
    hb = [h for h in H if h["event"] == "PreToolUse" and h["input"].get("tool_name") == "SubagentHandback"]
    msg = hb[-1]["input"]["tool_input"]["message"] if hb else ""
    fired = [(h["input"].get("tool_name"), h.get("used"), h.get("elapsed_s")) for h in H if h.get("fired") in ("80","hard")]
    covered = len({m.group(1) for ln in msg.splitlines() for m in [re.search(r"f(\d\d)", ln)] if m and re.search(r"\b1[0-9]{3}\b", ln)})
    last_used = [h.get("used") for h in H if h["event"] == "PostToolUse" and h["input"].get("tool_name") == "SubagentHandback"]
    # how many bash calls after the 80% note
    n_after = None
    if fired:
        idx = [i for i, h in enumerate(H) if h.get("fired") in ("80","hard")][0]
        n_after = sum(1 for h in H[idx + 1:] if h["event"] == "PostToolUse" and h["input"].get("agent_id") and h["input"].get("tool_name") == "Bash")
    sa = [h for h in H if h["event"] == "SubagentStart"]
    wall = None
    if sa and H: wall = round(H[-1]["t"] - sa[0]["t"], 1)
    bm = bool(re.search(r"budget|token", msg, re.I))
    rows.append((cell, len(bash), covered, last_used[0] if last_used else None, fired[0][1:] if fired else None, n_after, bm, len(msg), res and round(res["total_cost_usd"], 4)))
print("cell bash_calls files_covered used_at_handback fired(used,elapsed) bash_after_note mentions_budget_in_report report_chars usd")
for r in rows: print(*r)

import statistics as st, collections
by = collections.defaultdict(list)
for r in rows:
    if r[3] is not None and r[0].count("-") == 2: by[r[0].split("-")[1]].append(r)
print()
print("cond n  files_covered(list)  used_at_handback/B(40000) mean  bash_after_note(list)")
for c, rs in sorted(by.items()):
    print(c, len(rs), sorted(r[2] for r in rs), round(st.mean(r[3] for r in rs) / 40000, 2), [r[5] for r in rs])
