# w06-c3: runs every stage-1 (E1) run of claim w06-c3 in sequence (build the test plugins, run the headless scenarios, then write the metric tables), under /private/tmp/murmuration-w06/author-w06-3/runs; inputs: optional --quick; outputs: run directories, tables.md beside them
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
S = "/private/tmp/murmuration-w06/author-w06-3"
quick = "--quick" in sys.argv
R = S + ("/runs_quick" if quick else "/runs")
os.makedirs(R, exist_ok=True)
py = lambda *a: subprocess.run([sys.executable, *a], check=False)
build = lambda var, name, wt, *x: py(HERE + "/w06c3_build_plugin.py", var, "%s/%s/plugin" % (R, name), wt, *x)


def run(scen, plugname, wtname, mode, perm, env=None):
    wt = "%s/%s" % (R, wtname)
    os.makedirs(wt, exist_ok=True)
    e = dict(os.environ, **(env or {}))
    r = subprocess.run([sys.executable, HERE + "/w06c3_run.py", scen, "%s/%s/plugin" % (R, plugname), wt, S + "/work", mode, perm], capture_output=True, text=True, env=e, cwd=S)
    print(wtname, scen, mode, perm, r.stdout.strip().replace("\n", " "), r.stderr.strip()[-200:], flush=True)


n_full, n_lean, n_pair, n_out = (1, 1, 1, 1) if quick else (2, 5, 3, 2)
# m1/m2/m6: platform stdin recorded beside the server (truth plugin); auto mode (SubagentHandback exists) and bypassPermissions (last_assistant_message)
for k in range(n_full):
    build("truth", "t_auto%d" % k, R + "/t_auto%d" % k); run("full2", "t_auto%d" % k, "t_auto%d" % k, "live", "auto")
    build("truth", "t_byp%d" % k, R + "/t_byp%d" % k); run("full", "t_byp%d" % k, "t_byp%d" % k, "live", "bypassPermissions")
# m5 volume (25 workers): server alone
for k in range(n_lean):
    build("live", "v%d" % k, R + "/v%d" % k); run("lean5", "v%d" % k, "v%d" % k, "live", "auto")
# m3 pairs: plugin without server against plugin with server answering nothing; same agents; order alternates
for k in range(n_pair):
    for arm in (("off", "on_") if k % 2 == 0 else ("on_", "off")):
        name = "m3_%s%d" % (arm, k)
        build("off" if arm == "off" else "live", name, R + "/" + name); run("lean2", name, name, "quiet", "auto")
build("live", "m3_open", R + "/m3_open", "--open"); run("lean2", "m3_open", "m3_open", "quiet", "auto")
# m4: a = kill by the server's own pid (platform restarts it); b = and the restart exits at once; c = and the restart never answers
for k in range(n_out):
    for v, refuse in (("a", ""), ("b", "echo exit > %s/m4%s%d/refuse;"), ("c", "echo hang > %s/m4%s%d/refuse;")):
        name = "m4%s%d" % (v, k)
        build("live", name, R + "/" + name)
        run("outage", name, name, "live", "auto", env={"WT_REFUSE": (refuse % (R, v, k)) if refuse else ""})
print("done")
