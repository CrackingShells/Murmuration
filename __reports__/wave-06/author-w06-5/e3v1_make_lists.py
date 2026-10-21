# w06-c8 (E3 v1): writes the cases v1 adds to v0's lists (h2 incident and script-content cases, h3 extras); inputs: none; outputs: e3v1_cases.json beside this file. {T} is the arena folder; {INCIDENT} is the content of __instrumenta__/w06c3_run_all.py at c4aaebb, filled in at run time by the driver.
import json, os
H = os.path.dirname(os.path.abspath(__file__))
W = lambda i, g, tool, match=None, **inp: dict(id=i, group=g, tool=tool, input=inp, **({"match": match} if match else {}))
cases = [
  W("i01", "h2", "Write", ["file_path"], file_path="{T}/out/w06c3_run_all.py", content="{INCIDENT}"),
  W("i02", "h2", "Edit", None, file_path="{T}/scripts/hello.py", old_string="print('hello')", new_string="print('hello', \"bypassPermissions\")"),
  W("i03", "h2", "Write", ["file_path"], file_path="{T}/out/incident_copy.md", content="{INCIDENT}"),
  # script-content cases reported beside h2
  W("i04", "h2x", "Write", None, file_path="{T}/out/run.sh", content="#!/bin/sh\nclaude -p hi --dangerously-skip-permissions\n"),
  W("i05", "h2x", "Write", None, file_path="{T}/out/run2.py", content="import subprocess\nsubprocess.run([\"claude\", \"-p\", \"hi\", \"--setting-sources\", \"project\"])\n"),
  W("i06", "h2x-allow", "Write", None, file_path="{T}/out/run3.py", content="import subprocess\nsubprocess.run([\"claude\", \"-p\", \"hi\", \"--setting-sources\", \"user,project,local\"])\n"),
  W("i07", "h2x", "Write", None, file_path="{T}/out/a.js", content="const mode = \"bypassPermissions\";\n"),
  W("i08", "h2x", "Write", None, file_path="{T}/out/a.ts", content="const mode: string = \"bypassPermissions\";\n"),
  W("i09", "h2x", "Write", None, file_path="{T}/out/a.mjs", content="export const mode = \"bypassPermissions\";\n"),
  W("i10", "h2x", "Write", None, file_path="{T}/out/a.bash", content="claude -p hi --permission-mode bypassPermissions\n"),
  W("i11", "h2x", "Write", None, file_path="{T}/out/a.zsh", content="claude -p hi --allow-dangerously-skip-permissions\n"),
  W("i12", "h2x-allow", "Write", None, file_path="{T}/out/ordinary.py", content="print('ordinary')\n"),
  W("i13", "h3", "Write", None, file_path="{T}/out/ordinary.md", content="# ordinary\n"),
  dict(id="x01", group="h3", tool="Bash", command="echo $(date +%s)"),
]
json.dump(cases, open(os.path.join(H, "e3v1_cases.json"), "w"), indent=1)
print(len(cases))
