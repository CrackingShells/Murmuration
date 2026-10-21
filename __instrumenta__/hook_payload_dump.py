"""Hook probe: logs, from a hook's stdin payload and environment, the cwd, CLAUDE_PROJECT_DIR and the head of the transcript, to a JSONL file given as argv[1].

Used as a command hook (UserPromptSubmit, SessionStart) in headless runs. Output: one JSON line per event with
payload_cwd, env_CLAUDE_PROJECT_DIR, proc_cwd, transcript_path, whether the transcript exists, its size, and for its
first 6 lines the record type, the `cwd` key and the byte length. Never prints to stdout, never fails.
"""
import json, os, sys, time

try:
    d = json.load(sys.stdin)
    tp = d.get("transcript_path")
    head = []
    exists = bool(tp) and os.path.exists(tp)
    if exists:
        with open(tp, "rb") as fh:
            for i, line in enumerate(fh):
                if i >= 6:
                    break
                try:
                    r = json.loads(line)
                    head.append({"type": r.get("type"), "cwd": r.get("cwd"), "n": len(line)})
                except Exception:
                    head.append({"type": "unparsed", "n": len(line)})
    rec = {"t": time.time(), "event": d.get("hook_event_name"), "payload_cwd": d.get("cwd"),
           "env_CLAUDE_PROJECT_DIR": os.environ.get("CLAUDE_PROJECT_DIR"), "proc_cwd": os.getcwd(),
           "transcript_path": tp, "transcript_exists": exists,
           "transcript_size": os.path.getsize(tp) if exists else None, "head": head,
           "prompt": (d.get("prompt") or "")[:40], "keys": sorted(d)}
    with open(sys.argv[1], "a") as out:
        out.write(json.dumps(rec) + "\n")
except Exception as e:  # a probe must never break the session
    with open(sys.argv[1], "a") as out:
        out.write(json.dumps({"error": repr(e)}) + "\n")
