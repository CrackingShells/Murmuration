# w06-c7 (E3): turns the run summary json written by w06c7_e3_all.py into the markdown tables of the claim (each metric against the registered rule), with no raw run output; inputs: <S>/e3_results_<sha>_<mode>.json and the committed lists; outputs: __reports__/wave-06/author-w06-5/e3_results_<sha>_<mode>.md and the same on stdout. Usage: python3 -I __instrumenta__/w06c7_e3_report.py <sha> <mode>
import json, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w06c7_e3_run as E

sha, mode = sys.argv[1], sys.argv[2]
import glob


def merge(a, b):
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            merge(a[k], v)
        elif k not in a:
            a[k] = v
    return a


files = sorted(glob.glob("%s/e3_results_%s_%s.json" % (E.S, sha, mode)) + glob.glob("%s/shard*/e3_results_%s_%s_s*.json" % (E.S, sha, mode)))
R = {}
for f in files:
    merge(R, json.load(open(f)))
OUT = os.path.join(E.LISTS, "e3_results_%s_%s.md" % (sha, mode))
lists = {n: {c["id"]: c for c in json.load(open("%s/e3_%s.json" % (E.LISTS, n)))} for n in ("attacks", "ordinary", "mention", "evasions")}
DOLLAR = re.compile(r"\$\(|`|\$[A-Za-z_{]")
L = []


def p(*a):
    L.append(" ".join(str(x) for x in a))


def cases(res):
    return {k: v for k, v in res.items() if not k.startswith("_run_")}


def runs(res):
    return {k[5:]: v for k, v in res.items() if k.startswith("_run_")}


def cmd_of(lst, cid):
    c = lists[lst][cid]
    return c.get("command") or ("%s %s" % (c["tool"], c["input"].get("file_path")))


def esc(s):
    return s.replace("|", "\\|").replace("\n", "\\n")[:90]


p("# E3 results (derived), commit %s, mode %s" % (R["commit"], mode))
p("")
p("Preflight (stub first on PATH in the live session): `%s`" % R["preflight"].replace("\n", " ; "))
p("")
g1 = cases(R["g1"])
den = [k for k, v in g1.items() if v["outcome"] == "denied"]
p("## g1 attacks denied: %d of %d tested (%d in the list)" % (len(den), len(g1), len(lists["attacks"])))
p("")
p("| id | group | outcome | command or edit |")
p("|:--|:--|:--|:--|")
for k, v in sorted(g1.items()):
    p("| %s | %s | %s | `%s` |" % (k, lists["attacks"][k]["group"], v["outcome"], esc(cmd_of("attacks", k))))
bad = {k: v["outcome"] for k, v in g1.items() if v["outcome"] != "denied"}
p("")
p("Not denied: %s" % (json.dumps(bad) if bad else "none"))
p("")
g2 = cases(R["g2"])
ok = [k for k, v in g2.items() if v["outcome"] not in ("denied", "not-called") and v["spawns_for_case"] == 0]
p("## g2 ordinary: %d of %d passed with 0 hook spawns (denied or spawned or not called: the rest)" % (len(ok), len(g2)))
p("")
p("| id | outcome | spawns for this call | has `$` expansion | command |")
p("|:--|:--|--:|:--|:--|")
for k, v in sorted(g2.items()):
    c = lists["ordinary"][k]
    s = c.get("command") or json.dumps(c["input"])
    p("| %s | %s | %d | %s | `%s` |" % (k, v["outcome"], v["spawns_for_case"], "yes" if DOLLAR.search(s) else "no", esc(cmd_of("ordinary", k))))
p("")
if "mention" in R:
    m = cases(R["mention"])
    p("## mention-only commands (not gated): %d of %d denied" % (sum(1 for v in m.values() if v["outcome"] == "denied"), len(m)))
    p("")
    for k, v in sorted(m.items()):
        p("- %s %s `%s` (spawns %d)" % (k, v["outcome"], esc(cmd_of("mention", k)), v["spawns_for_case"]))
    p("")
if "g5" in R:
    e = cases(R["g5"])
    p("## g5 evasions (reported, not gated)")
    p("")
    p("| id | kind | outcome | spawns | command |")
    p("|:--|:--|:--|--:|:--|")
    for k, v in sorted(e.items()):
        p("| %s | %s | %s | %d | `%s` |" % (k, lists["evasions"][k]["group"], v["outcome"], v["spawns_for_case"], esc(cmd_of("evasions", k))))
    p("")
p("## g3 fail closed")
p("")
p("| variant | a01 | a05 | a08 |")
p("|:--|:--|:--|:--|")
for name, v in R["g3"].items():
    c = cases(v)
    p("| %s | %s |" % (name, " | ".join("%s" % c[k]["outcome"] if k in c else "-" for k in ("a01", "a05", "a08"))))
p("")
p("## g4 cost")
p("")
allr = {}
for sect in ("g2",):
    allr.update(runs(R[sect]))
spawn_total = sum(v["dbg_spawns"] for v in allr.values())
nodollar = [k for k in g2 if not DOLLAR.search(lists["ordinary"][k].get("command") or json.dumps(lists["ordinary"][k]["input"]))]
p("Ordinary list: %d spawns in the debug logs (guard log lines %d); spawns for the %d calls without `$`: %d; for the %d calls with `$`: %d." % (
    spawn_total, sum(v["guard_log_lines"] for v in allr.values()), len(nodollar), sum(g2[k]["spawns_for_case"] for k in nodollar),
    len(g2) - len(nodollar), sum(g2[k]["spawns_for_case"] for k in g2 if k not in nodollar)))
ms = []
for k, v in g1.items():
    r = runs(R["g1"]).get(v["run"], {})
    if v["outcome"] == "denied" and not DOLLAR.search(lists["attacks"][k].get("command") or "$") and r.get("dbg_spawns") == 1:
        ms += r["ms"]
if ms:
    p("Platform time of the guard on a matched call without `$` (one spawn, debug log): n=%d median %d ms, min %d, max %d." % (len(ms), statistics.median(ms), min(ms), max(ms)))
dol = [v for k, v in runs(R["g2"]).items() if v["dbg_spawns"] > 1]
if dol:
    p("A call with `$` made %s spawns, last finishing at %s ms." % (",".join(str(v["dbg_spawns"]) for v in dol), ",".join(str(v["ms"][-1]) for v in dol)))
if "single_row" in R:
    sr = R["single_row"]
    so = cases(sr["ordinary"])
    p("")
    p("One unconditional Bash row (alternative arm): ordinary list %d spawns for %d calls (%d Bash calls); coverage of the calls the `if` rows cannot see: %s." % (
        sum(v["dbg_spawns"] for v in runs(sr["ordinary"]).values()), len(so), sum(1 for k in so if lists["ordinary"][k]["tool"] == "Bash"),
        json.dumps({k: v["outcome"] for k, v in sorted(cases(sr["gaps"]).items())})))
open(OUT, "w").write("\n".join(L) + "\n")
print("\n".join(L))
