# Measures the size of what a PI would open instead of a long hand-back: the "## Result" section of each explorer findings report, the head of each claim file (above its first "## verdict:"), and each verifier's verdict section; inputs: lab root; output: OUTDIR/sections.tsv (kind, owner name, path-free id, characters).
# usage: w08_c2_sections.py LABROOT OUTDIR
import sys, os, re, glob
root, out = sys.argv[1], sys.argv[2]
rows = [["kind", "owner", "id", "chars"]]
for p in sorted(glob.glob(os.path.join(root, "__reports__", "wave-*", "*", "[0-9][0-9]-findings_v*.md"))):
    t = open(p, encoding="utf-8", errors="replace").read()
    m = re.search(r"^## Result[^\n]*\n(.*?)(?=^## |\Z)", t, re.S | re.M)
    owner = p.split(os.sep)[-2]
    rows.append(["report_result", owner, os.path.basename(p), len(m.group(0)) if m else 0])
    rows.append(["report_whole", owner, os.path.basename(p), len(t)])
for p in sorted(glob.glob(os.path.join(root, "__pondus__", "w*-c*.md"))):
    t = open(p, encoding="utf-8", errors="replace").read()
    cid = os.path.basename(p)[:-3]
    parts = re.split(r"^(?=## verdict: )", t, flags=re.M)
    a = re.search(r"^author: (\S+)", parts[0], re.M)
    rows.append(["claim_head", a.group(1) if a else "", cid, len(parts[0])])
    mm = re.search(r"^method:", parts[0], re.M)
    rows.append(["claim_headline", a.group(1) if a else "", cid, mm.start() if mm else len(parts[0])])   # title, label, scope, evidence: what the claim states
    for s in parts[1:]:
        who = re.match(r"## verdict: (\S+)", s).group(1)
        rows.append(["verdict_section", who, cid, len(s)])
        vv = [m.start() for m in re.finditer(r"^verdict:", s, re.M)]
        rows.append(["verdict_tail", who, cid, len(s) - vv[-1] if vv else 0])   # the verdict and reason lines
open(os.path.join(out, "sections.tsv"), "w").write("\n".join("\t".join(str(x) for x in r) for r in rows) + "\n")
print(len(rows) - 1, "rows")
