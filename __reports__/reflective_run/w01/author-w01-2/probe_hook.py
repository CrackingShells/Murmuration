"""Hook probe.  usage (as a command hook): python3 -I probe_hook.py <outdir>
Logs the raw hook input.  On SubagentStop / Stop / SessionEnd it also snapshots the transcript the
hook is pointed at (agent_transcript_path, transcript_path) and records the per-request token sums
AT HOOK TIME, so they can be compared with the file as it stands after the run."""
import sys, os, json, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sumtx

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except Exception:
    d = {"_raw": raw}
rec = {"t": time.time(), "event": d.get("hook_event_name"), "input": d}
ev = d.get("hook_event_name")
for field in ("agent_transcript_path", "transcript_path"):
    p = d.get(field)
    if ev in ("SubagentStop", "Stop", "SessionEnd") and p:
        info = {"path": p, "exists": os.path.exists(p)}
        if info["exists"]:
            info["size"] = os.path.getsize(p)
            info["mtime"] = os.path.getmtime(p)
            s = sumtx.summarize(p)
            info["requests"] = s["requests"]
            info["sums"] = s["sums"]
            info["n_null_stop_last"] = s["n_null_stop_last"]
            snap = os.path.join(out, "snap_%s_%s_%d.jsonl" % (ev, d.get("agent_id", "main"), int(time.time() * 1000)))
            shutil.copyfile(p, snap)
            info["snapshot"] = snap
        rec[field + "_at_hook"] = info
        if ev == "SubagentStop" and field == "agent_transcript_path" and os.environ.get("PROBE_POLL") == "1" and info["exists"]:
            # remedy test: poll the same file until every request has a stop_reason (final usage), max 4 s
            t0 = time.time(); samples = []
            while time.time() - t0 < 4.0:
                s2 = sumtx.summarize(p)
                samples.append((round(time.time() - t0, 3), s2["n_null_stop_last"], s2["sums"]["last"]["output_tokens"], s2["requests"]))
                if s2["n_null_stop_last"] == 0:
                    break
                time.sleep(0.05)
            rec["poll"] = samples
with open(os.path.join(out, "hooks.jsonl"), "a") as f:
    f.write(json.dumps(rec, default=str) + "\n")
sys.exit(0)
