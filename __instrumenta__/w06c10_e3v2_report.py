# w06-c10 (E3 v2): merges the shard result files of w06c10_e3v2_all.py and writes the tables of the claim, each metric h1-h6 against the registered rule (no raw output); inputs: <S>/v2shard*/e3v2_results_<sha>_s*.json and the committed lists; outputs: __reports__/wave-06/author-w06-5/e3v2_results_<sha>.md and the same on stdout. Usage: python3 -I __instrumenta__/w06c10_e3v2_report.py <sha>
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


files = sorted(glob.glob("%s/v2shard*/e3v2_results_%s_s*.json" % (E.S, sha)))
for f in files:
    merge(R, json.load(open(f)))


def reclassify(node):
    """Re-derive each case's outcome from the raw session with the final classifier (a tool result that merely names permission_guard.py in a path is not a hook failure)."""
    for k, v in node.items():
        if isinstance(v, dict) and "outcome" in v and "run" in v:
            dirs = glob.glob("%s/v2shard*/runs/%s" % (E.S, v["run"]))
            if dirs and os.path.exists(dirs[0] + "/cases.json"):
                for row in E.match(dirs[0], json.load(open(dirs[0] + "/cases.json"))["cases"]):
                    if row[0] == k:
                        v["outcome"] = row[1]
        elif isinstance(v, dict):
            reclassify(v)


reclassify(R)
load = lambda n: {c["id"]: c for c in json.load(open("%s/%s.json" % (E.LISTS, n)))}
a0, o0, c1, c2 = load("e3_attacks"), load("e3_ordinary"), load("e3v1_cases"), load("e3v2_cases")
DOLLAR = re.compile(r"\$\(|`|\$[A-Za-z_{]")
L = []
p = lambda *a: L.append(" ".join(str(x) for x in a))
cases = lambda r: {k: v for k, v in r.items() if not k.startswith("_run_")}
esc = lambda s: s.replace("|", "\\|").replace("\n", "\\n")[:90]
txt = lambda c: c.get("command") or ("%s %s" % (c["tool"], c["input"].get("file_path")))
PASS = lambda ok: "PASS" if ok else "FAIL"


def table(res, src, title):
    p("### " + title)
    p("")
    p("| id | outcome | guard spawns | what |")
    p("|:--|:--|--:|:--|")
    for k, v in sorted(cases(res).items()):
        p("| %s | %s | %d | `%s` |" % (k, v["outcome"], v["spawns_for_case"], esc(txt(src[k]))))
    p("")


p("# E3 v2 results (derived), commit %s, %d shard files" % (sha, len(files)))
p("")
p("Preflight: `%s`" % R.get("preflight", "").replace("\n", " ; "))
p("")
h1 = cases(R["h1"])
n_a = sum(1 for k in h1 if k.startswith("a") and h1[k]["outcome"] == "denied")
b3 = h1.get("b03", {}).get("outcome")
ok1 = n_a == 21 and b3 == "denied"
p("## h1 flags: %d of 21 G1 forms denied; b03 (`--setting-sources project,local`) %s -> %s" % (n_a, b3, PASS(ok1)))
p("")
table(R["h1"], a0, "h1 cases")
h2 = cases(R["h2"])
ok2 = h2["i01"]["outcome"] == "denied" and h2["i02"]["outcome"] == "denied" and h2["i03"]["outcome"] not in ("denied", "blocked-failure", "not-called") and h2["i03"]["spawns_for_case"] == 0
p("## h2 incident: i01 (new .py with the c4aaebb text) %s; i02 (Edit adds the word to a .py) %s; i03 (.md) %s, %d spawns -> %s" % (
    h2["i01"]["outcome"], h2["i02"]["outcome"], h2["i03"]["outcome"], h2["i03"]["spawns_for_case"], PASS(ok2)))
