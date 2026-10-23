# Finds, in worker transcripts of waves 4-8, requests that carried one tool call followed by a request whose calls did not depend on the first's result, and estimates the USD that merging them into one message would have saved; inputs: parsed turns (w07b_loop_parse.py JSON) and signature files (w08g_sig.py) in a scratch folder; outputs: tables (markdown, tsv) in an output folder and an audit sample with call heads in the scratch folder (not committed).
# usage: w08g_pairs.py PARSED_DIR SIG_DIR OUTDIR AUDIT_FILE   (dependence is judged by tokens: a call depends on the previous request when one of its path-like tokens first appeared in that request's tool results; see the report for tiers loose, strict, brief)
import sys, os, json, glob, random, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L
PARSED, SIGD, OUT, AUDIT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
A_SIG, B_SIG = 0.3278, 806.4          # thinking_tokens = A (signature chars - B), w08-f fit (R2 0.962)
CAP = 8
def price(model): return L.PRICES.get((model or "").rsplit("-20", 1)[0], L.PRICES["claude-sonnet-5-5"])
def kind_of(t):
    ks = {c["cls"] for c in t["calls"]}
    return (ks.pop() if len(ks) == 1 else "mixed") if t["ncalls"] > 0 else None
def role_of(d):
    ty = d.get("type") or ""
    for r in ("author", "reproducer", "explorer", "proof-adversary"):
        if ty.endswith(r): return r
    return "other"
def pair_ok(T, j, mode, br, s=None, bcls=None):
    """True when request j could have gone out in the message of request j-1 (and of the batch starting at index s when given)."""
    t = T[j]; prev = T[j - 1]
    if t["ncalls"] == 0 or prev["ncalls"] == 0 or prev["missing_results"] or t["wait_s"] is not None or t["new_prompt"]: return False
    ks = kind_of(t)
    if ks not in ("R", "F"): return False
    if bcls is not None and ks != bcls: return False
    lo = j - 1 if s is None else s
    if any(c["err"] for tt in T[lo:j] for c in tt["calls"]): return False
    if any(d >= lo for c in t["calls"] for d in c["dep_idx"]) or any(c["jac"] >= 0.6 for c in t["calls"]): return False
    if mode in ("strict", "brief") and not all(c["ntok"] >= 1 and c["n_unseen"] == 0 for c in t["calls"]): return False
    if mode == "brief" and not br[j]: return False
    return True
def walk(T, br, mode):
    s = None; bcls = None; bcalls = 0; bpaths = set(); out = []
    for j, t in enumerate(T):
        kind = kind_of(t); ok_start = kind in ("R", "F"); can = False
        if s is not None and j > 0 and ok_start and bcalls + t["ncalls"] <= CAP and pair_ok(T, j, mode, br, s, bcls):
            if kind == "F":
                ps = [c["path"] for c in t["calls"]]
                can = all(p and p not in bpaths for p in ps) and len(set(ps)) == len(ps)
            else: can = True
        if can:
            out.append(j); bcalls += t["ncalls"]; bpaths |= {c["path"] for c in t["calls"]}
        elif ok_start:
            s = j; bcls = kind; bcalls = t["ncalls"]; bpaths = {c["path"] for c in t["calls"]}
        else: s = None
    return out
def saving(T, sig, j):
    t = T[j]; p = price(t["model"])
    a = (t["cr"] * p[2] + t["inp"] * p[0]) / 1e6
    tk = max(0.0, A_SIG * (sig[j] - B_SIG)) if sig[j] > 0 else 0.0
    nl = len(T) - j - 1
    wp = 0.0
    if j + 1 < len(T): wp = p[4] if T[j + 1]["cw1"] > T[j + 1]["cw5"] else p[3]
    c = tk * (p[1] + nl * p[2] + wp) / 1e6
    return a, c, tk
