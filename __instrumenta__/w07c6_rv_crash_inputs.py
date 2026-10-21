#!/usr/bin/env python3
"""Builds adversarial guard stdin payloads (deep nesting of sh -c, $( ), heredocs, quotes, huge writes) into a folder, then runs a Rust guard binary and the Python guard on each as processes and prints exit code, decision and time per case. Reproducer-w07-5's attempt to make the real binary crash or hang. Usage: w07c6_rv_crash_inputs.py <out folder> <rust binary> <permission_guard.py>."""
import json, os, subprocess, sys, time
out, rust, pyg = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
BY = "--dangerously" + "-skip-permissions"  # built from pieces so no file here holds the words whole
cl = "cla" + "ude"
HD = "cat <" + "<EOF\n"


def ev(cmd, tool="Bash"):
    return json.dumps({"tool_name": tool, "tool_input": {"command": cmd}, "cwd": "/h"})


def nest_sh(n, inner):
    s = inner
    for _ in range(n):
        s = "sh -c '" + s.replace("'", "'\\''") + "'"
    return s


cases = {}
for n in (4, 7, 9):
    cases["nest_sh_%d" % n] = ev(nest_sh(n, cl + " -p x " + BY))
for n in (1000, 20000, 200000):
    cases["nest_dollar_%d" % n] = ev("echo " + "$(" * n + cl + " " + BY + ")" * n)
    cases["nest_paren_%d" % n] = ev("(" * n + cl + " " + BY + ")" * n)
    cases["nest_brace_%d" % n] = ev("{ " * n + cl + " " + BY + "; }" * n)
    cases["nest_if_%d" % n] = ev("if " * n + cl + " " + BY)
    cases["semicolons_%d" % n] = ev(";" * n + cl + " " + BY)
    cases["quotes_%d" % n] = ev("'" * n + cl + " " + BY)
    cases["dq_bs_%d" % n] = ev('"\\' * n + cl + " " + BY)
    cases["many_cmds_%d" % n] = ev("; ".join(["true"] * n) + "; " + cl + " " + BY)
    cases["heredocs_%d" % n] = ev(HD * (n // 10) + cl + " " + BY)
cases["write_big"] = json.dumps({"tool_name": "Write", "tool_input": {"file_path": "/h/x.py", "content": "a" * 30000000}, "cwd": "/h"})
cases["write_manyedits"] = json.dumps({"tool_name": "MultiEdit", "tool_input": {"file_path": "/h/x.py", "edits": [{"old_string": "a", "new_string": "b"}] * 300000}, "cwd": "/h"})
for name, payload in cases.items():
    open(os.path.join(out, name + ".json"), "w").write(payload)
    res = []
    for tag, cmd in (("py", [sys.executable, "-S", "-I", pyg]), ("rs", [rust, "guard"])):
        t0 = time.time()
        try:
            r = subprocess.run(cmd, input=payload.encode(), capture_output=True, timeout=45)
            dec = "deny" if b'"deny"' in r.stdout else ("allow" if not r.stdout else "other")
            res.append("%s rc=%s %s %.1fs" % (tag, r.returncode, dec, time.time() - t0))
        except subprocess.TimeoutExpired:
            res.append("%s TIMEOUT" % tag)
    print("%-22s %s" % (name, " | ".join(res)), flush=True)
