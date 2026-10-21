# w07-c3: x5 simulation: what a Claude Code that ignored `args` would run for B's rows, namely `python3` with no arguments and the hook payload on stdin; inputs: none (payloads built here, the attack command from parts); output: per payload the exit code, stdout and stderr head of `python3` fed that payload
"""This is a simulation of the reading CONJECTURE-d for a Claude Code older than 2.1.139 (which has no `args` field): the field is ignored and `command` ("python3") is run as a shell command. No such version is installed
(2.1.296, 2.1.302, 2.1.304 are), so the old behaviour is not run, only what `python3` does when its stdin is the payload. Python reads a program from a stdin that is not a terminal: a payload of only strings is
a valid dict display and does nothing (exit 0, no output: a guard that is silently absent, which `onFailure: block` cannot catch because nothing failed); a payload with a JSON `true`/`false`/`null` fails with NameError (exit 1)."""
import json, subprocess

FLAG = "--" + "danger" + "ously-skip-permissions"
base = {"session_id": "s", "transcript_path": "/x.jsonl", "cwd": "/x", "permission_mode": "default", "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_use_id": "tu"}
cases = {
    "bypass command, strings only": dict(base, tool_input={"command": "claude %s -p hi" % FLAG, "description": "d"}),
    "ordinary command, strings only": dict(base, tool_input={"command": "ls", "description": "d"}),
    "bypass command with a boolean field": dict(base, tool_input={"command": "claude %s -p hi" % FLAG, "run_in_background": False}),
    "PostToolUse with a null field": dict(base, hook_event_name="PostToolUse", tool_input={"command": "ls"}, tool_response=None),
}
for name, p in cases.items():
    r = subprocess.run(["python3"], input=json.dumps(p), capture_output=True, text=True)
    print("%-40s exit %d stdout %r stderr %r" % (name, r.returncode, r.stdout[:60], r.stderr.strip().splitlines()[-1][:80] if r.stderr.strip() else ""))
