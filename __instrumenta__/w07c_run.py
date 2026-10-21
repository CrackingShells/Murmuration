"""Runs one w07-c probe session: builds a throwaway plugin `w7c` for a named variant, starts the local hook server (own pid), runs one `claude -p --model haiku` session against it, stops the server by pid; inputs: VARIANT name (see VARIANTS below), optional --out DIR; outputs under DIR/<variant>/: hooks.json, run.json (claude's JSON result), dbg.log (debug file), hooks.log (command hooks' own start/end), server.log(+.bodies.jsonl), truth.jsonl (stdin of the ground-truth command hooks), transcript copies (main + subagents).
Default permission mode with --allowedTools Bash (no auto classifier, no bypass). Usage: python3 w07c_run.py VARIANT [--out /private/tmp/murmuration-w07/explorer-w07-c/runs]
"""
import json, os, shutil, signal, socket, subprocess, sys, time, glob, secrets

HERE = os.path.dirname(os.path.abspath(__file__))
variant = sys.argv[1]
OUT = os.path.abspath(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "/private/tmp/murmuration-w07/explorer-w07-c/runs")
D = os.path.join(OUT, variant); shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
P = os.path.join(D, "plugin"); CWD = os.path.join(D, "cwd")
for d in (".claude-plugin", "agents", "hooks", "scripts"): os.makedirs(os.path.join(P, d))
os.makedirs(CWD)
shutil.copy(os.path.join(HERE, "w07c_hook.py"), os.path.join(P, "scripts", "hook.py"))
json.dump({"name": "w7c", "version": "0.0.0", "description": "throwaway w07-c probe plugin"}, open(os.path.join(P, ".claude-plugin", "plugin.json"), "w"))
open(os.path.join(P, "agents", "worker.md"), "w").write("---\nname: worker\ndescription: Test worker. Does small steps exactly as told.\nmodel: haiku\ntools: Bash\nmaxTurns: 12\n---\n\nYou are a test worker. Do exactly what your brief says, step by step, keep replies short. Hand back with a short final report.\n")

