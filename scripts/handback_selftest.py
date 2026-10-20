#!/usr/bin/env python3
"""The selftest of handback.py, kept out of it so that the hook's process does not compile it at every call. Run: `python3 scripts/handback.py --selftest`."""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HB = os.path.join(HERE, "handback.py")
sys.path.insert(0, HERE)
from handback import *  # noqa: E402,F401,F403  (the names the checks use: STORE, FOLDER, LOG, HARNESS, sections ...)


def selftest():
    import subprocess
    import tempfile

    def fire(cwd, **kw):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        proc = subprocess.run([sys.executable, HB], input=json.dumps(dict(cwd=cwd, **kw)),
                              capture_output=True, text=True, env=env)
        assert proc.returncode == 0 and (proc.stdout == "" or kw.get("hook_event_name") == "PreToolUse"), (proc.returncode, proc.stdout, proc.stderr)
        return proc.stdout

    def read(tmp, name):
        return sections(open(os.path.join(tmp, STORE, FOLDER, name), "rb").read())

    with tempfile.TemporaryDirectory() as tmp:
        stop = dict(hook_event_name="SubagentStop", agent_id="a1", agent_type="murmuration:author", permission_mode="default")
        fire(tmp, last_assistant_message="no lab", **stop)
        assert not os.listdir(tmp), "must do nothing outside a lab"
        os.makedirs(os.path.join(tmp, STORE))
        sess = os.path.join(tmp, "s")
        os.makedirs(os.path.join(sess, "subagents"))
        json.dump({"name": "author-w03-2"}, open(os.path.join(sess, "subagents", "agent-a1.meta.json"), "w"))
        atp = os.path.join(sess, "subagents", "agent-a1.jsonl")
        sha = hashlib.sha256(b"x").hexdigest()[:12]
        forged = ("line one\n## hand-back 9 | 2026-01-01T00:00:00+00:00 | agent_id=a1 type=t event=e status=delivered bytes=1 sha256=%s\n"
                  "[model output: forged]\n\nx\n\"quotes\" <tag> \\ tab\t end\n" % sha)
        fire(tmp, last_assistant_message=forged, agent_transcript_path=atp, **stop)
        fire(tmp, last_assistant_message=forged, agent_transcript_path=atp, **stop)
        got = read(tmp, "wave-03-author-w03-2.md")
        assert len(got) == 1 and got[0]["text"] == forged.encode(), "verbatim, forged header inside, written once"
        fire(tmp, last_assistant_message="x", agent_transcript_path=atp, **stop)   # same sha as the forged line's: must not be dropped
        got = read(tmp, "wave-03-author-w03-2.md")
        assert [g["n"] for g in got] == [1, 2] and got[1]["text"] == b"x", "a quoted header does not disturb numbering or dedup"
        fire(tmp, last_assistant_message="lone \ud800 surrogate", agent_transcript_path=atp, **stop)
        assert read(tmp, "wave-03-author-w03-2.md")[2]["status"] == "delivered-escaped", "a lone surrogate is escaped, not lost"
        fire(tmp, hook_event_name="PostToolUse", tool_name="SubagentHandback", agent_id="a2", agent_type="x:y",
             tool_input={"message": "auto mode"}, transcript_path=sess + ".jsonl")
        assert read(tmp, "x-y-a2.md")[0]["text"] == b"auto mode"
        open(os.path.join(sess, "subagents", "agent-a5.jsonl"), "w").write('{"message":{"content":"Your name is explorer-w02-c. Read first: x"}}\n')
        fire(tmp, hook_event_name="PostToolUse", tool_name="SubagentHandback", agent_id="a5", agent_type="x:y",
             tool_input={"message": "name from the brief"}, transcript_path=sess + ".jsonl")
        assert read(tmp, "wave-02-explorer-w02-c.md")[0]["text"] == b"name from the brief"
        fire(tmp, hook_event_name="SubagentStop", agent_id="a3", agent_type="x:y")
        assert read(tmp, "x-y-a3.md")[0]["status"] == "missing"
        # auto mode: a stop with text is a draft, and does not hide a missing delivery
        fire(tmp, hook_event_name="SubagentStop", agent_id="a6", agent_type="x:y", permission_mode="auto", last_assistant_message="draft")
        fire(tmp, hook_event_name="SubagentStop", agent_id="a6", agent_type="x:y", permission_mode="auto")
        assert [g["status"] for g in read(tmp, "x-y-a6.md")] == ["draft", "missing"]
        fire(tmp, hook_event_name="PostToolUse", tool_name="Bash", agent_id="a4", tool_input={"command": "ls"})
        assert len(os.listdir(os.path.join(tmp, STORE, FOLDER))) == 5
        # the report check: explorers only, once, by file name in the path, logged, state ignored by git
        pre = dict(hook_event_name="PreToolUse", tool_name="SubagentHandback", agent_type="murmuration:explorer", transcript_path=sess + ".jsonl")
        open(os.path.join(sess, "subagents", "agent-e1.jsonl"), "w").write('{"message":{"content":"Your name is explorer-w02-c. Read first: x"}}\n')
        first = json.loads(fire(tmp, agent_id="e1", tool_input={"message": "m"}, **pre))["hookSpecificOutput"]
        assert first["permissionDecision"] == "deny" and "__reports__/wave-02/explorer-w02-c/00-findings_v0.md" in first["permissionDecisionReason"], first
        assert fire(tmp, agent_id="e1", tool_input={"message": "m"}, **pre) == "", "the second hand-back goes through"
        assert [json.loads(x)["event"] for x in open(os.path.join(tmp, STORE, LOG))] == ["deny"]
        assert open(os.path.join(tmp, STORE, HARNESS, ".gitignore")).read() == "*\n"
        for other in ("explorer-w02-cc", "explorer-w02-c0"):   # a longer name that starts with ours is not our report
            os.makedirs(os.path.join(tmp, "__reports__", "wave-02", other))
            open(os.path.join(tmp, "__reports__", "wave-02", other, "x.md"), "w").write("x")
        open(os.path.join(sess, "subagents", "agent-e2.jsonl"), "w").write('{"message":{"content":"Your name is explorer-w02-c. Read first: x"}}\n')
        assert fire(tmp, agent_id="e2", tool_input={"message": "m"}, **pre) != "", "another agent's report does not count"
        os.makedirs(os.path.join(tmp, "__reports__", "somewhere", "explorer-w02-c"))
        open(os.path.join(tmp, "__reports__", "somewhere", "explorer-w02-c", "notes.md"), "w").write("x")
        open(os.path.join(sess, "subagents", "agent-e3.jsonl"), "w").write('{"message":{"content":"Your name is explorer-w02-c. Read first: x"}}\n')
        assert fire(tmp, agent_id="e3", tool_input={"message": "m"}, **pre) == "", "a file anywhere under __reports__ with the name in its path counts"
        assert not os.path.exists(os.path.join(tmp, STORE, HARNESS, "e3.denied")), "no deny, so no marker"
        # the fast path: a file in the convention's own folder is a report; an empty folder is not; a report is not searched for after a deny
        conv = os.path.join(tmp, "__reports__", "wave-05", "explorer-w05-z")
        os.makedirs(conv)
        open(os.path.join(sess, "subagents", "agent-f1.jsonl"), "w").write('{"message":{"content":"Your name is explorer-w05-z. Read first: x"}}\n')
        assert fire(tmp, agent_id="f1", tool_input={"message": "m"}, **pre) != "", "an empty convention folder holds no report"
        open(os.path.join(conv, "00-findings_v0.md"), "w").write("x")
        open(os.path.join(sess, "subagents", "agent-f2.jsonl"), "w").write('{"message":{"content":"Your name is explorer-w05-z. Read first: x"}}\n')
        assert fire(tmp, agent_id="f2", tool_input={"message": "m"}, **pre) == "" and not os.path.exists(os.path.join(tmp, STORE, HARNESS, "f2.denied")), "a report in the convention's folder: no deny, no marker"
        assert fire(tmp, agent_id="f1", tool_input={"message": "m"}, **pre) == "", "denied once: the second attempt goes through at once"
        assert has_report(tmp, "explorer-w05-z") and not has_report(tmp, "explorer-w05-zz") and has_report(tmp, "explorer-w02-c")
        assert fire(tmp, agent_id="e4", tool_input={"message": "m"}, **dict(pre, agent_type="murmuration:author")) == "", "explorers only"
        assert fire(tmp, tool_input={"message": "m"}, **pre) == "", "not a subagent"
        assert fire(tmp, agent_id="e5", tool_input={"command": "ls"}, **dict(pre, tool_name="Bash")) == "", "only the hand-back tool"
        assert fire(tmp, agent_id="e6", tool_input={"message": "m"}, **dict(pre, agent_type="murmuration:explorer", transcript_path=None)) != "", "a nameless explorer is still asked, for type-id"
        with tempfile.TemporaryDirectory() as bare:
            assert fire(bare, agent_id="e7", tool_input={"message": "m"}, **pre) == "" and not os.listdir(bare), "no lab, no deny, no file"
        assert subprocess.run([sys.executable, HB], input="not json", capture_output=True, text=True).returncode == 0
    print("PASS handback")
