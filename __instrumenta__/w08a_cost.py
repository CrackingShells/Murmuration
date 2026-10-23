# Attributes each worker request's input-side USD (cache read, cache write 5m/1h, uncached input, at list price) to the items in its context by token position, from the per-worker JSON of w08a_items.py; inputs: items folder; outputs: items.tsv (one row per context element: class, kind, ref, chars, est tokens, later requests, first-write / read / re-write USD) and check.txt (attribution vs recorded cost). Usage: w08a_cost.py ITEMS_DIR OUT_DIR
import json, sys, os, glob, re
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L

items_dir, outdir = sys.argv[1:3]
os.makedirs(outdir, exist_ok=True)
A = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(items_dir, "*.json")))]

GROUP = {"readother": "other", "bashother": "other", "brief": "msg"}
def grp(c):
    return GROUP.get(c, c)

def ctx(t):
    return t["cr"] + t["cw1"] + t["cw5"] + t["inp"]

# ---- calibration: tokens per character by class, from growth of context between consecutive requests.
# The transcript's output_tokens is the value at the start of the stream (a few tokens), so the assistant's own tokens are
# fitted too: from the characters of its tool-call inputs, its thinking blocks (signature + text) and its text.
CL = ["readdoc", "readsrc", "bashdoc", "bashsrc", "script", "git", "search", "web", "other", "msg", "harness", "hook"]
def has_ts(t):
    return any(i["kind"].startswith("ToolSearch") for i in t["in"])
X, y = [], []
for a in A:
    T = a["turns"]
    for k in range(1, len(T)):
        g = ctx(T[k]) - ctx(T[k - 1])
        if g <= 0 or has_ts(T[k]):
            continue
        row = [0.0] * (len(CL) + 4)
        for it in T[k]["in"]:
            c = grp(it["cls"])
            if c in CL and it["kind"] != "total_tokens reminder":
                row[CL.index(c)] += it["chars"]
        row[len(CL)] = T[k - 1]["call_chars"]; row[len(CL) + 1] = T[k - 1]["sig_chars"]; row[len(CL) + 2] = T[k - 1]["text_chars"]; row[len(CL) + 3] = 1
        X.append(row); y.append(g)
X = np.array(X); y = np.array(y)
coef = np.linalg.lstsq(X, y, rcond=None)[0]
TPC = {c: float(min(0.55, max(0.30, coef[i]))) for i, c in enumerate(CL)}
TPC["reminder"] = 0.40
ACALL, ASIG, ATXT, AWRAP = (float(max(0.0, coef[len(CL) + j])) for j in range(4))
lines = ["calibration (OLS of context growth between consecutive requests on characters of new items by class, the previous turn's tool-call input characters, thinking characters and text characters, and a constant; intervals without a ToolSearch result; n=%d):" % len(y)]
for i, c in enumerate(CL):
    lines.append("  %-9s fitted %.3f tokens/char (%.2f chars/token), used %.3f" % (c, coef[i], 1 / coef[i] if coef[i] > 0 else 0, TPC[c]))
lines.append("  tool-call input %.3f tokens/char; thinking (signature+text) %.3f tokens/char; text %.3f tokens/char; constant per turn %.0f tokens" % (ACALL, ASIG, ATXT, AWRAP))
lines.append("  R2 = %.3f" % (1 - ((y - X @ coef) ** 2).sum() / ((y - y.mean()) ** 2).sum()))

def est_tokens(it):
    if it["kind"] == "total_tokens reminder":
        return 49 * TPC["reminder"] + 8
    c = grp(it["cls"])
    return it["chars"] * TPC.get(c, 0.42)

def prices(model):
    return L.PRICES.get(re.sub(r"-\d{8}$", "", model or ""), L.PRICES["claude-sonnet-5-5"])

