#!/usr/bin/env python3
"""Tell the worker and the PI that the hooks are down, with a hook that does not depend on the resident hook server.

The server's hooks are `mcp_tool` rows; when the server cannot restart, every one of them fails with a `hook_non_blocking_error` record in the
transcript and nothing the model sees (w06-c3, m4b). This script runs as a `command` hook at the three events that are rare (once per worker or per
dispatch, not per tool call) and reads those records, which the platform writes in the main transcript and in each subagent's:

  SubagentStart               the worker's note: the server does not load (`hook_server.modules()` raises), or the PI's transcript holds failures of the
                              last 10 minutes. `additionalContext`.
  PreToolUse(Agent|Task)      the PI, at a dispatch, with no agent_id: failures in its own transcript since the last note. `additionalContext`, and a
                              `hook_fault` line (kind `down`) in `__statera__/harness.jsonl`.
  PreToolUse(SubagentHandback) the worker, at its hand-back: failures in its own transcript. The first hand-back is denied, once, with a reason that
                              asks for the line `HOOKS DOWN: ...` at the top of the hand-back, which is how the PI is told by the worker.
A failure is a `hook_non_blocking_error` whose stderr names `plugin:murmuration:hooks`. Nothing is written outside a lab. The script never fails an agent.

    outage.py              read a hook event from stdin
    outage.py --selftest   check the script on a temporary project
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER, TAIL, RECENT = "plugin:murmuration:hooks", 2_000_000, 600


def epoch(stamp):
    try:
        return datetime.datetime.fromisoformat(str(stamp).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def failures(path, since=0.0, tail=TAIL):
    """(count, newest time) of the server's failure records in a transcript (its last `tail` bytes) newer than `since`."""
    n, newest = 0, 0.0
    try:
        with open(path, "rb") as fh:
            fh.seek(max(0, os.path.getsize(path) - tail))
            for line in fh.read().decode("utf-8", "replace").splitlines():
                if '"hook_non_blocking_error"' in line and SERVER in line:
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    t = epoch(rec.get("timestamp"))
                    if (rec.get("attachment") or {}).get("type") == "hook_non_blocking_error" and t > since:
                        n, newest = n + 1, max(newest, t)
    except OSError:
        pass
    return n, newest


def reply(kind, **fields):
    return {"hookSpecificOutput": dict(hookEventName=kind, **fields)}


