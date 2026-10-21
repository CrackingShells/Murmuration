#!/usr/bin/env python3
"""The resident hook server: runs `budget.py` and `handback.py` in one long-lived process, so a hook starts no process.

A stdio MCP server (Python standard library), bundled through `.mcp.json`. `hooks/hooks.json` registers `type: mcp_tool` rows that call its
one tool, `hook`, with the payload fields as arguments (`${field}`) and `script: budget|handback`. The tool is not listed to the model (`tools/list`
is empty; the platform calls a tool it does not list, measured in w06-c4), so no agent's request carries it. The server calls the same
functions the scripts call (`budget.handle`, `handback.run`), with the same event; nothing else decides an answer.

What a resident process could change, and what is done about it:
  state       every state of the budget and the hand-back is on disk (`__statera__/.harness/`, under the file lock); the server keeps none of it.
  code        a fresh process ran the current file. The server compares the two files' modification times at each call and reloads them
              when they changed; a file that no longer loads keeps the loaded version, and the fault is logged.
  fields      the platform substitutes an absent field as "" and an object as a JSON string: "" is dropped, `tool_input` and `tool_calls` are parsed.
  a fault     an exception in a handler, or a handler over DEADLINE seconds, is logged as a `hook_fault` line in `__statera__/harness.jsonl` and
              the call answers at once. On PostToolBatch and SubagentStart the answer is a note to the agent (to the PI too, on its own thread)
              that the notes and the 150% block may not be running, at most once per agent per 10 minutes.
  a death     the platform restarts a stopped server at its next hook (w06-c3, m4a); a server that cannot start leaves only a
              `hook_non_blocking_error` record in the transcript, which `lab_status.py` reports and `outage.py` (a `command` hook at the events
              that are rare) turns into text for the worker and the PI.

    hook_server.py             serve MCP on stdin and stdout
    hook_server.py --selftest  check the server on a temporary project
"""
import datetime
import importlib
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DEADLINE = 2.5       # seconds a handler may take; the hooks' `timeout` is 3
NOTE_EVERY = 600     # seconds between two fault notes to one agent
JSON_FIELDS = ("tool_input", "tool_calls")
_files, _loaded, _noted, _lock = ("handback.py", "budget.py"), {}, {}, threading.Lock()


def modules():
    """(budget, handback), reloaded when either file changed since the last call; a reload that fails keeps the loaded code and says so."""
    with _lock:
        stamp = tuple(os.stat(os.path.join(HERE, f)).st_mtime_ns for f in _files)
        if _loaded.get("stamp") != stamp:
            first = "stamp" not in _loaded
            _loaded["stamp"] = stamp
            try:
                handback = importlib.import_module("handback") if first else importlib.reload(sys.modules["handback"])
                budget = importlib.import_module("budget") if first else importlib.reload(sys.modules["budget"])
            except Exception as exc:   # a half-written file: the old code goes on
                if first:
                    raise
                _loaded["error"] = "reload failed: %s: %s" % (type(exc).__name__, exc)
        return sys.modules["budget"], sys.modules["handback"]


def clean(args):
    """The event a script would have read from stdin: absent fields dropped, JSON strings parsed."""
    event = {k: v for k, v in args.items() if k != "script" and v != ""}
    for k in JSON_FIELDS:
        if isinstance(event.get(k), str):
            event[k] = json.loads(event[k])
    return event


def lab_dir(event):
    """The nearest folder with a `__statera__/`, from the event's cwd up 5 levels, then CLAUDE_PROJECT_DIR (as handback.lab_root does)."""
    p = os.path.abspath(event.get("cwd") or os.getcwd())
    chain = [p] + [os.path.abspath(os.path.join(p, *[".."] * n)) for n in range(1, 6)] + [os.environ.get("CLAUDE_PROJECT_DIR") or ""]
    return next((c for c in chain if c and os.path.isdir(os.path.join(c, "__statera__"))), None)


