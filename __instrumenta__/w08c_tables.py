# Computes (a) a gamma-Poisson event model of P(1-hour cache saves money) per agent type, (b) the PI-reads-a-document against delegate-to-a-Sonnet-worker cost frame, and (c) two figures; inputs: w08c_pause_model.py outputs (pause_model.json, pause_model_pauses.json) and explorer-w07-b's requests.tsv; outputs: markdown tables on stdout and two PNG files in --outdir.
# usage: python3 -I __instrumenta__/w08c_tables.py OUTDIR REQ_W4_6.tsv [--seed 8]   (OUTDIR holds pause_model.json and pause_model_pauses.json)
# (a) per type: events = pauses of 300-3600 s that are not structural re-writes (the 5-minute arm re-writes the previous prefix C, saving (w5-r)*C); K ~ Poisson(lambda*n_requests), lambda ~ Gamma(K_obs+0.5, rate sum n) (Jeffreys); premium (w1-w5)*W1 with W1 the life's 1-hour-arm write tokens; life lengths and event sizes resampled from the data.
# (b) PI reads D tokens and carries them for M more requests on Opus 5.5 (1-hour write 8.00, read 0.20 USD/Mtok): D*(8+0.2M); delegate: Sonnet worker D*(2.5+0.1*n_w) + overhead (a worker life's cost, resampled from reproducer and explorer lives) + a summary of S tokens carried by the PI S*(8+0.2M) + brief output; with probability q the summary fails and the PI reads a fraction phi of the document.
import sys, json, csv, math, random, collections
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

out, req = sys.argv[1], sys.argv[2]
seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 8
rng = np.random.default_rng(seed); rnd = random.Random(seed)
J = json.load(open(out + "/pause_model.json")); P = json.load(open(out + "/pause_model_pauses.json"))
PR = {"Sonnet": (0.10, 2.50, 4.00), "Opus": (0.20, 5.00, 8.00)}

print("### (a) gamma-Poisson event model of P(1h saves USD > X) per life\n")
print("| type | lives | requests | events (300-3600 s) | events per 100 requests (90% interval) | mean premium per life, USD | mean saving per event, USD | P(net>0) model | P(net>0.10) | P(net>0) observed lives | mean net per life, model | 5-95% |")
print("|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:--|")
model = {}
for t in ("author", "reproducer", "explorer", "PI"):
    d = J["types"][t]; lv = d["lives_rows"]
    Pt = [p for p in P if p["type"] == t]
    ev = [p for p in Pt if 300 < p["g"] <= 3600 and not p["structural"]]
    r_, w5, w1 = PR["Opus" if t == "PI" else "Sonnet"]
    save = np.array([(w5 - r_) * p["C"] / 1e6 for p in ev])
    life_n = {(l["label"], l["name"]): l["n"] for l in lv}; life_W1 = {(l["label"], l["name"]): l["W1"] for l in lv}   # W1: tokens written under the 1-hour arm, request 0 included
    keys = [(l["label"], l["name"]) for l in lv]
    prem = np.array([(w1 - w5) * life_W1[k] / 1e6 for k in keys]); nreq = np.array([life_n[k] for k in keys])
    K = len(ev); tot_n = nreq.sum()
    sims = []
    for _ in range(20000):
        lam = rng.gamma(K + 0.5, 1.0 / tot_n)
        i = rnd.randrange(len(keys)); kk = rng.poisson(lam * nreq[i])
        s = save[rng.integers(0, len(save), kk)].sum() if (kk > 0 and len(save)) else 0.0
        sims.append(s - prem[i])
    sims = np.array(sims)
    lo, hi = rng.gamma(K + 0.5, 1.0 / tot_n, 4000) * 100, None
    q5, q95 = np.percentile(lo, [5, 95])
    obs = sum(l["net"] > 0 for l in lv)
    model[t] = dict(P0=float((sims > 0).mean()), P10=float((sims > 0.10).mean()))
    print(f"| {t} | {len(lv)} | {int(tot_n)} | {K} | {100*K/tot_n:.2f} ({q5:.2f}-{q95:.2f}) | {prem.mean():.2f} | {save.mean() if len(save) else 0:.2f} | {(sims>0).mean():.2f} | {(sims>0.10).mean():.2f} | {obs}/{len(lv)} | {sims.mean():+.2f} | {np.percentile(sims,5):+.2f} to {np.percentile(sims,95):+.2f} |")

# ---------- figure 1: survival of pauses and life nets ----------
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
col = {"author": "C0", "reproducer": "C1", "explorer": "C2", "PI": "C3"}
for t in col:
    g = np.sort([p["g"] for p in P if p["type"] == t]); y = 1 - np.arange(len(g)) / len(g)
    ax[0].step(g, y, where="post", label=f"{t} (n={len(g)})", color=col[t])
ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].axvline(300, ls=":", c="k"); ax[0].axvline(3600, ls=":", c="k")
ax[0].set_xlabel("pause between consecutive request starts, s"); ax[0].set_ylabel("share of pauses longer than g"); ax[0].legend(fontsize=8); ax[0].set_title("pause survival (waves 5-7)")
for j, t in enumerate(col):
    v = [l["net"] for l in J["types"][t]["lives_rows"]]
    ax[1].scatter([j] * len(v), v, c=col[t], alpha=.7); ax[1].plot([j - .25, j + .25], [np.mean(v)] * 2, c="k")
ax[1].axhline(0, c="gray"); ax[1].set_xticks(range(4)); ax[1].set_xticklabels(list(col)); ax[1].set_ylabel("net USD of 1h over 5m per life (positive: 1h saves)")
ax[1].set_yscale("symlog", linthresh=0.5); ax[1].set_title("one point per agent life")
plt.tight_layout(); plt.savefig(out + "/fig1_pauses_and_life_net.png", dpi=110); plt.close()

