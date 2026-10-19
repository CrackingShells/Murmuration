#!/usr/bin/env python3
"""Headless end-to-end test of ask_capture.py: a host that answers the AskUserQuestion permission request
(the SDK/Desktop protocol: --permission-prompt-tool stdio), the prototype registered as PostToolUse hook,
a throwaway lab. Task 2 of w02-c2.

Usage: python3 -I e2e_headless.py <scratch dir OUTSIDE the worktree>
Cost: three haiku turns, about USD 0.01 each (Claude Code 2.1.302). Writes raw run output only under <scratch dir>
(it holds session ids and paths: never commit it). Prints a redacted summary.
Cases: single-select; multi-select with a comma and non-ASCII text in one item; the dialog declined.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
scratch = os.path.abspath(sys.argv[1])
assert "claude-worktrees" not in scratch or "scratchpad" in scratch, "run outside the worktree"
proj = os.path.join(scratch, "proj")
os.makedirs(os.path.join(proj, "__statera__"), exist_ok=True)
words = os.path.join(proj, "__statera__", "user_words.md")
dump = os.path.join(scratch, "dump.py")
open(dump, "w").write("import sys,json,os\nd=sys.stdin.read()\nopen(os.path.join(os.path.dirname(os.path.abspath(__file__)),'hook_dump.jsonl'),'a').write(json.dumps({'argv':sys.argv[1:],'payload':json.loads(d)})+'\\n')\n")
settings = os.path.join(scratch, "settings.json")
cmd = lambda args: {"type": "command", "command": args}
json.dump({"hooks": {
    "PreToolUse": [{"matcher": "AskUserQuestion", "hooks": [cmd("python3 -I %s pre" % dump)]}],
    "PostToolUse": [{"matcher": "AskUserQuestion", "hooks": [cmd("python3 -I %s post" % dump), cmd("python3 -I %s" % os.path.join(HERE, "ask_capture.py"))]}],
    "PostToolUseFailure": [{"matcher": "AskUserQuestion", "hooks": [cmd("python3 -I %s postfail" % dump)]}],
}}, open(settings, "w"))
for f in (words, os.path.join(scratch, "hook_dump.jsonl")):
    if os.path.exists(f):
        os.remove(f)
CASES = [
    ("single", {}, 'Call the AskUserQuestion tool once with one single-select question: header Pick, question "Which colour?", options red and blue. Then say the answer in one sentence.', {"Which colour?": "blue"}),
    ("multi", {}, 'Call the AskUserQuestion tool once with two questions. Q1 multi-select (header Data, question "Which extras?", options imatrix quants, FP8 pair, GGUF). Q2 single-select (header Move, question "Where to?", options banyan, here). Then say the answers in one sentence.',
     {"Which extras?": ["imatrix quants", "another family, but more recent, \u65e5\u672c\u8a9e ok", "FP8 pair"], "Where to?": "banyan"}),
    ("declined", {"DENY": "1"}, 'Call the AskUserQuestion tool once with one single-select question: header Pick, question "Which colour?", options red and blue. Then say what happened in one sentence.', {}),
]
for name, env, prompt, answers in CASES:
    out = os.path.join(scratch, "out_%s.jsonl" % name)
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "drive_ask.py"), proj, settings, out, prompt, json.dumps(answers)],
                   cwd=proj, env={**os.environ, **env, "CLAUDE_PROJECT_DIR": proj}, timeout=150)
    cost = [json.loads(l).get("total_cost_usd") for l in open(out) if '"type":"result"' in l.replace(" ", "")]
    print("case %-9s run cost USD %s" % (name, cost))
events = [(r["argv"][0], r["payload"]) for r in map(json.loads, open(os.path.join(scratch, "hook_dump.jsonl")))]
print("hook events seen for AskUserQuestion:", [e for e, _ in events])
for e, p in events:
    if e == "post":
        print("  PostToolUse payload keys:", sorted(p.keys()))
        print("  tool_response keys:", sorted(p["tool_response"].keys()), "| tool_input has answers:", "answers" in p["tool_input"])
print("--- __statera__/user_words.md written by ask_capture.py ---")
print(open(words, encoding="utf-8").read() if os.path.exists(words) else "(none)")
