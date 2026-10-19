#!/usr/bin/env python3
"""Mid-run coordinator message probe: how does a message from the PI (the main session) to a worker that is still running appear in its transcript?
A haiku parent dispatches an author in the background (its brief makes it work for about 40 s), then at once sends it, with SendMessage, a message
with `Budget:` and `Time:` lines. The logging plugin (plugin_probe) is used. usage: coord_probe.py <scratch> <cell>"""
import json, os, shutil, subprocess, sys, time
S = os.path.abspath(sys.argv[1]); cell = sys.argv[2]
base = os.path.join(S, "runs", cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab); open(os.path.join(lab, "s1.txt"), "w").write("file s1: ok\n")
a = "author-w03-%sa" % cell
brief = "Your name is %s.\nRun `sleep 20` with Bash, twice, one call each. Then run `cat s1.txt` with Bash and hand back with the file's content and, word for word, every message that reached you." % a
prompt = ("Step 1: call the Agent tool once with subagent_type 'murmuration:author', name '%s', run_in_background true, with exactly the text between the lines ==== as its prompt.\n====\n%s\n====\n"
          "Step 2: at once, without waiting, load SendMessage with ToolSearch (query select:SendMessage) if needed and call SendMessage with to '%s' and as message exactly the lines between ++++ (keep every line).\n++++\nBudget: USD 9\nTime: min 99\nHow is it going?\n++++\n"
          "Step 3: wait for the completion notification (run `sleep 10` with Bash, one call at a time, at most 15 times). Then say DONE." % (a, brief, a))
cmd = ["claude", "-p", "--model", "haiku", "--plugin-dir", os.path.join(S, "plugin_probe"), "--setting-sources", "project", "--strict-mcp-config", "--permission-mode", "auto",
       "--max-budget-usd", "0.6", "--output-format", "stream-json", "--verbose", "--include-hook-events", prompt]
env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
env.update(PROBE_LOG=os.path.join(base, "events.jsonl"), PROBE_MODE="log", CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS="0")
t0 = time.time(); p = subprocess.run(cmd, capture_output=True, text=True, cwd=lab, env=env, timeout=900)
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout)
res = None
for l in p.stdout.splitlines():
    try:
        r = json.loads(l)
    except ValueError:
        continue
    if r.get("type") == "result": res = r
json.dump(dict(cell=cell, wall_s=round(time.time() - t0, 1), usd=res and res.get("total_cost_usd"), session=res and res.get("session_id")), open(os.path.join(base, "meta.json"), "w"))
print(open(os.path.join(base, "meta.json")).read())
