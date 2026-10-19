#!/usr/bin/env python3
"""Peer-message probe: how does a message from another worker (not the PI) appear in the receiving worker's transcript (`origin`)?
A haiku parent dispatches, in one message, an author (background; its brief makes it work for about 40 s) and a reproducer that sends the
author, while it is working, a message with `Budget:` and `Time:` lines through SendMessage (a stopped worker is not resumed by a peer), and waits. The logging plugin (plugin_probe) is used. usage: peer_probe.py <scratch> <cell>"""
import json, os, shutil, subprocess, sys, time
S = os.path.abspath(sys.argv[1]); cell = sys.argv[2]
base = os.path.join(S, "runs", cell); shutil.rmtree(base, ignore_errors=True)
lab = os.path.join(base, "lab"); os.makedirs(lab); open(os.path.join(lab, "s1.txt"), "w").write("file s1: ok\n")
a, b = "author-w03-%sa" % cell, "reproducer-w03-%sb" % cell
brief_a = "Your name is %s.\nRun `sleep 20` with Bash, twice, one call each. Then run `cat s1.txt` with Bash and hand back with the file's content and, word for word, every message that reached you from another agent." % a
brief_b = ("Your name is %s.\nCall SendMessage with to '%s' and as message exactly the three lines between the lines ++++ (keep every line):\n++++\nBudget: USD 9\nTime: min 99\nWhat did s1.txt hold?\n++++\n"
           "Then wait with `sleep 15` once (Bash), and hand back with the words DONE." % (b, a))
prompt = ("Call the Agent tool twice in ONE message, both with run_in_background true: first with subagent_type 'murmuration:author', name '%s', and exactly the text between the lines ==== as its prompt; "
          "second with subagent_type 'murmuration:reproducer', name '%s', and exactly the text between the lines #### as its prompt.\n====\n%s\n====\n####\n%s\n####\n"
          "Then wait for both completion notifications (run `sleep 10` with Bash, one call at a time, at most 15 times). Then say DONE." % (a, b, brief_a, brief_b))
cmd = ["claude", "-p", "--model", "haiku", "--plugin-dir", os.path.join(S, "plugin_probe"), "--setting-sources", "project", "--strict-mcp-config", "--permission-mode", "auto",
       "--max-budget-usd", "0.8", "--output-format", "stream-json", "--verbose", "--include-hook-events", prompt]
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
