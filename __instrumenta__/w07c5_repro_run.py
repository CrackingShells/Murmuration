# Runs reproducer-w07-2's live sessions for w07-c2/w07-c5: exports the branch commit (v1, async) and main's tree as plugins, builds crashing variants, and runs `claude` (haiku, default permission mode, --debug-file) in scratch labs; inputs: argv[1] = work folder under /private/tmp, argv[2] = path of the author's worktree (branch w07-p2-origin), argv[3] = main's checkout path, argv[4..] = session names (i0-i2 inherited env, c0-c1 11 CLAUDE_* variables dropped, s0-s1 every CLAUDE* variable dropped, s0r resume of s0 with a second prompt, m-i0 m-i1 m-c0 m-c1 = main's tree (sync script), x-sync = main's tree with a crashing user_words.py, x-async = branch tree with a crashing user_words.py, p1 = interactive typed prompt through a pty, p2 = interactive typed prompt then an immediate exit); outputs: <work>/runs.jsonl, dbg-<name>.log, out-<name>.json, lab-<name>/.
import json, os, subprocess, sys, time, shutil, pty, select, signal, fcntl, termios, struct
work = os.path.abspath(sys.argv[1]); BR = os.path.abspath(sys.argv[2]); MAIN = os.path.abspath(sys.argv[3]); names = sys.argv[4:]
assert work.startswith("/private/tmp/")
os.makedirs(work, exist_ok=True)
def export(repo, rev, dest):
    if os.path.exists(dest): return
    os.makedirs(dest); subprocess.run("git -C %s archive %s | tar -x -C %s" % (repo, rev, dest), shell=True, check=True)
    open(dest + ".rev", "w").write(subprocess.run(["git", "-C", repo, "rev-parse", rev], capture_output=True, text=True).stdout)
export(BR, "HEAD", work + "/exp-branch"); export(MAIN, "main", work + "/exp-main")
def crashing(src, dest):
    if os.path.exists(dest): return
    shutil.copytree(src, dest, symlinks=True)
    p = dest + "/scripts/user_words.py"; s = open(p).read()
    assert "import datetime\n" in s
    open(p, "w").write(s.replace("import datetime\n", "import datetime\nimport repro_no_such_module\n", 1))
