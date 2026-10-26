# Draws the five figures of explorer-w09-k (raw-open rate by sender role; by wave; escalation sizes and fate; banner against none; wave-8 timeline) and writes figure_numbers.txt with every count and Clopper-Pearson interval behind them, from the tables of w09k_extract.py (wakes, arrivals, turns, opens, r2 .tsv) and from explorer-w09-h's escalation table and ranges.tsv.
# usage: python3 -I w09k_figures.py <datadir with the w09k tables> <escalation_table.md> <ranges.tsv> <outdir for figures and figure_numbers.txt>
import sys, os, csv, re, math, collections, datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# Okabe-Ito colour-blind-safe palette; shapes carry the same information as colours
ROLE = ["explorer", "author", "verifier"]
COL = {"explorer": "#0072B2", "author": "#E69F00", "verifier": "#009E73", "all": "#000000"}
MRK = {"explorer": "o", "author": "s", "verifier": "^", "all": "D"}
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9, "legend.fontsize": 8, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 100, "savefig.dpi": 200, "pdf.fonttype": 42})
NUM = []


def say(s=""):
    NUM.append(s)


def rd(path):
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def cp(k, n, alpha=0.05):
    """exact two-sided Clopper-Pearson interval by bisection on the binomial tail (math.comb only)"""
    if n == 0:
        return (float("nan"), float("nan"))
    def cdf(x, p):  # P(X <= x)
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, x + 1))
    def bis(f, lo, hi):
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid):
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else bis(lambda p: 1 - cdf(k - 1, p) >= alpha / 2, 0.0, 1.0)   # smallest p with P(X>=k) >= alpha/2
    hi = 1.0 if k == n else bis(lambda p: cdf(k, p) <= alpha / 2, 0.0, 1.0)            # p where P(X<=k) = alpha/2
    return (lo, hi)


def pt(ax, x, k, n, color, marker, filled=True, ms=6.5, orient="v", label=None, lw=1.3):
    p = k / n if n else float("nan")
    lo, hi = cp(k, n)
    mfc = color if filled else "white"
    if orient == "v":
        ax.errorbar(x, 100 * p, yerr=[[100 * (p - lo)], [100 * (hi - p)]], fmt=marker, color=color, mfc=mfc, mec=color, ms=ms, capsize=2.5, lw=lw, label=label, zorder=3)
    else:
        ax.errorbar(100 * p, x, xerr=[[100 * (p - lo)], [100 * (hi - p)]], fmt=marker, color=color, mfc=mfc, mec=color, ms=ms, capsize=2.5, lw=lw, label=label, zorder=3)
    return p, lo, hi


def rate(rows, key):
    return sum(int(r[key]) for r in rows), len(rows)


def line(name, k, n):
    p = k / n if n else float("nan")
    lo, hi = cp(k, n)
    say("  %-34s %3d/%-3d = %5.1f%%   95%% CP [%4.1f, %4.1f]" % (name, k, n, 100 * p, 100 * lo, 100 * hi))


def fisher(a, n1, b, n2):
    N = n1 + n2; K = a + b; tot = math.comb(N, K); p0 = math.comb(n1, a) * math.comb(n2, b) / tot
    return sum(math.comb(n1, x) * math.comb(n2, K - x) / tot for x in range(max(0, K - n2), min(n1, K) + 1) if math.comb(n1, x) * math.comb(n2, K - x) / tot <= p0 * (1 + 1e-9))


def wave_group(lab):
    return {"w123": "w1-3"}.get(lab, lab)


