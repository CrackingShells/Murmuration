# For each claim file cut at its ESCALATE verdict (w09h_extract.py output), prints the line range of the escalating verifier's section, the line range of its `### exchange`, their character sizes, and the length of the pointer notice "[claim file: __pondus__/<id>.md lines A-B hold the verdict section; exchange C-B]" that a hook could add; also totals and median over the files; output TSV on stdout.
# usage: python3 -I w09h_ranges.py <outdir>
import sys, os, glob, statistics as st
out = sys.argv[1]
rows = []
for p in sorted(glob.glob(os.path.join(out, "claim_at_verdict", "*.md"))):
    cid = os.path.basename(p)[:-3]
    L = open(p, encoding="utf-8").read().split("\n")
    if L and L[-1] == "": L.pop()
    a = max(i for i, l in enumerate(L) if l.startswith("## verdict:")) + 1
    b = len(L)
    e = next((i for i in range(a - 1, b) if L[i].startswith("### exchange")), None)
    e = e + 1 if e is not None else None
    sec = sum(len(x) + 1 for x in L[a - 1:b]); ex = sum(len(x) + 1 for x in L[e - 1:b]) if e else 0
    ptr = "[claim file: __pondus__/%s.md lines %d-%d hold the verdict section, the exchange from line %s]" % (cid, a, b, e)
    rows.append((cid, a, b, e, sec, ex, len(ptr)))
print("claim\tsec_from\tsec_to\texch_from\tsec_chars\texch_chars\tpointer_chars")
for r in rows: print("\t".join(str(x) for x in r))
for k, n in ((4, "sec_chars"), (5, "exch_chars"), (6, "pointer_chars")):
    v = [r[k] for r in rows]
    print("# %s: n=%d min=%d median=%d mean=%d max=%d sum=%d" % (n, len(v), min(v), st.median(v), st.mean(v), max(v), sum(v)))
