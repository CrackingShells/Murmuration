# Computes, per agent type (author, reproducer, explorer, PI) and per pause phase, the distribution of pauses between consecutive requests and the net USD of a 1-hour against a 5-minute prompt cache per agent life, with decision rules (expected value, CVaR, minimax regret, ski-rental break-even); inputs: explorer-w07-b's requests.tsv (waves 4-6) and author-w07-6's requests_w7.tsv (wave 7, PI only); outputs: JSON (--out) with per-life rows, pause rows and rule results, plus a markdown summary on stdout.
# usage: python3 -I __instrumenta__/w08c_pause_model.py REQ_W4_6.tsv REQ_W7.tsv --out OUT.json [--seed 8]
# Phases of the pause before request i: handback (request i-1 called SubagentHandback; the worker waits to be resumed), resume (no tool call in i-1, wait_s recorded), job (tool_s of i-1 over 60 s), idle (client gap over 60 s), loop (the rest).
# Model (ESTIMATE): for request i>=1 let C = cache_read + cache_write (tokens the cache covers), N = max(0, C_i - C_{i-1}), pause g_i = start-to-start time = model_s_{i-1} + tool_s_{i-1} + gap_prev_i (or + wait_i when the previous turn had no tool call).
#   arm T in {300, 3600} s with write price w (5m or 1h), read price r:  structural rewrite (observed read < 0.5 C_{i-1} although g_i is inside the arm the worker really ran: 300 s workers, 3600 s PI) -> w*C_i;  else g_i <= T -> r*C_{i-1} + w*N;  else w*C_i.  Request 0: w*cache_write_0.
#   net_i = cost(5m) - cost(1h); a positive net means the 1-hour cache saves money.  Prices (USD per Mtok, docs 2026-10-24 and scripts/lab_status.py): Sonnet 5.5 r 0.10 / w5 2.50 / w1 4.00; Opus 5.5 (PI) r 0.20 / w5 5.00 / w1 8.00.
import csv, sys, json, math, random, collections, argparse

ap = argparse.ArgumentParser()
ap.add_argument("req46"); ap.add_argument("req7"); ap.add_argument("--out", required=True); ap.add_argument("--seed", type=int, default=8)
a = ap.parse_args()
rnd = random.Random(a.seed)
PRICE = {"sonnet": (0.10, 2.50, 4.00), "opus": (0.20, 5.00, 8.00)}
fl = lambda x: float(x) if x not in ("", None) else None
typ = lambda n: "PI" if n == "PI" else next((t for t in ("explorer", "author", "reproducer") if n.startswith(t)), "other")

rows = list(csv.DictReader(open(a.req46), delimiter="\t"))
# wave-7 authors carry no type in requests_w7.tsv; the six are matched to author-w07-N by request count (c4_break_even.md: 35, 62, 64, 36, 4, 24 requests); other agent ids are of unknown type and are left out
W7A = {"a9fea2964323f27b0": "author-w07-1", "a025b8a8c146ef11c": "author-w07-2", "a189798bcb4e02fc0": "author-w07-3", "a095514b3a5c0a062": "author-w07-4", "a4bf5d14740bab988": "author-w07-5", "a16341e7bf93778ec": "author-w07-6"}
for r in csv.DictReader(open(a.req7), delimiter="\t"):
    if r["name"] == "PI":
        rows.append(r)
    elif r["name"] in W7A:
        r["name"] = W7A[r["name"]]; rows.append(r)
W = collections.defaultdict(list)
for r in rows:
    W[(r["label"], r["name"])].append(r)

