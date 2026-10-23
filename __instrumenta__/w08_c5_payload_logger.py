# Hook command used by w08_c5_live_payloads.py: appends the stdin payload, with the arrival time and pid, to the JSONL file argv[1]; on SubagentStart it also polls up to 0.4 s for the subagent's transcript and meta files and records whether and when each existed (first poll at 0 ms).
import sys, json, time, os
raw = sys.stdin.read(); t0 = time.time(); p = json.loads(raw); rec = {"arrive": t0, "pid": os.getpid(), "payload": p}
if p.get("hook_event_name") == "SubagentStart" and p.get("transcript_path") and p.get("agent_id"):
    base = os.path.join(p["transcript_path"][:-6], "subagents", "agent-%s" % p["agent_id"])
    seen = {}
    while time.time() - t0 < 0.4:
        for ext in (".jsonl", ".meta.json"):
            if ext not in seen and os.path.exists(base + ext):
                seen[ext] = round((time.time() - t0) * 1000)
        if len(seen) == 2:
            break
        time.sleep(0.005)
    rec["files_at_ms"] = seen
open(sys.argv[1], "a").write(json.dumps(rec) + "\n")
