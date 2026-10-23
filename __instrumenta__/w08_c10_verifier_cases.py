# w08-c10: re-runs the verifier's case file (a JSON list of {id, kind, shape, command, plain_denied_base}) on a checkout (python in process and the Rust binary), counting cases whose plain form is denied (field plain_denied_base) but the case itself is allowed; input: --cases FILE (e.g. /private/tmp/murmuration-w08/reproducer-w08-10/holes1.json), --repo DIR; output: stdout counts per shape of cases allowed although their plain form is denied, and python/rust differences.
# usage: python3 -I w08_c10_verifier_cases.py --cases FILE --repo DIR [--jobs 8]
import argparse, collections, concurrent.futures, importlib.util, json, os, platform, subprocess
ap = argparse.ArgumentParser(); ap.add_argument("--cases", required=True); ap.add_argument("--repo", required=True); ap.add_argument("--jobs", type=int, default=8)
a = ap.parse_args()
spec = importlib.util.spec_from_file_location("pg", os.path.join(a.repo, "scripts", "permission_guard.py")); pg = importlib.util.module_from_spec(spec); spec.loader.exec_module(pg)
rust = os.path.join(a.repo, "bin", "%s-apple-darwin" % ("aarch64" if platform.machine() in ("arm64", "aarch64") else platform.machine()), "murmuration")
cases = json.load(open(a.cases))
def rs(c):
    ev = json.dumps(dict(tool_name="Bash", tool_input={"command": c["command"]}, cwd="/h/proj"))
    return bool(subprocess.run([rust, "guard"], input=ev.encode(), capture_output=True).stdout)
with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
    rsd = list(ex.map(rs, cases))
open_py, open_rs, diff, by = 0, 0, 0, collections.Counter()
for c, r in zip(cases, rsd):
    p = bool(pg.decide(dict(tool_name="Bash", tool_input={"command": c["command"]}, cwd="/h/proj")))
    diff += p != r
    if c.get("plain_denied_base"):
        open_py += not p; open_rs += not r
        if not p: by[c["shape"]] += 1
print("%d cases; plain form denied on base for %d; of those allowed here: python %d, rust %d; python and rust differ on %d" % (len(cases), sum(1 for c in cases if c.get("plain_denied_base")), open_py, open_rs, diff))
for k, v in by.most_common(20): print("  ", k, v)
