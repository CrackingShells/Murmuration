# w07-c3: x1, shows that two hooks.json files (A shell form, B exec form) differ only in `command` turning into `command` + `args` with every argument equal after the shell's own word splitting of A's string; inputs: A.json B.json (paths) [--mutant]; output: one line per check, PASS/FAIL, exit 1 on FAIL
"""usage: w07c3_x1_form.py A.json B.json [--mutant]
Checks, for every handler of every row (event, matcher group, position): (1) same events, same groups in the same order, same matchers, same number of handlers; (2) every key other than `command` and `args`
is equal (type, `if`, timeout, onFailure, ...); (3) A has no `args`, B has `args` (a list of strings); (4) argv equality by two routes: `shlex.split(A.command)` equals [B.command] + B.args, and a real `sh` splits A.command
(the executable replaced by a printer of its arguments, the plugin root placeholder replaced by a path with a space and an apostrophe, as the platform substitutes it) into the same arguments as B's list after
the same substitution. --mutant changes one argument of B in memory first: every check that compares arguments must then FAIL (it shows the check can fail)."""
import json, shlex, subprocess, sys

a, b = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
if "--mutant" in sys.argv:
    for g in b["hooks"]["PostToolUse"]:
        g["hooks"][0]["args"][-1] = g["hooks"][0]["args"][-1] + "X"
        break
ROOT = "/tmp/w07 c3/ro'ot"
fails = []
def fail(msg):
    fails.append(msg)

if list(a["hooks"]) != list(b["hooks"]):
    fail("events differ: %s vs %s" % (list(a["hooks"]), list(b["hooks"])))
n = nargv = nshell = 0
for ev in a["hooks"]:
    ga, gb = a["hooks"][ev], b["hooks"].get(ev, [])
    if len(ga) != len(gb):
        fail("%s: %d groups vs %d" % (ev, len(ga), len(gb))); continue
    for i, (x, y) in enumerate(zip(ga, gb)):
        if {k: v for k, v in x.items() if k != "hooks"} != {k: v for k, v in y.items() if k != "hooks"}:
            fail("%s[%d]: group keys differ" % (ev, i))
        if len(x["hooks"]) != len(y["hooks"]):
            fail("%s[%d]: handler counts differ" % (ev, i)); continue
        for j, (ha, hb) in enumerate(zip(x["hooks"], y["hooks"])):
            n += 1; where = "%s[%d][%d]" % (ev, i, j)
            if {k: v for k, v in ha.items() if k != "command"} != {k: v for k, v in hb.items() if k not in ("command", "args")}:
                fail(where + ": keys other than command/args differ")
            if "args" in ha or not isinstance(hb.get("args"), list) or not all(isinstance(t, str) for t in hb["args"]):
                fail(where + ": args present in A or missing/not a string list in B"); continue
            if shlex.split(ha["command"]) != [hb["command"]] + hb["args"]:
                fail(where + ": shlex.split(A) != [command]+args");
            else:
                nargv += 1
            sub = lambda s: s.replace("${CLAUDE_PLUGIN_ROOT}", ROOT)
            first, _, rest = ha["command"].partition(" ")
            probe = "printf '%s\\n' " + sub(rest)          # a real shell splits what follows the executable
            got = subprocess.run(["sh", "-c", probe], capture_output=True, text=True).stdout.split("\n")[:-1]
            if first != hb["command"] or got != [sub(t) for t in hb["args"]]:
                fail(where + ": real sh splitting differs: %r vs %r" % (got, [sub(t) for t in hb["args"]]))
            else:
                nshell += 1
print("handlers compared: %d; shlex argv equal: %d; real-sh argv equal: %d; failures: %d" % (n, nargv, nshell, len(fails)))
for f in fails[:10]:
    print("  FAIL", f)
print("PASS" if not fails else "FAIL")
sys.exit(1 if fails else 0)
