# w09-j: draws the five figures of the classifier-alignment report (block rates, weighted ROC, written vs recorded cases, latency, rewrite pairs) from the committed result rows of explorer-w09-c and explorer-w09-i and the text-free case_meta.jsonl (made by w09j_meta.py), and writes every plotted number to figure_numbers.md; no case text, no model run. Usage: python3 -I w09j_figures.py REPORTS_WAVE09_DIR OUT_DIR   (REPORTS_WAVE09_DIR = __reports__/wave-09; reads explorer-w09-c/results, explorer-w09-i/results, explorer-w09-j/data/case_meta.jsonl)
import sys, os, json, math, random, collections, statistics
from math import comb
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RC, RI = os.path.join(BASE, "explorer-w09-c", "results"), os.path.join(BASE, "explorer-w09-i", "results")
META = os.path.join(BASE, "explorer-w09-j", "data", "case_meta.jsonl")
SEED = 20261026
NB = 1000  # bootstrap draws

plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10, "legend.fontsize": 8.5, "figure.dpi": 100,
                     "savefig.dpi": 200, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})

# ---------- metadata (text-free)
meta = {}
for l in open(META):
    r = json.loads(l); meta[r["cid"]] = r
REF = sorted(c for c, m in meta.items() if m["group"] == "refusal")
NAT = sorted(c for c, m in meta.items() if m["group"] == "allow" and m["source"] == "natural")
W = {c: meta[c]["weight"] for c in NAT}
SESS = {c: meta[c]["session"] for c in REF + NAT}
PAIRS = {}  # pair id -> (refusal cid, allow cid)
for c, m in meta.items():
    if m["group"] == "pair_block": PAIRS.setdefault(m["pair"], [None, None])[0] = m["ref_id"]
    if m["group"] == "pair_allow": PAIRS.setdefault(m["pair"], [None, None])[1] = c
assert len(REF) == 67 and len(NAT) == 212 and len(PAIRS) == 19


def segments(path):
    """all result rows, and the rows after the last meta line (the last, resumed run segment, which is what explorer-w09-c used for latency)"""
    rows = [json.loads(l) for l in open(path)]
    last = max((i for i, r in enumerate(rows) if "cid" not in r), default=-1)
    return [r for r in rows if "cid" in r], [r for r in rows[last + 1:] if "cid" in r]


def load(path):
    rows = [json.loads(l) for l in open(path)]
    return {r["cid"]: r for r in rows if "cid" in r}, [r for r in rows if "cid" not in r]


# ---------- judges and arms: key -> (label, rows path, backend, has_score, marker, colour, linestyle)
OI = {"blue": "#0072B2", "sky": "#56B4E9", "orange": "#E69F00", "yellow": "#F0E442", "verm": "#D55E00", "green": "#009E73", "pink": "#CC79A7", "black": "#000000"}
J = collections.OrderedDict([
    ("qwen_full", dict(label="qwen3.6-35b-a3b, full rules", path=os.path.join(RI, "qwen36_full.jsonl"), backend="llama-server", m="o", c=OI["blue"], ls="-")),
    ("qwen_short", dict(label="qwen3.6-35b-a3b, short criterion", path=os.path.join(RI, "qwen36_short.jsonl"), backend="llama-server", m="s", c=OI["sky"], ls="--")),
    ("gemma_full", dict(label="gemma-4-26b-a4b, full rules", path=os.path.join(RI, "gemma4_full.jsonl"), backend="llama-server", m="^", c=OI["orange"], ls="-.")),
    ("gemma_short", dict(label="gemma-4-26b-a4b, short criterion", path=os.path.join(RI, "gemma4_short.jsonl"), backend="llama-server", m="v", c=OI["yellow"], ls=":")),
    ("granite_short", dict(label="Granite Guardian 4.1 8B, short criterion", path=os.path.join(RI, "granite_short_scored.jsonl"), backend="llama-server", m="D", c=OI["verm"], ls="-")),
    ("safeguard_short", dict(label="gpt-oss-safeguard-20b, short criterion", path=os.path.join(RC, "safeguard_short.jsonl"), backend="LM Studio", m="P", c=OI["green"], ls="-")),
    ("granite_full", dict(label="Granite Guardian 4.1 8B, full rules (variant B)", path=os.path.join(RC, "granite_full.jsonl"), backend="LM Studio", m="D", c=OI["verm"], ls="-")),
    ("safeguard_full", dict(label="gpt-oss-safeguard-20b, full rules", path=os.path.join(RC, "safeguard_full.jsonl"), backend="LM Studio", m="P", c=OI["green"], ls="-")),
])
for k, j in J.items():
    j["R"], j["meta"] = load(j["path"])
    j["has_score"] = all(j["R"][c].get("score") is not None for c in REF + NAT if c in j["R"]) and k in ("qwen_full", "qwen_short", "gemma_full", "gemma_short", "granite_short")
    j["block"] = {c: r["verdict"] == "block" for c, r in j["R"].items() if r["verdict"] in ("block", "allow")}
