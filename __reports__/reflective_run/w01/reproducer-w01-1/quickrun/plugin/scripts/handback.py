#!/usr/bin/env python3
"""Keep every subagent's hand-back, verbatim, in a lab project.

Runs as a SubagentStop hook and as a PostToolUse hook on the `SubagentHandback` tool. It reads the
hook JSON from stdin and, when the project is an initialized lab (it has a `__statera__/` folder),
appends the agent's final message to `__statera__/handbacks/wave-NN-<agent name>.md` (or
`<agent name>.md` when the name carries no wave). A resumed agent appends a second section.

Where the message sits depends on the permission mode (probe row 24, re-measured in w01-c1):
  default, bypassPermissions  SubagentStop.last_assistant_message
  auto                        PostToolUse(SubagentHandback).tool_input.message; SubagentStop has no text

Each section starts with a header line carrying `bytes=N`, so a reader can slice the text exactly
even when it contains lines that look like headers. If a SubagentStop arrives without text and no
section of that agent was written in the last 30 s, a `MISSING` section records the gap.

The script never blocks an agent and always exits 0 with no output. Anything unexpected is dropped.

Usage:
    handback.py              read a hook event from stdin
    handback.py --selftest   check the script on a temporary project
"""
import datetime
import hashlib
import json
import os
import re
import sys

STORE, FOLDER = "__statera__", "handbacks"
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
HEAD = re.compile(r"^## hand-back (\d+) \| (\S+) \| agent_id=(\S+) .*? bytes=(\d+) sha256=(\w+)$", re.M)


def lab_root(event):
    """The nearest folder, from the event's cwd upward and then CLAUDE_PROJECT_DIR, with a `__statera__/`."""
    p = os.path.abspath(event.get("cwd") or os.getcwd())
    chain = [p]
    for _ in range(5):
        p = os.path.dirname(p)
        chain.append(p)
    chain.append(os.environ.get("CLAUDE_PROJECT_DIR") or "")
    return next((c for c in chain if c and os.path.isdir(os.path.join(c, STORE))), None)


def message(event):
    """The hand-back text carried by this event, or None."""
    kind = event.get("hook_event_name")
    if kind == "SubagentStop":
        text = event.get("last_assistant_message")
    elif kind == "PostToolUse" and event.get("tool_name") == "SubagentHandback":
        text = (event.get("tool_input") or {}).get("message")
    else:
        return None
    return text if isinstance(text, str) and text.strip() else None


def agent_name(event):
    """The name the agent was dispatched with: its .meta.json, else the brief's 'Your name is', else type-id."""
    aid = event.get("agent_id") or "unknown"
    stem = event.get("agent_transcript_path")
    if not stem and event.get("transcript_path"):
        stem = os.path.join(event["transcript_path"][:-6], "subagents", "agent-%s.jsonl" % aid)
    for read in (lambda: json.load(open(stem[:-6] + ".meta.json")).get("name"),
                 lambda: re.search(r"Your name is ([a-z0-9-]+)", open(stem).read(20000)).group(1)):
        try:
            name = read()
            if isinstance(name, str) and NAME.match(name):
                return name
        except Exception:
            pass
    return re.sub(r"[^a-z0-9-]", "-", (event.get("agent_type") or "agent").lower()) + "-" + aid[:8]


def file_for(root, name):
    wave = re.search(r"-w(\d+)-", name)
    return os.path.join(root, STORE, FOLDER, ("wave-%s-%s.md" % (wave.group(1), name)) if wave else name + ".md")


def handle(event, now=None):
    """Append the event's hand-back to the lab's file for that agent. Returns the path or None."""
    root = lab_root(event)
    if not root or not event.get("agent_id"):
        return None
    text = message(event)
    if text is None and event.get("hook_event_name") != "SubagentStop":
        return None
    path = file_for(root, agent_name(event))
    now = now or datetime.datetime.now().astimezone()
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    mine = [h for h in HEAD.findall(old) if h[2] == event["agent_id"]]
    sha = hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:12]
    if text is None:   # a stop with no text: fine if the PostToolUse capture just ran, else a visible gap
        if mine and (now - datetime.datetime.fromisoformat(mine[-1][1])).total_seconds() < 30:
            return None
        text = "(no text in the %s event; see %s)" % (event.get("hook_event_name"), event.get("agent_transcript_path"))
        sha = "MISSING"
    elif mine and mine[-1][4] == sha:
        return None    # the same text twice in a row: both hooks fired for one hand-back
    head = "" if old else "# Hand-backs of %s\n\nFinal messages, verbatim, appended by the lab's hook. Read it; never edit it.\n" % os.path.basename(path)[:-3]
    body = text.encode("utf-8")
    entry = "%s\n## hand-back %d | %s | agent_id=%s type=%s event=%s bytes=%d sha256=%s\n\n" % (
        head, len(HEAD.findall(old)) + 1, now.isoformat(timespec="seconds"), event["agent_id"],
        event.get("agent_type"), event.get("hook_event_name"), len(body), sha)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    try:
        os.write(fd, entry.encode("utf-8") + body + b"\n")   # one write: concurrent agents never interleave
    finally:
        os.close(fd)
    return path


