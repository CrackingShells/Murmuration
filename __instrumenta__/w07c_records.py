"""Lists, per Bash tool call of one w07-c probe session, what the platform's transcript recorded: tool_result text, hook attachment records (type, hook name, durationMs, exit code, the first 110 chars of stderr/stdout/content), in time order; input: a run directory (with transcript.jsonl and subagents/), optional --all to print every hook-related record; output: text table on stdout.
"""
import json, sys, glob, os
d = sys.argv[1]
files = [os.path.join(d, "transcript.jsonl")] + sorted(glob.glob(os.path.join(d, "subagents", "**", "agent-*.jsonl"), recursive=True))
for f in files:
    print("##", os.path.relpath(f, d))
    for l in open(f):
        r = json.loads(l); ty = r.get("type"); ts = (r.get("timestamp") or "")[11:23]
        if ty == "attachment":
            a = r["attachment"]; at = a.get("type", "")
            if at.startswith("hook") or at.startswith("async_hook"):
                keep = {k: (str(v)[:110]) for k, v in a.items() if k in ("hookName", "hookEvent", "durationMs", "exitCode", "stderr", "stdout", "content", "error", "message", "toolUseID", "command", "outcome", "decision", "reason") and v not in ("", None, [])}
                print(ts, "ATT", at, json.dumps(keep)[:400])
        elif ty == "assistant":
            for c in r["message"]["content"]:
                if c["type"] == "tool_use": print(ts, "TOOL_USE", json.dumps(c["input"])[:70])
        elif ty == "user":
            m = r["message"]["content"]
            if isinstance(m, list):
                for c in m:
                    if c.get("type") == "tool_result": print(ts, "TOOL_RESULT", ("ERR " if c.get("is_error") else "") + str(c["content"])[:300].replace("\n", " | "))
        elif ty == "system" and ("hook" in json.dumps(r)[:300].lower()):
            print(ts, "SYSTEM", json.dumps(r)[:300])
