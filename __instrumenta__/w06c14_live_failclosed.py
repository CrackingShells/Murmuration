# w06-c14: two headless haiku sessions (default permission mode, Bash allowed, stub `claude` first on PATH) against `git archive` of a commit with the lean guard command: a control with the guard readable (the call must run and MURMURATION_GUARD_LOG must get one line, which shows the variable passes `-I`) and a run with scripts/permission_guard.py at mode 000 (the call must not run: fail closed); inputs: commit; outputs: per run the tool_result texts, hook events, guard.log, and a PASS/FAIL line, on stdout; raw runs stay under /private/tmp/murmuration-w06/author-w06-7/live/
import json, os, shutil, subprocess, sys, time
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
commit = sys.argv[1]
B = "/private/tmp/murmuration-w06/author-w06-7/live"
shutil.rmtree(B, ignore_errors=True); os.makedirs(B + "/stubbin")
open(B + "/stubbin/claude", "w").write("#!/bin/sh\necho \"stub claude: $*\" >> %s/stub.log\n" % B); os.chmod(B + "/stubbin/claude", 0o755)
CLAUDE = shutil.which("claude")
MARK = "w06c14-marker-%d" % os.getpid()
res = {}
for name in ("readable", "unreadable"):
    R = "%s/%s" % (B, name); ex = R + "/export"; lab = R + "/lab"
    os.makedirs(ex); os.makedirs(lab)
    subprocess.run("git -C %s archive %s | tar -x -C %s" % (REPO, commit, ex), shell=True, check=True)
    if name == "unreadable":
        os.chmod(ex + "/scripts/permission_guard.py", 0)
    cmd = [CLAUDE, "-p", "Call the Bash tool once with exactly this command: `echo %s`. Then reply with the word done." % MARK, "--model", "haiku",
           "--plugin-dir", ex, "--permission-mode", "default", "--allowedTools", "Bash", "--output-format", "stream-json", "--verbose", "--include-hook-events", "--debug-file", R + "/dbg.log"]
    env = dict(os.environ, PATH=B + "/stubbin:" + os.environ["PATH"], CLAUDE_CODE_SHELL="/bin/bash", MURMURATION_GUARD_LOG=R + "/guard.log")
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=lab, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=200, env=env); out = r.stdout
    except subprocess.TimeoutExpired as e:
        out = (e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout) or ""
    open(R + "/stream.jsonl", "w").write(out)
    results = []
    for line in out.splitlines():
        try: m = json.loads(line)
        except ValueError: continue
        if m.get("type") == "user":
            for b in (m.get("message", {}).get("content") or []):
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    c = b.get("content"); results.append(c if isinstance(c, str) else json.dumps(c))
    ran = any(MARK in x and "Error" not in x and "blocked" not in x.lower() and "hook" not in x.lower() for x in results)
    glog = open(R + "/guard.log").read().strip().splitlines() if os.path.exists(R + "/guard.log") else []
    res[name] = dict(ran=ran, results=[x[:300] for x in results], guard_log_lines=len(glog), wall_s=round(time.time() - t0, 1))
    print(name, json.dumps(res[name]))
    if name == "unreadable": os.chmod(ex + "/scripts/permission_guard.py", 0o644)
ok = res["readable"]["ran"] and res["readable"]["guard_log_lines"] == 1 and not res["unreadable"]["ran"] and res["unreadable"]["results"]
print("PASS" if ok else "FAIL", "(readable: call ran + 1 guard log line; unreadable: call did not run, a blocked result came back)")