rows = collections.defaultdict(lambda: collections.Counter())
perworker = []; audit = []; contrib = []
for f in sorted(glob.glob(PARSED + "/*.json")):
    d = json.load(open(f)); sg = json.load(open(f.replace("/parsed/", "/sig/")[:-5] + ".sig.json"))
    if d["name"] == "explorer-w08-g": continue
    T = d["turns"]; n = min(len(T), len(sg["sig"])); T = T[:n]; sig = sg["sig"][:n]; br = sg["brief"][:n]
    role = "PI" if d["agent"] == "PI" else role_of(d)
    keys = [(d["label"], role), ("all", role), (d["label"], "all workers"), ("all", "all workers")] if role != "PI" else [(d["label"], "PI"), ("all", "PI")]
    c = collections.Counter()
    c["workers"] = 1; c["requests"] = n
    c["req_with_call"] = sum(1 for t in T if t["ncalls"] > 0); c["single_call"] = sum(1 for t in T if t["ncalls"] == 1)
    c["calls"] = sum(t["ncalls"] for t in T)
    for t in T:
        p = price(t["model"])
        c["usd_ctx"] += (t["cr"] * p[2] + t["cw5"] * p[3] + t["cw1"] * p[4] + t["inp"] * p[0]) / 1e6
        c["usd_rec"] += t["usd"]
    c["think_tok"] = sum(max(0.0, A_SIG * (x - B_SIG)) for x in sig if x > 0)
    for j in range(1, n):
        if T[j - 1]["ncalls"] == 1 and T[j]["ncalls"] > 0 and not T[j - 1]["missing_results"] and T[j]["wait_s"] is None and not T[j]["new_prompt"]:
            c["pairs_candidate"] += 1
            t_, pv = T[j], T[j - 1]
            if any(x["err"] for x in pv["calls"]): c["why_error_in_previous_result"] += 1
            elif kind_of(pv) not in ("R", "F") or kind_of(t_) not in ("R", "F"):
                c["why_class_%s_then_%s" % (kind_of(pv), kind_of(t_))] += 1
                if not any(d >= j - 1 for x in t_["calls"] for d in x["dep_idx"]) and not any(x["jac"] >= 0.6 for x in t_["calls"]): c["anyclass_token_independent"] += 1
            elif any(d >= j - 1 for x in t_["calls"] for d in x["dep_idx"]): c["why_token_first_seen_in_previous_result"] += 1
            elif any(x["jac"] >= 0.6 for x in t_["calls"]): c["why_near_copy_of_previous_call"] += 1
            else: c["why_independent_loose"] += 1
            for mode in ("loose", "strict", "brief"):
                if kind_of(T[j - 1]) in ("R", "F") and pair_ok(T, j, mode, br): c["pair_" + mode] += 1
            if kind_of(T[j - 1]) in ("R", "F") and pair_ok(T, j, "loose", br): c["pair_loose_n2"] += T[j]["ncalls"]
    for mode in ("loose", "strict", "brief"):
        for j in walk(T, br, mode):
            a, cc, tk = saving(T, sig, j)
            if mode == "loose" and role != "PI": contrib.append((cc, a, tk, d["name"], j, sig[j]))
            c["abs_" + mode] += 1; c["usdA_" + mode] += a; c["usdC_" + mode] += cc; c["thinktok_" + mode] += tk
            if mode == "strict": audit.append((d["label"], d["name"], j, role, T[j - 1]["calls"] and sg["heads"][j - 1], sg["heads"][j] if j < len(sg["heads"]) else None, kind_of(T[j])))
    for k in keys: rows[k].update(c)
    perworker.append((d["label"], d["name"], role, n, c))
tiers = ("loose", "strict", "brief")
def line(k, c):
    r = [k[0], k[1], c["workers"], c["requests"], c["single_call"], c["pairs_candidate"]]
    r += [c["pair_" + m] for m in tiers] + [c["abs_" + m] for m in tiers]
    r += ["%.1f" % (100 * c["abs_loose"] / max(1, c["requests"])), "%.1f" % (100 * c["abs_strict"] / max(1, c["requests"]))]
    r += ["%.3f" % c["usdA_loose"], "%.3f" % (c["usdA_loose"] + c["usdC_loose"]), "%.3f" % c["usdA_strict"], "%.3f" % (c["usdA_strict"] + c["usdC_strict"]), "%.3f" % c["usdA_brief"], "%.3f" % (c["usdA_brief"] + c["usdC_brief"]), "%.2f" % c["usd_ctx"], "%.2f" % c["usd_rec"],
          "%.2f" % (100 * (c["usdA_loose"] + c["usdC_loose"]) / max(1e-9, c["usd_rec"])), "%.2f" % (100 * c["usdA_strict"] / max(1e-9, c["usd_rec"]))]
    return "\t".join(str(x) for x in r)
