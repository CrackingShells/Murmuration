# w07-c6 g2, live part: three headless haiku sessions (default permission mode, all Bash allowed, a stub `claude` first on PATH so that nothing real can start), one per failure of the binary: Bstub (crash on call 1, hang on call 2 past the 20 s timeout, the real binary from call 3), Bro (data folder read-only, so the SessionStart copy fails and the binary is missing), Bnobin (no binary for the platform, so the Python launcher decides six commands, two of them allowed and four denied by the rules); inputs: scratch folder S with exp_* from w07c6_make_exports.py, the prompt files S/p_stub.txt, S/p_bro.txt, S/p_launcher.txt; outputs: S/g2/<variant>.jsonl (stream-json with hook events), S/g2/<variant>.dbg, S/g2/summary.txt.
# usage: python3 -I __instrumenta__/w07c6_g2_live.py S [variant ...]   (default: Bstub Bro Bnobin; the data folder of Bro is created read-only before its session and removed after)
import json, os, shutil, subprocess, sys, time
S = os.path.abspath(sys.argv[1]); variants = sys.argv[2:] or ["Bstub", "Bro", "Bnobin"]
CLAUDE = shutil.which("claude")
os.makedirs(S + "/g2", exist_ok=True)
PROMPT = {"Bstub": "p_stub.txt", "Bro": "p_bro.txt", "Bnobin": "p_launcher.txt"}
for v in variants:
    data = os.path.expanduser("~/.claude/plugins/data/w07c6-%s-inline" % v.lower())
    if v == "Bro":
        shutil.rmtree(data, ignore_errors=True); os.makedirs(data); os.chmod(data, 0o500)
    elif v in ("Bstub", "Bnobin"):
        shutil.rmtree(data, ignore_errors=True)
    for f in ("stub_counter",):
        if os.path.exists(S + "/" + f): os.remove(S + "/" + f)
    if os.path.exists(S + "/stub.log"): os.remove(S + "/stub.log")
    prompt = open(S + "/" + PROMPT[v]).read()
    env = dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash", PATH=S + "/stubbin:" + os.environ["PATH"])
    cmd = [CLAUDE, "-p", prompt, "--model", "haiku", "--permission-mode", "default", "--allowedTools", "Bash", "--output-format", "stream-json", "--verbose", "--include-hook-events",
           "--debug-file", "%s/g2/%s.dbg" % (S, v), "--plugin-dir", "%s/exp_%s" % (S, v)]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=S + "/work", capture_output=True, text=True, timeout=400, env=env)
    open("%s/g2/%s.jsonl" % (S, v), "w").write(r.stdout)
    stub = open(S + "/stub.log").read() if os.path.exists(S + "/stub.log") else ""
    open(S + "/g2/summary.txt", "a").write("%s rc %d %.1fs stub.log lines %d\n" % (v, r.returncode, time.time() - t0, len(stub.splitlines())))
    print(v, "rc", r.returncode, "%.1fs" % (time.time() - t0), "stub claude calls", len(stub.splitlines()), flush=True)
    if v == "Bro":
        os.chmod(data, 0o700); shutil.rmtree(data, ignore_errors=True)
