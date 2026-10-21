# w06-c8 (E3 v1): merges the shard result files of w06c8_e3v1_all.py and writes the tables of the claim, each metric h1-h5 against the registered rule (no raw output); inputs: <S>/v1shard*/e3v1_results_<sha>_s*.json and the committed lists; outputs: __reports__/wave-06/author-w06-5/e3v1_results_<sha>.md and the same on stdout. Usage: python3 -I __instrumenta__/w06c8_e3v1_report.py <sha>
import glob, json, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w06c7_e3_run as E

sha = sys.argv[1]
R = {}


def merge(a, b):
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            merge(a[k], v)
        elif k not in a:
            a[k] = v
    return a


files = sorted(glob.glob("%s/v1shard*/e3v1_results_%s_s*.json" % (E.S, sha)))
for f in files:
    merge(R, json.load(open(f)))
v0 = {n: {c["id"]: c for c in json.load(open("%s/e3_%s.json" % (E.LISTS, n)))} for n in ("attacks", "ordinary", "evasions")}
v1 = {c["id"]: c for c in json.load(open(E.LISTS + "/e3v1_cases.json"))}
DOLLAR = re.compile(r"\$\(|`|\$[A-Za-z_{]")
L = []
p = lambda *a: L.append(" ".join(str(x) for x in a))
cases = lambda r: {k: v for k, v in r.items() if not k.startswith("_run_")}
runs = lambda r: {k[5:]: v for k, v in r.items() if k.startswith("_run_")}
esc = lambda s: s.replace("|", "\\|").replace("\n", "\\n")[:90]


def txt(c):
    return c.get("command") or ("%s %s" % (c["tool"], c["input"].get("file_path")))


def table(res, src, title):
    p("### " + title)
    p("")
    p("| id | outcome | guard spawns | what |")
    p("|:--|:--|--:|:--|")
    for k, v in sorted(cases(res).items()):
        p("| %s | %s | %d | `%s` |" % (k, v["outcome"], v["spawns_for_case"], esc(txt(src[k]))))
    p("")


p("# E3 v1 results (derived), commit %s, %d shard files" % (sha, len(files)))
p("")
p("Preflight: `%s`" % R.get("preflight", "").replace("\n", " ; "))
p("")
h1 = cases(R["h1"])
a_den = [k for k in h1 if k.startswith("a") and h1[k]["outcome"] == "denied"]
b3 = h1.get("b03", {}).get("outcome")
p("## h1 flags: %d of 21 G1 forms denied; `--setting-sources project,local` (b03): %s. Rule: 21/21 and b03 denied -> %s" % (
    len(a_den), b3, "PASS" if len(a_den) == 21 and b3 == "denied" else "FAIL"))
p("")
table(R["h1"], v0["attacks"], "h1 cases")
h2 = cases(R["h2"])
ok2 = h2.get("i01", {}).get("outcome") == "denied" and h2.get("i02", {}).get("outcome") == "denied" and h2.get("i03", {}).get("outcome") not in ("denied", "blocked-failure", "not-called") and h2["i03"]["spawns_for_case"] == 0
p("## h2 incident: i01 (Write of the c4aaebb file as .py) %s; i02 (Edit adds \"bypassPermissions\" to a .py) %s; i03 (same text to .md) %s with %d spawns. Rule -> %s" % (
    h2.get("i01", {}).get("outcome"), h2.get("i02", {}).get("outcome"), h2.get("i03", {}).get("outcome"), h2.get("i03", {}).get("spawns_for_case", -1), "PASS" if ok2 else "FAIL"))