SCORED = [k for k in J if J[k]["has_score"]]
NUMS = []  # lines of figure_numbers.md


def note(s): NUMS.append(s)


# ---------- statistics
def cp(k, n, a=.05):
    cdf = lambda x, p: sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(x + 1))
    lo, hi = 0.0, 1.0
    if k > 0:
        l, h = 0.0, 1.0
        for _ in range(60):
            m = (l + h) / 2
            if 1 - cdf(k - 1, m) > a / 2: h = m
            else: l = m
        lo = (l + h) / 2
    if k < n:
        l, h = 0.0, 1.0
        for _ in range(60):
            m = (l + h) / 2
            if cdf(k, m) > a / 2: l = m
            else: h = m
        hi = (l + h) / 2
    return lo, hi


def wrate(B, nats):
    """stratum-weighted block rate over the natural allows a judge scored: sum_h N_h * (blocked_h / scored_h) / sum_h N_h over the strata it covers (equals sum w*b / sum w when all of a stratum was scored)"""
    by = collections.defaultdict(list)
    for c in nats: by[meta[c]["stratum"]].append(c)
    num = sum(meta[cs[0]]["N_h"] * sum(B[c] for c in cs) / len(cs) for cs in by.values()); den = sum(meta[cs[0]]["N_h"] for cs in by.values())
    return num / den


def wauc(sp, sn, wn):
    sp = np.asarray(sp, float); sn = np.asarray(sn, float); wn = np.asarray(wn, float)
    o = np.argsort(sn, kind="stable"); s = sn[o]; cw = np.concatenate([[0.0], np.cumsum(wn[o])])
    lo = np.searchsorted(s, sp, side="left"); hi = np.searchsorted(s, sp, side="right")
    return float(((cw[lo] + 0.5 * (cw[hi] - cw[lo])).sum()) / (len(sp) * wn.sum()))


def roc(sp, sn, wn):
    """weighted ROC: block iff score >= t; returns fpr, tpr arrays from (0,0) to (1,1)"""
    sp = np.asarray(sp, float); sn = np.asarray(sn, float); wn = np.asarray(wn, float)
    ts = np.unique(np.concatenate([sp, sn]))[::-1]
    fpr = [0.0]; tpr = [0.0]
    for t in ts:
        fpr.append(wn[sn >= t].sum() / wn.sum()); tpr.append((sp >= t).mean())
    return np.array(fpr), np.array(tpr), ts


def tpr_at(sp, sn, wn, target):
    sp = np.asarray(sp, float); sn = np.asarray(sn, float); wn = np.asarray(wn, float)
    best = (0.0, 0.0, None, 0, 0)
    for t in np.unique(np.concatenate([sp, sn]))[::-1]:
        f = wn[sn >= t].sum() / wn.sum()
        if f <= target:
            tp = (sp >= t).mean()
            if tp >= best[0]: best = (tp, f, float(t), int((sp >= t).sum()), int((sn >= t).sum()))
        else: break
    return best


def draws(refs, nats, n, seed):
    """session-cluster bootstrap: yields lists of resampled case ids (refusals and natural allows together)"""
    rng = random.Random(seed); sess = collections.defaultdict(list)
    for c in refs + nats: sess[SESS[c]].append(c)
    ks = sorted(sess)
    for _ in range(n):
        ch = []
        for _ in ks: ch += sess[rng.choice(ks)]
        yield ch


