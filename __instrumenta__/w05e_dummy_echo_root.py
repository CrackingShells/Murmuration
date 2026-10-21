#!/usr/bin/env python3
# Dummy-plugin SessionStart hook: reads the event on stdin, appends one JSON line (plugin root, MARKER file, cwd, CLAUDE_PROJECT_DIR, git toplevel, W05_* env) to $W05_LOG and prints it as additionalContext.
import os, sys, json, subprocess, time
p = json.load(sys.stdin) if not sys.stdin.isatty() else {}
root = os.environ.get("CLAUDE_PLUGIN_ROOT", "?")
proj = os.environ.get("CLAUDE_PROJECT_DIR", "?")
try:
    top = subprocess.run(["git","-C",p.get("cwd","."),"rev-parse","--show-toplevel"],capture_output=True,text=True).stdout.strip()
except Exception as e:
    top = "err"
marker = open(os.path.join(root, "MARKER")).read().strip() if os.path.exists(os.path.join(root,"MARKER")) else "none"
line = {"t": time.time(), "event": p.get("hook_event_name"), "source": p.get("source"), "root": root, "marker": marker, "cwd": p.get("cwd"), "project_dir": proj, "git_toplevel": top, "root_is_toplevel": os.path.realpath(root)==os.path.realpath(top), "w05_env": {k:v for k,v in os.environ.items() if k.startswith("W05_")}}
open(os.environ.get("W05_LOG","/private/tmp/murmuration-w05/explorer-w05-e/hook.log"),"a").write(json.dumps(line)+"\n")
print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"DUMMY_ROOT=%s MARKER=%s" % (root, marker)}}))
