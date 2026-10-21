"""CPU seconds that system daemons (Falcon sensor, endpointsecurityd, opendirectoryd, trustd, syspolicyd, amfid, mds, logd) use during a window of N spawns of one binary (w07a_spawn_bench) against an equally long idle window, alternating the two in pairs; usage: w07a_daemon_cpu_pairs.py N PAIRS -- CMD ARGS (CMD performs N spawns); output: markdown table of per-daemon CPU ms per spawn (spawn window minus idle window, per pair, median and spread). ps cputime has 10 ms resolution, so windows are seconds long."""
import subprocess, sys, time, re, statistics as st
N, pairs = int(sys.argv[1]), int(sys.argv[2]); cmd = sys.argv[sys.argv.index("--") + 1:]  # N = loop count the command performs (for the per-spawn figure)
names = ("Falcon", "falcon.Agent", "endpointsecurityd", "opendirectoryd", "trustd", "syspolicyd", "amfid", "mds", "mds_stores", "logd", "xprotectd", "launchd", "fseventsd", "notifyd")
def snap():
    out = subprocess.run(["ps", "-axo", "pid=,time=,comm="], capture_output=True, text=True).stdout
    d = {}
    for l in out.splitlines():
        pid, t, c = l.split(None, 2)
        base = c.rsplit("/", 1)[-1]
        if base in ("endpointsecurityd", "opendirectoryd", "trustd", "syspolicyd", "amfid", "mds", "mds_stores", "logd", "xprotectd", "launchd", "fseventsd", "notifyd") or "falcon.Agent" in base:
            m, s = t.split(":"); d[(pid, base)] = int(m) * 60 + float(s)
    return d
def agg(d):
    o = {}
    for (pid, b), v in d.items(): o[b] = o.get(b, 0) + v
    return o
res = {}
for k in range(pairs):
    for arm in (("spawn", "idle") if k % 2 == 0 else ("idle", "spawn")):
        a = agg(snap()); t0 = time.time()
        if arm == "spawn":
            subprocess.run(cmd, stdout=subprocess.DEVNULL); T = time.time() - t0
            Tspawn = T
        else:
            time.sleep(Tspawn if "Tspawn" in dir() else 12); T = time.time() - t0
        b = agg(snap())
        for n in b: res.setdefault(n, {}).setdefault(arm, []).append((b[n] - a.get(n, 0), T))
print("| daemon | spawn window cpu s (per pair) | idle window cpu s (per pair) | (spawn - idle) ms per spawn, median [min, max] over pairs |\n|:--|:--|:--|:--|")
for n, v in sorted(res.items(), key=lambda kv: -sum(x[0] for x in kv[1].get("spawn", []))):
    sp = v.get("spawn", []); idl = v.get("idle", [])
    if not sp or not idl: continue
    # normalise idle to the spawn window length
    diffs = [(s[0] - i[0] * s[1] / i[1]) * 1000 / N for s, i in zip(sp, idl)]
    print("| %s | %s | %s | %.2f [%.2f, %.2f] |" % (n, " ".join("%.2f" % x[0] for x in sp), " ".join("%.2f" % x[0] for x in idl), st.median(diffs), min(diffs), max(diffs)))