def pct(v):
    v = sorted(v); return v[int(.025 * len(v))], v[min(len(v) - 1, int(.975 * len(v)))]


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)


# =====================================================================  Figure 1: block rates
note("## Figure 1: block rate on refusals against block rate on natural allows\n")
note(f"| judge, arm | refusals blocked | CP 95% | natural allows blocked, raw | CP 95% | weighted rate | session-cluster bootstrap 95% (1,000 draws, seed {SEED}) |\n|:--|--:|:--|--:|:--|--:|:--|")
F1 = {}
for k, j in J.items():
    B = j["block"]
    refs = [c for c in REF if c in B]; nats = [c for c in NAT if c in B]
    kr = sum(B[c] for c in refs)
    d = dict(kr=kr, nr=len(refs), cpr=cp(kr, len(refs)))
    if nats:
        kn = sum(B[c] for c in nats); wr = wrate(B, nats)
        bw = []
        for ch in draws(refs, nats, NB, SEED):
            q = [c for c in ch if c in W]
            if q: bw.append(wrate(B, q))
        d.update(kn=kn, nn=len(nats), cpn=cp(kn, len(nats)), wr=wr, bw=pct(bw))
    F1[k] = d
    if nats:
        note(f"| {j['label']} | {kr} of {len(refs)} = {100*kr/len(refs):.1f}% | {100*d['cpr'][0]:.1f} to {100*d['cpr'][1]:.1f}% | {d['kn']} of {d['nn']} = {100*d['kn']/d['nn']:.1f}% | {100*d['cpn'][0]:.1f} to {100*d['cpn'][1]:.1f}% | {100*d['wr']:.1f}% | {100*d['bw'][0]:.1f} to {100*d['bw'][1]:.1f}% |")
    else:
        note(f"| {j['label']} | {kr} of {len(refs)} = {100*kr/len(refs):.1f}% | {100*d['cpr'][0]:.1f} to {100*d['cpr'][1]:.1f}% | not run | | | |")

fig, axs = plt.subplots(1, 3, figsize=(13.5, 5.4), gridspec_kw={"width_ratios": [4, 4, 1.35]}, sharey=True)
for ax, mode in zip(axs[:2], ("raw", "weighted")):
    ax.plot([0, 1], [0, 1], color="0.35", lw=1, ls=(0, (4, 3)), zorder=1)
    ax.text(0.80, 0.70, "same rate on both:\nno separation", rotation=0, color="0.35", fontsize=8.5, ha="center", va="center")
    for k in ("qwen_full", "qwen_short", "gemma_full", "gemma_short", "granite_short", "safeguard_short"):
        d, j = F1[k], J[k]
        y = d["kr"] / d["nr"]; ylo, yhi = d["cpr"]
        if mode == "raw": x = d["kn"] / d["nn"]; xlo, xhi = d["cpn"]; hollow = False
        else:
            x = d["wr"]; xlo, xhi = d["bw"]; hollow = k == "safeguard_short"
            if hollow: xlo, xhi = d["cpn"]  # bootstrap too narrow with about 1 case per stratum: show the raw CP instead
        ax.errorbar([x], [y], xerr=[[x - xlo], [xhi - x]], yerr=[[y - ylo], [yhi - y]], fmt="none", ecolor=j["c"] if not hollow else "0.2", elinewidth=1.4, capsize=3, zorder=2, linestyle=(":" if hollow else "-"))
        ax.plot([x], [y], marker=j["m"], ms=10, mfc=("white" if hollow else j["c"]), mec="black", mew=1.2, ls="none", zorder=3)
    ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.03); ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("natural allows blocked (" + ("raw share of 212; 28 for safeguard" if mode == "raw" else "weighted by stratum, share of 19,243") + ")")
    ax.set_title(("A. raw counts, Clopper-Pearson 95%" if mode == "raw" else "B. stratum-weighted, session-cluster bootstrap 95%"), loc="left")
    ax.grid(alpha=.25)
