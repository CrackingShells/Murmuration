# w08-c10: decides the registered cases of wave 6 (e3_attacks, e3_ordinary, e3_mention, e3_evasions, e3v1..e3v3_cases) with the Python guard of two checkouts (before, after) and prints per list how many are denied, and every case whose decision differs; inputs: --before DIR, --after DIR (checkouts), the lists under __reports__/wave-06/author-w06-5 of the AFTER checkout, scripts/check_guard_equal.py of the AFTER checkout for the arena; output: stdout.
# usage: python3 -I w08_c10_registered_diff.py --before DIR --after DIR --scratch DIR   (scratch is new)
import argparse, importlib.util, json, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("--before", required=True)
ap.add_argument("--after", required=True)
ap.add_argument("--scratch", required=True)
a = ap.parse_args()


def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pb = load(os.path.join(a.before, "scripts", "permission_guard.py"), "pb")
pa = load(os.path.join(a.after, "scripts", "permission_guard.py"), "pa")
cge = load(os.path.join(a.after, "scripts", "check_guard_equal.py"), "cge")
vocab = json.load(open(os.path.join(a.after, "rust", "tests", "fuzz_vocab.json")))
os.makedirs(a.scratch)
T, src, incident = cge.make_arena(a.scratch, vocab["arena_exists_py"])
rows, diffs = {}, []
for name, payload in cge.registered_events(T, src, incident):
    lst = name.split(":")[1]
    ev = json.loads(payload)
    db, da = pb.decide(ev), pa.decide(ev)
    r = rows.setdefault(lst, [0, 0, 0])
    r[0] += 1
    r[1] += bool(db)
    r[2] += bool(da)
    if bool(db) != bool(da) or (db and da and db[0] != da[0]):
        diffs.append((name, db and db[0], da and da[0]))
print("%-12s %6s %14s %14s" % ("list", "cases", "denied before", "denied after"))
for k, (n, b, af) in rows.items():
    print("%-12s %6d %14d %14d" % (k, n, b, af))
print("cases whose decision or rule differs: %d %s" % (len(diffs), diffs))