TOKEN = secrets.token_hex(8)
S = lambda n: os.path.join(D, n)
dead = socket.socket(); dead.bind(("127.0.0.1", 0)); DEAD = dead.getsockname()[1]; dead.close()   # a port with no listener
need_server = not variant.startswith(("async", "sib", "exec"))
srv = None; PORT = 0
if need_server:
    env = dict(os.environ, W7C_TOKEN=TOKEN)
    srv = subprocess.Popen([sys.executable, os.path.join(HERE, "w07c_http_server.py"), "--port-file", S("port"), "--log", S("server.log")], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    open(S("server.pid"), "w").write(str(srv.pid))
    for _ in range(100):
        if os.path.exists(S("port")) and open(S("port")).read(): break
        time.sleep(0.05)
    PORT = int(open(S("port")).read())

HOOK = 'python3 -S -I "${CLAUDE_PLUGIN_ROOT}/scripts/hook.py"'
def cmd(label, only=None, sleep=None, emit=None, exit=None, stderr=None, dump=False, **extra):
    c = "%s %s" % (HOOK, label)
    if only: c += " --only %s" % only
    if sleep: c += " --sleep %s" % sleep
    if emit: c += " --emit %s" % emit
    if exit is not None: c += " --exit %d" % exit
    if stderr: c += " --stderr %s" % stderr
    if dump: c += " --dump %s" % S("truth.jsonl")
    return dict({"type": "command", "command": c}, **extra)
def exe(label, only=None, sleep=None, **kw):   # exec form: no `sh -c`
    a = ["-S", "-I", "${CLAUDE_PLUGIN_ROOT}/scripts/hook.py", label] + (["--only", only] if only else []) + (["--sleep", str(sleep)] if sleep else [])
    return {"type": "command", "command": "python3", "args": a}
def http(path, port=None, **extra):
    h = {"type": "http", "url": "http://127.0.0.1:%d%s" % (port or PORT, path), "headers": {"X-W7C-Token": "$W7C_TOKEN"}, "allowedEnvVars": ["W7C_TOKEN"]}
    h.update(extra); return h
def row(hook, matcher=None, **kw):
    g = {"hooks": [hook]}
    if matcher: g["matcher"] = matcher
    return g
def iff(word, hook): return dict(hook, **{"if": "Bash(echo %s*)" % word})

BASH = "Bash"
H = {}; PROMPT = ""; AGENTS_LEAD = ""
def steps(cmds): return "Run these Bash commands strictly one per message, in this exact order, each as its own tool call, waiting for each result before the next, and carry on even if one is blocked or refused: " + ", then ".join("`echo %s`" % c for c in cmds) + ". "

if variant == "async":
    cs = ["A-SLOW", "step2", "step3", "B-SYNC", "A-FAIL", "A-REWAKE", "ASYNCDENY", "A-BLOCK", "step9", "Z-END"]
    H["PreToolUse"] = [row(cmd("pre-async-deny", only="ASYNCDENY", emit="deny", **{"async": True}), BASH)]
    H["PostToolUse"] = [row(cmd("post-sync-fast", dump=True), BASH), row(cmd("post-async-slow", only="A-SLOW", sleep=6, emit="ctx", **{"async": True}), BASH),
        row(cmd("post-async-fail", only="A-FAIL", exit=1, stderr="ASYNC-FAIL-STDERR", **{"async": True}), BASH),
        row(cmd("post-async-rewake", only="A-REWAKE", sleep=2, exit=2, stderr="REWAKE-NONCE", **{"asyncRewake": True}), BASH),
        row(cmd("post-sync-slow", only="B-SYNC", sleep=3, emit="ctx"), BASH), row(cmd("post-async-blk", only="A-BLOCK", emit="block", **{"async": True}), BASH),
        row(cmd("post-async-last", only="Z-END", sleep=8, emit="ctx", **{"async": True}), BASH)]
    PROMPT = steps(cs) + "After the last, reply with one short line listing every string beginning CMDCTX-NONCE, REWAKE or ASYNC-FAIL that appeared anywhere in your context, and say whether `echo ASYNCDENY` was blocked."
elif variant in ("http_pre", "http_post"):
    ev = "PreToolUse" if variant == "http_pre" else "PostToolUse"; pfx = "H" if ev == "PreToolUse" else "P"
    B = {"onFailure": "block"}
    rows = [("OK", http("/ok")), ("CTX", http("/ctx")), ("DENY", http("/deny")), ("BLOCK", http("/block")),
            ("DOWN", http("/ok", port=DEAD, timeout=5, **B)), ("HANG", http("/hang", timeout=3, **B)), ("GARB", http("/garbage", **B)), ("ARR", http("/array", **B)),
            ("S500", http("/s500", **B)), ("TOKENV", {"type": "http", "url": "http://127.0.0.1:%d/ok" % PORT, "headers": {"X-W7C-Token": "$W7C_TOKEN"}, "onFailure": "block"}),
            ("XDOWNC", http("/ok", port=DEAD, timeout=5)), ("XGARBC", http("/garbage")), ("XHANGC", http("/hang", timeout=3))]
    H[ev] = [row(cmd("truth", dump=True), BASH)] + [row(iff("%s-%s" % (pfx, n), h), BASH) for n, h in rows]
    PROMPT = steps(["%s-%s" % (pfx, n) for n, _ in rows]) + "After the last, reply with one short line per command: its name, whether it ran or was blocked, and any hook message or HTTP*/CMD* string you saw, word for word."
elif variant == "http_ctl":   # default onFailure (continue): the same failures as http_pre/http_post, on Pre and Post; prefixes chosen so no `if` rule matches two commands
    rows = [("XDOWNC", http("/ok", port=DEAD, timeout=5)), ("XGARBC", http("/garbage")), ("XHANGC", http("/hang", timeout=3)), ("XS500C", http("/s500")), ("XTOKENVC", {"type": "http", "url": "http://127.0.0.1:%d/ok" % PORT, "headers": {"X-W7C-Token": "$W7C_TOKEN"}})]
    H["PreToolUse"] = [row(iff("H-" + n, h), BASH) for n, h in rows]
    H["PostToolUse"] = [row(iff("P-" + n, h), BASH) for n, h in rows]
    PROMPT = steps(["%s-%s" % (a, n) for a in "HP" for n, _ in rows]) + "After the last, reply with one short line per command: its name, whether it ran or was blocked, and any hook message or error string you saw, word for word, or none."
elif variant == "http_sub":
    H["SubagentStart"] = [row(cmd("truth", dump=True)), row(http("/ctx"))]
    H["SubagentStop"] = [row(cmd("truth", dump=True)), row(http("/blockonce"))]
    H["PostToolBatch"] = [row(cmd("truth", dump=True)), row(http("/ctx"))]
    H["PreToolUse"] = [row(http("/ok"), BASH)]
    PROMPT = "Call the Agent tool once with subagent_type `w7c:worker`, name `worker-1` and this exact prompt (between the markers, markers excluded) and wait: <<<Run Bash `echo w1`, then Bash `echo w2`, then hand back with a report that quotes word for word every string beginning HTTP that appeared in your context and every hook message you saw, or none.>>> Then reply with one line: the worker's report, and any string beginning HTTP that you yourself saw."
elif variant in ("sub_stop_dead", "batch_dead", "batch_hang", "batch_garb", "batch_ok_dead_pre"):
    B = {"onFailure": "block"}
    if variant == "sub_stop_dead": H["SubagentStop"] = [row(http("/ok", port=DEAD, timeout=5, **B))]
    elif variant == "batch_dead": H["PostToolBatch"] = [row(http("/ok", port=DEAD, timeout=5, **B))]
    elif variant == "batch_hang": H["PostToolBatch"] = [row(http("/hang", timeout=3, **B))]
    elif variant == "batch_garb": H["PostToolBatch"] = [row(http("/garbage", **B))]
    H["SessionStart"] = [row(cmd("truth", dump=True))]
    if variant == "sub_stop_dead":
        PROMPT = "Call the Agent tool once with subagent_type `w7c:worker`, name `worker-1` and prompt `Run Bash echo w1 then hand back with the word done`. Then run Bash `echo after-worker`. Then reply with one line: what the worker returned, and any hook message or error you saw."
    else:
        PROMPT = steps(["first", "second"]) + "Then reply with one line: what happened after each, and any hook message or error you saw, word for word."
elif variant.startswith(("sib", "exec")):
    form, n = ("exe", int(variant[4:])) if variant.startswith("exec") else ("cmd", int(variant[3:]))
    mk = (lambda i: exe("sib%d" % i)) if form == "exe" else (lambda i: cmd("sib%d" % i))
    mkp = (lambda i: exe("sibpre%d" % i, only="SLEEPY", sleep=0.5)) if form == "exe" else (lambda i: cmd("sibpre%d" % i, only="SLEEPY", sleep=0.5))
    H["PostToolUse"] = [{"matcher": BASH, "hooks": [mk(i) for i in range(n)]}]
    H["PreToolUse"] = [{"matcher": BASH, "hooks": [mkp(i) for i in range(n)]}]
    PROMPT = steps(["t1", "t2", "SLEEPY1", "t4", "t5", "SLEEPY2", "t7", "t8"]) + "Then reply with the word done."
else:
    raise SystemExit("unknown variant " + variant)

json.dump({"hooks": H}, open(os.path.join(P, "hooks", "hooks.json"), "w"), indent=1)
json.dump({"hooks": H}, open(S("hooks.json"), "w"), indent=1)
open(S("prompt.txt"), "w").write(PROMPT)
env = dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash", W7C_LOG=S("hooks.log"), W7C_TOKEN=TOKEN)
c = ["claude", "-p", PROMPT, "--model", "haiku", "--plugin-dir", P, "--allowedTools", "Bash", "--debug-file", S("dbg.log"), "--output-format", "json"] + (["--setting-sources", "project"] if os.environ.get("W7C_PROJECT_ONLY") else [])
t0 = time.time()
try:
    r = subprocess.run(c, cwd=CWD, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env, timeout=int(os.environ.get("W7C_TIMEOUT", "240")))
    open(S("run.json"), "w").write(r.stdout); open(S("run.err"), "w").write(r.stderr); rc = r.returncode
except subprocess.TimeoutExpired as e:
    rc = "timeout"
wall = round(time.time() - t0, 1)
if srv:
    os.kill(srv.pid, signal.SIGTERM); srv.wait(timeout=10)
    try: os.kill(srv.pid, 0); print("SERVER STILL ALIVE", srv.pid)
    except ProcessLookupError: pass
try:
    sid = json.load(open(S("run.json")))["session_id"]
    for f in glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % sid)):
        shutil.copy(f, S("transcript.jsonl"))
        sub = f[:-6] + "/subagents"
        if os.path.isdir(sub): shutil.copytree(sub, S("subagents"))
except Exception as e: print("no transcript", e)
print(variant, "rc", rc, "wall_s", wall, "port", PORT, "dead", DEAD)