axs[0].set_ylabel("recorded refusals blocked (share of 67)")
ax = axs[2]
for i, k in enumerate(("granite_full", "safeguard_full")):
    d, j = F1[k], J[k]; y = d["kr"] / d["nr"]
    ax.errorbar([i], [y], yerr=[[y - d["cpr"][0]], [d["cpr"][1] - y]], fmt="none", ecolor="0.2", elinewidth=1.4, capsize=3)
    ax.plot([i], [y], marker=j["m"], ms=10, mfc="white", mec="black", mew=1.2, ls="none")
    ax.text(i, y + 0.07 if y < 0.5 else y - 0.1, f"{d['kr']} of {d['nr']}", ha="center", fontsize=8.5)
ax.set_xlim(-0.7, 1.7); ax.set_xticks([]); ax.tick_params(labelleft=True); ax.set_title("C. allows not run:\nrefusals only", loc="left", fontsize=10); ax.grid(alpha=.25)
handles = [Line2D([], [], marker=J[k]["m"], ls="none", ms=9, mfc=J[k]["c"], mec="black", label=J[k]["label"]) for k in ("qwen_full", "qwen_short", "gemma_full", "gemma_short", "granite_short", "safeguard_short")]
handles += [Line2D([], [], marker="D", ls="none", ms=9, mfc="white", mec="black", label="Granite, full rules (panel C, left)"),
            Line2D([], [], marker="P", ls="none", ms=9, mfc="white", mec="black", label="safeguard, full rules (panel C, right)")]
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.17))
fig.suptitle("Figure 1. A judge that separates sits above the diagonal; blocks everything: top right; allows everything: bottom left", x=0.01, ha="left", fontsize=11, y=1.01)
save(fig, "fig1_block_rates")

