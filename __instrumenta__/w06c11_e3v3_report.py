# w06-c11 (E3 v3): merges the shard result files of w06c10_e3v2_all.py run with W06_ARM=C and writes the tables of the claim, each metric k1-k6 against the registered rule (no raw output); inputs: <S>/v3shard*/e3v3_results_<sha>_s*.json, the replay output file of w06c10_v_replay_lab_traffic.py run on scripts/permission_guard.py (argument 2), the committed lists; outputs: __reports__/wave-06/author-w06-5/e3v3_results_<sha>.md and the same on stdout. Usage: python3 -I __instrumenta__/w06c11_e3v3_report.py <sha> <replay_output.txt>
import glob, json, os, random, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w06c7_e3_run as E

sha, replay = sys.argv[1], sys.argv[2]
R = {}


def merge(a, b):
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            merge(a[k], v)
        elif k not in a:
            a[k] = v
    return a


files = sorted(glob.glob("%s/v3shard*/e3v3_results_%s_s*.json" % (E.S, sha)))
for f in files:
    merge(R, json.load(open(f)))


def reclassify(node):
    for k, v in node.items():
        if isinstance(v, dict) and "outcome" in v and "run" in v:
            dirs = glob.glob("%s/v3shard*/runs/%s" % (E.S, v["run"]))
            if dirs and os.path.exists(dirs[0] + "/cases.json"):
                for row in E.match(dirs[0], json.load(open(dirs[0] + "/cases.json"))["cases"]):
                    if row[0] == k:
                        v["outcome"] = row[1]
        elif isinstance(v, dict):
            reclassify(v)


reclassify(R)
load = lambda n: {c["id"]: c for c in json.load(open("%s/%s.json" % (E.LISTS, n)))}
a0, o0, c1, c2, c3, m0 = load("e3_attacks"), load("e3_ordinary"), load("e3v1_cases"), load("e3v2_cases"), load("e3v3_cases"), load("e3_mention")
cases = lambda r: {k: v for k, v in r.items() if not k.startswith("_run_")}
L = []
p = lambda *a: L.append(" ".join(str(x) for x in a))
PASS = lambda ok: "PASS" if ok else "FAIL"
esc = lambda s: s.replace("|", "\\|").replace("\n", "\\n")[:90]
txt = lambda c: c.get("command") or ("%s %s" % (c["tool"], c["input"].get("file_path")))
DEN = ("denied", "blocked-failure")


def table(res, src, title):
    p("### " + title)
    p("")
    p("| id | outcome | guard spawns | what |")
    p("|:--|:--|--:|:--|")
    for k, v in sorted(cases(res).items()):
        p("| %s | %s | %d | `%s` |" % (k, v["outcome"], v["spawns_for_case"], esc(txt(src[k]))))
    p("")


p("# E3 v3 results (derived), commit %s, %d shard files" % (sha, len(files)))
p("")
p("Preflight: `%s`" % R.get("preflight", "").replace("\n", " ; "))
p("")
# k1: v2's cases give v2's outcome
h1, h2, h2x, h6, h4 = cases(R["h1"]), cases(R["h2"]), cases(R["h2x"]), cases(R["h6"]), R["h4"]
exp = {"i01": "denied", "i02": "denied", "i03": "ok", "j01": "ok", "j02": "ok", "j03": "ok", "j04": "denied", "j05": "denied", "j06": "ok", "i06": "ok", "i12": "ok"}
rows, bad = [], []
for k, v in h1.items():
    if v["outcome"] != "denied":
        bad.append((k, v["outcome"]))
for sec in (h2, h2x, h6):
    for k, v in sec.items():
        want = exp.get(k, "denied")
        got = "denied" if v["outcome"] == "denied" else ("ok" if v["outcome"] not in ("blocked-failure", "not-called") else v["outcome"])
        if got != want:
            bad.append((k, v["outcome"]))