lives, pauses, skipped = [], [], collections.Counter()
for (lab, name), rs in W.items():
    rs.sort(key=lambda r: int(r["k"]))
    t = typ(name)
    if t == "other":
        continue
    if all(r["model_s"] == "" for r in rs):  # wave 4: no model time or gap recorded
        skipped[(lab, t)] += 1
        continue
    r_, w5, w1 = PRICE["opus" if t == "PI" else "sonnet"]
    Tobs = 3600 if t == "PI" else 300
    cost = {300: 0.0, 3600: 0.0}
    prevC = None
    life = dict(label=lab, name=name, type=t, n=len(rs), net=0.0, W=(fl(rs[0]["cache_write"]) or 0.0), Rr=0.0, n_pauses=0, n_unknown=0, span_min=0.0)
    for i, r in enumerate(rs):
        cr, cw = fl(r["cache_read"]) or 0, fl(r["cache_write"]) or 0
        C = cr + cw
        if i == 0:
            cost[300] += w5 * cw; cost[3600] += w1 * cw
            prevC = C; continue
        p = rs[i - 1]
        m, tl, gp, wt = fl(p["model_s"]) or 0, fl(p["tool_s"]) or 0, fl(r["gap_prev_s"]), fl(r["wait_s"])
        unknown = False
        hb = "SubagentHandback" in (p["calls"] or "")     # the previous request ended in the hand-back call: the worker waits to be resumed (its verifier or the PI)
        if wt is not None:
            g = m + wt; phase = "handback" if hb else "resume"
        elif gp is not None:
            g = m + tl + gp; phase = "handback" if hb else ("job" if tl > 60 else ("idle" if gp > 60 else "loop"))
        else:
            g = m + tl; unknown = True; phase = "job" if tl > 60 else "loop"
        N = max(0.0, C - prevC)
        miss_obs = cr < 0.5 * prevC
        structural = miss_obs and g <= Tobs
        c = {}
        for T, w in ((300, w5), (3600, w1)):
            if structural:
                c[T] = w * C
            elif g <= T:
                c[T] = r_ * prevC + w * N
            else:
                c[T] = w * C
        for T in c:
            cost[T] += c[T]
        net = (c[300] - c[3600]) / 1e6
        pauses.append(dict(label=lab, name=name, type=t, k=i, g=g, phase=phase, unknown=unknown, C=prevC, N=N, structural=structural,
                           miss_obs=miss_obs, net=net, loss5=(c[300]) / 1e6, loss1=(c[3600]) / 1e6, w5=w5, w1=w1, r=r_))
        life["n_pauses"] += 1; life["n_unknown"] += unknown
        life["W"] += (C if (structural or g > 3600) else N)          # tokens written under the 1-hour arm (excluding request 0, added below)
        if (not structural) and 300 < g <= 3600:
            life["Rr"] += prevC                                           # tokens the 5-minute arm re-writes that the 1-hour arm reads
        life["span_min"] += g / 60
        prevC = C
    life["cost5"] = cost[300] / 1e6; life["cost1"] = cost[3600] / 1e6; life["net"] = life["cost5"] - life["cost1"]
    lives.append(life)

# ---- calibration of the TTL rule on the observed arms ----
cal = {}
for t in ("author", "reproducer", "explorer", "PI"):
    T = 3600 if t == "PI" else 300
    c = collections.Counter()
    for q in pauses:
        if q["type"] == t and not q["unknown"]:
            c[("g>T" if q["g"] > T else "g<=T", "miss" if q["miss_obs"] else "hit")] += 1
    cal[t] = {f"{k[0]}|{k[1]}": v for k, v in c.items()}

# ---- helpers ----
def q(xs, p):
    xs = sorted(xs)
    if not xs: return None
    k = (len(xs) - 1) * p; f = math.floor(k); c_ = math.ceil(k)
    return xs[f] + (xs[c_] - xs[f]) * (k - f)
def cvar(xs, al):
    xs = sorted(xs, reverse=True); k = max(1, math.ceil((1 - al) * len(xs)))
    return sum(xs[:k]) / k
def wilson(k, n, z=1.645):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n; c0 = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c0 - h) / d, (c0 + h) / d)

