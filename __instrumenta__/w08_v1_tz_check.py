# Runs one budget SubagentStart and one hand-back SubagentStop at fixed clock readings (MURMURATION_NOW) around the DST transitions of several time zones, once through the Python scripts (fixed-clock shim) and once through the Rust test build, and compares the whole lab folder (the log's local-time `t` field and the hand-back header carry the zone offset).
# inputs: author's worktree, a Rust test build, scratch folder; outputs: a count of compared instants and the differences, on stdout.
# usage: python3 -I w08_v1_tz_check.py WT RUSTBIN SCRATCH
import json, os, shutil, subprocess, sys, datetime
from zoneinfo import ZoneInfo
wt, rust, scratch = sys.argv[1:4]
ZONES = ["UTC", "America/New_York", "Europe/London", "Europe/Berlin", "Australia/Lord_Howe", "Asia/Kolkata", "Asia/Kathmandu", "Pacific/Apia", "Pacific/Chatham", "America/St_Johns", "Asia/Tokyo", "Africa/Casablanca", "America/Sao_Paulo", "Pacific/Kiritimati", "Antarctica/Troll"]
def transitions(z):
    tz = ZoneInfo(z); out = []
    t = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc).timestamp(); end = t + 2 * 365 * 86400
    prev = datetime.datetime.fromtimestamp(t, tz).utcoffset()
    while t < end:
        t += 3600
        o = datetime.datetime.fromtimestamp(t, tz).utcoffset()
        if o != prev:
            for s in range(-3700, 1, 1):   # find the second
                pass
            lo = t - 3600
            while t - lo > 1:
                mid = (lo + t) // 2
                if datetime.datetime.fromtimestamp(mid, tz).utcoffset() == prev: lo = mid
                else: t = mid
            out.append(t); prev = o; t = lo + 3600
    return out
def run(cmd, raw, now, tz):
    env = {k: v for k, v in os.environ.items() if k not in ("TZ",)}
    env.update(TZ=tz, MURMURATION_NOW=repr(now), CLAUDE_PLUGIN_ROOT=wt, LC_ALL="en_US.UTF-8")
    return subprocess.run(cmd, input=raw, capture_output=True, env=env, cwd="/private/tmp", timeout=30)
def snap(lab):
    o = {}
    for r, d, f in os.walk(lab):
        for x in f: o[os.path.relpath(os.path.join(r, x), lab)] = open(os.path.join(r, x), "rb").read()
    return o
n = bad = 0
shim = os.path.join(wt, "__instrumenta__", "w08c1_pyshim.py")
for z in ZONES:
    tr = transitions(z)
    instants = []
    for t in tr[:4]:
        instants += [t - 1.5, t - 0.001, float(t), t + 0.001, t + 1.5, t + 3600.0 - 0.5]
    instants += [1792700000.5, 1800000000.999]
    for now in instants:
        res = {}
        for impl in ("py", "rs"):
            base = os.path.join(scratch, "tz"); shutil.rmtree(base, ignore_errors=True)
            lab = os.path.join(base, "lab"); os.makedirs(os.path.join(lab, "__statera__"))
            outs = []
            for which, ev in (("budget", dict(cwd=lab, hook_event_name="SubagentStart", agent_id="z1", agent_type="murmuration:author")),
                              ("handback", dict(cwd=lab, hook_event_name="SubagentStop", agent_id="z1", agent_type="murmuration:author", last_assistant_message="x"))):
                cmd = [sys.executable, "-S", "-I", shim, os.path.join(wt, "scripts"), which] if impl == "py" else [rust, which]
                p = run(cmd, json.dumps(ev).encode(), now, z); outs.append((p.returncode, p.stdout, p.stderr))
            res[impl] = (outs, snap(lab))
        n += 1
        if res["py"] != res["rs"]:
            bad += 1; print("DIFF", z, now, [ (k, res["py"][1].get(k), res["rs"][1].get(k)) for k in set(res["py"][1]) | set(res["rs"][1]) if res["py"][1].get(k) != res["rs"][1].get(k)][:1])
print("zones", len(ZONES), "instants compared", n, "differences", bad)
