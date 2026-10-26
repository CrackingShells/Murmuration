# Counts, from the <outdir>/<label>_turns.jsonl and read_table.tsv that w09d_turns.py writes, (a) raw-open share of hand-back wakes by wave and sender role, (b) re-read shares of PI reads in waves 5-8 (by file name, by normalised path, by identical call text), (e) raw-open share with and without the platform banner; prints a text table to stdout.
# usage: python3 -I w09c2_counts.py <outdir>   (outdir holds w123, w4, w5, w6, w7, w8 _turns.jsonl and read_table.tsv)
import json, sys, os, re, csv, collections
out = sys.argv[1]
LABELS = [l for l in ["w123", "w4", "w5", "w6", "w7", "w8"] if os.path.exists(os.path.join(out, l + "_turns.jsonl"))]
BANNER = "[harness: subagent output matched"

def pct(a, b):
    return "%d/%d (%d%%)" % (a, b, round(100 * a / b)) if b else "0/0"

turns = {l: [json.loads(x) for x in open(os.path.join(out, l + "_turns.jsonl"))] for l in LABELS}
# wake = turn whose first trigger is B or N; request = the turn has at least one assistant step
print("(a) wakes with a request: raw artifact opened in the same turn (tn['raw_here'], strict rule of w09d_turns.py:is_raw)")
tot = [0, 0]
for l in LABELS:
    w = [t for t in turns[l] if t["triggers"][0]["kind"] in ("B", "N") and t["n_steps"] > 0]
    r = [t for t in w if t["raw_here"]]
    rn = [t for t in w if t["raw_here"] or t["raw_next"]]
    allw = [t for t in turns[l] if t["triggers"][0]["kind"] in ("B", "N")]
    print("  %-5s wakes=%d with request=%d  raw same turn %s  same or next %s" % (l, len(allw), len(w), pct(len(r), len(w)), pct(len(rn), len(w))))
print("(a2) B-led wakes with a request, waves 5-8, by sender role (role = prefix of the agent name in the trigger)")
byrole = collections.defaultdict(lambda: [0, 0]); bywr = collections.defaultdict(lambda: [0, 0])
for l in [x for x in ["w5", "w6", "w7", "w8"] if x in turns]:
    for t in turns[l]:
        g = t["triggers"][0]
        if g["kind"] != "B" or t["n_steps"] == 0:
            continue
        nm = g.get("agent") or ""
        role = nm.split("-")[0] if re.match(r"(explorer|author|reproducer|proof-adversary)-w\d\d", nm) else "other"
        byrole[role][0] += 1; byrole[role][1] += t["raw_here"]
        bywr[(l, role)][0] += 1; bywr[(l, role)][1] += t["raw_here"]
n = sum(v[0] for v in byrole.values()); k = sum(v[1] for v in byrole.values())
for role, v in sorted(byrole.items()):
    print("  %-10s %s" % (role, pct(v[1], v[0])))
print("  all        %s" % pct(k, n))
for key in sorted(bywr):
    print("   ", key, "%d/%d" % (bywr[key][1], bywr[key][0]))
print("(a3) the same, with the raw read in the same turn OR the next turn, by role")
byrole2 = collections.defaultdict(lambda: [0, 0])
for l in [x for x in ["w5", "w6", "w7", "w8"] if x in turns]:
    for t in turns[l]:
        g = t["triggers"][0]
        if g["kind"] != "B" or t["n_steps"] == 0:
            continue
        nm = g.get("agent") or ""
        role = nm.split("-")[0] if re.match(r"(explorer|author|reproducer|proof-adversary)-w\d\d", nm) else "other"
        byrole2[role][0] += 1; byrole2[role][1] += (t["raw_here"] or t["raw_next"])
for role, v in sorted(byrole2.items()):
    print("  %-10s %s" % (role, pct(v[1], v[0])))

