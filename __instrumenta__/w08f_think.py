# Tests whether thinking blocks of earlier requests are billed again as input: from w08f stream-json runs of the six-problem tool loop (<S>/runs/T-*-*.jsonl, think-*.jsonl) to a table per run and arm and a least-squares fit of the context growth between consecutive requests on thinking tokens, other output tokens and tool-result characters.
# usage: w08f_think.py S [prefix ...]  (default prefixes: T- think-). Platform-reported counts: output_tokens and output_tokens_details.thinking_tokens of each request's message_delta; context = input + cache_read + cache_creation of the next request's message_start. Fit: growth_k = a + b_think*think_k + b_vis*(out_k - think_k) + b_res*result_chars_k, over requests k that are followed by another request. Answers: the `echo` argument of each Bash call against 401, 30240, 4, 48 36, 242, 88.
import sys, os, re, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w08f_requests import parse
import numpy as np
S = sys.argv[1]; prefixes = sys.argv[2:] or ["T-", "think-"]
TRUTH = ["401", "30240", "4", "48 36", "242", "88"]
def calls_and_results(path):
    calls = []; res = []
    for l in open(path):
        try: d = json.loads(l)
        except Exception: continue
        if d.get("type") == "assistant":
            for b in d["message"]["content"]:
                if b["type"] == "tool_use" and b["name"] == "Bash": calls.append((d["message"]["id"], b["input"].get("command", "")))
        elif d.get("type") == "user" and isinstance(d["message"]["content"], list):
            for b in d["message"]["content"]:
                if b.get("type") == "tool_result":
                    x = b.get("content"); x = x if isinstance(x, str) else json.dumps(x); res.append(len(x))
    seen = {}
    for mid, c in calls: seen.setdefault(mid, c)
    return list(seen.values()), res
X = []; Y = []; tab = []
print("run\treq\tusd\tout\tthinking\tvisible_out\tgrowth_minus_out(mean over non-final)\tanswers_ok\tarm")
for pre in prefixes:
    for f in sorted(glob.glob(os.path.join(S, "runs", pre + "*.jsonl"))):
        label = os.path.basename(f)[:-6]; rows, _ = parse(f); calls, res = calls_and_results(f)
        ans = [re.sub(r"^\s*echo\s+", "", c).strip().strip("'\"") for c in calls]
        ok = sum(1 for a, t in zip(ans, TRUTH) if a.replace(",", "").replace(" and ", " ") .startswith(t) or a == t)
        n = len(rows)
        gm = []
        for k in range(n - 1):
            g = rows[k + 1]["ctx"] - rows[k]["ctx"]; th = rows[k]["think"] or 0; o = rows[k]["out"] or 0
            X.append([1, th, o - th, res[k] if k < len(res) else 0]); Y.append(g); gm.append(g - o)
        arm = label.split("-")[1] if label.startswith("T-") else "cli-" + label.split("-")[1]
        usd = sum(r["usd"] for r in rows)
        tab.append((label, n, usd, sum(r["out"] or 0 for r in rows), sum(r["think"] or 0 for r in rows), ok, arm))
        print("%s\t%d\t%.4f\t%d\t%d\t%d\t%.1f\t%d/6\t%s" % (label, n, usd, tab[-1][3], tab[-1][4], tab[-1][3] - tab[-1][4], sum(gm) / max(1, len(gm)), ok, arm))
X = np.array(X, float); Y = np.array(Y, float)
b, *_ = np.linalg.lstsq(X, Y, rcond=None); r = Y - X @ b
print("\nfit over %d request pairs: growth = %.1f + %.3f*thinking_tokens + %.3f*other_output_tokens + %.3f*result_chars ; R2 %.4f ; residual sd %.1f tokens" % (len(Y), b[0], b[1], b[2], b[3], 1 - r.var() / Y.var(), r.std()))
# bootstrap CI for the thinking coefficient
rng = np.random.default_rng(1); bs = []
for _ in range(2000):
    i = rng.integers(0, len(Y), len(Y)); bb, *_ = np.linalg.lstsq(X[i], Y[i], rcond=None); bs.append(bb[1])
print("thinking coefficient bootstrap 95%% interval %.3f .. %.3f (2000 resamples of request pairs, seed 1)" % tuple(np.percentile(bs, [2.5, 97.5])))
print("\narm\truns\tmean_usd\tmean_requests\tmean_out\tmean_thinking\tthinking_share_of_out\tanswers_ok\tusd_range")
by = collections.defaultdict(list)
for t in tab: by[t[6]].append(t)
for arm, g in by.items():
    n = len(g); print("%s\t%d\t%.4f\t%.1f\t%.0f\t%.0f\t%.0f%%\t%d/%d\t%.4f-%.4f" % (arm, n, sum(x[2] for x in g) / n, sum(x[1] for x in g) / n, sum(x[3] for x in g) / n, sum(x[4] for x in g) / n, 100 * sum(x[4] for x in g) / max(1, sum(x[3] for x in g)), sum(x[5] for x in g), 6 * n, min(x[2] for x in g), max(x[2] for x in g)))