res = {"calibration": cal, "skipped_wave4_workers": {f"{k[0]}|{k[1]}": v for k, v in skipped.items()}, "types": {}}
for t in ("author", "reproducer", "explorer", "PI"):
    L = [l for l in lives if l["type"] == t]
    P = [p for p in pauses if p["type"] == t]
    if not L:
        continue
    nets = [l["net"] for l in L]
    d = dict(lives=len(L), pauses=len(P), unknown_pauses=sum(p["unknown"] for p in P), requests=sum(l["n"] for l in L))
    g = [p["g"] for p in P]
    d["pause_q"] = {k: round(q(g, v), 1) for k, v in (("p10", .1), ("p50", .5), ("p75", .75), ("p90", .9), ("p99", .99), ("max", 1.0))}
    for T in (300, 3600):
        k = sum(x > T for x in g); d[f"share_over_{T}"] = (k, len(g), round(k / len(g), 4), [round(x, 4) for x in wilson(k, len(g))])
    d["phase"] = {}
    for ph in ("loop", "idle", "job", "resume", "handback"):
        Q = [p for p in P if p["phase"] == ph]
        if Q:
            gg = [p["g"] for p in Q]
            d["phase"][ph] = dict(n=len(Q), median_g=round(q(gg, .5), 1), p90_g=round(q(gg, .9), 1), over300=sum(x > 300 for x in gg), over3600=sum(x > 3600 for x in gg),
                                  median_C=round(q([p["C"] for p in Q], .5)), net_sum=round(sum(p["net"] for p in Q), 3))
    # per life
    d["life_net"] = dict(mean=round(sum(nets) / len(nets), 4), sd=round(math.sqrt(sum((x - sum(nets) / len(nets)) ** 2 for x in nets) / max(1, len(nets) - 1)), 4),
                         p10=round(q(nets, .1), 3), median=round(q(nets, .5), 3), p90=round(q(nets, .9), 3), min=round(min(nets), 3), max=round(max(nets), 3))
    d["life_cost5_mean"] = round(sum(l["cost5"] for l in L) / len(L), 3); d["life_cost1_mean"] = round(sum(l["cost1"] for l in L) / len(L), 3)
    for X in (0.0, 0.05, 0.25):
        k = sum(x > X for x in nets); d[f"P_net_gt_{X}"] = (k, len(nets), round(k / len(nets), 3), [round(x, 3) for x in wilson(k, len(nets))])
    # cluster bootstrap of mean over lives
    B = 4000; ms = []
    for _ in range(B):
        s = [nets[rnd.randrange(len(nets))] for _ in nets]; ms.append(sum(s) / len(s))
    d["boot_mean_net"] = dict(p5=round(q(ms, .05), 3), p50=round(q(ms, .5), 3), p95=round(q(ms, .95), 3), P_mean_gt0=round(sum(m > 0 for m in ms) / B, 3))
    # iid pause bootstrap: life length n from the empirical lives; pauses resampled from the type pool
    ns = [l["n_pauses"] for l in L]; sim = []
    for _ in range(4000):
        n = ns[rnd.randrange(len(ns))]
        sim.append(sum(P[rnd.randrange(len(P))]["net"] for _ in range(n)))
    d["iid_pause_life_net"] = dict(mean=round(sum(sim) / len(sim), 4), p10=round(q(sim, .1), 3), p50=round(q(sim, .5), 3), p90=round(q(sim, .9), 3),
                                   P_gt0=round(sum(x > 0 for x in sim) / len(sim), 3))
    # decision rules on the observed lives
    regret1 = [max(0.0, -x) for x in nets]   # extra USD paid by choosing 1h when 5m was cheaper
    regret5 = [max(0.0, x) for x in nets]    # extra USD paid by choosing 5m when 1h was cheaper
    ratio1 = [l["cost1"] / min(l["cost1"], l["cost5"]) for l in L]
    ratio5 = [l["cost5"] / min(l["cost1"], l["cost5"]) for l in L]
    mean = sum(nets) / len(nets)
    rules = {}
    rules["expected_value"] = ("1h" if mean > 0 else "5m", round(mean, 4))
    for al in (0.8, 0.9):
        c1, c5 = cvar(regret1, al), cvar(regret5, al)
        rules[f"CVaR{al}_regret"] = ("1h" if c1 < c5 else "5m", dict(cvar_regret_1h=round(c1, 4), cvar_regret_5m=round(c5, 4)))
        k1, k5 = cvar([l["cost1"] for l in L], al), cvar([l["cost5"] for l in L], al)
        rules[f"CVaR{al}_cost"] = ("1h" if k1 < k5 else "5m", dict(cvar_cost_1h=round(k1, 3), cvar_cost_5m=round(k5, 3)))
    rules["minimax_regret"] = ("1h" if max(regret1) < max(regret5) else "5m", dict(max_regret_1h=round(max(regret1), 4), max_regret_5m=round(max(regret5), 4)))
    rules["worst_competitive_ratio"] = ("1h" if max(ratio1) < max(ratio5) else "5m", dict(max_ratio_1h=round(max(ratio1), 3), max_ratio_5m=round(max(ratio5), 3)))
    rules["expected_competitive_ratio"] = ("1h" if sum(ratio1) < sum(ratio5) else "5m", dict(ecr_1h=round(sum(ratio1) / len(L), 4), ecr_5m=round(sum(ratio5) / len(L), 4)))
    # break-even on token shares (w07 rule): 1h pays iff re-written tokens / written tokens > 0.385
    WW = sum(l["W"] for l in L); RR = sum(l["Rr"] for l in L)   # WW: tokens written under 1h; RR: tokens 5m would re-write after 300-3600 s pauses
    rules["token_share_rule"] = ("1h" if RR / max(1, WW + RR) > 1.5 / 3.9 else "5m", dict(R=round(RR), W5=round(WW + RR), share=round(RR / max(1, WW + RR), 3), threshold=0.385))
    # ski-rental break-even with a hypothetical in-life switch: start 5m, switch to 1h when accumulated avoided-miss losses reach x * B, B = premium (w1-w5) on the current prefix
    def sim_life(lname, x):
        Q = [p for p in pauses if p["name"] == lname[1] and p["label"] == lname[0]]
        Q.sort(key=lambda p: p["k"]); acc = 0.0; on1 = False; tot = 0.0; sw = None
        for p in Q:
            if on1: tot += p["loss1"]
            else:
                tot += p["loss5"]
                acc += max(0.0, p["net"] + (p["w1"] - p["w5"]) * p["N"] / 1e6)  # avoided miss loss, net of nothing: the miss saving alone
                if acc >= x * (p["w1"] - p["w5"]) * p["C"] / 1e6: on1 = True
        return tot
    base = {(l["label"], l["name"]): l for l in L}
    sr = {}
    for x in (0.25, 0.5, 1.0, 2.0):
        tots = [sim_life(k, x) for k in base]
        # cost of the static arms restricted to pauses (without request 0), for a like-for-like ratio
        ref = []
        for k in base:
            Q = [p for p in pauses if p["name"] == k[1] and p["label"] == k[0]]
            ref.append((sum(p["loss5"] for p in Q), sum(p["loss1"] for p in Q)))
        rr = [tt / min(r5, r1) for tt, (r5, r1) in zip(tots, ref)]
        sr[str(x)] = dict(mean_ratio=round(sum(rr) / len(rr), 3), max_ratio=round(max(rr), 3), mean_cost=round(sum(tots) / len(tots), 3),
                          ref_mean_5m=round(sum(r[0] for r in ref) / len(ref), 3), ref_mean_1h=round(sum(r[1] for r in ref) / len(ref), 3))
    # randomized ski rental: x ~ density e^x/(e-1) on [0,1] (Karlin et al.), expected over a 40-point grid
    grid = [(i + 0.5) / 40 for i in range(40)]; wts = [math.exp(x) for x in grid]; sw_ = sum(wts)
    ex = []
    for k in base:
        Q = [p for p in pauses if p["name"] == k[1] and p["label"] == k[0]]
        r5, r1 = sum(p["loss5"] for p in Q), sum(p["loss1"] for p in Q)
        e = sum(w * sim_life(k, x) for w, x in zip(wts, grid)) / sw_
        ex.append(e / min(r5, r1))
    sr["randomized_e_over_e_minus_1"] = dict(mean_ratio=round(sum(ex) / len(ex), 3), max_ratio=round(max(ex), 3))
    rules["ski_rental_switch_simulation"] = ("needs in-life switching; not available on the platform (see report)", sr)
    d["rules"] = rules
    # phase-aware value: per phase, switch to 1h only in phases whose summed net is positive (needs the phase known at write time)
    ph_net = collections.defaultdict(float)
    for p in P: ph_net[p["phase"]] += p["net"]
    d["phase_oracle"] = dict(static_best=round(max(0.0, sum(ph_net.values())), 3), by_phase_best=round(sum(max(0.0, v) for v in ph_net.values()), 3), by_phase_net={k: round(v, 3) for k, v in ph_net.items()})
    d["lives_rows"] = [dict(label=l["label"], name=l["name"], n=l["n"], span_min=round(l["span_min"], 1), cost5=round(l["cost5"], 3), cost1=round(l["cost1"], 3), net=round(l["net"], 3), W1=round(l["W"])) for l in L]
    res["types"][t] = d

json.dump(res, open(a.out, "w"), indent=1)
json.dump(pauses, open(a.out.replace(".json", "_pauses.json"), "w"))
for t, d in res["types"].items():
    print(f"## {t}: lives {d['lives']} requests {d['requests']} pauses {d['pauses']} (unknown {d['unknown_pauses']}); g quantiles {d['pause_q']}; >300s {d['share_over_300'][:3]}, >3600s {d['share_over_3600'][:3]}")
    print("   life net mean/sd", d["life_net"]["mean"], d["life_net"]["sd"], "P(net>0)", d["P_net_gt_0.0"], "boot P(mean>0)", d["boot_mean_net"]["P_mean_gt0"], "iid P>0", d["iid_pause_life_net"]["P_gt0"])
    for k, v in d["rules"].items():
        print("   ", k, v[0])
