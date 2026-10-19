"""Probe hook. env: HOOK_LOG (jsonl path), HOOK_MODE (log|canary|budget), BUDGET_TOK, BUDGET_FRAC.
Logs raw input + live spend of the subagent transcript if a path is known."""
import sys, os, json, time, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
t0 = time.time()
raw = sys.stdin.read()
try: d = json.loads(raw)
except Exception: d = {"_raw": raw}
ev = d.get("hook_event_name")
log = os.environ.get("HOOK_LOG", "/dev/null")
mode = os.environ.get("HOOK_MODE", "log")
state_dir = os.environ.get("HOOK_STATE", os.path.dirname(log))

def spend(path):
    """sum usage over distinct requestId (last record per request); also last-request footprint"""
    last = {}
    try:
        for line in open(path):
            try: r = json.loads(line)
            except Exception: continue
            if r.get("type") != "assistant": continue
            u = (r.get("message") or {}).get("usage")
            if not u: continue
            last[r.get("requestId") or r.get("message", {}).get("id")] = u
    except Exception as e:
        return {"err": str(e)}
    s = {"requests": len(last), "in": 0, "cr": 0, "cw": 0, "out": 0, "last_ctx": 0}
    for u in last.values():
        s["in"] += u.get("input_tokens", 0); s["cr"] += u.get("cache_read_input_tokens", 0)
        s["cw"] += u.get("cache_creation_input_tokens", 0); s["out"] += u.get("output_tokens", 0)
        s["last_ctx"] = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
    return s

aid = d.get("agent_id")
# find the subagent transcript: SubagentStop gives agent_transcript_path; else derive from transcript_path
tp = d.get("agent_transcript_path")
if not tp and aid and d.get("transcript_path"):
    base = d["transcript_path"][:-6]  # strip .jsonl
    cand = os.path.join(base, "subagents", "agent-%s.jsonl" % aid)
    tp = cand
rec = {"t": t0, "event": ev, "keys": sorted(d.keys()), "input": d}
if tp:
    rec["tp"] = tp; rec["tp_exists"] = os.path.exists(tp)
    if rec["tp_exists"]: rec["spend"] = spend(tp)
out = None
# per-agent state: start time
sf = os.path.join(state_dir, "state_%s.json" % (aid or "main"))
if ev == "SubagentStart":
    json.dump({"start": t0, "fired80": False, "n": 0}, open(os.path.join(state_dir, "state_%s.json" % d.get("agent_id")), "w"))
if mode == "canary":
    if ev == "SubagentStart":
        out = {"hookSpecificOutput": {"hookEventName": ev, "additionalContext": "CANARY-START-7731: hook text injected at SubagentStart."}}
    elif ev in ("PreToolUse", "PostToolUse") and aid:
        st = json.load(open(sf)) if os.path.exists(sf) else {"n": 0}
        st["n"] = st.get("n", 0) + 1; json.dump(st, open(sf, "w"))
        out = {"hookSpecificOutput": {"hookEventName": ev, "additionalContext": "CANARY-%s-%d: hook text injected at %s number %d." % (ev.upper(), st["n"], ev, st["n"])}}
    elif ev in ("PreToolUse", "PostToolUse"):
        out = {"hookSpecificOutput": {"hookEventName": ev, "additionalContext": "CANARY-MAIN-%s: main-thread hook text." % ev.upper()}}
elif mode == "gate" and ev == "SubagentStop":
    gate = os.path.join(d.get("cwd", "."), "report.txt")
    rec["gate_file_exists"] = os.path.exists(gate)
    if not os.path.exists(gate):
        out = {"decision": "block", "reason": "GATE: before you stop, write your report to report.txt in the current directory with the Bash tool (for example cat > report.txt), then hand back again."}
elif mode == "gate3" and ev == "PreToolUse" and d.get("tool_name") == "SubagentHandback":
    gate = os.path.join(d.get("cwd", "."), "report.txt"); flag = os.path.join(state_dir, "denied_%s" % aid)
    rec["gate_file_exists"] = os.path.exists(gate)
    # durable copy of the hand-back text, independent of the model
    open(os.path.join(state_dir, "handback_copy_%s.txt" % aid), "w").write(d["tool_input"].get("message", ""))
    if not os.path.exists(gate) and not os.path.exists(flag):
        open(flag, "w").write("1")
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Before you hand back: write the same report to report.txt in the current directory (Bash, cat > report.txt), then call SubagentHandback again."}}
elif mode == "gate2" and ev == "PreToolUse" and d.get("tool_name") == "SubagentHandback":
    gate = os.path.join(d.get("cwd", "."), "report.txt")
    rec["gate_file_exists"] = os.path.exists(gate)
    if not os.path.exists(gate):
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "GATE: not yet. Write your report to report.txt in the current directory with the Bash tool first, then call SubagentHandback again."}}
elif mode == "raw":
    cfg = json.loads(os.environ["HOOK_RAW"])
    if ev == cfg["event"] and (aid or not cfg.get("aid_only", True)):
        cnt = os.path.join(state_dir, "cnt_%s_%s" % (ev, aid or "main"))
        n = (int(open(cnt).read()) if os.path.exists(cnt) else 0) + 1; open(cnt, "w").write(str(n))
        if n == cfg.get("nth", 1): out = cfg["out"]; rec["fired_raw"] = n
elif mode == "budget" and aid:
    B = int(os.environ.get("BUDGET_TOK", "100000")); frac = float(os.environ.get("BUDGET_FRAC", "0.8"))
    def wused(sp): return sp["in"] + sp["cw"] + sp["out"] + 0.1 * sp["cr"]
    if ev == "SubagentStart" and os.environ.get("BUDGET_START_NOTE"):
        out = {"hookSpecificOutput": {"hookEventName": ev, "additionalContext": os.environ["BUDGET_START_NOTE"].replace("{B}", str(B))}}
        rec["fired"] = "start"
    if ev == "PostToolUse" and os.path.exists(sf) and rec.get("spend"):
        st = json.load(open(sf)); sp = rec["spend"]
        used = wused(sp); rec["elapsed_s"] = round(t0 - st["start"], 1)
        if os.environ.get("BUDGET_UNIT") == "time": used = t0 - st["start"]
        rec["used"] = round(used)
        if os.environ.get("BUDGET_FIRE80", "1") == "1" and not st.get("fired80") and used >= frac * B:
            st["fired80"] = True; json.dump(st, open(sf, "w"))
            out = {"hookSpecificOutput": {"hookEventName": ev, "additionalContext": os.environ["BUDGET_MSG"].replace("{B}", str(B))}}
            rec["fired"] = "80"
        elif os.environ.get("BUDGET_HARD") == "1" and not st.get("fired100") and used >= B and ev == "PostToolUse" and d.get("tool_name") != "SubagentHandback":
            st["fired100"] = True; json.dump(st, open(sf, "w"))
            out = {"continue": False, "stopReason": "Budget exhausted: your %d-token budget is used. Stop now and hand back a report of what you have done and what you did not cover." % B}
            rec["fired"] = "hard"
rec["dt_ms"] = round((time.time() - t0) * 1000, 1)
rec["out"] = out
with open(log, "a") as f: f.write(json.dumps(rec, default=str) + "\n")
if out: print(json.dumps(out))
sys.exit(0)