# =====================================================================  Figure 2: ROC
note("\n## Figure 2: weighted ROC (refusals positive, natural allows weighted N_h/m_h)\n")
note(f"| judge, arm | AUC weighted | 95% session-cluster bootstrap (1,000 draws, seed {SEED}) | AUC unweighted | TPR at weighted FPR <= 10% | threshold | weighted FPR there | judge's own verdict: TPR / weighted FPR |\n|:--|--:|:--|--:|--:|--:|--:|:--|")
F2 = {}
fig, ax = plt.subplots(figsize=(7.4, 6.6))
ax.plot([0, 1], [0, 1], color="0.35", lw=1, ls=(0, (4, 3)), zorder=1)
ax.axvline(0.10, color="0.5", lw=0.9, ls=":", zorder=1); ax.text(0.115, 0.985, "10% false blocks", fontsize=8.5, color="0.35", va="top", bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
for k in SCORED:
    j = J[k]; S = {c: float(j["R"][c]["score"]) for c in REF + NAT}
    sp = [S[c] for c in REF]; sn = [S[c] for c in NAT]; wn = [W[c] for c in NAT]
    a = wauc(sp, sn, wn); au = wauc(sp, sn, [1.0] * len(sn))
    ba = []
    for ch in draws(REF, NAT, NB, SEED):
        p = [S[c] for c in ch if meta[c]["group"] == "refusal"]; q = [c for c in ch if meta[c]["group"] == "allow"]
        if p and q: ba.append(wauc(p, [S[c] for c in q], [W[c] for c in q]))
    lo, hi = pct(ba)
    f, t, _ = roc(sp, sn, wn)[:3]
    tp10, f10, th10, kp10, kn10 = tpr_at(sp, sn, wn, 0.10)
    B = j["block"]; vt = sum(B[c] for c in REF) / 67; vf = wrate(B, NAT)
    F2[k] = dict(auc=a, ci=(lo, hi), aucu=au, tp10=tp10, f10=f10, th=th10, vt=vt, vf=vf)
    ax.step(f, t, where="post", color=j["c"], ls=j["ls"], lw=2.0, zorder=2, label=f"{j['label']}: AUC {a:.2f} ({lo:.2f} to {hi:.2f})")
    ax.plot([f10], [tp10], marker=j["m"], ms=10, mfc=j["c"], mec="black", mew=1.2, ls="none", zorder=4)
    ax.plot([vf], [vt], marker="x", ms=8, mec="black", mew=2.0, ls="none", zorder=4)
    note(f"| {j['label']} | {a:.3f} | {lo:.3f} to {hi:.3f} | {au:.3f} | {kp10} of 67 = {100*tp10:.1f}% | {th10:.2f} | {100*f10:.1f}% | {100*vt:.1f}% / {100*vf:.1f}% |")
Fs = F1["safeguard_short"]
ax.plot([Fs["wr"]], [Fs["kr"] / 67], marker="P", ms=10, mfc="white", mec=OI["green"], mew=2, ls="none", zorder=4, label="gpt-oss-safeguard-20b, short: verdict only, no score (28 allows)")
note(f"| gpt-oss-safeguard-20b, short criterion | no score | | | | | | {100*Fs['kr']/67:.1f}% / {100*Fs['wr']:.1f}% (28 allows) |")
ax.plot([], [], marker="o", ls="none", mfc="0.6", mec="black", ms=9, label="marker on curve: best point at weighted FPR up to 10%")
ax.plot([], [], marker="x", ls="none", mec="black", ms=8, mew=2, label="x: the judge's own yes/no verdict")
ax.set_xlim(-0.01, 1.01); ax.set_ylim(-0.01, 1.01); ax.set_aspect("equal", adjustable="box"); ax.grid(alpha=.25)
ax.set_xlabel("natural allows blocked (false blocks; weighted share of 19,243)"); ax.set_ylabel("recorded refusals blocked (share of 67)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False, ncol=1)
ax.set_title("Figure 2. Weighted ROC of five scoring judges (in-sample)", loc="left")
save(fig, "fig2_roc")

# =====================================================================  Figure 3: written vs recorded
note("\n## Figure 3: wave 8's 22 hand-written cases against recorded decisions (balanced accuracy at the judge's own verdict)\n")
note("| judge, arm | written cases: correct (CP 95%) | written: refuse-labelled blocked of 11 | allow-labelled blocked of 11 | recorded: balanced accuracy (weighted allows) | bootstrap 95% (1,000 draws) | AUC (weighted) |\n|:--|:--|--:|--:|--:|:--|--:|")
HAND_ARMS = [k for k in ("qwen_full", "qwen_short", "gemma_full", "gemma_short", "granite_short", "safeguard_short")]
hand_rows = {}
for k in HAND_ARMS:
    R = J[k]["R"] if k != "safeguard_short" else load(os.path.join(RI, "safeguard_short_hand.jsonl"))[0]
    hand_rows[k] = {c: r for c, r in R.items() if r.get("group", "").startswith("hand")}
F3 = {}
for k in HAND_ARMS:
    h = hand_rows[k]; assert len(h) == 22, (k, len(h))
    ok = sum((h[c]["verdict"] == "block") == (h[c]["label"] == "refuse") for c in h)
    rb = sum(h[c]["verdict"] == "block" for c in h if h[c]["label"] == "refuse"); ab = sum(h[c]["verdict"] == "block" for c in h if h[c]["label"] == "allow")
    nr = sum(h[c]["label"] == "refuse" for c in h); na = 22 - nr
    wbal = 0.5 * (rb / nr + (1 - ab / na))
    B = J[k]["block"]; refs = [c for c in REF if c in B]; nats = [c for c in NAT if c in B]
    def bal(ch):
        p = [c for c in ch if meta[c]["group"] == "refusal" and c in B]; q = [c for c in ch if meta[c]["group"] == "allow" and c in B]
        return 0.5 * (sum(B[c] for c in p) / len(p) + 1 - wrate(B, q))
    rec = bal(refs + nats); bs = pct([bal(ch) for ch in draws(refs, nats, NB, SEED) if any(meta[c]["group"] == "refusal" for c in ch) and any(meta[c]["group"] == "allow" for c in ch)])
    F3[k] = dict(ok=ok, n=22, cpw=cp(ok, 22), bal=wbal, rec=rec, recci=bs, auc=F2[k]["auc"] if k in F2 else None)
    note(f"| {J[k]['label']} | {ok} of 22 | {rb} of {nr} | {ab} of {na} | {rec:.3f} | {bs[0]:.3f} to {bs[1]:.3f} | {F2[k]['auc']:.3f} |" if k in F2 else f"| {J[k]['label']} | {ok} of 22 | {rb} of {nr} | {ab} of {na} | {rec:.3f} | {bs[0]:.3f} to {bs[1]:.3f} | no score |")
fig, ax = plt.subplots(figsize=(9, 4.6))
ys = np.arange(len(HAND_ARMS))[::-1]
for y, k in zip(ys, HAND_ARMS):
    d = F3[k]; wv = d["bal"]
    ax.plot([d["rec"], wv], [y, y], color="0.6", lw=2, zorder=1)
    ax.plot([wv], [y], marker="s", ms=10, mfc=OI["black"], mec="black", ls="none", zorder=3)
    ax.errorbar([d["rec"]], [y], xerr=[[d["rec"] - d["recci"][0]], [d["recci"][1] - d["rec"]]], fmt="none", ecolor=OI["verm"], elinewidth=1.6, capsize=3, zorder=2)
    ax.plot([d["rec"]], [y], marker="o", ms=10, mfc=OI["verm"], mec="black", ls="none", zorder=3)
    ax.text(1.015, y, f"{d['ok']}/22", va="center", fontsize=9)
ax.axvline(0.5, color="0.35", lw=1, ls=(0, (4, 3)))
ax.text(0.505, len(HAND_ARMS) - 0.45, "0.5 = no better than a coin", fontsize=8.5, color="0.35")
ax.set_yticks(ys); ax.set_yticklabels([J[k]["label"] for k in HAND_ARMS]); ax.set_xlim(0.3, 1.1); ax.set_ylim(-0.6, len(HAND_ARMS) - 0.2)
ax.set_xlabel("balanced accuracy at the judge's own yes/no verdict\n(mean of: share of calls to block that it blocks, share of calls to allow that it allows)")
ax.legend(handles=[Line2D([], [], marker="s", ls="none", ms=9, mfc="black", mec="black", label="wave 8's 22 written cases (11 to block, 11 to allow); label = cases correct"),
                   Line2D([], [], marker="o", ls="none", ms=9, mfc=OI["verm"], mec="black", label="recorded decisions: 67 refusals, 212 natural allows (weighted); bar: 95% bootstrap")], loc="upper center", bbox_to_anchor=(0.45, -0.17), frameon=False)
ax.set_title("Figure 3. Written cases are solved; recorded decisions are not", loc="left"); ax.grid(axis="x", alpha=.25)
save(fig, "fig3_written_vs_recorded")

# =====================================================================  Figure 4: latency
note("\n## Figure 4: latency on unique cases (one row per case id; first call apart from the rest)\n")
note("| judge, arm (backend) | first call (s) | first call kind | steady p50 (s) | steady p90 (s) | steady n |\n|:--|--:|:--|--:|:--|--:|")
COLD = {  # key -> list of (seconds, hollow?, note); cold rows from the committed cold-first-call files where the main run was warm
    "qwen_full": [(load(os.path.join(RI, "qwen36_cold_first_call.jsonl"))[0]["H-smoke-a1"]["ms"] / 1000, False, "test call, rules prefix uncached")],
    "gemma_full": [(load(os.path.join(RI, "gemma4_cold_first_call.jsonl"))[0]["H-smoke-a1"]["ms"] / 1000, False, "test call, rules prefix uncached")],
}
smk = [json.loads(l) for f in ("smoke_granite_full.jsonl", "smoke_granite_full_b.jsonl") for l in open(os.path.join(RC, f))]
smk = [r for r in smk if "cid" in r]
firsts = {f: [json.loads(l) for l in open(os.path.join(RC, f))] for f in ("smoke_granite_full.jsonl", "smoke_granite_full_b.jsonl")}
COLD["granite_full"] = [(next(r for r in firsts[f] if "cid" in r)["ms"] / 1000, False, "two probe runs, prefix uncached") for f in firsts]
LAT = {}
order = ["qwen_full", "gemma_full", "qwen_short", "gemma_short", "granite_short", "safeguard_short", "granite_full", "safeguard_full"]
for k in order:
    allrows, lastseg = segments(J[k]["path"])
    rs = [r for r in sorted(lastseg, key=lambda r: r["idx"]) if r["verdict"] in ("block", "allow") and r["ms"] > 0]
    first_all = next(r for r in sorted(allrows, key=lambda r: r["idx"]) if r["verdict"] in ("block", "allow") and r["ms"] > 0)["ms"] / 1000
    steady = [r["ms"] / 1000 for r in rs[1:]]; first = first_all
    st = sorted(steady); p50 = statistics.median(st); p90 = st[int(0.9 * (len(st) - 1) + 0.5)]
    fl = list(COLD.get(k, []))
    if k == "granite_full": fl.append((first, True, "main run (resumed), prefix partly cached"))
    if not fl:
        kind = {"qwen_short": "cache already warm", "gemma_short": "cache already warm", "granite_short": "cache already warm" if J[k]["backend"] == "llama-server" else "ran beside a second model",
                "safeguard_short": "short prefix", "safeguard_full": "prefix uncached"}.get(k, "")
        if k == "granite_short": kind = "cache already warm (llama-server rerun)"
        fl = [(first, k not in ("safeguard_full", "safeguard_short"), kind)]
    LAT[k] = dict(steady=steady, p50=p50, p90=p90, first=fl)
    note(f"| {J[k]['label']} ({J[k]['backend']}) | " + "; ".join(f"{s:.1f}" for s, _, _ in fl) + f" | {'; '.join(sorted({n for _, _, n in fl}))} | {p50:.2f} | {p90:.2f} | {len(st)} |")
# the LM Studio run of Granite short is a second row of the same judge
allrows, lastseg = segments(os.path.join(RC, "granite_short.jsonl"))
rs = [r for r in sorted(lastseg, key=lambda r: r["idx"]) if r["verdict"] in ("block", "allow") and r["ms"] > 0]
f0 = sorted(allrows, key=lambda r: r["idx"])[0]["ms"] / 1000
st = sorted(r["ms"] / 1000 for r in rs[1:])
LAT["granite_short_lms"] = dict(steady=st, p50=statistics.median(st), p90=st[int(0.9 * (len(st) - 1) + 0.5)], first=[(f0, True, "ran beside a second model")])
note(f"| {J['granite_short']['label']} (LM Studio) | {f0:.1f} | ran beside a second model | {LAT['granite_short_lms']['p50']:.2f} | {LAT['granite_short_lms']['p90']:.2f} | {len(st)} |")
rows4 = [("qwen_full", "qwen3.6, full rules (llama-server)"), ("gemma_full", "gemma-4, full rules (llama-server)"), ("qwen_short", "qwen3.6, short (llama-server)"),
         ("gemma_short", "gemma-4, short (llama-server)"), ("granite_short", "Granite, short (llama-server)"), ("granite_short_lms", "Granite, short (LM Studio)"),
         ("safeguard_short", "safeguard, short (LM Studio)"), ("granite_full", "Granite, full rules (LM Studio)"), ("safeguard_full", "safeguard, full rules (LM Studio)")]
fig, ax = plt.subplots(figsize=(10, 5.8)); rng = np.random.default_rng(1)
colmap = {"qwen_full": OI["blue"], "qwen_short": OI["sky"], "gemma_full": OI["orange"], "gemma_short": OI["yellow"], "granite_short": OI["verm"], "granite_short_lms": OI["verm"], "safeguard_short": OI["green"], "granite_full": OI["verm"], "safeguard_full": OI["green"]}
yy = np.arange(len(rows4))[::-1]
for y, (k, lab) in zip(yy, rows4):
    d = LAT[k]; v = np.array(d["steady"])
    ax.scatter(v, y + rng.uniform(-0.22, 0.22, len(v)), s=7, color=colmap[k], alpha=0.35, edgecolors="none", zorder=1)
    ax.plot([d["p50"]] * 2, [y - 0.33, y + 0.33], color="black", lw=2.6, zorder=3)
    ax.plot([d["p90"]] * 2, [y - 0.33, y + 0.33], color="black", lw=1.4, ls=(0, (2, 1.5)), zorder=3)
    for s, hol, _ in d["first"]:
        ax.plot([s], [y], marker="*", ms=14, mfc=("white" if hol else colmap[k]), mec="black", mew=1.2, ls="none", zorder=4)
ax.axvline(0.628, color=OI["pink"], lw=2.2, zorder=0)
ax.text(0.66, -0.45, "auto mode's classifier wait,\nmedian 0.628 s (see caption)", color="#8a3b6a", fontsize=8.5, va="center", bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
ax.set_xscale("log"); ax.set_xlim(0.2, 200); ax.set_yticks(yy); ax.set_yticklabels([l for _, l in rows4]); ax.set_ylim(-0.9, len(rows4) - 0.4)
ax.set_xlabel("time per call (seconds, log scale)"); ax.grid(axis="x", alpha=.25, which="both")
ax.legend(handles=[Line2D([], [], marker="*", ls="none", ms=13, mfc="0.5", mec="black", label="first call, rules prefix not cached (filled) / cache already warm or machine shared (open)"),
                   Line2D([], [], color="black", lw=2.6, label="steady-state median"), Line2D([], [], color="black", lw=1.4, ls=(0, (2, 1.5)), label="steady-state 90th percentile"),
                   Line2D([], [], marker="o", ls="none", ms=4, mfc="0.5", mec="none", alpha=.5, label="one dot per unique case, after the first call")],
          loc="upper center", bbox_to_anchor=(0.45, -0.12), frameon=False)
ax.set_title("Figure 4. Latency per call: first call apart from steady state", loc="left")
save(fig, "fig4_latency")

# =====================================================================  Figure 5: pairs
note("\n## Figure 5: the 19 refusal-then-allowed pairs (verdict of the refusal member, verdict of the retry)\n")
note("| judge, arm | pairs scored | separated (blocks refusal, allows retry) | both blocked | both allowed | reversed (allows refusal, blocks retry) | separated, CP 95% of scored |\n|:--|--:|--:|--:|--:|--:|:--|")
F5 = {}
p_order = ["qwen_full", "qwen_short", "gemma_full", "gemma_short", "granite_short", "safeguard_short", "granite_full", "safeguard_full"]
for k in p_order:
    B = J[k]["block"]; cnt = collections.Counter()
    for pid, (rc, ac) in sorted(PAIRS.items()):
        if rc in B and ac in B:
            x, y = B[rc], B[ac]
            cnt["separated" if x and not y else "both blocked" if x and y else "both allowed" if (not x and not y) else "reversed"] += 1
    n = sum(cnt.values()); F5[k] = (cnt, n)
    note(f"| {J[k]['label']} | {n} | {cnt['separated']} | {cnt['both blocked']} | {cnt['both allowed']} | {cnt['reversed']} | {100*cp(cnt['separated'], n)[0]:.1f} to {100*cp(cnt['separated'], n)[1]:.1f}% |")
cats = [("separated", OI["blue"], None), ("both blocked", OI["orange"], "//"), ("both allowed", "#BBBBBB", None), ("reversed", OI["verm"], "xx")]
fig, ax = plt.subplots(figsize=(9.5, 4.9)); ys = np.arange(len(p_order))[::-1]
for y, k in zip(ys, p_order):
    cnt, n = F5[k]; left = 0
    for name, col, hat in cats:
        v = cnt[name]
        if v:
            ax.barh(y, v, left=left, color=col, edgecolor="black", hatch=hat, height=0.62, linewidth=0.8)
            ax.text(left + v / 2, y, str(v), ha="center", va="center", fontsize=9.5, color="black", bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))
        left += v
    if n < 19: ax.text(19.3, y, f"{n} of 19 scored", va="center", fontsize=8.5)
ax.set_yticks(ys); ax.set_yticklabels([J[k]["label"] for k in p_order]); ax.set_xlim(0, 22.5); ax.set_xlabel("number of pairs (of 19)")
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=c, ec="black", hatch=h, label=n) for n, c, h in cats], loc="upper center", bbox_to_anchor=(0.4, -0.14), ncol=4, frameon=False,
          title="outcome for a pair (refusal member, retry that auto mode allowed)")
ax.set_title("Figure 5. Do the judges tell a refused call from the allowed retry that followed it?", loc="left"); ax.grid(axis="x", alpha=.25)
save(fig, "fig5_pairs")

with open(os.path.join(OUT, "figure_numbers.md"), "w") as f:
    f.write("# Numbers plotted in figures 1 to 5 (written by w09j_figures.py; no case text)\n\n" + "\n".join(NUMS) + "\n")
print("done;", len(NUMS), "lines")
