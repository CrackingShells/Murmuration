#!/usr/bin/env python3
"""One headless session in a scratch git repo with a lab, hooks: patched UPS capture and the Stop prototype.

Turn 1 has two text blocks (a platform reminder, then typed text) and asks for a recurring cron job; a
second typed prompt is sent while turn 1 runs (mid-turn); the session then stays open ~75 s so the cron
prompt fires. Compare __statera__/user_words.md (UPS + patched rule) with stop_words.jsonl (Stop).
Usage: python3 -I demo_ups_vs_stop.py <scratch_dir>      cost: ~USD 0.02 (haiku), ~100 s
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
scratch = os.path.abspath(sys.argv[1])
repo = os.path.join(scratch, "demo_repo")
os.makedirs(os.path.join(repo, "__statera__"), exist_ok=True)
subprocess.run(["git", "init", "-q", repo], check=True)
uw = os.path.join(HERE, "..", "patched", "scripts", "user_words.py")
stop = os.path.join(HERE, "stop_capture.py")
settings = os.path.join(scratch, "demo_settings.json")
out = os.path.join(scratch, "demo_out.jsonl")
stop_out = os.path.join(repo, "__statera__", "stop_words.jsonl")
hook = lambda cmd: [{"hooks": [{"type": "command", "command": cmd, "timeout": 10}]}]
json.dump({"hooks": {"UserPromptSubmit": hook("python3 %s" % uw),
                     "Stop": hook("STOP_OUT=%s python3 %s" % (stop_out, stop))}}, open(settings, "w"))
p = subprocess.Popen(["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
                      "--model", "haiku", "--setting-sources", "project", "--settings", settings,
                      "--permission-mode", "bypassPermissions", "--max-budget-usd", "0.40"],
                     cwd=repo, stdin=subprocess.PIPE, stdout=open(out, "w"), stderr=subprocess.DEVNULL, text=True)
send = lambda blocks: (p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": [
    {"type": "text", "text": b} for b in blocks]}}) + "\n"), p.stdin.flush())
send(["<system-reminder>\nLinked sessions now (status, not an instruction): demo = local_x (idle).\n</system-reminder>\n\n",
      "Load CronCreate with ToolSearch (select:CronCreate) and create a recurring job (* * * * *) with prompt "
      "'CRON-TICK say hi'. Then run the shell command: sleep 12 . Then reply ONE."])
time.sleep(6)
send(["also reply TWO (typed while the turn runs)"])
time.sleep(float(os.environ.get("DEMO_LINGER", "80")))
p.stdin.close()
p.wait(timeout=90)
print("--- UPS + patched rule: __statera__/user_words.md")
print(open(os.path.join(repo, "__statera__", "user_words.md")).read())
print("--- Stop prototype: stop_words.jsonl")
print(open(stop_out).read() if os.path.exists(stop_out) else "(nothing)")