crashing(work + "/exp-main", work + "/exp-main-crash"); crashing(work + "/exp-branch", work + "/exp-branch-crash")
DROP11 = ("CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_SESSION_ATTENDED", "CLAUDE_CODE_HOST_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "CLAUDECODE", "CLAUDE_CODE_DESKTOP_APP_VERSION", "CLAUDE_AGENT_SDK_VERSION", "CLAUDE_CODE_ENTRYPOINT_ON_REQUESTS", "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN")
runs = open(work + "/runs.jsonl", "a")
def mkenv(kind, lab):
    env = dict(os.environ)
    if kind == "c": env = {k: v for k, v in env.items() if k not in DROP11}
    if kind == "s": env = {k: v for k, v in env.items() if not k.startswith("CLAUDE")}
    env["CLAUDE_CODE_SHELL"] = "/bin/bash"; env.pop("CLAUDE_PROJECT_DIR", None)
    return env
def mklab(name):
    lab = work + "/lab-" + name; os.makedirs(lab + "/__statera__", exist_ok=True); return lab
def log(rec): runs.write(json.dumps(rec) + "\n"); runs.flush(); print(rec, flush=True)
def run_p(name, kind, plugin, prompt, resume=None, labname=None):
    lab = mklab(labname or name); env = mkenv(kind, lab)
    cmd = ["claude", "-p", prompt, "--model", "haiku", "--plugin-dir", plugin, "--output-format", "json", "--permission-mode", "default", "--debug-file", work + "/dbg-%s.log" % name]
    if resume: cmd += ["--resume", resume]
    t0 = time.time(); p = subprocess.run(cmd, cwd=lab, env=env, capture_output=True, text=True, timeout=240, stdin=subprocess.DEVNULL)
    open(work + "/out-%s.json" % name, "w").write(p.stdout); res = {}
    try: res = json.loads(p.stdout)
    except ValueError: pass
    log({"name": name, "kind": kind, "plugin": os.path.basename(plugin), "rc": p.returncode, "t_start": t0, "t_end": time.time(), "session_id": res.get("session_id"), "cost_usd": res.get("total_cost_usd"), "result": (res.get("result") or "")[:80], "stderr": p.stderr[-200:], "prompt": prompt, "lab": lab})
def run_pty(name, plugin, prompt, quick_exit):
    lab = mklab(name); env = mkenv("s", lab); env["TERM"] = "xterm-256color"
    cmd = ["claude", "--model", "haiku", "--plugin-dir", plugin, "--permission-mode", "default", "--debug-file", work + "/dbg-%s.log" % name]
    pid, fd = pty.fork()
    if pid == 0:
        fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 120, 0, 0))
        os.chdir(lab); os.execvpe("claude", cmd, env)
    buf = b""; t0 = time.time(); sent = False; t_sent = None
    def pump(sec):
        nonlocal buf
        end = time.time() + sec
        while time.time() < end:
            r, _, _ = select.select([fd], [], [], 0.1)
            if r:
                try: d = os.read(fd, 65536)
                except OSError: return False
                if not d: return False
                buf += d
        return True
    trust = 0
    for _ in range(40):
        pump(0.5)
        txt = buf.decode("utf-8", "replace")
        if ("trust" in txt.lower() or "Yes, proceed" in txt) and trust < 3 and "Try \"" not in txt[-3000:]:
            os.write(fd, b"\r"); trust += 1; buf = b""; pump(1.5); continue
        if "? for shortcuts" in txt or "Try \"" in txt or "bypass" in txt.lower() and "shortcuts" in txt: break
    t_ready = time.time()
    open(work + "/pty-%s.txt" % name, "wb").write(buf)
    os.write(fd, prompt.encode()); pump(0.3); os.write(fd, b"\r"); t_sent = time.time()
    if quick_exit:
        pump(0.15); os.write(fd, b"\x03"); pump(0.15); os.write(fd, b"\x03"); pump(1.5)
    else:
        pump(14)
        os.write(fd, b"/exit\r"); pump(3)
    try: os.kill(pid, signal.SIGTERM)
    except OSError: pass
    try: os.waitpid(pid, 0)
    except OSError: pass
    open(work + "/pty-%s.txt" % name, "wb").write(buf)
    log({"name": name, "kind": "pty", "plugin": os.path.basename(plugin), "t_start": t0, "t_ready": t_ready, "t_sent": t_sent, "quick_exit": quick_exit, "prompt": prompt, "lab": lab, "trust_enters": trust})
def sid_of(name):
    for l in open(work + "/runs.jsonl"):
        d = json.loads(l)
        if d["name"] == name: return d["session_id"]
B, M = work + "/exp-branch", work + "/exp-main"
if any(n.startswith("v0-") for n in names): export(BR, "b2ab80d", work + "/exp-v0")  # v0 script, synchronous row, 0.3 s poll
P1 = "Reply with the single word ok."
for n in names:
    if n[0] == "i": run_p(n, "i", B, P1)
    elif n[0] == "c": run_p(n, "c", B, P1)
    elif n == "s0r": run_p(n, "s", B, "Reply with the word again.", resume=sid_of("s0"), labname="s0")
    elif n[0] == "s": run_p(n, "s", B, P1)
    elif n.startswith("v0-"): run_p(n, "i", work + "/exp-v0", P1)
    elif n.startswith("m-"): run_p(n, n[2], M, P1)
    elif n == "x-sync": run_p(n, "i", work + "/exp-main-crash", P1)
    elif n == "x-async": run_p(n, "i", work + "/exp-branch-crash", P1)
    elif n == "p1": run_pty(n, B, "Reply with the single word ok.", False)
    elif n == "p2": run_pty(n, B, "Reply with the single word ok.", True)