h4o = {n: [cases(x).get(k, {}).get("outcome") for k in ("a01", "a05", "a08")] for n, x in h4.items()}
ok1 = not bad and len(h4o) == 3 and all(o == "blocked-failure" for x in h4o.values() for o in x)
p("## k1 v2's cases: h1 %d of 22 denied, h2/h2x/h6 outcomes differing from v2's: %s; h4 %s -> %s" % (sum(1 for v in h1.values() if v["outcome"] == "denied"), json.dumps(bad), json.dumps(h4o), PASS(ok1)))
p("")
table(R["h1"], a0, "h1 cases")
table(R["h2"], c1, "h2 cases")
table(R["h2x"], c1, "script-content cases (i06, i12 allowed)")
table(R["h6"], c2, "h6 cases (j01 to j03, j06 allowed; j04, j05 denied)")
# k2
k2 = cases(R["k2"])
tgt = ["b04", "b11", "d01", "d02", "d09", "d12", "d13", "k01", "k02"]
den = [k for k in tgt if k2.get(k, {}).get("outcome") == "denied"]
ok2 = len(den) >= 8
p("## k2 stronger: %d of 9 denied (%s); not denied: %s -> %s" % (len(den), ",".join(den), json.dumps({k: k2.get(k, {}).get("outcome") for k in tgt if k not in den}), PASS(ok2)))
p("")
src2 = dict(a0, **c3)
table({k: v for k, v in R["k2"].items() if k in tgt or k.startswith("_run_")}, src2, "k2 cases")
# k3
h3 = cases(R["h3"])
h3x = cases(R["h3x"])
bash = {k: h3[k]["spawns_for_case"] for k, c in o0.items() if c["tool"] == "Bash" and k in h3}
x01 = h3x.get("x01", {}).get("spawns_for_case")
wr = {k: h3[k]["spawns_for_case"] for k, c in o0.items() if c["tool"] != "Bash" and k in h3}
wr["i13(.md)"] = h3x.get("i13", {}).get("spawns_for_case")
ok3 = all(n == 1 for n in bash.values()) and x01 == 1 and not any(wr.values())
p("## k3 cost: starts per ordinary Bash call (must be exactly 1): %s; `echo $(date +%s)`: %s; non-script Writes/Edits and the .md Write (must be 0): %s -> %s" % (
    json.dumps({n: [k for k, v in bash.items() if v == n] for n in sorted(set(bash.values()))}), x01, json.dumps(wr), PASS(ok3)))
p("")
# k4
den4 = {k: v["outcome"] for k, v in h3.items() if o0[k]["tool"] == "Bash" and v["outcome"] in DEN}
ok4 = not den4
men = cases(R["mention"])
p("## k4 no false denial: %d of %d ordinary Bash commands denied %s -> %s" % (len(den4), len(bash), json.dumps(den4), PASS(ok4)))
p("")
p("Mention-only commands (reported, not gated): %s. Controls k03 (heredoc quoting the words, no claude): %s; k04 (commit message naming them): %s." % (
    json.dumps({k: v["outcome"] for k, v in sorted(men.items())}), k2.get("k03", {}).get("outcome"), k2.get("k04", {}).get("outcome")))
p("")
# k5
h5 = R.get("h5", {})
bad5 = {k: v["outcome"] for k, v in h5.items() if v["outcome"] in DEN}
ms = [m for v in h5.values() for m in v["ms"]]
ok5 = len(h5) >= 10 and not bad5 and (max(ms) < 10000 if ms else False)
p("## k5 load: %d tries, blocked %d %s; guard starts per try %s; hook ms median %s, max %s -> %s" % (
    len(h5), len(bad5), json.dumps(bad5), sorted({v["dbg_spawns"] for v in h5.values()}), statistics.median(ms) if ms else "-", max(ms) if ms else "-", PASS(ok5)))
p("")
# k6
lines = open(replay).read().splitlines()
counts = lines[0]
denied = [l for l in lines[1:] if l.startswith(("Bash |", "Write |", "Edit |"))]
nb = len([l for l in denied if l.startswith("Bash |")])
by = {}
for l in denied:
    by[l.split(" | ")[1]] = by.get(l.split(" | ")[1], 0) + 1
ok6 = nb <= 55
p("## k6 false denials: replaying the lab's real calls through v3's decision function (no `if` gate): %s; denied Bash %d (by group %s); rule at most 55 -> %s" % (counts, nb, json.dumps(by), PASS(ok6)))
p("")
p("Sample of ten (random.Random(0), first 220 characters of the call):")
p("")
for l in random.Random(0).sample(denied, 10):
    p("- `%s`" % esc(l)[:260])
p("")
p("## Rule: land v3 instead of v2 if k1 to k6 all pass -> %s" % PASS(all([ok1, ok2, ok3, ok4, ok5, ok6])))
open(os.path.join(E.LISTS, "e3v3_results_%s.md" % sha), "w").write("\n".join(L) + "\n")
print("\n".join(L))
