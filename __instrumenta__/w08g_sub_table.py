# Summarises the w08-g batching-line runs: from <S>/runs/<label>.jsonl (result record of the Haiku parent) and the Sonnet subagent's transcript under ~/.claude/projects to one row per run (requests, tool calls, calls per request, request shape, USD of the subagent recomputed from usage at list price, correctness against truth.json) and one row per arm.
# usage: w08g_sub_table.py S TRUTH.json [PREFIX=V] [out.tsv]   (a request = a distinct assistant message id; correct = verdict is not SUPPORTED and recomputed total within 0.005 of true_total)
import sys, os, re, json, glob, collections, statistics as st
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L
S = sys.argv[1]; TR = json.load(open(sys.argv[2])); PRE = sys.argv[3] if len(sys.argv) > 3 else "V"; OUT = sys.argv[4] if len(sys.argv) > 4 else None
rows = []
for f in sorted(glob.glob(os.path.join(S, "runs", PRE + "-*-*.jsonl"))):
    label = os.path.basename(f)[:-6]; arm = label.split("-")[1]; res = None; alltxt = []
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        if d.get("type") == "result": res = d; alltxt.append(d.get("result", "") or "")   # a background subagent makes the parent print several result records
    if not res: continue
    sid = res["session_id"]
    sub = glob.glob(os.path.expanduser("~/.claude/projects/*explorer-w08-g*-work-%s/%s/subagents/*.jsonl" % (label, sid)))
    msgs = collections.OrderedDict(); first_ts = last_ts = None
    for sf in sub:
        for l in open(sf):
            try: r = json.loads(l)
            except Exception: continue
            m = r.get("message") or {}
            if r.get("type") == "assistant" and m.get("id"):
                e = msgs.setdefault(m["id"], {"u": {}, "calls": [], "model": m.get("model")})
                L.merge_usage(e["u"], m.get("usage") or {})
                for b in m.get("content") or []:
                    if b.get("type") == "tool_use": e["calls"].append(b["name"])
    reqs = list(msgs.values())
    usd = sum(L.message_usd(e["model"], e["u"]) or 0 for e in reqs)
    ncalls = sum(len(e["calls"]) for e in reqs)
    shape = ",".join(str(len(e["calls"])) for e in reqs)
    cr = sum(int(e["u"].get("cache_read_input_tokens") or 0) for e in reqs)
    txt = "\n".join(alltxt)
    ma = re.search(r"recomputed_total_usd:\s*\$?([0-9.,]+)", txt); mv = re.search(r"verdict:\s*\**\s*(\w+)", txt)
    ans = float(ma.group(1).rstrip(".").replace(",", "")) if ma else None; ver = mv.group(1) if mv else None
    ok = bool(ver and ver != "SUPPORTED" and ans is not None and abs(ans - TR["true_total"]) <= 0.005)
    if "wrong" in TR:   # read-only count task: answer is the set of wrong files
        mw = re.findall(r"wrong_files:\s*([^\n]*)", txt); got = set(re.findall(r"shard_\d+\.csv", mw[-1])) if mw else set()
        ok = bool(ver and ver != "SUPPORTED" and got == set(TR["wrong"])); ans = ",".join(sorted(got))
    mu = res.get("modelUsage", {}); s = next((v for k, v in mu.items() if "sonnet" in k), None); h = next((v for k, v in mu.items() if "haiku" in k), None)
    rows.append(dict(label=label, arm=arm, req=len(reqs), calls=ncalls, cpr=ncalls / max(1, len(reqs)), shape=shape, cr=cr, ans=ans, ver=ver, ok=ok, out=s and s["outputTokens"], think=s and s.get("thinkingTokens"), usd=usd, mu_usd=s and s["costUSD"], husd=h and h["costUSD"]))
hdr = "run\tarm\trequests\ttool_calls\tcalls_per_request\tcalls_by_request\tcache_read_tokens\tanswer\tverdict\tcorrect\tsonnet_out\tsonnet_thinking\tsubagent_usd_recomputed\tsonnet_usd_result_record\thaiku_usd"
lines = [hdr] + ["%s\t%s\t%d\t%d\t%.2f\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%.4f\t%s\t%s" % (r["label"], r["arm"], r["req"], r["calls"], r["cpr"], r["shape"], r["cr"], r["ans"], r["ver"], r["ok"], r["out"], r["think"], r["usd"], "%.4f" % r["mu_usd"] if r["mu_usd"] is not None else None, "%.4f" % r["husd"] if r["husd"] is not None else None) for r in rows]
lines.append("")
lines.append("arm\tn\tmean_requests\tmean_tool_calls\tmean_calls_per_request\tmean_cache_read_tokens\tmean_thinking\tmean_subagent_usd\tmin-max_usd\tcorrect")
by = collections.defaultdict(list)
for r in rows: by[r["arm"]].append(r)
for a, g in by.items():
    lines.append("%s\t%d\t%.2f\t%.2f\t%.2f\t%.0f\t%.0f\t%.4f\t%.4f-%.4f\t%d/%d" % (a, len(g), st.mean(x["req"] for x in g), st.mean(x["calls"] for x in g), st.mean(x["cpr"] for x in g), st.mean(x["cr"] for x in g), st.mean(x["think"] or 0 for x in g), st.mean(x["usd"] for x in g), min(x["usd"] for x in g), max(x["usd"] for x in g), sum(1 for x in g if x["ok"]), len(g)))
print("\n".join(lines))
if OUT: open(OUT, "w").write("\n".join(lines) + "\n")