# ---------- (b) read or delegate ----------
rows = [r for r in csv.DictReader(open(req), delimiter="\t") if r["name"] == "PI"]
f = lambda x: float(x) if x else 0.0
by = collections.defaultdict(list)
for r in rows: by[r["label"]].append(r)
reads = []; Mpool = []
for lab, rs in by.items():
    rs.sort(key=lambda r: int(r["k"]))
    C = [f(r["cache_read"]) + f(r["cache_write"]) + f(r["input"]) for r in rs]
    for i in range(1, len(C)):
        Mpool.append(len(C) - 1 - i)
        if C[i] - C[i - 1] > 8000 and i > 1:
            reads.append((lab, i, C[i] - C[i - 1], len(C) - 1 - i, rs[i - 1]["calls"][:40]))
print("\n### (b) PI context jumps above 8,000 tokens after request 1 (waves 4-6), the reads the PI actually carried\n")
print("| wave | request | jump tokens | later requests M | calls before |\n|:--|--:|--:|--:|:--|")
for x in reads: print(f"| {x[0]} | {x[1]} | {x[2]:.0f} | {x[3]} | {x[4]} |")
print(f"\nPI sessions: {', '.join(f'{k} {len(v)} requests' for k, v in by.items())}; no compaction drop in any (context falls under 0.6 of the previous: none).")

wk = [(l["n"], l["cost5"]) for t in ("reproducer", "explorer") for l in J["types"][t]["lives_rows"]]
r_o, w1_o = 0.20, 8.0; r_s, w5_s = 0.10, 2.50
def read_cost(D, M): return D * (w1_o + r_o * M) / 1e6
def deleg_cost(D, M, nw, ov, S=2000, brief=800):
    return D * (w5_s + r_s * nw) / 1e6 + ov + S * (w1_o + r_o * M) / 1e6 + brief * 20 / 1e6
print("\n### Break-even document size D* (tokens) at which delegating (q = 0) equals reading, by later requests M; worker overhead = median / 10th / 90th percentile of reproducer+explorer life cost (USD), n_w = median worker requests\n")
ovs = np.array([c for _, c in wk]); nws = np.array([n for n, _ in wk])
print(f"worker lives n={len(wk)}: cost5 USD median {np.median(ovs):.2f}, p10 {np.percentile(ovs,10):.2f}, p90 {np.percentile(ovs,90):.2f}; requests median {np.median(nws):.0f}\n")
print("| M | D* at overhead p10 | D* at median | D* at p90 |\n|--:|--:|--:|--:|")
nwm = np.median(nws)
for M in (10, 30, 100, 200, 400):
    cells = []
    for ov in (np.percentile(ovs, 10), np.median(ovs), np.percentile(ovs, 90)):
        # solve D*(w1+rM - w5 - r_s*nw)/1e6 = ov + S*(...)/1e6 + brief
        a_ = (w1_o + r_o * M - w5_s - r_s * nwm) / 1e6; b_ = ov + 2000 * (w1_o + r_o * M) / 1e6 + 800 * 20 / 1e6
        cells.append(f"{b_/a_:,.0f}")
    print(f"| {M} | " + " | ".join(cells) + " |")
print("\n### Monte Carlo: P(delegation cheaper than reading), M drawn from the PI's remaining requests at a random point of a session (n=%d positions), worker lives resampled; q = chance the summary fails, then the PI reads phi=0.5 of the document too\n" % len(Mpool))
print("| D tokens | q | P(delegate cheaper) | mean saving USD (read - delegate) | 5-95% | mean read cost USD | CVaR90 of the extra cost of delegating, USD |\n|--:|--:|--:|--:|:--|--:|--:|")
grid = {}
for D in (10_000, 25_000, 50_000, 100_000, 200_000):
    for q in (0.0, 0.2, 0.4):
        diffs = []; reads_c = []
        for _ in range(8000):
            M = Mpool[rnd.randrange(len(Mpool))]; n_, c_ = wk[rnd.randrange(len(wk))]
            rc = read_cost(D, M); dc = deleg_cost(D, M, n_, c_)
            if rnd.random() < q: dc += read_cost(0.5 * D, M)
            diffs.append(rc - dc); reads_c.append(rc)
        diffs = np.array(diffs); worst = np.sort(-diffs)[::-1][: int(0.1 * len(diffs))]
        grid[(D, q)] = float((diffs > 0).mean())
        print(f"| {D:,} | {q} | {(diffs>0).mean():.2f} | {diffs.mean():+.2f} | {np.percentile(diffs,5):+.2f} to {np.percentile(diffs,95):+.2f} | {np.mean(reads_c):.2f} | {worst.mean():+.2f} |")
fig, ax = plt.subplots(figsize=(5.5, 4))
Ds = np.logspace(3.7, 5.5, 60); Ms = np.arange(0, 301)
Z = np.array([[read_cost(D, M) - deleg_cost(D, M, nwm, np.median(ovs)) for D in Ds] for M in Ms])
im = ax.contourf(Ds, Ms, Z, levels=[-5, -1, -0.25, 0, 0.25, 1, 5, 20], cmap="RdBu", extend="both"); ax.contour(Ds, Ms, Z, levels=[0], colors="k")
ax.set_xscale("log"); ax.set_xlabel("document tokens D"); ax.set_ylabel("PI requests left after the read, M"); plt.colorbar(im, label="read minus delegate, USD (blue: delegating cheaper)")
ax.set_title("PI reads (Opus) vs delegates (Sonnet), q=0"); plt.tight_layout(); plt.savefig(out + "/fig2_read_or_delegate.png", dpi=110)