def fault(event, kind, detail):
    """Log a `hook_fault` line (one write) when the event is in a lab. Returns the note for the agent, or None."""
    root = lab_dir(event)
    if not root:
        return None
    now = time.time()
    rec = dict(event="hook_fault", kind=kind, detail=detail[:300], hook=event.get("hook_event_name"), agent_id=event.get("agent_id"),
               t=datetime.datetime.now().astimezone().isoformat(timespec="milliseconds"))
    fd = os.open(os.path.join(root, "__statera__", "harness.jsonl"), os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    try:
        os.write(fd, (json.dumps(rec, sort_keys=True) + "\n").encode())
    finally:
        os.close(fd)
    who = event.get("agent_id") or "main"
    with _lock:
        if now - _noted.get(who, 0) < NOTE_EVERY or event.get("hook_event_name") not in ("PostToolBatch", "SubagentStart"):
            return None
        _noted[who] = now
    return {"hookSpecificOutput": {"hookEventName": event["hook_event_name"], "additionalContext":
            "Hook server fault (%s): the budget notes, the 150%% block and the hand-back capture may not be running for this call. It is logged in "
            "__statera__/harness.jsonl; `/lab-status` shows it. Go on; say so in your hand-back." % kind}}


def answer(args, now=None):
    """The answer (dict or None) of one tool call. `now` (epoch seconds) is for replays; the platform's calls leave it out."""
    event = {k: v for k, v in args.items() if isinstance(v, str)}   # for the fault line only
    try:
        event = clean(args)
        budget, handback = modules()
        if _loaded.pop("error", None):
            fault(event, "reload", "a script changed and no longer loads; the loaded version is used")
        if args.get("script") == "budget":
            return budget.handle(event, now)
        return handback.run(event, datetime.datetime.fromtimestamp(now, datetime.timezone.utc) if now else None)
    except Exception as exc:
        return fault(event, "exception", "%s in %s: %s" % (type(exc).__name__, args.get("script"), exc))


def bounded(args):
    """`answer` in a thread, given up on after DEADLINE seconds (the work goes on; its answer is dropped)."""
    box = []
    worker = threading.Thread(target=lambda: box.append(answer(args)), daemon=True)
    worker.start()
    worker.join(DEADLINE)
    if worker.is_alive():
        return fault({k: v for k, v in args.items() if isinstance(v, str)}, "slow", "%s took over %s s" % (args.get("script"), DEADLINE))
    return box[0] if box else None


def serve():
    out, sys.stdout, wlock = sys.stdout, sys.stderr, threading.Lock()   # a stray print must not break the protocol

    def send(i, result):
        with wlock:
            out.write(json.dumps({"jsonrpc": "2.0", "id": i, "result": result}) + "\n")
            out.flush()

    def call(i, args):
        try:
            got = bounded(args)
        except Exception:
            got = None   # a call is always answered
        send(i, {"content": [{"type": "text", "text": json.dumps(got) if got else ""}]})

    for line in sys.stdin:
        try:
            m = json.loads(line)
        except ValueError:
            continue
        i, method = m.get("id"), m.get("method")
        if i is None:
            continue
        if method == "initialize":
            send(i, {"protocolVersion": (m.get("params") or {}).get("protocolVersion", "2024-11-05"), "capabilities": {"tools": {}}, "serverInfo": {"name": "murmuration-hooks", "version": "1"}})
        elif method == "tools/list":
            send(i, {"tools": []})
        elif method == "tools/call":
            threading.Thread(target=call, args=(i, (m.get("params") or {}).get("arguments") or {}), daemon=True).start()
        else:
            send(i, {})


def selftest():
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "__statera__"))
        sess = os.path.join(tmp, "s")
        os.makedirs(os.path.join(sess, "subagents"))
        ev = dict(script="budget", hook_event_name="SubagentStart", cwd=tmp, agent_id="a1", agent_type="murmuration:author", transcript_path=sess + ".jsonl",
                  agent_transcript_path="", permission_mode="", tool_input="", tool_calls="")
        proc = subprocess.Popen([sys.executable, os.path.abspath(__file__)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd="/")

        def rpc(n, method, params=None):
            proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": n, "method": method, "params": params or {}}) + "\n")
            proc.stdin.flush()
            return json.loads(proc.stdout.readline())["result"]

        def tool(n, **kw):
            text = rpc(n, "tools/call", {"name": "hook", "arguments": kw})["content"][0]["text"]
            return json.loads(text) if text else None

        assert rpc(1, "initialize", {"protocolVersion": "2025-03-26"})["protocolVersion"] == "2025-03-26" and rpc(2, "tools/list") == {"tools": []}
        start = tool(3, **ev)["hookSpecificOutput"]["additionalContext"]
        assert "USD 3.00 and 20 minutes" in start, start   # the real budget.py answered, from a process whose cwd is not the lab
        assert tool(4, **dict(ev, script="handback", hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_type="murmuration:explorer")) is not None, "the report check ran"
        assert tool(5, **dict(ev, hook_event_name="PostToolBatch", tool_calls='[{"tool_name": "Bash"}]')) is None
        # the files change under the server: the next call runs the new code; a file that does not load keeps the old one and the fault is logged
        import shutil
        shutil.copytree(HERE, os.path.join(tmp, "scripts"), ignore=shutil.ignore_patterns("__pycache__"))
        p2 = subprocess.Popen([sys.executable, os.path.join(tmp, "scripts", "hook_server.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd="/")
        proc, old = p2, proc
        old.stdin.close()
        old.wait()
        assert "USD 3.00" in tool(6, **dict(ev, agent_id="a6"))["hookSpecificOutput"]["additionalContext"]
        src = os.path.join(tmp, "scripts", "budget.py")
        text = open(src).read()
        open(src, "w").write(text.replace('"author": 3.0,', '"author": 4.0,', 1))
        os.utime(src, (time.time() + 5, time.time() + 5))
        assert "USD 4.00" in tool(7, **dict(ev, agent_id="a2"))["hookSpecificOutput"]["additionalContext"], "a changed script is reloaded"
        open(src, "w").write("def broken(:\n")
        os.utime(src, (time.time() + 10, time.time() + 10))
        got = tool(8, **dict(ev, agent_id="a3"))
        assert "USD 4.00" in got["hookSpecificOutput"]["additionalContext"], "a script that does not load: the loaded code answers"
        faults = [json.loads(x) for x in open(os.path.join(tmp, "__statera__", "harness.jsonl")) if '"hook_fault"' in x]
        assert [f["kind"] for f in faults] == ["reload"], faults
        # a handler that raises: logged, a note on PostToolBatch, once per agent per NOTE_EVERY; none on a PostToolUse
        proc.stdin.close()
        proc.wait()
        proc = subprocess.Popen([sys.executable, os.path.join(tmp, "scripts", "hook_server.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd="/")
        rpc(1, "initialize")
        note = tool(9, **dict(ev, hook_event_name="PostToolBatch", tool_calls="not json"))
        assert "Hook server fault (exception)" in note["hookSpecificOutput"]["additionalContext"], note
        assert tool(10, **dict(ev, hook_event_name="PostToolBatch", tool_calls="not json")) is None, "one note per agent per 10 minutes"
        assert tool(11, **dict(ev, hook_event_name="PostToolUse", agent_id="a9", tool_input="not json")) is None
        faults = [json.loads(x) for x in open(os.path.join(tmp, "__statera__", "harness.jsonl")) if '"hook_fault"' in x]
        assert [f["kind"] for f in faults][-3:] == ["exception"] * 3 and not any(f["agent_id"] is None for f in faults[-3:]), faults
        proc.stdin.close()
        proc.wait()
        assert clean(dict(script="x", a="", b="1", tool_input='{"k": ""}')) == {"b": "1", "tool_input": {"k": ""}}
        # not in a lab: nothing is written
        with tempfile.TemporaryDirectory() as bare:
            assert fault(dict(cwd=bare, hook_event_name="PostToolBatch"), "x", "y") is None and not os.listdir(bare)
    print("PASS hook_server")


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        selftest()
        sys.exit(0)
    serve()