p("")
table(R["h2x"], c1, "script-content cases beside h2 (i06 and i12 must be allowed)")
h3 = cases(R["h3"])
flag = {"o08", "o09", "o11", "o12"}
nd = [k for k, c in o0.items() if c["tool"] == "Bash" and not DOLLAR.search(c["command"]) and "setting-sources" not in c["command"]]
spawned = {k: h3[k]["spawns_for_case"] for k in nd if k in h3 and h3[k]["spawns_for_case"]}
named = {k: (h3[k]["outcome"], h3[k]["spawns_for_case"]) for k in sorted(flag) if k in h3}
named_ok = all(v[0] not in ("denied", "blocked-failure", "not-called") for v in named.values())
h3x = cases(R["h3x"])
dol = {k: h3[k]["spawns_for_case"] for k, c in o0.items() if c["tool"] == "Bash" and DOLLAR.search(c["command"]) and k in h3}
dol.update({"x01": h3x["x01"]["spawns_for_case"]} if "x01" in h3x else {})
writes = {k: h3[k]["spawns_for_case"] for k, c in o0.items() if c["tool"] != "Bash" and k in h3}
ok3 = not spawned and all(n <= 3 for n in dol.values()) and named_ok and h3x.get("i13", {}).get("spawns_for_case", 9) == 0 and not any(writes.values())
p("## h3 cost: %d of %d ordinary Bash commands that name no `--setting-sources` and have no expansion started the guard %s; `$` commands %s (at most 3); the commands naming the flag (reported): %s (each must be allowed); non-script Writes %s; .md Write i13 %s spawns -> %s" % (
    len(spawned), len([k for k in nd if k in h3]), json.dumps(spawned), json.dumps(dol), json.dumps(named), json.dumps(writes), h3x.get("i13", {}).get("spawns_for_case"), PASS(ok3)))
p("")
table(R["h3"], o0, "h3 ordinary list")
h4 = {n: [cases(v).get(k, {}).get("outcome") for k in ("a01", "a05", "a08")] for n, v in R["h4"].items()}
ok4 = len(h4) == 3 and all(o == "blocked-failure" for v in h4.values() for o in v)
p("## h4 fail closed: %s -> %s" % (json.dumps(h4), PASS(ok4)))
p("")
h5 = R.get("h5", {})
bad5 = {k: v["outcome"] for k, v in h5.items() if v["outcome"] in ("blocked-failure", "denied")}
ms5 = [m for v in h5.values() for m in v["ms"]]
ok5 = len(h5) >= 10 and not bad5
p("## h5 load: %d tries, blocked %d %s; guard starts per try %s; hook time ms median %s, max %s -> %s" % (
    len(h5), len(bad5), json.dumps(bad5), sorted({v["dbg_spawns"] for v in h5.values()}), statistics.median(ms5) if ms5 else "-", max(ms5) if ms5 else "-", PASS(ok5)))
p("")
h6 = cases(R["h6"])
ok6 = all(h6.get(k, {}).get("outcome") not in ("denied", "blocked-failure", "not-called", None) for k in ("j01", "j02", "j03"))
p("## h6 engineering: j01 (Edit of an unrelated line of handback.py) %s; j02 (Edit of the guard's message) %s; j03 (Write of handback.py over itself) %s -> %s" % (
    h6.get("j01", {}).get("outcome"), h6.get("j02", {}).get("outcome"), h6.get("j03", {}).get("outcome"), PASS(ok6)))
p("")
p("Added-words cases beside h6: j04 (Edit adds a second occurrence) %s [deny expected]; j05 (Write over an existing .py adds the word) %s [deny expected]; j06 (Edit keeps the count) %s [allow expected]." % (
    h6.get("j04", {}).get("outcome"), h6.get("j05", {}).get("outcome"), h6.get("j06", {}).get("outcome")))
p("")
p("Offline on the exact texts (CHECKED; True = denied): %s" % json.dumps(R["offline"]))
p("")
p("## Rule: land if h1 to h6 all pass -> %s" % PASS(all([ok1, ok2, ok3, ok4, ok5, ok6])))
open(os.path.join(E.LISTS, "e3v2_results_%s.md" % sha), "w").write("\n".join(L) + "\n")
print("\n".join(L))
