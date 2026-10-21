# Runs the live r2-r5 sessions of w07-c5: exports the branch commit as the plugin (hooks.json with the async user_words row), builds a throwaway "mixed" plugin (main's script sync, a crashing script sync and async), and runs `claude -p` (haiku, default permission mode, --debug-file) in scratch labs; inputs: argv[1] = work folder under /private/tmp, argv[2] = main's user_words.py, argv[3..] = session names to run (f00..f09 first prompts: even = Desktop-like env, odd = terminal-like env; t-resume = second prompt of f01's session; mixed = main sync + crash sync + crash async); outputs: <work>/runs.jsonl, <work>/dbg-<name>.log, <work>/lab-<name>/, <work>/out-<name>.json.
import json, os, subprocess, sys, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, ".."))
work = os.path.abspath(sys.argv[1]); main_script = os.path.abspath(sys.argv[2]); names = sys.argv[3:]
assert work.startswith("/private/tmp/")
os.makedirs(work, exist_ok=True)
export = os.path.join(work, "export")
if not os.path.exists(export):
    os.makedirs(export)
    subprocess.run("git -C %s archive HEAD | tar -x -C %s" % (REPO, export), shell=True, check=True)
    open(os.path.join(work, "export.commit"), "w").write(subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout)
mixed = os.path.join(work, "mixed-plugin")
if not os.path.exists(mixed):
    os.makedirs(os.path.join(mixed, ".claude-plugin")); os.makedirs(os.path.join(mixed, "hooks"))
    json.dump({"name": "w07c5-mixed", "version": "0.0.1", "description": "throwaway for w07-c5 r5"}, open(os.path.join(mixed, ".claude-plugin", "plugin.json"), "w"))
    crash = os.path.join(mixed, "crash_words.py")
    src = open(os.path.join(export, "scripts", "user_words.py")).read()
    open(crash, "w").write(src.replace("import datetime\n", "import datetime\nimport w07c5_no_such_module\n", 1))  # an import error escapes the script's own handlers
    shutil.copy(main_script, os.path.join(mixed, "main_words.py"))
    row = lambda cmd, **kw: dict({"type": "command", "command": cmd, "timeout": 10}, **kw)
    json.dump({"hooks": {"UserPromptSubmit": [{"hooks": [row('python3 "${CLAUDE_PLUGIN_ROOT}/main_words.py"'), row('python3 "${CLAUDE_PLUGIN_ROOT}/crash_words.py"'), row('python3 "${CLAUDE_PLUGIN_ROOT}/crash_words.py"', **{"async": True})]}]}}, open(os.path.join(mixed, "hooks", "hooks.json"), "w"))
DROP = ("CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_SESSION_ATTENDED", "CLAUDE_CODE_HOST_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "CLAUDECODE", "CLAUDE_CODE_DESKTOP_APP_VERSION", "CLAUDE_AGENT_SDK_VERSION", "CLAUDE_CODE_ENTRYPOINT_ON_REQUESTS", "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN")
runs = open(os.path.join(work, "runs.jsonl"), "a")
def run(name, prompt, plugin, drop=(), resume=None, lab_name=None):
    lab = os.path.join(work, "lab-" + (lab_name or name)); os.makedirs(os.path.join(lab, "__statera__"), exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k not in drop}; env["CLAUDE_CODE_SHELL"] = "/bin/bash"; env.pop("CLAUDE_PROJECT_DIR", None)
    cmd = ["claude", "-p", prompt, "--model", "haiku", "--plugin-dir", plugin, "--output-format", "json", "--permission-mode", "default", "--debug-file", os.path.join(work, "dbg-%s.log" % name)]
    if resume: cmd += ["--resume", resume]
    t_wall = time.time(); p = subprocess.run(cmd, cwd=lab, env=env, capture_output=True, text=True, timeout=240, stdin=subprocess.DEVNULL)
    open(os.path.join(work, "out-%s.json" % name), "w").write(p.stdout)
    try: res = json.loads(p.stdout)
    except ValueError: res = {}
    rec = {"name": name, "rc": p.returncode, "t_start": t_wall, "t_end": time.time(), "session_id": res.get("session_id"), "cost_usd": res.get("total_cost_usd"), "terminal_like": bool(drop), "resume": bool(resume), "plugin": os.path.basename(plugin)}
    runs.write(json.dumps(rec) + "\n"); runs.flush(); print(rec, flush=True); return rec
def sid_of(name):
    for l in open(os.path.join(work, "runs.jsonl")):
        d = json.loads(l)
        if d["name"] == name and not d["resume"]: return d["session_id"]
for n in names:
    if n.startswith("f"): run(n, "Reply with the single word ok.", export, drop=DROP if int(n[1:]) % 2 else ())
    elif n == "t-resume": run(n, "Reply with the word again.", export, drop=DROP, resume=sid_of("f01"), lab_name="f01")
    elif n == "mixed": run(n, "Reply with the single word ok.", mixed)
