# Computes one row per (claim, verifier section) of __pondus__/*.md with wave, author label, verifier name and type, every `verdict:` line in order, whether a `changed_by:` follows, and the claim's current state; input: __pondus__ via scripts/lab_status.py's own parser; output: a TSV on stdout and, with --summary, the counts by wave and verifier type.
# usage: python3 -I __instrumenta__/w08i_claims_table.py [--summary] > __reports__/wave-08/explorer-w08-i/claims_verdicts.tsv
import sys, os, re, glob, collections
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(root, "scripts"))
import lab_status as L

def head_field(text, name):
    rx = L.field_re(name)
    for line in text.split("\n## verdict")[0].splitlines():
        m = rx.match(line)
        if m: return L.clean_value(m.group(1))
    return ""

rows = []
claims = L.read_claims(root)
by = {c["id"]: c for c in claims}
for c in claims:
    text = L.read(os.path.join(root, c["file"]))
    cl = L.parse_claim(text)
    wave = c["id"][:3]
    author = head_field(text, "author")
    lab = c["label"].split()[0].strip("*`") if c["label"] else ""
    if not cl["sections"]:
        rows.append([c["id"], wave, lab, author, "", "none", "", "0", "no", c["current"], ",".join(c["superseded_by"])])
    for name, lines in cl["sections"]:
        vs = [L.normalise_verdict(m.group(1))[0] or L.clean_value(m.group(1))[:20] for m in map(L.VERDICT_RE.match, lines) if m]
        has_cb = any(L.CHANGED_BY_RE.match(l) for l in lines)
        typ = "proof-adversary" if "proof" in name else "reproducer" if "reproducer" in name else "other"
        rows.append([c["id"], wave, lab, author, name, typ, ">".join(vs), str(len(vs)), "yes" if has_cb else "no", c["current"], ",".join(c["superseded_by"])])
hdr = ["claim", "wave", "label", "author", "verifier", "vtype", "verdict_sequence", "n_verdict_lines", "changed_by", "current", "superseded_by"]
if "--summary" not in sys.argv:
    print("\t".join(hdr))
    for r in rows: print("\t".join(r))
else:
    cnt = collections.defaultdict(collections.Counter)
    for r in rows:
        if r[5] == "none": cnt[r[1]]["(no verdict)"] += 1; continue
        seq = r[6].split(">")
        cnt[r[1]][seq[-1]] += 1
    allv = sorted({v for c in cnt.values() for v in c})
    print("wave\t" + "\t".join(allv) + "\tsections")
    for w in sorted(cnt): print(w + "\t" + "\t".join(str(cnt[w][v]) for v in allv) + "\t" + str(sum(cnt[w].values())))
    print("TOTAL\t" + "\t".join(str(sum(cnt[w][v] for w in cnt)) for v in allv) + "\t" + str(sum(sum(c.values()) for c in cnt.values())))
