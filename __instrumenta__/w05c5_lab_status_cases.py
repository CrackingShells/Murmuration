"""Writes the case file for cmd_cost_interleaved.py that times lab_status.py versions on a frozen transcript tree, and checks that their outputs are byte-identical, from versions given as NAME=SCRIPT to a cases JSON and a verdict on stdout.

usage: w05c5_lab_status_cases.py --project DIR --config FROZEN_CLAUDE_CONFIG_DIR --scratch DIR --out cases.json NAME=lab_status.py ... [--cached NAME=lab_status.py ...]
Each plain version runs `python3 SCRIPT --project DIR` with CLAUDE_CONFIG_DIR=FROZEN and LAB_STATUS_CACHE=off (a version without the cache ignores it). Each --cached version gets three cases: NAME-nocache (LAB_STATUS_CACHE=off), NAME-cold (the cache file removed in the same command), NAME-warm (a cache file in SCRATCH, filled by the check run below).
The check: every version's stdout (cached ones: cold, then warm, then off) is compared with the first version's, byte for byte; a difference is printed with its first differing line, and the exit code is 1.
Purpose (w05-c5): E8 of `__reports__/wave-05/00-experiment_protocol_v0.md`: m1 identical output, m2 the wall times by `cmd_cost_interleaved.py cases.json --n 30` (the frozen tree keeps both versions on the same bytes).
"""
import json, os, subprocess, sys
argv = sys.argv[1:]
opt = lambda k: argv[argv.index(k) + 1]
project, config, scratch, out = opt("--project"), opt("--config"), opt("--scratch"), opt("--out")
cached_at = argv.index("--cached") if "--cached" in argv else len(argv)
plain = [a.split("=", 1) for a in argv[:cached_at] if "=" in a and not a.startswith("--") and a.split("=")[0] not in ("--project", "--config", "--scratch", "--out")]
plain = [(n, p) for n, p in plain if os.path.isfile(p)]
cached = [a.split("=", 1) for a in argv[cached_at + 1:] if "=" in a]
os.makedirs(scratch, exist_ok=True)
cases, runs = [], []
def case(name, script, cache, pre=""):
    env = {"CLAUDE_CONFIG_DIR": config, "LAB_STATUS_CACHE": cache}
    cases.append({"name": name, "sh": "%spython3 %s --project %s" % (pre, script, project), "stdin": None, "env": env})
    runs.append((name, script, env))
for n, p in plain:
    case(n, p, "off")
for n, p in cached:
    f = os.path.join(scratch, n + ".cache.json")
    case(n + "-nocache", p, "off")
    case(n + "-cold", p, f, "rm -f %s; " % f)
    case(n + "-warm", p, f)
json.dump(cases, open(out, "w"), indent=1)
ref, bad = None, 0
order = [r for r in runs if not r[0].endswith(("-nocache", "-cold", "-warm"))]   # the plain versions first (the first is the reference), then each cached version: cold, warm (made by the cold run), off
for n, _ in cached:
    order += [r for suffix in ("-cold", "-warm", "-nocache") for r in runs if r[0] == n + suffix]
for name, script, env in order:
    e = dict(os.environ, **env)
    if name.endswith("-cold"):
        try: os.unlink(env["LAB_STATUS_CACHE"])
        except OSError: pass
    o = subprocess.run([sys.executable, script, "--project", project], capture_output=True, env=e).stdout
    if ref is None:
        ref = (name, o)
    ok = o == ref[1]
    bad += not ok
    print("%-22s %7d bytes  %s" % (name, len(o), "identical to " + ref[0] if ok else "DIFFERS from " + ref[0]))
    if not ok:
        a, b = ref[1].decode().splitlines(), o.decode().splitlines()
        i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
        print("   first difference at line %d:\n   %s\n   %s" % (i, a[i:i + 1], b[i:i + 1]))
sys.exit(1 if bad else 0)