print("(a4) sensitivity, waves 5-8, B-led wakes with a request, same turn, by role: (view) only Read/cat/sed/head/tail/grep/jq-type view calls count, not ls/du/find/wc/awk/python3 queries; (linked) only a path naming the sender, or a claim file whose id (wNN-cK) is in the first 260 characters of the hand-back")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w09d_turns import obj_class, RAW
VIEW = ("read-whole", "read-part", "bash-view")
agg = collections.defaultdict(lambda: [0, 0, 0, 0])
for l in [x for x in ["w5", "w6", "w7", "w8"] if x in turns]:
    for t in turns[l]:
        g = t["triggers"][0]
        if g["kind"] != "B" or t["n_steps"] == 0:
            continue
        nm = g.get("agent") or ""
        role = nm.split("-")[0] if re.match(r"(explorer|author|reproducer|proof-adversary)-w\d\d", nm) else "other"
        calls = [c for s_ in t["steps"] for c in s_["calls"]]
        ids = set(re.findall(r"w\d\d-c\d+", g.get("head") or ""))
        v = any(c["kind"] in VIEW and any(obj_class(p) in RAW or (nm and nm in p) for p in c["paths"]) for c in calls)
        k = any(c["kind"] in ("read-whole", "read-part", "bash-view", "bash-query") and any((nm and nm in p) or (obj_class(p) == "claim file" and any(i in p for i in ids)) for p in c["paths"]) for c in calls)
        agg[role][0] += 1; agg[role][1] += t["raw_here"]; agg[role][2] += v; agg[role][3] += k
for role, a in sorted(agg.items()):
    print("  %-10s n=%d  rule as coded %d  view-only %d  linked-to-sender %d" % (role, a[0], a[1], a[2], a[3]))

print("(b) reads in waves 5-8 (rows of read_table.tsv; a call naming up to 3 paths gives up to 3 rows)")
rows = [r for r in csv.DictReader(open(os.path.join(out, "read_table.tsv")), delimiter="\t") if r["label"] in ("w5", "w6", "w7", "w8")]
def ch(r):
    return int(r["chars"]) if r["chars"] not in ("", "None") else 0
def norm(p):
    m = re.search(r"(__\w+__/.*|skills/.*|agents/.*|scripts/.*|hooks/.*)", p)
    return m.group(1) if m else os.path.join(os.path.basename(os.path.dirname(p)), os.path.basename(p))
print("  rows %d, characters %d" % (len(rows), sum(ch(r) for r in rows)))
withpath = [r for r in rows if r["path"]]
print("  rows with a path (lab_status, search, git-without-path have none): %d" % len(withpath))
rep = [r for r in rows if r["repeat"] == "True"]
print("  repeat by file NAME (w09d_turns.py rule): %s of all rows, %s of rows with a path" % (pct(len(rep), len(rows)), pct(len(rep), len(withpath))))
seen = collections.defaultdict(set); nrep = 0
for r in withpath:
    k = norm(r["path"])
    if k in seen[r["label"]]:
        nrep += 1
    seen[r["label"]].add(k)
print("  repeat by NORMALISED PATH (worktree prefix stripped; no basename collisions): %s of rows with a path" % pct(nrep, len(withpath)))
ks = collections.defaultdict(set); ni = 0; nic = 0
for r in rows:
    if r["repeat"] == "True" and r["key"] in ks[r["label"]]:
        ni += 1; nic += ch(r)
    ks[r["label"]].add(r["key"])
print("  of the name-repeats, identical call text to an earlier row: %d rows, %d characters" % (ni, nic))
rw = sum(1 for r in rep if r["repeat_after_own_write"] == "True")
print("  name-repeats after the PI's own write to that file: %d" % rw)
syn = [r for r in rows if r["class"] == "synthesis"]; print("  synthesis reads %d, repeats %d" % (len(syn), sum(r["repeat"] == "True" for r in syn)))
wn = [r for r in rows if r["class"] == "wave note"]; print("  wave-note reads %d, repeats %d" % (len(wn), sum(r["repeat"] == "True" for r in wn)))

print("(e) B-led wakes with a request, all waves 1-8: raw read in the same turn, banner in the first 260 characters of the hand-back vs not")
c = collections.defaultdict(lambda: [0, 0])
for l in LABELS:
    for t in turns[l]:
        g = t["triggers"][0]
        if g["kind"] != "B" or t["n_steps"] == 0:
            continue
        b = BANNER in (g.get("head") or "")
        c[b][0] += 1; c[b][1] += t["raw_here"]
for b in (True, False):
    print("  banner=%s %s" % (b, pct(c[b][1], c[b][0])))
