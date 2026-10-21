# w06-c3: builds the throwaway test plugin `wt` (agents, hooks.json, .mcp.json, server copy, optional ground-truth command hooks) in a variant (live|truth|off) under a given directory; inputs: variant, output dir, WT_OUT dir; output: the plugin directory tree
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
variant, dest, wt_out = sys.argv[1], os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3])
assert variant in ("live", "truth", "off")
OPEN = "--open" in sys.argv   # control for m3: the lead does not deny the server tool and the worker allowlist names it
shutil.rmtree(dest, ignore_errors=True)
for d in (".claude-plugin", "agents", "hooks", "server"):
    os.makedirs(os.path.join(dest, d))
json.dump({"name": "wt", "version": "0.0.0", "description": "throwaway stage-1 test plugin for w06-c3"}, open(os.path.join(dest, ".claude-plugin", "plugin.json"), "w"))
open(os.path.join(dest, "agents", "worker.md"), "w").write("""---
name: worker
description: Test worker. Does small steps exactly as told.
model: haiku
tools: Bash, Read, Write%s
""" % (", mcp__plugin_wt_res__hook" if OPEN else "") + """maxTurns: 20
---

You are a test worker. Do exactly what your brief says, step by step, and keep every reply short.
When your brief says to hand back, give your final report as your last action.
""")
open(os.path.join(dest, "agents", "lead.md"), "w").write("""---
name: lead
description: Test lead (main thread).
model: haiku
%s
""" % ("" if OPEN else "disallowedTools: mcp__plugin_wt_res__hook") + """maxTurns: 30
---

You are a test lead. Do exactly what the user message says, step by step, and keep every reply short.
""")
if variant == "off":
    sys.exit(0)
shutil.copy(os.path.join(HERE, "w06c3_resident_server.py"), os.path.join(dest, "server", "res.py"))
json.dump({"mcpServers": {"res": {"command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/server/res.py"], "env": {"WT_OUT": wt_out}}}}, open(os.path.join(dest, ".mcp.json"), "w"), indent=1)
truth = os.path.join(dest, "hooks", "truth.sh")
open(truth, "w").write('#!/bin/sh\n{ cat; echo; } >> "%s/truth.jsonl"\n' % wt_out)
os.chmod(truth, 0o755)


def call(event, **fields):
    inp = {"event": event}
    for k, v in fields.items():
        inp[k] = "${%s}" % v.replace("__", ".") if v else "${%s}" % k
    return {"type": "mcp_tool", "server": "plugin:wt:res", "tool": "hook", "input": inp, "timeout": 10}


def group(_hook, matcher, **kw):
    hs = [call(**kw)]
    if variant == "truth":
        hs.append({"type": "command", "command": truth})
    g = {"hooks": hs}
    if matcher:
        g["matcher"] = matcher
    return g


F = lambda *names: {n: "" for n in names}
ident = F("hook_event_name", "cwd", "agent_id", "agent_type", "transcript_path", "agent_transcript_path", "permission_mode")
hooks = {
    "SubagentStart": [group("SubagentStart", None, event="SubagentStart", **ident)],
    "PreToolUse": [
        group("PreToolUse", "Agent|Task", event="PreToolUse:Agent", hook_event_name="", tool_name="", cwd="", agent_id="", tool_input_subagent_type="tool_input.subagent_type",
              tool_input_prompt="tool_input.prompt", tool_input_name="tool_input.name", tool_use_id=""),
        group("PreToolUse", "SubagentHandback", event="PreToolUse:SubagentHandback", hook_event_name="", tool_name="", cwd="", agent_id="", agent_type="", transcript_path="", agent_transcript_path=""),
    ],
    "PostToolUse": [
        group("PostToolUse", None, event="PostToolUse", tool_name="", tool_input_command="tool_input.command", **ident),
        group("PostToolUse", "SubagentHandback", event="PostToolUse:SubagentHandback", tool_name="", tool_input_message="tool_input.message", **ident),
    ],
    "PostToolBatch": [group("PostToolBatch", None, event="PostToolBatch", tool_calls="", **ident)],
    "SubagentStop": [group("SubagentStop", None, event="SubagentStop", last_assistant_message="", **ident)],
}
json.dump({"hooks": hooks}, open(os.path.join(dest, "hooks", "hooks.json"), "w"), indent=1)