def main():
    dd, esc_md, ranges_tsv, out = sys.argv[1:5]
    os.makedirs(out, exist_ok=True)
    W = rd(os.path.join(dd, "wakes.tsv"))
    A = rd(os.path.join(dd, "arrivals.tsv"))
    T = rd(os.path.join(dd, "turns.tsv"))
    O = rd(os.path.join(dd, "opens.tsv"))
    R2 = rd(os.path.join(dd, "r2.tsv"))
    HB = [w for w in W if w["peer"] == "0"]                    # hand-back wakes with a request, peer messages out
    HB58 = [w for w in HB if w["label"] in ("w5", "w6", "w7", "w8")]
    say("population: hand-back wakes with a request (n_steps>0), peer messages that open 'Another Claude session sent a message' left out")
    say("  waves 1-8: %d (w09c5: 178 + 35 = 213); waves 5-8: %d (w09c5: 120)" % (len(HB), len(HB58)))

    # ---- Figure 1: by role, waves 5-8, two codings plus the second coder
    say("\nFIGURE 1: raw open in the wake turn, by sender role, waves 5-8 (as coded / lab_status masked / second coder R2)")
    r2 = [r for r in R2 if r["label"] in ("w5", "w6", "w7", "w8") and int(r["n_asst"]) >= 1]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ys = {"explorer": 2, "author": 1, "verifier": 0}
    off = {"coded": 0.24, "masked": 0.0, "r2": -0.24}
    for role in ROLE:
        rs = [w for w in HB58 if w["role"] == role]
        for kind, key, filled, mk in (("coded", "raw_coded", True, MRK[role]), ("masked", "raw_masked", False, MRK[role])):
            k, n = rate(rs, key)
            pt(ax, ys[role] + off[kind], k, n, COL[role], mk, filled, orient="h")
            line("%s, %s" % (role, "as coded" if kind == "coded" else "masked"), k, n)
            ax.text(103, ys[role] + off[kind], "%d/%d" % (k, n), va="center", fontsize=7.5)
        rr = [r for r in r2 if r["role"] == role]
        k, n = sum(int(r["open"]) for r in rr), len(rr)
        pt(ax, ys[role] + off["r2"], k, n, "#555555", "D", True, ms=5, orient="h")
        line("%s, second coder R2" % role, k, n)
        ax.text(103, ys[role] + off["r2"], "%d/%d" % (k, n), va="center", fontsize=7.5, color="#555555")
    ax.set_yticks([2, 1, 0])
    ax.set_yticklabels(["explorer", "author", "verifier\n(reproducer)"])
    ax.set_xlim(-2, 112)
    ax.set_xticks(range(0, 101, 20))
    ax.set_xlabel("hand-back wakes with a raw artifact opened in the same PI turn (% of wakes)")
    ax.set_ylim(-0.6, 2.6)
    ax.grid(axis="x", color="#dddddd", lw=0.6, zorder=0)
    h = [Line2D([], [], marker="o", color="k", mfc="k", ls="", label="as coded (w09d rule)"),
         Line2D([], [], marker="o", color="k", mfc="white", ls="", label='"lab_status" masked'),
         Line2D([], [], marker="D", color="#555555", ls="", ms=5, label="second coder, rule R2")]
    ax.legend(handles=h, loc="center left", frameon=False, bbox_to_anchor=(0.42, 0.40))
    ax.set_title("Raw-artifact opens per hand-back wake, by who handed back (waves 5-8)", loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig1_rawopen_by_role.png")); fig.savefig(os.path.join(out, "fig1_rawopen_by_role.pdf")); plt.close(fig)
    # agreement of R2 with the as-coded and masked flags on the hand-backs both cut
    m = {(w["label"], round(float(w["epoch"]), 2)): w for w in HB58}
    pairs = []
    allr2 = {}
    for r in R2:
        if r["label"] in ("w5", "w6", "w7", "w8") and int(r["n_asst"]) >= 1:
            allr2[(r["label"], round(float(r["epoch"]), 2))] = r
    for key, r in allr2.items():
        if key in m:
            pairs.append((int(r["open"]), int(m[key]["raw_coded"]), int(m[key]["raw_masked"])))
    def kappa(a, b):
        n = len(a); po = sum(x == y for x, y in zip(a, b)) / n; pa = sum(a) / n; pb = sum(b) / n; pe = pa * pb + (1 - pa) * (1 - pb)
        return po, (po - pe) / (1 - pe)
    say("  second coder R2 against the as-coded / masked flag on the hand-backs both cut (matched by label and timestamp): n matched %d of R2's %d and the rule's %d" % (len(pairs), len(allr2), len(m)))
    for nm, i in (("as coded", 1), ("masked", 2)):
        a = [p[0] for p in pairs]; b = [p[i] for p in pairs]
        po, kp = kappa(a, b)
        say("  R2 vs %-9s agree %d/%d, Cohen kappa %.2f" % (nm, sum(x == y for x, y in zip(a, b)), len(a), kp))

    # ---- Figure 2: by wave (all, and per role)
    waves = ["w1-3", "w4", "w5", "w6", "w7", "w8"]
    first_day = {}
    for w in HB:
        g = wave_group(w["label"])
        first_day.setdefault(g, w["time_jst"][5:10])
    say("\nFIGURE 2: raw open in the wake turn, by wave, as coded (filled) and masked (open); peer messages out")
    fig, axes = plt.subplots(1, 4, figsize=(11.5, 3.9), sharey=True)
    panels = [("all hand-backs", None)] + [(r, r) for r in ROLE]
    for ax, (title, role) in zip(axes, panels):
        for i, g in enumerate(waves):
            rs = [w for w in HB if wave_group(w["label"]) == g and (role is None or w["role"] == role)]
            if not rs:
                ax.text(i, 3, "none", ha="center", fontsize=7.5, color="#777777")
                continue
            c = COL[role or "all"]; mk = MRK[role or "all"]
            for dx, key, filled in ((-0.08, "raw_coded", True), (0.08, "raw_masked", False)):
                k, n = rate(rs, key)
                pt(ax, i + dx, k, n, c, mk, filled, ms=5.5, lw=1.1)
                line("%s, %s, %s" % (title, g, "coded" if filled else "masked"), k, n)
            k, n = rate(rs, "raw_coded")
            ax.text(i, 104, "%d/%d" % (k, n), ha="center", fontsize=7, color="#333333")
        ax.set_xticks(range(len(waves)))
        ax.set_xticklabels(["%s\n%s" % (g, first_day.get(g, "")) for g in waves])
        ax.set_title(title, loc="left")
        ax.set_ylim(-3, 112)
        ax.grid(axis="y", color="#dddddd", lw=0.6, zorder=0)
        ax.set_xlim(-0.6, len(waves) - 0.4)
    axes[0].set_ylabel("hand-back wakes with a raw artifact opened\nin the same PI turn (% of wakes)")
    axes[0].set_yticks(range(0, 101, 20))
    fig.text(0.5, 0.005, "wave (session; first hand-back date, month-day JST)  -  numbers above the points: as coded, opens/wakes", ha="center", fontsize=8)
    fig.suptitle("Raw-artifact opens per hand-back wake, by wave and sender (filled: as coded, open: lab_status masked; bars: 95% Clopper-Pearson)", x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(os.path.join(out, "fig2_rawopen_by_wave.png")); fig.savefig(os.path.join(out, "fig2_rawopen_by_wave.pdf")); plt.close(fig)
    say("  median hand-back length (characters, after the harness frame), by wave:")
    for g in waves:
        v = sorted(int(w["hb_chars"]) for w in HB if wave_group(w["label"]) == g)
        say("    %-5s n=%3d median %5d" % (g, len(v), v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2))

    # ---- Figure 3: escalations
    say("\nFIGURE 3: the 14 claims with a verifier ESCALATE verdict (explorer-w09-h's table; sizes from ranges.tsv)")
    rng = {r["claim"]: r for r in rd(ranges_tsv)}
    rows = []
    txt = open(esc_md).read().replace("\\|", "¦")
    for ln in txt.splitlines():
        if not ln.startswith("| w"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        claim = c[0]
        hb = None if "not located" in c[2] else int(re.sub(r"[^\d]", "", c[2].split()[0]))
        read = "yes" if c[4].upper().startswith("YES") else ("not checked" if c[4].startswith("not checked") else "no")
        state = c[9]
        fate = "superseded" if state.startswith("superseded") else "restated"
        delivery = "queued" if "queued" in c[1] else ("peer" if "peer" in c[1] else "not located")
        rows.append(dict(claim=claim, hb=hb, sec=int(rng[claim]["sec_chars"]), exch=int(rng[claim]["exch_chars"]), read=read, fate=fate, state=state, delivery=delivery, wake=c[1]))
    rows.sort(key=lambda r: r["claim"])
    for r in rows:
        say("  %-8s hb %-6s section %5d exchange %5d read-in-wake %-11s delivery %-11s fate %-10s | %s" % (r["claim"], r["hb"], r["sec"], r["exch"], r["read"], r["delivery"], r["fate"], r["state"][:60]))
    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    n = len(rows)
    fcol = {"superseded": "#D6EAF8", "restated": "#FDEBD0"}
    for i, r in enumerate(rows):
        y = n - 1 - i
        ax.axhspan(y - 0.5, y + 0.5, color=fcol[r["fate"]], zorder=0, lw=0)
        vals = [(r["hb"], "o", "#0072B2", "hand-back as received"), (r["exch"], "v", "#CC79A7", "verifier's exchange (in the claim file)"), (r["sec"], "s", "#D55E00", "verifier's whole section (in the claim file)")]
        xs = [v[0] for v in vals if v[0] is not None]
        ax.plot([min(xs), max(xs)], [y, y], color="#999999", lw=1.0, zorder=1)
        for v, mk, col, lab in vals:
            if v is not None:
                ax.plot(v, y, mk, color=col, mfc=col, ms=7, zorder=3, mec="black", mew=0.4)
        rd_txt = {"no": "no", "yes": "YES (verdict section, lines cut at 500 characters)", "not checked": "not checked"}[r["read"]]
        ax.text(-300, y, "%s%s" % (r["claim"], " *" if r["delivery"] == "queued" else (" **" if r["delivery"] == "not located" else "")), ha="right", va="center", fontsize=8.5, fontweight="bold")
        ax.text(12500, y, "%s | %s" % (rd_txt if r["read"] != "yes" else "YES (section, cut)", r["fate"]), ha="left", va="center", fontsize=8,
                fontweight="bold" if r["read"] == "yes" else "normal")
    ax.set_yticks([])
    ax.set_xlim(-300, 12400)
    ax.set_ylim(-0.7, n - 0.3)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("characters")
    ax.text(12500, n - 0.35, "claim file read in the\nwake? | decision today", ha="left", va="bottom", fontsize=8, fontweight="bold")
    h = [Line2D([], [], marker="o", color="#0072B2", mec="black", mew=0.4, ls="", label="hand-back as the PI received it"),
         Line2D([], [], marker="v", color="#CC79A7", mec="black", mew=0.4, ls="", label="verifier's exchange section"),
         Line2D([], [], marker="s", color="#D55E00", mec="black", mew=0.4, ls="", label="verifier's whole section"),
         Patch(facecolor=fcol["superseded"], label="fate: superseded by a new claim"), Patch(facecolor=fcol["restated"], label="fate: restated in place (not re-verified)")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.45, -0.1), ncol=3, frameon=False, fontsize=8)
    fig.suptitle("Escalated claims: size of what the PI received and of what sat in the claim file, and what came of the decision", x=0.01, ha="left", fontsize=9.5)
    fig.text(0.01, 0.01, "* hand-back arrived as a queued attachment.  ** wake not located (no hand-back length).  Source: explorer-w09-h 01-escalation_table.md and out/ranges.tsv (an explorer's report, not a verified claim).", fontsize=7.5)
    fig.subplots_adjust(left=0.08, right=0.74, bottom=0.2, top=0.88)
    fig.savefig(os.path.join(out, "fig3_escalations.png")); fig.savefig(os.path.join(out, "fig3_escalations.pdf")); plt.close(fig)
    hbv = sorted(r["hb"] for r in rows if r["hb"]); sv = sorted(r["sec"] for r in rows); ev = sorted(r["exch"] for r in rows)
    say("  claims %d; read in wake: %s; fate: %s" % (len(rows), dict(collections.Counter(r["read"] for r in rows)), dict(collections.Counter(r["fate"] for r in rows))))
    say("  hand-back chars n=%d median %s; section median %s; exchange median %s" % (len(hbv), hbv[len(hbv) // 2] if len(hbv) % 2 else (hbv[len(hbv) // 2 - 1] + hbv[len(hbv) // 2]) / 2,
        sv[len(sv) // 2 - 1:len(sv) // 2 + 1], ev[len(ev) // 2 - 1:len(ev) // 2 + 1]))

    # ---- Figure 4: banner against none, by role, waves 1-8
    say("\nFIGURE 4: raw open in the wake turn, banner in the first 260 characters of the hand-back against none, by role, waves 1-8 (peer messages out)")
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    groups = ROLE + ["all"]
    for gi, role in enumerate(groups):
        rs = [w for w in HB if role == "all" or w["role"] == role]
        for dx, ban, filled in ((0.13, "1", True), (-0.13, "0", False)):
            sub = [w for w in rs if w["banner"] == ban]
            k, n = rate(sub, "raw_coded")
            x = (3 - gi)
            pt(ax, x + dx, k, n, COL[role], MRK[role], filled, orient="h")
            line("%s, %s, as coded" % (role, "banner" if ban == "1" else "no banner"), k, n)
            k2, n2 = rate(sub, "raw_masked")
            line("%s, %s, masked" % (role, "banner" if ban == "1" else "no banner"), k2, n2)
            ax.text(103, x + dx, "%d/%d" % (k, n), va="center", fontsize=7.5)
        for key in ("raw_coded", "raw_masked"):
            kb, nb = rate([w for w in rs if w["banner"] == "1"], key); kn, nn = rate([w for w in rs if w["banner"] == "0"], key)
            say("  %-9s %s: banner %d/%d vs none %d/%d, two-sided Fisher exact p = %.2f" % (role, key, kb, nb, kn, nn, fisher(kb, nb, kn, nn)))
    ax.set_yticks([3, 2, 1, 0])
    ax.set_yticklabels(["explorer", "author", "verifier", "all roles"])
    ax.set_xlim(-2, 114)
    ax.set_xticks(range(0, 101, 20))
    ax.set_ylim(-0.6, 3.6)
    ax.set_xlabel("hand-back wakes with a raw artifact opened in the same PI turn (% of wakes)")
    ax.grid(axis="x", color="#dddddd", lw=0.6, zorder=0)
    h = [Line2D([], [], marker="o", color="k", mfc="k", ls="", label="hand-back carried the platform banner"),
         Line2D([], [], marker="o", color="k", mfc="white", ls="", label="no banner")]
    ax.legend(handles=h, loc="center left", frameon=False, bbox_to_anchor=(0.42, 0.36))
    ax.set_title("Did the platform's banner on a hand-back send the PI to the raw artifact? (waves 1-8, as coded)", loc="left", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig4_banner_by_role.png")); fig.savefig(os.path.join(out, "fig4_banner_by_role.pdf")); plt.close(fig)

    # ---- Figure 5: wave-8 timeline
    say("\nFIGURE 5: wave 8 (PI session 70daedf1), hand-back arrivals and the PI's raw opens, JST")
    t0 = min(float(a["epoch"]) for a in A if a["label"] == "w8")
    GAP0, GAP1 = 5.2, 13.2          # hours: nothing happens between (axis break)
    def xm(h):
        return h if h <= GAP0 else h - (GAP1 - GAP0)
    w8wake = {round(float(w["epoch"]), 2): w for w in W if w["label"] == "w8"}
    fig, ax = plt.subplots(figsize=(11.5, 5.3))
    lanes = [("busy", "PI working (one bar per turn)"), ("explorer", "explorer hand-back"), ("author", "author hand-back"), ("verifier", "verifier hand-back"),
             ("claim file", "PI opens: claim file"), ("puzzle file", "PI opens: puzzle file"), ("worker report", "PI opens: worker report"), ("other", "PI opens: other raw")]
    ly = {k: len(lanes) - 1 - i for i, (k, _) in enumerate(lanes)}
    for tr in [t for t in T if t["label"] == "w8"]:
        a, b = xm((float(tr["t0"]) - t0) / 3600), xm((float(tr["t1"]) - t0) / 3600)
        ax.barh(ly["busy"], max(b - a, 0.012), left=a, height=0.5, color="#888888", lw=0, zorder=2)
    nA = collections.Counter(); nAopen = collections.Counter()
    for a in [x for x in A if x["label"] == "w8"]:
        if a["peer"] == "1" or a["role"] not in ROLE:
            continue
        x = xm((float(a["epoch"]) - t0) / 3600)
        w = w8wake.get(round(float(a["epoch"]), 2))
        opened = bool(w and w["raw_masked"] == "1" and a["leads_turn"] == "1")
        led = a["leads_turn"] == "1"
        nA[a["role"]] += 1; nAopen[a["role"]] += opened
        ax.plot(x, ly[a["role"]], MRK[a["role"]], color=COL[a["role"]], mfc=COL[a["role"]] if opened else "white", ms=7.5 if led else 5.5, mew=1.3, zorder=3)
        ax.plot([x, x], [ly[a["role"]], ly["busy"]], color=COL[a["role"]], lw=0.4, alpha=0.35, zorder=1)
    cmap = {"claim file": "claim file", "puzzle file": "puzzle file", "worker report": "worker report"}
    nO = collections.Counter()
    for o in [x for x in O if x["label"] == "w8"]:
        k = cmap.get(o["class"], "other")
        x = xm((float(o["epoch"]) - t0) / 3600)
        wake = o["turn_trigger"] == "B"
        nO[(k, wake)] += 1
        ax.plot(x, ly[k], "|", color="#D55E00", ms=11, mew=2.0 if wake else 1.0, alpha=1.0 if wake else 0.55, zorder=3)
    ax.set_yticks([ly[k] for k, _ in lanes]); ax.set_yticklabels([l for _, l in lanes])
    ax.set_xlim(-0.2, xm((max(float(tr["t1"]) for tr in T if tr["label"] == "w8") - t0) / 3600) + 0.2)
    tk = [0, 1, 2, 3, 4, 5, xm(13.5), xm(14.0), xm(14.5)]
    ax.set_xticks(tk); ax.set_xticklabels(["0", "1", "2", "3", "4", "5", "13.5", "14", "14.5"])
    ax.axvline(GAP0 + 0.15, color="#555555", ls=":", lw=1); ax.axvline(GAP0 + 0.15 + 0.0, color="#555555", ls=":", lw=1)
    ax.text(GAP0 + 0.2, ly["claim file"] + 0.0, "axis break 5.2-13.2 h: no turn", fontsize=7.5, color="#444444", va="center")
    ax.set_ylim(-0.6, len(lanes) - 0.4)
    ax.set_xlabel("hours since the first hand-back of wave 8 (24 Oct 2026 00:25 JST)")
    ax.grid(axis="x", color="#dddddd", lw=0.6, zorder=0)
    h = [Line2D([], [], marker="o", color="k", mfc="k", ls="", label="hand-back, raw artifact opened in that wake turn"),
         Line2D([], [], marker="o", color="k", mfc="white", ls="", label="hand-back, none opened in that turn"),
         Line2D([], [], marker="|", color="#D55E00", ls="", ms=10, mew=2, label="PI raw open in a hand-back wake turn (bold) / in another turn (pale)")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=8)
    ax.set_title("Wave 8: when hand-backs arrived and when the PI opened raw artifacts (JST, one PI session)", loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig5_wave8_timeline.png")); fig.savefig(os.path.join(out, "fig5_wave8_timeline.pdf")); plt.close(fig)
    say("  hand-back arrivals (peer messages out) by role: %s; leading a turn with a raw open (masked): %s" % (dict(nA), dict(nAopen)))
    say("  PI raw opens in wave 8 by lane and (in a hand-back wake turn?): %s" % dict(nO))
    say("  arrivals total %d; arrivals mid-turn %d" % (sum(1 for a in A if a["label"] == "w8" and a["peer"] == "0"), sum(1 for a in A if a["label"] == "w8" and a["peer"] == "0" and a["leads_turn"] == "0")))
    with open(os.path.join(out, "figure_numbers.txt"), "w") as f:
        f.write("\n".join(NUM) + "\n")
    print("\n".join(NUM))


if __name__ == "__main__":
    main()