def answer(event, now=None):
    """The hook's answer (a dict) or None."""
    sys.path.insert(0, HERE)
    import handback
    root, kind, now = handback.lab_root(event), event.get("hook_event_name"), now or datetime.datetime.now().timestamp()
    aid, main = event.get("agent_id"), event.get("transcript_path")
    if not root:
        return None
    if kind == "SubagentStart" and aid:
        try:
            import hook_server
            hook_server.modules()
            n = failures(main, now - RECENT)[0] if main else 0
            why = "%d hook calls of the hook server failed in the last 10 minutes" % n if n else None
        except Exception as exc:
            why = "hook_server.py does not load (%s)" % type(exc).__name__
        if why:
            handback.log_line(root, dict(event="hook_fault", kind="down", detail=why, hook=kind, agent_id=aid))
            return reply(kind, additionalContext="Hooks down: %s. The budget notes, the 150%% block and the hand-back capture may not be running for this run. "
                                                 "Go on; start your hand-back with a line `HOOKS DOWN: <what you saw>`." % why)
    elif kind == "PreToolUse" and event.get("tool_name") in ("Agent", "Task") and not aid and main:
        seen = os.path.join(handback.harness_dir(root), "outage.seen")
        try:
            since = float(open(seen).read())
        except (OSError, ValueError):
            since = 0.0
        n, newest = failures(main, since)
        if n:
            open(seen, "w").write(str(newest))
            handback.log_line(root, dict(event="hook_fault", kind="down", detail="%d hook calls failed since the last note" % n, hook=kind, agent_id=None))
            return reply(kind, additionalContext="Hooks down: %d calls of the hook server failed in this session since the last note (the budget notes, the 150%% block, the "
                                                 "hand-back capture and the dispatch record did not run for them). Workers dispatched now have no budget; /lab-status lists the failures." % n)
    elif kind == "PreToolUse" and event.get("tool_name") == "SubagentHandback" and aid:
        path = event.get("agent_transcript_path") or (main[:-6] + "/subagents/agent-%s.jsonl" % aid if main else None)
        n = failures(path)[0] if path else 0
        if n:
            try:
                fd = os.open(os.path.join(handback.harness_dir(root), "%s.outage" % aid), os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                os.close(fd)
            except FileExistsError:
                return None
            handback.log_line(root, dict(event="hook_fault", kind="down", detail="%d hook calls failed during the run" % n, hook=kind, agent_id=aid))
            return reply(kind, permissionDecision="deny", permissionDecisionReason=(
                "Lab harness check (genuine, sent by the hook that runs you): %d of your hook calls failed during this run, so your budget notes, the 150%% block and the "
                "capture of your hand-back were not running. Call SubagentHandback again; start the message with a line `HOOKS DOWN: %d hook calls failed`. This check happens once." % (n, n)))
    return None


def main():
    try:
        event = json.loads(sys.stdin.read() or "{}")
        out = answer(event) if isinstance(event, dict) else None
        if out:
            print(json.dumps(out))
    except Exception:
        pass
    return 0


def selftest():
    import subprocess
    import tempfile

    def rec(t, text='MCP server "plugin:murmuration:hooks" is not connected', kind="hook_non_blocking_error"):
        return json.dumps({"type": "attachment", "timestamp": t, "attachment": {"type": kind, "hookName": "PostToolUse:Bash", "stderr": text}}) + "\n"

    def fire(tmp, **kw):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input=json.dumps(dict(cwd=tmp, **kw)), capture_output=True, text=True, env=env)
        assert proc.returncode == 0 and not proc.stderr, (proc.returncode, proc.stderr)
        return json.loads(proc.stdout)["hookSpecificOutput"] if proc.stdout.strip() else None

    with tempfile.TemporaryDirectory() as tmp:
        sess = os.path.join(tmp, "s")
        os.makedirs(os.path.join(sess, "subagents"))
        now = datetime.datetime.now(datetime.timezone.utc)
        stamp = lambda ago: (now - datetime.timedelta(seconds=ago)).isoformat().replace("+00:00", "Z")
        ev = dict(transcript_path=sess + ".jsonl")
        assert fire(tmp, hook_event_name="SubagentStart", agent_id="a1", **ev) is None and not os.path.exists(os.path.join(tmp, "__statera__")), "no lab, nothing"
        os.makedirs(os.path.join(tmp, "__statera__"))
        assert fire(tmp, hook_event_name="SubagentStart", agent_id="a1", **ev) is None, "the server loads and the transcript is clean"
        open(sess + ".jsonl", "w").write(rec(stamp(5000)) + rec(stamp(5), text="other server") + rec(stamp(60)) * 2 + rec(stamp(30), kind="hook_success"))
        got = fire(tmp, hook_event_name="SubagentStart", agent_id="a1", **ev)
        assert "2 hook calls of the hook server failed in the last 10 minutes" in got["additionalContext"] and "HOOKS DOWN" in got["additionalContext"], got
        assert fire(tmp, hook_event_name="SubagentStart", **ev) is None, "the main thread is not a worker"
        # the PI at a dispatch: the failures since the last note, once
        pre = dict(hook_event_name="PreToolUse", tool_name="Agent", **ev)
        got = fire(tmp, **pre)
        assert got["hookEventName"] == "PreToolUse" and "Hooks down: 3 calls" in got["additionalContext"], got
        assert fire(tmp, **pre) is None, "told once"
        open(sess + ".jsonl", "a").write(rec(stamp(1)))
        assert "Hooks down: 1 calls" in fire(tmp, **pre)["additionalContext"], "a later failure is told again"
        assert fire(tmp, **dict(pre, agent_id="a2")) is None, "a worker's own Agent call is not the PI's dispatch"
        # the worker at its hand-back: denied once, from its own transcript
        wt = os.path.join(sess, "subagents", "agent-a3.jsonl")
        hb = dict(hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_id="a3", **ev)
        assert fire(tmp, **hb) is None, "no failure in its transcript"
        open(wt, "w").write(rec(stamp(3)) * 4)
        got = fire(tmp, **hb)
        assert got["permissionDecision"] == "deny" and "HOOKS DOWN: 4 hook calls failed" in got["permissionDecisionReason"], got
        assert fire(tmp, **hb) is None, "once"
        log = [json.loads(x) for x in open(os.path.join(tmp, "__statera__", "harness.jsonl"))]
        assert [(x["event"], x["kind"], x["agent_id"]) for x in log] == [("hook_fault", "down", "a1"), ("hook_fault", "down", None), ("hook_fault", "down", None), ("hook_fault", "down", "a3")], log
        assert subprocess.run([sys.executable, os.path.abspath(__file__)], input="not json", capture_output=True, text=True).returncode == 0
    print("PASS outage")


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        selftest()
        sys.exit(0)
    sys.exit(main())
