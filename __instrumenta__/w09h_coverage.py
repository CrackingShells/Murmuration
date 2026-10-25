# For each claim with an ESCALATE verdict and a located verifier hand-back, counts the characters of the claim file's escalating verifier section (independent result, exchange, verdict) and of the hand-back, and the share of the section's numeric tokens (digits with 2+ characters, e.g. 0.8655, 14, 2.1.302) and of its backtick-quoted paths that occur in the hand-back; inputs <outdir>/wakes.json and <outdir>/claim_at_verdict/*.md from w09h_extract.py; output a TSV on stdout.
# usage: python3 -I w09h_coverage.py <outdir>
import sys, os, re, json
out = sys.argv[1]
R = json.load(open(os.path.join(out, "wakes.json")))
num = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)*(?![\w])")
print("claim\tverifier\twake\thandback_chars\tsection_chars\texchange_chars\tnum_tokens_in_section\tnum_in_handback\tshare\tpath_tokens\tpaths_in_handback")
for cid, r in R.items():
    wk = [w for w in r["wakes"] if w["agent"] == r["verifier"]]
    txt = open(os.path.join(out, "claim_at_verdict", cid + ".md")).read()
    i = txt.find("## verdict: " + r["verifier"])
    sec = txt[i:]
    j = sec.find("### exchange"); k = sec.find("\nverdict", j) if j >= 0 else -1
    ex = len(sec) - j if j >= 0 else 0
    ns = {t.rstrip(".,") for t in num.findall(sec) if len(t.replace(",", "")) >= 2}
    ps = set(re.findall(r"`([^`\s]*[/.][^`\s]*)`", sec))
    if not wk:
        print("\t".join([cid, r["verifier"], "none", "", str(len(sec)), str(ex), str(len(ns)), "", "", str(len(ps)), ""])); continue
    w = wk[0]; hb = w["body"]
    inh = {t for t in ns if t in hb}
    ph = {p for p in ps if p in hb}
    print("\t".join([cid, r["verifier"], "%s/T%d" % (w["label"], w["turn"]), str(len(hb)), str(len(sec)), str(ex), str(len(ns)), str(len(inh)), "%.2f" % (len(inh) / max(1, len(ns))), str(len(ps)), str(len(ph))]))
