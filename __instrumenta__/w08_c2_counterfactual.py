# Prices the gate on the lab's past hand-backs: for each N, how many hand-backs it would catch, and the USD net of the PI keeping only a short message (CF1), of the PI then opening the file for every fired hand-back (CF2-all), and for those it did not open in the past (CF2-new); inputs: OUTDIR with handbacks.tsv, pi_side.tsv, sections.tsv; output: OUTDIR/counterfactual.md and counterfactual.tsv. ESTIMATE: formulas in the md.
# usage: w08_c2_counterfactual.py OUTDIR [S_KEPT=1200] [full] [low]
import csv, sys, os, re, statistics as st, collections
D = sys.argv[1]
S = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
LOW = "low" in sys.argv[3:]   # low: the dropped detail is already in the worker's file, so only the second message is new output
FULL = len(sys.argv) > 3 and sys.argv[3] == "full"   # full: the whole claim head and verdict section; default: the claim headline and the verdict lines
HEADKIND, VERKIND = ("claim_head", "verdict_section") if FULL else ("claim_headline", "verdict_tail")
rd = lambda f: list(csv.DictReader(open(os.path.join(D, f)), delimiter="\t"))
W, P, SEC = rd("handbacks.tsv"), rd("pi_side.tsv"), rd("sections.tsv")
byid = {w["agent_id"]: w for w in W}
byname = collections.defaultdict(list)
for w in W:
    byname[w["name"]].append(w)
secs = collections.defaultdict(dict)
for r in SEC:
    secs[r["kind"]][(r["owner"], r["id"])] = int(r["chars"])
res_by_owner = {o: c for (o, i), c in secs["report_result"].items()}
head_by_author = collections.defaultdict(list)
for (o, i), c in secs[HEADKIND].items():
    head_by_author[o].append(c)
ver_by_owner = collections.defaultdict(list)
for (o, i), c in secs[VERKIND].items():
    ver_by_owner[o].append(c)
med = {"explorer": st.median(res_by_owner.values()), "author": st.median(c for v in head_by_author.values() for c in v), "reproducer": st.median(c for v in ver_by_owner.values() for c in v)}
rows = []
for p in P:
    if not p["usd_item"]:
        continue
    nm = p["name"]
    w = byid.get(nm) or None
    role = p["role"] if p["role"] != "?" else ((w or {}).get("role") or "?")
    wnm = (w or {}).get("name") or nm
    hb = int(p["hb_chars"])
    cands = [x for x in byname.get(wnm, [])]
    extra_w = [float(x["extra_request_read_usd"]) for x in cands if x["extra_request_read_usd"]]
    wreq = float(w["extra_request_read_usd"]) if w and w["extra_request_read_usd"] else (st.median(extra_w) if extra_w else 0.02)
    if role == "explorer":
        sec = res_by_owner.get(wnm, med["explorer"])
    elif role == "author":
        v = head_by_author.get(wnm)
        sec = st.median(v) if v else med["author"]
    elif role == "reproducer":
        v = ver_by_owner.get(wnm)
        sec = st.median(v) if v else med["reproducer"]
    else:
        sec = 0
    rows.append(dict(session=p["session"], role=role, name=wnm, hb=hb, u=float(p["usd_per_char"]), wreq=wreq, sec=sec, nreq=float(p["next_request_read_usd"] or 0.07),
                     read=int(p["pi_read"]), usd_item=float(p["usd_item"]), frame=int(p["pi_chars"]) - hb, sonnet_out=10 / 1e6, tpc=0.4))
