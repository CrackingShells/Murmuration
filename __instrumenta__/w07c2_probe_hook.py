# Probe hook for w07-c2 q2: on UserPromptSubmit, polls (every 5 ms; up to LIMIT s in the hook itself, or up to 10 s in a detached child that lets the hook return at once when argv[2] == 'detach') the transcript for the user record whose promptId equals the payload's prompt_id, and appends one JSON line to argv[1] with the payload keys, selected env names/values, whether the file existed at hook start, the wait until the record was readable, and the record's origin fields; never prints, never fails.
import json, os, sys, time
import subprocess
t0 = float(os.environ.get("W07C2_T0") or time.time())
log = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "block"
LIMIT = 10.0 if mode == "child" else 0.3
try:
    raw = sys.stdin.read()
    if mode == "detach":  # return at once; a child polls the transcript for up to 10 s
        env = dict(os.environ, W07C2_T0=repr(t0))
        ch = subprocess.Popen([sys.executable, "-I", os.path.abspath(__file__), log, "child"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, start_new_session=True)
        ch.stdin.write(raw.encode()); ch.stdin.close()
        sys.exit(0)
    d = json.loads(raw)
    pid, tp = d.get("prompt_id"), d.get("transcript_path")
    out = {"t0": t0, "keys": sorted(d), "payload": {k: v for k, v in d.items() if k not in ("prompt", "transcript_path", "cwd", "scratchpad_dir", "session_id", "prompt_id")},
           "env_claude": sorted(k for k in os.environ if k.startswith("CLAUDE")),
           "env_entrypoint": os.environ.get("CLAUDE_CODE_ENTRYPOINT"), "env_child": os.environ.get("CLAUDE_CODE_CHILD_SESSION"),
           "env_attended": os.environ.get("CLAUDE_CODE_SESSION_ATTENDED"), "env_has_host_session": "CLAUDE_CODE_HOST_SESSION_ID" in os.environ,
           "existed_at_start": bool(tp) and os.path.exists(tp), "size_at_start": os.path.getsize(tp) if tp and os.path.exists(tp) else None}
    found = None
    while time.time() - t0 < LIMIT and tp and pid:
        try:
            with open(tp, "rb") as fh:
                data = fh.read()
            for line in data.split(b"\n"):
                if pid.encode() in line:
                    try: r = json.loads(line)
                    except ValueError: continue
                    if r.get("type") == "user" and r.get("promptId") == pid and "toolUseResult" not in r:
                        found = r; break
        except OSError:
            pass
        if found: break
        time.sleep(0.005)
    out["mode"] = mode
    out["wait_s"] = (time.time() - t0) if found else None
    if found:
        out["record_ts"] = found.get("timestamp")
        out["record_fields"] = {k: found.get(k) for k in ("origin", "promptSource", "turnOrigin", "entrypoint", "isMeta", "permissionMode", "userType", "version")}
        out["record_keys"] = sorted(found)
    with open(log, "a") as fh:
        fh.write(json.dumps(out) + "\n")
except SystemExit:
    raise
except Exception as e:
    with open(log, "a") as fh:
        fh.write(json.dumps({"error": repr(e)}) + "\n")