p("")
p("Offline check on the exact c4aaebb text (%s lines): Write as .py denied = %s, Write as .md denied = %s (CHECKED)." % (R["offline"]["n_lines"], R["offline"]["incident_py"], R["offline"]["incident_md"]))
p("")
table(R["h2x"], v1, "script-content cases beside h2 (i06 and i12 must be allowed)")
h3 = cases(R["h3"])
bash_nd = [k for k, c in v0["ordinary"].items() if c["tool"] == "Bash" and not DOLLAR.search(c["command"])]
sp = {k: h3[k]["spawns_for_case"] for k in bash_nd if k in h3}
writes = {k: h3[k]["spawns_for_case"] for k, c in v0["ordinary"].items() if c["tool"] != "Bash" and k in h3}
h3x = cases(R["h3x"])
dol = {k: h3[k]["spawns_for_case"] for k, c in v0["ordinary"].items() if c["tool"] == "Bash" and DOLLAR.search(c["command"]) and k in h3}
dol.update({k: v["spawns_for_case"] for k, v in h3x.items() if k == "x01"})
spawned = {k: n for k, n in sp.items() if n}
ok3 = not spawned and all(n == 0 for k, n in list(writes.items())) and h3x.get("i13", {}).get("spawns_for_case", 9) == 0 and all(n <= 3 for n in dol.values())
p("## h3 cost: %d of %d ordinary Bash commands without an expansion started the guard (%s); Writes/Edits of non-script files %s; i13 (.md Write) %s spawns; `$` commands %s (must be at most 3). Rule -> %s" % (
    len(spawned), len(sp), json.dumps(spawned), json.dumps(writes), h3x.get("i13", {}).get("spawns_for_case"), json.dumps(dol), "PASS" if ok3 else "FAIL"))
p("")
table(R["h3"], v0["ordinary"], "h3 ordinary list")
h4 = R["h4"]
blocked = {n: [cases(v).get(k, {}).get("outcome") for k in ("a01", "a05", "a08")] for n, v in h4.items()}
ok4 = all(o == "blocked-failure" for v in blocked.values() for o in v) and len(blocked) == 3
p("## h4 fail closed: %s. Rule (all blocked, 3 variants) -> %s" % (json.dumps(blocked), "PASS" if ok4 else "FAIL"))
p("")
h5 = R.get("h5", {})
bad5 = {k: v["outcome"] for k, v in h5.items() if v["outcome"] in ("blocked-failure", "denied")}
ms5 = [m for v in h5.values() for m in v["ms"]]
p("## h5 load: %d tries (five sessions in parallel, while the other shards ran), blocked by a timeout or denied: %d %s; guard starts per try %s; hook times ms: median %s, max %s. Rule (0 false blocks in at least 10) -> %s" % (
    len(h5), len(bad5), json.dumps(bad5), sorted({v["dbg_spawns"] for v in h5.values()}), statistics.median(ms5) if ms5 else "-", max(ms5) if ms5 else "-",
    "PASS" if len(h5) >= 10 and not bad5 else "FAIL"))
p("")
p("## Rule: land if h1 to h5 all pass -> %s" % ("PASS" if (len(a_den) == 21 and b3 == "denied" and ok2 and ok3 and ok4 and len(h5) >= 10 and not bad5) else "FAIL (see the lines above)"))
p("")
p("## Reported: v0 cases outside h1 against the v1 rows (g1 attacks and g5 evasions)")
p("")
rep = cases(R["reported"])
let, den = [], []
for k, v in sorted(rep.items()):
    (den if v["outcome"] == "denied" else let).append(k)
p("Denied by v1: %s" % ", ".join(den))
p("")
p("Let through, not denied (outcome): %s" % ", ".join("%s=%s" % (k, rep[k]["outcome"]) for k in let))
p("")
table(R["reported"], dict(v0["attacks"], **v0["evasions"]), "reported cases")
if "armB" in R:
    p("## Arm B (reported variant, not registered): `--setting-sources` row replaced by four rows (` p`, ` l`, `=p`, `=l`)")
    p("")
    bo = cases(R["armB"]["ordinary"])
    bsp = {k: bo[k]["spawns_for_case"] for k in bash_nd if k in bo}
    ba = cases(R["armB"]["attacks"])
    p("Ordinary Bash without expansion that started the guard: %s of %d. Attacks and the `$()` call: %s." % (
        json.dumps({k: n for k, n in bsp.items() if n}), len(bsp), json.dumps({k: (v["outcome"], v["spawns_for_case"]) for k, v in sorted(ba.items())})))
    p("")
open(os.path.join(E.LISTS, "e3v1_results_%s.md" % sha), "w").write("\n".join(L) + "\n")
print("\n".join(L))
