# w08-j: scores the guard decisions on the frozen replay set against its hand labels; inputs: the frozen set JSON (argv[1]) and the decisions JSONL of w08j_replay.py (argv[2]); output: markdown tables on stdout (false denials by rule, false allows by expected rule, per implementation and per source), and lists of the false-denied and false-allowed ids. Usage: python3 -I w08j_score.py SET.json DECISIONS.jsonl
import collections, json, sys
cases = {c["id"]: c for c in json.load(open(sys.argv[1]))["cases"]}
dec = {}
for l in open(sys.argv[2]):
    r = json.loads(l); dec[r["id"]] = r
for impl in ("py", "rs"):
    fd, fa, td, ta = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    fdi, fai = [], []
    for i, c in cases.items():
        d = dec[i][impl]
        key = (c["source"].split(":")[0],)
        if c["label"] == "false" and d:
            fd[(d,) + key] += 1; fdi.append(i)
        elif c["label"] == "false":
            ta[key] += 1
        elif c["label"] == "true" and not d:
            fa[((c["rule_expected"] or "?"), "indirect" if c["indirect"] else "direct") + key] += 1; fai.append(i)
        else:
            td[(d,) + key] += 1
    print("## %s: false denials %d, false allows %d (direct %d, indirect %d), true denials %d, true allows %d" % (
        impl, sum(fd.values()), sum(fa.values()), sum(v for k, v in fa.items() if k[1] == "direct"), sum(v for k, v in fa.items() if k[1] == "indirect"), sum(td.values()), sum(ta.values())))
    print("false denials by (rule, source):", dict(sorted(fd.items())))
    print("false allows by (expected rule, kind, source):", dict(sorted(fa.items())))
    print("false-denied ids:", " ".join(fdi))
    print("false-allowed ids:", " ".join(fai))
agree = sum(1 for r in dec.values() if r["py"] == r["rs"])
print("python and rust agree on %d of %d" % (agree, len(dec)))
