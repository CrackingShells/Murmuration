"""usage: run.py <cell> --hook-mode M [--perm auto|default|bypassPermissions] [--task file] [--agent file] ..."""
import argparse, json, os, subprocess, sys, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument("cell"); ap.add_argument("--hook-mode", default="log"); ap.add_argument("--perm", default="auto")
ap.add_argument("--prompt", required=True); ap.add_argument("--agent-prompt", required=True)
ap.add_argument("--events", default="SessionStart,SubagentStart,SubagentStop,PreToolUse,PostToolUse,PostToolBatch,PostToolUseFailure,Stop")
ap.add_argument("--budget-tok", default="100000"); ap.add_argument("--budget-msg", default="")
ap.add_argument("--maxturns", default=""); ap.add_argument("--extra-hooks", default="")
ap.add_argument("--files", default="")  # name=content pairs separated by ||
ap.add_argument("--cap", default="0.30"); ap.add_argument("--copy-task", default=""); ap.add_argument("--start-note", default=""); ap.add_argument("--fire80", default="1")
a = ap.parse_args()
base = os.path.join(ROOT, "runs", a.cell); shutil.rmtree(base, ignore_errors=True)
work = os.path.join(base, "work"); os.makedirs(work)
for kv in filter(None, a.files.split("||")):
    k, v = kv.split("=", 1); open(os.path.join(work, k), "w").write(v.replace("\\n", "\n"))
if a.copy_task:
    for f in os.listdir(a.copy_task): shutil.copy(os.path.join(a.copy_task, f), work)
hk = {"type": "command", "command": "python3 -I %s/hook.py" % HERE, "timeout": 20}
settings = {"hooks": {e: [{"hooks": [hk]}] for e in a.events.split(",")}}
if a.extra_hooks: settings = json.load(open(a.extra_hooks))
sp = os.path.join(base, "settings.json"); json.dump(settings, open(sp, "w"), indent=1)
ag = {"worker": {"description": "worker subagent", "prompt": a.agent_prompt, "model": "haiku"}}
if a.maxturns: ag["worker"]["maxTurns"] = int(a.maxturns)
cmd = ["claude", "-p", "--model", "haiku", "--setting-sources", "project", "--settings", sp, "--agents", json.dumps(ag),
       "--output-format", "stream-json", "--verbose", "--strict-mcp-config", "--permission-mode", a.perm, a.prompt]
if a.cap != "none": cmd[-1:-1] = ["--max-budget-usd", a.cap]
if a.perm in ("default", "acceptEdits", "dontAsk"): cmd[-1:-1] = ["--allowedTools=Bash,Read,Write,Agent,Task"]
env = dict(os.environ)
env.update(HOOK_LOG=os.path.join(base, "hooks.jsonl"), HOOK_MODE=a.hook_mode, HOOK_STATE=base, BUDGET_TOK=a.budget_tok)
if a.budget_msg: env["BUDGET_MSG"] = a.budget_msg
if a.start_note: env["BUDGET_START_NOTE"] = a.start_note
env["BUDGET_FIRE80"] = a.fire80
if os.environ.get("BUDGET_HARD"): env["BUDGET_HARD"] = os.environ["BUDGET_HARD"]
if os.environ.get("HOOK_RAW"): env["HOOK_RAW"] = os.environ["HOOK_RAW"]
t0 = time.time()
p = subprocess.run(cmd, capture_output=True, text=True, cwd=work, env=env, timeout=500)
open(os.path.join(base, "stdout.jsonl"), "w").write(p.stdout); open(os.path.join(base, "stderr.txt"), "w").write(p.stderr)
res = None
for line in p.stdout.splitlines():
    try: r = json.loads(line)
    except Exception: continue
    if r.get("type") == "result": res = r
print(json.dumps({"cell": a.cell, "rc": p.returncode, "wall_s": round(time.time() - t0, 1), "usd": res and res.get("total_cost_usd"),
                  "turns": res and res.get("num_turns"), "result": res and (res.get("result") or "")[:1500]}, indent=1))
