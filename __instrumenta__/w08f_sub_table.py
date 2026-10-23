# Summarises the subagent-dispatch runs of w08-f (a Haiku parent calls the Agent tool on a Sonnet 5.5 test agent): from <S>/runs/<PREFIX>-<arm>-<rep>.jsonl result records (modelUsage per model) and the subagent transcripts under ~/.claude/projects (request count only) to one row per run and a per-arm table on stdout.
# usage: w08f_sub_table.py S [PREFIX=S] [TRUTH.json]   Sonnet columns are the subagent alone (the parent is Haiku). thinking = modelUsage.thinkingTokens (platform-reported). With a truth file (verifier task): correct = verdict is not SUPPORTED and recomputed_total_usd within 0.0005 of true_total.
import sys, os, re, json, glob, collections, statistics as st
S = sys.argv[1]; PRE = sys.argv[2] if len(sys.argv) > 2 else "S"; TR = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
rows = []
for f in sorted(glob.glob(os.path.join(S, "runs", PRE + "-*-*.jsonl"))):
    label = os.path.basename(f)[:-6]; arm = label.split("-")[1]; res = None; alltxt = []
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        if d.get("type") == "result": res = d; alltxt.append(d.get("result", "") or "")   # a background subagent makes the parent print several result records
    if not res: continue
    sid = res["session_id"]
    sub = glob.glob(os.path.expanduser("~/.claude/projects/*-w08-explorer-w08-f-work-%s/%s/subagents/*.jsonl" % (label, sid)))
    ids = set()
    for sf in sub:
        for l in open(sf):
            try: m = json.loads(l).get("message") or {}
            except Exception: continue
            if m.get("role") == "assistant" and m.get("id"): ids.add(m["id"])
    txt = "\n".join(alltxt)
    ma = re.search(r"recomputed_total_usd:\s*\$?([0-9.]+)", txt); mv = re.search(r"verdict:\s*\**\s*(\w+)", txt)
    ans = float(ma.group(1).rstrip(".")) if ma else None; ver = mv.group(1) if mv else None
    ok = None
    if TR: ok = bool(ver and ver != "SUPPORTED" and ans is not None and abs(ans - TR["true_total"]) <= 0.0005)
    mu = res.get("modelUsage", {}); s = next((v for k, v in mu.items() if "sonnet" in k), None); h = next((v for k, v in mu.items() if "haiku" in k), None)
    rows.append(dict(label=label, arm=arm, req=len(ids), ans=ans, ver=ver, ok=ok, out=s and s["outputTokens"], think=s and s.get("thinkingTokens"), usd=s and s["costUSD"], husd=h and h["costUSD"], total=res.get("total_cost_usd")))
print("run\tarm\tsubagent_requests\tanswer\tverdict\tcorrect\tsonnet_out\tsonnet_thinking\tsonnet_usd\thaiku_usd\ttotal_usd")
for r in rows: print("%s\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (r["label"], r["arm"], r["req"], r["ans"], r["ver"], r["ok"], r["out"], r["think"], "%.4f" % r["usd"] if r["usd"] is not None else None, "%.4f" % r["husd"] if r["husd"] is not None else None, "%.4f" % r["total"]))
print("\narm\tn\tmean_subagent_requests\tmean_sonnet_out\tmean_thinking\tmean_sonnet_usd\tmin-max_usd\tcorrect")
by = collections.defaultdict(list)
for r in rows:
    if r["usd"] is not None: by[r["arm"]].append(r)
for a in ("default", "low", "medium", "high", "max", "S"):
    g = by.get(a)
    if not g: continue
    print("%s\t%d\t%.1f\t%.0f\t%.0f\t%.4f\t%.4f-%.4f\t%s" % (a, len(g), st.mean(x["req"] for x in g), st.mean(x["out"] for x in g), st.mean(x["think"] or 0 for x in g), st.mean(x["usd"] for x in g), min(x["usd"] for x in g), max(x["usd"] for x in g), ("%d/%d" % (sum(1 for x in g if x["ok"]), len(g))) if TR else "-"))
