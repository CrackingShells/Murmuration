# Summarises the effort-arm runs of w08-f: from <S>/runs/<task>-<arm>-<rep>.jsonl and <S>/<src>/../truth/truth.json to one TSV row per run (requests, USD, output and thinking tokens, thinking USD share, answer, verdict, correct?) and a per-arm table on stdout.
# usage: w08f_arms_table.py S TASK:SRCDIR [TASK:SRCDIR ...]   e.g. A:src B:srcB. Correct = verdict is not SUPPORTED and recomputed_total_usd within 0.0005 of truth.true_total. Thinking USD = thinking tokens x output price + each later request's re-read of them (first at the recorded write rate, the rest at 0.10 per MTok) [ESTIMATE: assumes the carried thinking block is its thinking_tokens].
import sys, os, re, json, glob, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w08f_requests import parse
S = sys.argv[1]; out = []
for spec in sys.argv[2:]:
    task, src = spec.split(":"); truth = json.load(open(os.path.join(S, src.replace("src", "src") , "..", "truth", "truth.json"))) if False else json.load(open(os.path.join(S, src, "truth", "truth.json")))
    for f in sorted(glob.glob(os.path.join(S, "runs", task + "-*-*.jsonl"))):
        label = os.path.basename(f)[:-6]; arm = label.split("-")[1]
        rows, _ = parse(f)
        res = None
        for l in open(f):
            try: d = json.loads(l)
            except Exception: continue
            if d.get("type") == "result": res = d
        if not res: continue
        txt = res.get("result", "") or ""
        m = re.search(r"recomputed_total_usd:\s*\$?([0-9.]+)", txt); v = re.search(r"verdict:\s*(\w+)", txt)
        ans = float(m.group(1).rstrip(".")) if m else None; ver = v.group(1) if v else None
        ok = (ver is not None and ver != "SUPPORTED" and ans is not None and abs(ans - truth["true_total"]) <= 0.0005)
        usd = sum(r["usd"] for r in rows); outt = sum(r["out"] or 0 for r in rows); th = sum(r["think"] or 0 for r in rows)
        thusd = 0.0
        for k, r in enumerate(rows):
            t = r["think"] or 0
            thusd += t * 10 / 1e6
            for j in range(k + 1, len(rows)):
                thusd += t * (0.0000040 if j == k + 1 else 0.0000001)
        out.append(dict(task=task, arm=arm, label=label, req=len(rows), usd=usd, cost=res.get("total_cost_usd"), out=outt, think=th, thusd=thusd, ans=ans, ver=ver, ok=ok, ctxmax=max(r["ctx"] for r in rows)))
print("task\tarm\tlabel\trequests\tusd_stream\tusd_result\tout_tokens\tthinking_tokens\tthinking_usd\tanswer\tverdict\tcorrect")
for r in out: print("%s\t%s\t%s\t%d\t%.4f\t%.4f\t%d\t%d\t%.4f\t%s\t%s\t%s" % (r["task"], r["arm"], r["label"], r["req"], r["usd"], r["cost"] or 0, r["out"], r["think"], r["thusd"], r["ans"], r["ver"], r["ok"]))
print()
print("task\tarm\tn\tmean_usd\tmin-max\tmean_requests\tmean_out\tmean_thinking\tthinking_usd/usd\tcorrect")
for task in sorted({r["task"] for r in out}):
    for arm in ("default", "low", "medium", "high"):
        g = [r for r in out if r["task"] == task and r["arm"] == arm]
        if not g: continue
        u = [r["usd"] for r in g]
        print("%s\t%s\t%d\t%.4f\t%.4f-%.4f\t%.1f\t%.0f\t%.0f\t%.1f%%\t%d/%d" % (task, arm, len(g), st.mean(u), min(u), max(u), st.mean(r["req"] for r in g), st.mean(r["out"] for r in g), st.mean(r["think"] for r in g), 100 * sum(r["thusd"] for r in g) / sum(u), sum(r["ok"] for r in g), len(g)))
