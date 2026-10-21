# Runs the live q2 sessions of w07-c2: builds a throwaway plugin (probe hook + the branch's user_words.py as UserPromptSubmit hooks) and scratch labs under argv[1], runs `claude -p` (haiku) in each lab, and writes probe logs and a runs.jsonl; inputs: argv[1] = work folder (under /private/tmp), optional argv[2] = number of first-prompt sessions (default 10), `--quick` = 2 sessions and no variants; outputs: <work>/probe.jsonl, <work>/runs.jsonl, <work>/lab-*/__statera__/user_words.md.
import json, os, subprocess, sys, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
work = os.path.abspath(sys.argv[1]); quick = "--quick" in sys.argv
n_first = 2 if quick else (int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10)
assert work.startswith("/private/tmp/")
uw = os.path.abspath(os.path.join(HERE, "..", "scripts", "user_words.py"))
probe_log = os.path.join(work, "probe.jsonl")
def make_plugin(name, with_words):
    plug = os.path.join(work, name)
    os.makedirs(os.path.join(plug, ".claude-plugin"), exist_ok=True); os.makedirs(os.path.join(plug, "hooks"), exist_ok=True)
    shutil.copy(os.path.join(HERE, "w07c2_probe_hook.py"), os.path.join(plug, "probe_hook.py"))
    json.dump({"name": name, "version": "0.0.1", "description": "throwaway probe for w07-c2"}, open(os.path.join(plug, ".claude-plugin", "plugin.json"), "w"))
    hooks = [{"type": "command", "command": 'python3 -I "${CLAUDE_PLUGIN_ROOT}/probe_hook.py" %s detach' % probe_log, "timeout": 10}]
    if with_words: hooks.append({"type": "command", "command": 'python3 "%s"' % uw, "timeout": 10})
    json.dump({"hooks": {"UserPromptSubmit": [{"hooks": hooks}]}}, open(os.path.join(plug, "hooks", "hooks.json"), "w"))
    return plug
PLUGS = {"both": make_plugin("probe-plugin-both", True), "probe": make_plugin("probe-plugin-only", False)}
runs = open(os.path.join(work, "runs.jsonl"), "a")
def run(name, prompt, env_drop=(), resume=None, plugin="both", lab_name=None):
    lab = os.path.join(work, "lab-" + (lab_name or name))
    os.makedirs(os.path.join(lab, "__statera__"), exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k not in env_drop}
    env["CLAUDE_CODE_SHELL"] = "/bin/bash"; env.pop("CLAUDE_PROJECT_DIR", None)
    cmd = ["claude", "-p", prompt, "--model", "haiku", "--plugin-dir", PLUGS[plugin], "--output-format", "json", "--permission-mode", "default"]
    if resume: cmd += ["--resume", resume]
    t = time.time()
    p = subprocess.run(cmd, cwd=lab, env=env, capture_output=True, text=True, timeout=240)
    try: res = json.loads(p.stdout)
    except ValueError: res = {}
    rec = {"name": name, "rc": p.returncode, "wall_s": round(time.time() - t, 2), "session_id": res.get("session_id"), "cost_usd": res.get("total_cost_usd"), "env_dropped": list(env_drop), "resume": bool(resume), "plugin": plugin, "stderr": p.stderr[-200:]}
    runs.write(json.dumps(rec) + "\n"); runs.flush(); print(rec, flush=True)
    return res.get("session_id")
for i in range(n_first):
    run("f%02d" % i, "Reply with the single word ok.")
if not quick:
    drop = ("CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_SESSION_ATTENDED", "CLAUDE_CODE_HOST_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "CLAUDECODE", "CLAUDE_CODE_DESKTOP_APP_VERSION", "CLAUDE_AGENT_SDK_VERSION", "CLAUDE_CODE_ENTRYPOINT_ON_REQUESTS", "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN")
    run("t00", "Reply with the single word ok.", env_drop=drop)  # terminal-like start: no Desktop entrypoint, no parent-session markers
    p = run("p00", "Reply with the single word ok.", plugin="probe")  # the probe alone: the hook returns at once
    sid = json.loads(open(os.path.join(work, "runs.jsonl")).readline()).get("session_id")
    if sid: run("r-f00", "Reply with the word again.", resume=sid, lab_name="f00")  # a later prompt
    if p: run("r-p00", "Reply with the word again.", resume=p, plugin="probe", lab_name="p00")
