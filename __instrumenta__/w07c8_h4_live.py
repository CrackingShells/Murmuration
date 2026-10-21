# w07-c8 h4, live: two headless haiku sessions (default permission mode, all Bash allowed, CLAUDE_CODE_SHELL=/bin/bash), one with the faulty export (permission_guard.py edited after the build: the installer must fall back to the launcher and tell the session) and one with the clean export (the binary decides); inputs: scratch folder S with exp_Hfault and exp_Hclean from w07c8_make_exports.py and the prompt file S/p_h4.txt; outputs: S/h4/<variant>.jsonl (stream-json with hook events), S/h4/<variant>.dbg, and a summary on stdout; the data folders ~/.claude/plugins/data/w07c8-h{fault,clean}-inline are removed before and after.
# usage: python3 -I __instrumenta__/w07c8_h4_live.py S
import json, os, shutil, subprocess, sys, time
S = os.path.abspath(sys.argv[1]); CLAUDE = shutil.which("claude"); os.makedirs(S + "/h4", exist_ok=True)
prompt = open(S + "/p_h4.txt").read()
for v in ("Hfault", "Hclean"):
    data = os.path.expanduser("~/.claude/plugins/data/w07c8-%s-inline" % v[1:].lower()); shutil.rmtree(data, ignore_errors=True)
    cmd = [CLAUDE, "-p", prompt, "--model", "haiku", "--permission-mode", "default", "--allowedTools", "Bash", "--output-format", "stream-json", "--verbose", "--include-hook-events",
           "--debug-file", "%s/h4/%s.dbg" % (S, v), "--plugin-dir", "%s/exp_%s" % (S, v)]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=S + "/work", capture_output=True, text=True, timeout=300, env=dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash"))
    open("%s/h4/%s.jsonl" % (S, v), "w").write(r.stdout)
    b = open(data + "/bin/murmuration", "rb").read(4) if os.path.exists(data + "/bin/murmuration") else b""
    print(v, "rc", r.returncode, "%.1fs" % (time.time() - t0), "installed file starts with", b)
    shutil.rmtree(data, ignore_errors=True)