out = ["# Counterfactual price of the gate on past hand-backs (ESTIMATE)", "", "Hand-backs priced: %d of %d (PI cost known); kept size after the gate S = %d characters (ASSUMPTION; the live test replaces it)." % (len(rows), len(P), S), ""]
out += ["Formulas, per fired hand-back i (hb_i > N):",
        "- PI saving = u_i x (hb_i - S): u_i = USD of the PI-context item / its characters (write once + later reads + re-writes, explorer-w08-d's model).",
        "- worker cost w_i = the worker's own cache-read price x its context at the hand-back (one extra request) + (S + (hb_i - S)) x 0.4 tokens x USD 10 per M (the second message and a Write of all that was dropped, an upper bound: much of it is already in the file); with `low`, only S x 0.4 x 10 / 1e6 (the detail is already in the file).",
        "- CF1 net = saving - w_i. PI keeps the short message only.",
        "- opening cost o_i = u_i x section_i + the PI's next-request cache-read USD + USD 0.003 (a tool call's output). section_i = the worker's own report Result section (explorer), the claim's headline above `method:` (author) or the verdict and reason lines (reproducer); with `full`, the whole claim head and verdict section (median of the role when the worker's file is not in the lab).",
        "- CF2-all net = CF1 net - o_i for every fired hand-back. CF2-new net = CF1 net - o_i for those after which the PI did not open the named file in the past (pi_read = 0); the others are assumed to be opened anyway.",
        "- break-even p* = sum of (saving - w_i) / sum of o_i over the fired hand-backs: the share of them the PI may newly open before the net turns negative.", ""]
tsv = [["N", "role", "n_all", "n_fired", "pi_chars_dropped", "pi_saving_usd", "worker_cost_usd", "cf1_net", "opening_cost_all", "cf2_all_net", "opening_cost_new", "cf2_new_net", "p_star", "past_read_share_fired"]]
out += ["| N | role | hand-backs | fired | PI chars dropped | PI saving USD | worker cost USD | CF1 net | CF2-all net | CF2-new net | p* | share the PI opened in the past |", "|--|--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]
for N in (1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000):
    for role in ("all", "explorer", "author", "reproducer"):
        rr = [r for r in rows if role == "all" or r["role"] == role]
        f = [r for r in rr if r["hb"] > N]
        if not f:
            continue
        drop = sum(r["hb"] - S for r in f if r["hb"] > S)
        sav = sum(r["u"] * max(0, r["hb"] - S) for r in f)
        wc = sum(r["wreq"] + (S if LOW else r["hb"]) * r["tpc"] * r["sonnet_out"] for r in f)
        op = [r["u"] * r["sec"] + r["nreq"] + 0.003 for r in f]
        opn = sum(o for r, o in zip(f, op) if not r["read"])
        cf1 = sav - wc
        tsv.append([N, role, len(rr), len(f), drop, "%.3f" % sav, "%.3f" % wc, "%.3f" % cf1, "%.3f" % sum(op), "%.3f" % (cf1 - sum(op)), "%.3f" % opn, "%.3f" % (cf1 - opn), "%.2f" % (cf1 / sum(op)), "%.2f" % (sum(r["read"] for r in f) / len(f))])
        out.append("| " + " | ".join(str(x) for x in tsv[-1][:1] + [tsv[-1][1]] + tsv[-1][2:5] + tsv[-1][5:9] + [tsv[-1][9], tsv[-1][11], tsv[-1][12], tsv[-1][13]]) + " |")
open(os.path.join(D, "counterfactual_S%d%s.tsv" % (S, ("_full" if FULL else "") + ("_low" if LOW else ""))), "w").write("\n".join("\t".join(str(x) for x in r) for r in tsv) + "\n")
tot = sum(r["usd_item"] for r in rows)
out += ["", "Total USD the %d hand-backs cost the PI over their lives: %.2f (%d characters of worker text; PI frame about %d characters each)." % (len(rows), tot, sum(r["hb"] for r in rows), st.median(r["frame"] for r in rows))]
open(os.path.join(D, "counterfactual_S%d%s.md" % (S, ("_full" if FULL else "") + ("_low" if LOW else ""))), "w").write("\n".join(out) + "\n")
print("\n".join(out))