hdr = "wave\trole\tworkers\trequests\tsingle_call_requests\tsingle_then_next_candidates\tpairs_loose\tpairs_strict\tpairs_brief\tabsorbed_loose\tabsorbed_strict\tabsorbed_brief\tabs_loose_pct_req\tabs_strict_pct_req\tusd_loose_reads\tusd_loose_reads_plus_think\tusd_strict_reads\tusd_strict_reads_plus_think\tusd_brief_reads\tusd_brief_reads_plus_think\tusd_context\tusd_recorded\tloose_hi_pct_recorded\tstrict_lo_pct_recorded"
order = sorted(rows, key=lambda k: (k[0] != "all", k[0], k[1]))
open(os.path.join(OUT, "pairs_by_wave_role.tsv"), "w").write(hdr + "\n" + "\n".join(line(k, rows[k]) for k in order) + "\n")
pw = ["label\tworker\trole\trequests\tsingle_call\tabsorbed_loose\tabsorbed_strict\tabsorbed_brief\tusd_loose_hi\tusd_strict_lo\tusd_recorded"]
for (lb, nm, role, n, c) in sorted(perworker, key=lambda x: -(x[4]["usdA_loose"] + x[4]["usdC_loose"])):
    pw.append("%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%.3f\t%.3f\t%.2f" % (lb, nm, role, n, c["single_call"], c["abs_loose"], c["abs_strict"], c["abs_brief"], c["usdA_loose"] + c["usdC_loose"], c["usdA_strict"], c["usd_rec"]))
open(os.path.join(OUT, "pairs_per_worker.tsv"), "w").write("\n".join(pw) + "\n")
random.seed(1)
smp = random.sample(audit, min(40, len(audit)))
with open(AUDIT, "w") as fh:
    for i, (lb, nm, j, role, h1, h2, k) in enumerate(smp):
        fh.write("#%d %s %s k=%d %s\n   prev: %s\n   this: %s\n" % (i, lb, nm, j, role, " || ".join(h1 or [])[:260], " || ".join(h2 or [])[:260]))
contrib.sort(reverse=True)
with open(os.path.join(OUT, "pairs_think_sensitivity.txt"), "w") as fh:
    fh.write("loose-absorbed worker requests: %d; thinking carry USD %.3f; read USD %.3f\n" % (len(contrib), sum(x[0] for x in contrib), sum(x[1] for x in contrib)))
    fh.write("with thinking tokens capped per request at 2000 / 1000 / 500: carry USD %.3f / %.3f / %.3f\n" % tuple(sum(x[0] * min(1.0, cap / x[2]) if x[2] > 0 else 0 for x in contrib) for cap in (2000, 1000, 500)))
    fh.write("requests with a thinking block: %d; median thinking tokens (est.) of those: %.0f\n" % (sum(1 for x in contrib if x[5] > 0), sorted(x[2] for x in contrib if x[5] > 0)[sum(1 for x in contrib if x[5] > 0) // 2]))
    fh.write("five largest carry contributions (USD, est. thinking tokens, worker, request index, signature chars):\n")
    for x in contrib[:5]: fh.write("  %.3f\t%d\t%s\t%d\t%d\n" % (x[0], x[2], x[3], x[4], x[5]))
wk = sorted({k for c in rows.values() for k in c if k.startswith("why_") or k.startswith("anyclass")})
with open(os.path.join(OUT, "pairs_why_not.tsv"), "w") as fh:
    fh.write("wave\trole\tcandidates\t" + "\t".join(wk) + "\n")
    for k in order:
        if k[0] == "all": fh.write("%s\t%s\t%d\t%s\n" % (k[0], k[1], rows[k]["pairs_candidate"], "\t".join(str(rows[k][x]) for x in wk)))
print(open(os.path.join(OUT, "pairs_why_not.tsv")).read())
