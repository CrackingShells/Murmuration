# Joins the verdict sections of the claims (claims_verdicts.tsv from w08i_claims_table.py) with the per-agent list-price USD (agent_spend.tsv from w08i_agent_spend.py): USD per named verifier, per verdict section and per wave, against how many sections ended OVERSTATED/ESCALATE (errors caught) or SUPPORTED, and the same for the claims' authors; inputs: the two TSVs; output: markdown tables on stdout.
# usage: python3 -I __instrumenta__/w08i_verification_cost.py <claims_verdicts.tsv> <agent_spend.tsv>
import sys, csv, re, collections
cv = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
sp = {r["label"]: r for r in csv.DictReader(open(sys.argv[2]), delimiter="\t")}
def usd(label): return float(sp[label]["usd"]) if label in sp else None
ver = collections.OrderedDict()
for r in cv:
    if r["vtype"] == "none": continue
    base = re.match(r"(reproducer-w\d\d-\d+|proof-adversary-w\d\d-\d+)", r["verifier"]).group(1)
    v = ver.setdefault(base, {"sections": 0, "claims": set(), "final": collections.Counter()})
    v["sections"] += 1; v["claims"].add(r["claim"]); v["final"][r["verdict_sequence"].split(">")[-1]] += 1
print("| verifier | wave | USD list | claims verified | sections | SUPPORTED | OVERSTATED | ESCALATE | USD per section |")
print("|--|--|--|--|--|--|--|--|--|")
tot = collections.defaultdict(lambda: collections.Counter())
for b, v in ver.items():
    u = usd(b); w = b.split("-")[1]
    f = v["final"]
    print(f"| {b} | {w} | {'%.2f' % u if u is not None else 'n/a (unnamed agent file)'} | {len(v['claims'])} | {v['sections']} | {f['SUPPORTED']} | {f['OVERSTATED']} | {f['ESCALATE']} | {'%.2f' % (u / v['sections']) if u is not None else ''} |")
    t = tot[w]; t["n"] += 1; t["sections"] += v["sections"]; t["usd"] += u or 0; t["named"] += u is not None
    for k in ("SUPPORTED", "OVERSTATED", "ESCALATE"): t[k] += f[k]
print("\n| wave | verifiers | with a named spend row | USD (named) | sections | SUPPORTED | OVERSTATED | ESCALATE | non-SUPPORTED share |")
print("|--|--|--|--|--|--|--|--|--|")
g = collections.Counter()
for w in sorted(tot):
    t = tot[w]
    print(f"| {w} | {t['n']} | {t['named']} | {t['usd']:.2f} | {t['sections']} | {t['SUPPORTED']} | {t['OVERSTATED']} | {t['ESCALATE']} | {(t['OVERSTATED'] + t['ESCALATE']) / t['sections']:.2f} |")
    g.update(t)
print(f"| all | {g['n']} | {g['named']} | {g['usd']:.2f} | {g['sections']} | {g['SUPPORTED']} | {g['OVERSTATED']} | {g['ESCALATE']} | {(g['OVERSTATED'] + g['ESCALATE']) / g['sections']:.2f} |")
print("\nAuthors (named rows only), by wave:")
au = collections.defaultdict(lambda: [0, 0.0])
for l, r in sp.items():
    if r["role"] == "author" and r["wave"] and r["wave"] != "w99":
        au[r["wave"]][0] += 1; au[r["wave"]][1] += float(r["usd"])
cl = collections.Counter(r["claim"][:3] for r in cv if r["vtype"] != "none" or True)
claims_per_wave = collections.Counter(w for w in {(r["claim"], r["wave"]) for r in cv} for w in [w[1]])
print("| wave | named author rows | USD | claim files |"); print("|--|--|--|--|")
for w in sorted(au): print(f"| {w} | {au[w][0]} | {au[w][1]:.2f} | {claims_per_wave[w]} |")