def selftest():
    import subprocess
    import tempfile

    def fire(cwd, **kw):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input=json.dumps(dict(cwd=cwd, **kw)),
                              capture_output=True, text=True, env=env)
        assert proc.returncode == 0 and proc.stdout == "", (proc.returncode, proc.stdout, proc.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        stop = dict(hook_event_name="SubagentStop", agent_id="a1", agent_type="murmuration:author")
        fire(tmp, last_assistant_message="no lab", **stop)
        assert not os.listdir(tmp), "must do nothing outside a lab"
        os.makedirs(os.path.join(tmp, STORE))
        text = 'line one\n## hand-back 9 | x\n"quotes" <tag> \\ tab\t end\n'
        sess = os.path.join(tmp, "s")
        os.makedirs(os.path.join(sess, "subagents"))
        json.dump({"name": "author-w03-2"}, open(os.path.join(sess, "subagents", "agent-a1.meta.json"), "w"))
        fire(tmp, last_assistant_message=text, agent_transcript_path=os.path.join(sess, "subagents", "agent-a1.jsonl"), **stop)
        fire(tmp, last_assistant_message=text, agent_transcript_path=os.path.join(sess, "subagents", "agent-a1.jsonl"), **stop)
        out = os.path.join(tmp, STORE, FOLDER, "wave-03-author-w03-2.md")
        got = open(out, encoding="utf-8").read()
        assert text in got, "text is kept verbatim, including header-like lines"
        assert len(HEAD.findall(got)) == 1, "same text twice in a row is written once"
        fire(tmp, last_assistant_message="second, after resume", agent_transcript_path=os.path.join(sess, "subagents", "agent-a1.jsonl"), **stop)
        assert len(HEAD.findall(open(out, encoding="utf-8").read())) == 2, "a resumed agent appends a second section"
        fire(tmp, hook_event_name="PostToolUse", tool_name="SubagentHandback", agent_id="a2", agent_type="x:y",
             tool_input={"message": "auto mode"}, transcript_path=sess + ".jsonl")
        assert "auto mode" in open(os.path.join(tmp, STORE, FOLDER, "x-y-a2.md")).read()
        open(os.path.join(sess, "subagents", "agent-a5.jsonl"), "w").write('{"message":{"content":"Your name is explorer-w02-c. Read first: x"}}\n')
        fire(tmp, hook_event_name="PostToolUse", tool_name="SubagentHandback", agent_id="a5", agent_type="x:y",
             tool_input={"message": "name from the brief"}, transcript_path=sess + ".jsonl")
        assert "name from the brief" in open(os.path.join(tmp, STORE, FOLDER, "wave-02-explorer-w02-c.md")).read()
        fire(tmp, hook_event_name="SubagentStop", agent_id="a3", agent_type="x:y")
        assert "MISSING" in open(os.path.join(tmp, STORE, FOLDER, "x-y-a3.md")).read()
        fire(tmp, hook_event_name="PostToolUse", tool_name="Bash", agent_id="a4", tool_input={"command": "ls"})
        assert len(os.listdir(os.path.join(tmp, STORE, FOLDER))) == 4
        assert subprocess.run([sys.executable, os.path.abspath(__file__)], input="not json", capture_output=True, text=True).returncode == 0
    print("PASS handback")


def main():
    if "--selftest" in sys.argv[1:]:
        selftest()
        return 0
    try:
        event = json.loads(sys.stdin.read() or "{}")
        if isinstance(event, dict):
            handle(event)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except AssertionError:
        raise
    except Exception:
        code = 0
    sys.exit(code)