rows = []
chk = {"attributed": 0.0, "recorded_input_side": 0.0, "recorded_total": 0.0, "output_usd": 0.0, "neg_growth": 0, "scale_off": []}
for a in A:
    T = a["turns"]
    n = len(T)
    # ---- elements in context order, each entering at interval k (k = the request that first carries it)
    E = []  # dict(tokens, k, cls, kind, ref, chars)
    for k, t in enumerate(T):
        its = t["in"]
        est = [est_tokens(i) for i in its]
        if k == 0:
            C0 = ctx(t)
            tot = sum(est)
            if tot > 0.9 * C0:
                est = [e * 0.9 * C0 / tot for e in est]
            E.append({"tokens": C0 - sum(est), "k": 0, "cls": "base", "kind": "system prompt, tool list, harness (rest of the first request)", "ref": "", "chars": 0})
            for i, e in zip(its, est):
                E.append({"tokens": e, "k": 0, "cls": i["cls"], "kind": i["kind"], "ref": i["ref"], "chars": i["chars"], "tool": i["tool"]})
        else:
            g = ctx(t) - ctx(T[k - 1])
            if g < 0:
                chk["neg_growth"] += 1
            pv = T[k - 1]
            parts = [("calls", "the agent's tool calls (input text)", pv["call_chars"] * ACALL), ("think", "the agent's thinking blocks", pv["sig_chars"] * ASIG),
                     ("text", "the agent's text and per-turn wrapper", pv["text_chars"] * ATXT + AWRAP)]
            pred = sum(p[2] for p in parts) + sum(est)
            ts_items = [j for j, i in enumerate(its) if i["kind"].startswith("ToolSearch")]
            if ts_items and g > pred:
                extra = (g - pred) / len(ts_items)
                for j in ts_items:
                    est[j] += extra
            elif g > 0 and pred > 0:
                f = g / pred
                est = [e * f for e in est]; parts = [(a_, b_, c_ * f) for a_, b_, c_ in parts]
            for a_, b_, c_ in parts:
                E.append({"tokens": c_, "k": k, "cls": "asst", "kind": b_, "ref": "", "chars": 0})
            for i, e in zip(its, est):
                E.append({"tokens": e, "k": k, "cls": i["cls"], "kind": i["kind"], "ref": i["ref"], "chars": i["chars"], "tool": i["tool"]})
    for e in E:
        e["first"] = e["read"] = e["rewrite"] = 0.0
        e["n_rewrite"] = 0
    ntok = np.array([e["tokens"] for e in E])
    ek = np.array([e["k"] for e in E])
    # ---- per request
    for k, t in enumerate(T):
        p = prices(t["model"])
        fast = 2.0 if t["fast"] else 1.0
        cw = t["cw1"] + t["cw5"]
        pw = (t["cw5"] * p[3] + t["cw1"] * p[4]) / cw if cw else p[3]
        cr_p, in_p = p[2], p[0]
        C = ctx(t)
        m = ek <= k
        idx = np.nonzero(m)[0]
        tk = ntok[idx]
        tot = tk.sum()
        if tot <= 0:
            continue
        scale = C / tot
        if abs(scale - 1) > 0.02:
            chk["scale_off"].append((a["label"], a["agent"], k, round(scale, 3)))
        tk = tk * scale
        hi = np.cumsum(tk); lo = hi - tk
        r_end, w_end = t["cr"], t["cr"] + cw
        rd = np.clip(np.minimum(hi, r_end) - lo, 0, None)
        wr = np.clip(np.minimum(hi, w_end) - np.maximum(lo, r_end), 0, None)
        ip = tk - rd - wr
        usd = (rd * cr_p + wr * pw + ip * in_p) / 1e6 * fast
        chk["attributed"] += usd.sum()
        rec_in = (t["cr"] * cr_p + cw * pw + t["inp"] * in_p) / 1e6 * fast
        chk["recorded_input_side"] += rec_in
        # output cost is not attributed (assistant generation); recorded for the check
        chk["output_usd"] += 0.0
        for j, i in enumerate(idx):
            e = E[i]
            if e["k"] == k:
                e["first"] += usd[j]
            else:
                rdu = rd[j] * cr_p / 1e6 * fast
                wru = (wr[j] * pw + ip[j] * in_p) / 1e6 * fast
                e["read"] += rdu; e["rewrite"] += wru
                if wr[j] > 0.5:
                    e["n_rewrite"] += 1
        chk["recorded_total"] += (L.message_usd(t["model"], {"input_tokens": t["inp"], "output_tokens": 0, "cache_read_input_tokens": t["cr"], "cache_creation_input_tokens": cw, "cache_creation": {"ephemeral_1h_input_tokens": t["cw1"], "ephemeral_5m_input_tokens": t["cw5"]}, "speed": "fast" if t["fast"] else None}) or 0.0)
    for e in E:
        rows.append((a["label"], a["name"] or a["agent"], a["agent"], e["cls"], e["kind"], e["ref"], e.get("tool", ""), e["chars"], e["tokens"], n - 1 - e["k"], e["k"], e["first"], e["read"], e["rewrite"], e["n_rewrite"]))

with open(os.path.join(outdir, "items.tsv"), "w") as fh:
    fh.write("wave\tworker_name\tagent_id\tcls\tkind\tref\ttool\tchars\test_tokens\tlater_requests\tentered_at_request\tfirst_write_usd\tread_usd\trewrite_usd\tn_rewrites\n")
    for r in rows:
        fh.write("\t".join(("%.6f" % x) if isinstance(x, float) else str(x) for x in r) + "\n")
lines.append("")
lines.append("workers %d, requests %d, elements %d" % (len(A), sum(len(a["turns"]) for a in A), len(rows)))
lines.append("sum of attributed USD %.4f; recorded input-side USD (cache read + write + input) %.4f; intervals with shrinking context %d; requests whose element sizes needed rescaling by more than 2%%: %d of %d" % (chk["attributed"], chk["recorded_input_side"], chk["neg_growth"], len(chk["scale_off"]), sum(len(a["turns"]) for a in A)))
open(os.path.join(outdir, "check.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
