# w06-c4: runs one headless `claude -p` scenario against an export of the Murmuration plugin at a given commit (arm main or new), in a fresh lab folder, under /private/tmp/murmuration-w06/author-w06-4/; inputs: name, commit, scenario (base|block|outage_a|outage_b|outage_c|mutant), optional --wrap (server started through a wrapper that records its pid and honours a refuse file; outage and mutant tests only); outputs: <S>/runs/<name>/{run.json,dbg.log,lab/} and the session transcripts left in ~/.claude/projects (named in run.json's session_id)
import json, os, shutil, subprocess, sys, time

S = "/private/tmp/murmuration-w06/author-w06-4"
name, commit, scen = sys.argv[1:4]
wrap = "--wrap" in sys.argv
R = "%s/runs/%s" % (S, name)
lab = R + "/lab"
shutil.rmtree(R, ignore_errors=True)
os.makedirs(lab + "/__statera__"); os.makedirs(lab + "/__reports__")
plug = "%s/export_%s%s" % (S, commit, "_wrap" if wrap else "")
if not os.path.isdir(plug):   # git archive of the commit; the agents' models become haiku (cost), and with --wrap the server starts through a wrapper (pid file, refuse file)
    os.makedirs(plug)
    subprocess.run("git -C %s archive %s | tar -x -C %s" % (os.environ.get("REPO", os.getcwd()), commit, plug), shell=True, check=True)
    for a in os.listdir(plug + "/agents"):
        t = open(plug + "/agents/" + a).read()
        open(plug + "/agents/" + a, "w").write("".join("model: haiku\n" if l.startswith("model:") else l for l in t.splitlines(True)))
    if wrap and os.path.exists(plug + "/.mcp.json"):
        w = ("case $(cat %s/refuse 2>/dev/null) in exit) exit 1;; hang) sleep 600;; esac; echo $$ > %s/server.pid; echo $$ >> %s/server.starts; exec python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hook_server.py") % (S, S, S)
        json.dump({"mcpServers": {"hooks": {"command": "sh", "args": ["-c", w]}}}, open(plug + "/.mcp.json", "w"))


def worker(n, extra="", T="5"):
    return "Your name is explorer-w99-%s.\nBudget: USD 0.50\nTime: min %s\n%sThen call SubagentHandback with message `done`." % (n, T, extra)


def lead(workers, tail=""):
    steps = ["Step 1: run Bash `echo main-1`."]
    for n, prompt in workers:
        steps.append("Step %d: call the Agent tool with subagent_type `murmuration:explorer`, name `explorer-w99-%s` and this exact prompt (between the markers, markers excluded) and wait for it: <<<%s>>>" % (len(steps) + 1, n, prompt))
    return " ".join(steps) + tail + " Last step: reply with one line per worker giving its report text."


B = "Run Bash `echo a-%s`, then Bash `echo b-%s`. "
SC = {
    "base": lead([(str(i), worker(i, B % (i, i))) for i in range(2)]),
    "block": lead([("0", worker(0, "Run Bash `sleep 12`, then Bash `echo c`, then Bash `echo d`. ", "0.1"))]),
    "outage_a": ("Step 1: run Bash `echo before`. Step 2: run Bash `kill $(cat %s/server.pid); sleep 2`. Step 3: run Bash `echo after-1`. " % S) + lead([("0", worker(0, B % (0, 0)))])[len("Step 1: run Bash `echo main-1`. "):].replace("Step 2:", "Step 4:").replace("Step 3:", "Step 5:"),
}
SC["outage_b"] = SC["outage_c"] = SC["outage_a"]
SC["mutant"] = SC["base"]
perm = os.environ.get("PERM", "auto")
cmd = ["claude", "-p", SC[scen], "--model", "haiku", "--agent", "murmuration:research-pi", "--plugin-dir", plug, "--permission-mode", perm,
       "--debug-file", R + "/dbg.log", "--output-format", "json"]
t0 = time.time()
r = subprocess.run(cmd, cwd=lab, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=int(os.environ.get("W4_TIMEOUT", "280")),
                   env=dict(os.environ, CLAUDE_CODE_SHELL="/bin/bash"))
open(R + "/run.json", "w").write(r.stdout)
open(R + "/run.err", "w").write(r.stderr)
print(name, "rc", r.returncode, "wall_s", round(time.time() - t0, 1), "out", len(r.stdout))
