# Builds the loop-time, calls-per-message, batching-saving, cache-gap, large-output and denial tables from the per-agent JSON that w07b_loop_parse.py wrote; inputs: the parse output folder; outputs: <outdir>/tables.md plus per_worker.tsv, merges.tsv, tool_latency.tsv, big_results.tsv. Usage: w07b_loop_tables.py PARSED_DIR OUTDIR
import json, sys, os, glob, statistics as st, collections
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L

parsed, outdir = sys.argv[1:3]
os.makedirs(outdir, exist_ok=True)
A = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(parsed, "*.json")))]
W = [a for a in A if a["agent"] != "PI"]
PI = [a for a in A if a["agent"] == "PI"]
OUT = []


def P(s=""):
    OUT.append(s)


def med(x):
    x = [v for v in x if v is not None]
    return st.median(x) if x else float("nan")


def pct(x, q):
    x = sorted(v for v in x if v is not None)
    return x[min(len(x) - 1, int(q * len(x)))] if x else float("nan")


def price(model):
    return L.PRICES.get((model or "").rsplit("-20", 1)[0], L.PRICES["claude-sonnet-5-5"])


LONG = 120.0  # a tool phase over this many seconds is a long run, not loop overhead

# ---------------------------------------------------------------- model request time (waves with request timestamps)
P("## model request time (request sent to last assistant block; first-block time = request sent to first block), requests that end in a tool call")
P("")
P("| set | requests | model_s median | p90 | time to first block median | of which requests with no thinking block (n, median) | client gap after a tool result, median / p90 (gaps under 5 s) |")
P("|:--|--:|--:|--:|--:|--:|--:|")
nothink_all, gap_all_ = [], []
for name, S in (("workers w5", [a for a in W if a["label"] == "w5"]), ("workers w6", [a for a in W if a["label"] == "w6"]), ("PI w5", [a for a in PI if a["label"] == "w5"]), ("PI w6", [a for a in PI if a["label"] == "w6"])):
    ts_ = [t for a in S for t in a["turns"] if t["model_s"] is not None and t["ncalls"] > 0]
    nt = [t["ttfb_s"] for t in ts_ if t["think_ms"] == 0]
    gp = [t["gap_prev_s"] for a in S for t in a["turns"] if t["gap_prev_s"] is not None and t["gap_prev_s"] < 5]
    if name.startswith("workers"):
        nothink_all += nt; gap_all_ += gp
    P("| %s | %d | %.2f | %.2f | %.2f | %d, %.2f | %.2f / %.2f |" % (name, len(ts_), med([t["model_s"] for t in ts_]), pct([t["model_s"] for t in ts_], .9), med([t["ttfb_s"] for t in ts_]), len(nt), med(nt), med(gp), pct(gp, .9)))
FIX_FLOOR = med(nothink_all) + med(gap_all_)
P("")
P("fixed cost of one more request used below: floor = median time to first block of workers' requests with no thinking (%.2f s) + median client gap (%.2f s) = %.2f s." % (med(nothink_all), med(gap_all_), FIX_FLOOR))
P("")

# ---------------------------------------------------------------- per agent time decomposition
rows = []
for a in A:
    T = a["turns"]
    if not T:
        continue
    t0 = T[0]["R"] or T[0]["first"]
    end = max([t["E"] for t in T] + [t["E"] + (t["tool_s"] or 0) for t in T])
    wall = end - t0
    d = dict(first=0.0, model=0.0, gap=0.0, pre=0.0, tool=0.0, long=0.0, wait=0.0)
    for i, t in enumerate(T):
        if i == 0:
            d["first"] += t["model_s"] if t["model_s"] is not None else (t["E"] - t["first"])
        else:
            if t["wait_s"] is not None:
                d["wait"] += t["wait_s"]
                if t["model_s"] is not None:
                    d["model"] += t["model_s"]
            elif t["model_s"] is not None and t["gap_prev_s"] is not None and t["gap_prev_s"] > 5 and t["new_prompt"]:
                d["model"] += t["model_s"]; d["wait"] += t["gap_prev_s"]   # idle until a message arrived mid-run
            elif t["model_s"] is not None and t["gap_prev_s"] is not None:
                d["model"] += t["model_s"]; d["gap"] += t["gap_prev_s"]
            elif t["pre_s"] is not None and t["pre_s"] > 60 and t["new_prompt"]:
                d["wait"] += t["pre_s"]   # wave 4: no request timestamps; a message arrived and the gap is over 60 s: counted as idle
            elif t["pre_s"] is not None:
                d["pre"] += t["pre_s"]
        if t["tool_s"] is not None:
            if t["tool_s"] > LONG:
                d["long"] += t["tool_s"]
            else:
                d["tool"] += t["tool_s"]
    n = len(T); calls = sum(t["ncalls"] for t in T)
    rows.append(dict(label=a["label"], agent=a["agent"], name=a["name"], type=a["type"], n=n, calls=calls, wall=wall, usd=sum(t["usd"] for t in T), has_req=a["has_req_ts"],
                     one=sum(1 for t in T if t["ncalls"] == 1), multi=sum(1 for t in T if t["ncalls"] >= 2), zero=sum(1 for t in T if t["ncalls"] == 0), **d))

# ---------------------------------------------------------------- tables: time split per wave
P("## where a worker's wall time goes (sums over workers, seconds)")
P("")
P("`first` = model time of the first request; `model` = request sent to last assistant block (waves 5-6); `gap` = last tool result to the next request being sent (client side: hooks, reminders, request build); `pre` = model + gap together (wave 4 has no request timestamps); `tool` = last assistant block to last tool result, phases up to %d s; `long` = tool phases over %d s; `wait` = idle until a message arrived: after a turn that ended without a tool call, or a gap over 5 s after a tool result with a message arriving (a worker waiting on a peer); `resid` = wall minus the rest." % (LONG, LONG))
P("")
P("| wave | workers | wall | first | model | gap | pre (model+gap) | tool <=120 s | long tool | wait | resid |")
P("|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for lab in ("w4", "w5", "w6", "all"):
    R = [r for r in rows if r["agent"] != "PI" and (lab == "all" or r["label"] == lab)]
    s = {k: sum(r[k] for r in R) for k in ("wall", "first", "model", "gap", "pre", "tool", "long", "wait")}
    resid = s["wall"] - sum(s[k] for k in ("first", "model", "gap", "pre", "tool", "long", "wait"))
    P("| %s | %d | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f |" % (lab, len(R), s["wall"], s["first"], s["model"], s["gap"], s["pre"], s["tool"], s["long"], s["wait"], resid))
P("")
P("same, as shares of wall (waves 5-6 pooled; wave 4's pre split by the waves 5-6 model/gap ratio is not attempted):")
R = [r for r in rows if r["agent"] != "PI" and r["label"] in ("w5", "w6")]
s = {k: sum(r[k] for r in R) for k in ("wall", "first", "model", "gap", "pre", "tool", "long", "wait")}
P("")
P("| part | seconds | share of wall |")
P("|:--|--:|--:|")
for k in ("first", "model", "gap", "tool", "long", "wait"):
    P("| %s | %.0f | %.1f%% |" % (k, s[k], 100 * s[k] / s["wall"]))
P("| model + first (all model request time) | %.0f | %.1f%% |" % (s["model"] + s["first"], 100 * (s["model"] + s["first"]) / s["wall"]))
act = s["wall"] - s["wait"] - s["long"]
P("")
P("same without idle waits and long tool phases (the loop proper, %.0f s): model + first %.1f%%, client gap %.1f%%, tool phases <=120 s %.1f%%." % (act, 100 * (s["model"] + s["first"]) / act, 100 * s["gap"] / act, 100 * s["tool"] / act))
P("")
P("same, all three waves, wave 4 counted with its model+gap together as `pre` (%.0f s without waits and long phases): model+gap %.1f%%, tool %.1f%%." % (
    sum(r["wall"] - r["wait"] - r["long"] for r in rows if r["agent"] != "PI"),
    100 * sum(r["first"] + r["model"] + r["gap"] + r["pre"] for r in rows if r["agent"] != "PI") / sum(r["wall"] - r["wait"] - r["long"] for r in rows if r["agent"] != "PI"),
    100 * sum(r["tool"] for r in rows if r["agent"] != "PI") / sum(r["wall"] - r["wait"] - r["long"] for r in rows if r["agent"] != "PI")))
P("")

# ---------------------------------------------------------------- per-call latency by class
lat = collections.defaultdict(list)
lat_single = collections.defaultdict(list)
cl_count = collections.Counter()
pdc = collections.Counter()
for a in W:
    for t in a["turns"]:
        for c in t["calls"]:
            key = c["name"] if c["name"] != "Bash" else ("Bash[classifier]" if c["pd"] and c["pd"].endswith("classifier") else "Bash[mode/rule/none]")
            if c["lat"] is not None:
                lat[key].append(c["lat"])
                if t["ncalls"] == 1:
                    lat_single[key].append(c["lat"])
            if c["pd"]:
                pdc[(a["label"], c["pd"])] += 1
            if c["name"] == "Bash" and c["pd"] and c["pd"].endswith("classifier"):
                cl_count[a["label"]] += 1
P("## tool-phase latency per call (block complete to its result record), workers, single-call turns only unless noted")
P("")
P("| class | n single | median s | p90 s | p99 s | n all calls | median s (all) |")
P("|:--|--:|--:|--:|--:|--:|--:|")
with open(os.path.join(outdir, "tool_latency.tsv"), "w") as fh:
    fh.write("class\tn_single\tmedian\tp90\tp99\tn_all\tmedian_all\n")
    for k in sorted(lat, key=lambda k: -len(lat[k])):
        if len(lat_single[k]) < 5:
            continue
        vals = (k, len(lat_single[k]), med(lat_single[k]), pct(lat_single[k], 0.9), pct(lat_single[k], 0.99), len(lat[k]), med(lat[k]))
        P("| %s | %d | %.2f | %.2f | %.1f | %d | %.2f |" % vals)
        fh.write("\t".join(str(v) for v in vals) + "\n")
P("")
# trivial commands, classifier vs not
triv = collections.defaultdict(list)
for a in W:
    for t in a["turns"]:
        if t["ncalls"] == 1:
            c = t["calls"][0]
            if c["name"] == "Bash" and c["cmd0"] in ("ls", "cat", "head", "tail", "wc", "git", "grep", "sed", "echo", "date", "pwd", "stat", "test", "cd") and c["chars"] < 3000 and c["lat"] is not None:
                triv[("classifier" if c["pd"] and c["pd"].endswith("classifier") else "other")].append(c["lat"])
P("trivial single Bash calls (first word ls/cat/head/tail/wc/git/grep/sed/echo/date/pwd/stat/test/cd, result under 3000 chars): decided by classifier: n = %d, median %.2f s, p10 %.2f, p90 %.2f; decided by mode/rule/none: n = %d, median %.2f s, p10 %.2f, p90 %.2f." % (
    len(triv["classifier"]), med(triv["classifier"]), pct(triv["classifier"], .1), pct(triv["classifier"], .9), len(triv["other"]), med(triv["other"]), pct(triv["other"], .1), pct(triv["other"], .9)))
P("")
P("permission decisions on workers' tool results (label / decision/source/reasonType: count):")
P("")
P("| wave | decision/source/reasonType | n |")
P("|:--|:--|--:|")
for (lab, d), n in sorted(pdc.items()):
    P("| %s | %s | %d |" % (lab, d, n))
P("")
# multi-call concurrency
P("### do several calls in one message overlap? tool phase of turns with k calls, workers")
P("")
P("| calls in message | n turns | median tool_s | p90 | median of (slowest result - fastest result) |")
P("|--:|--:|--:|--:|--:|")
for k in (1, 2, 3, 4):
    ts_ = [t["tool_s"] for a in W for t in a["turns"] if t["ncalls"] == k and t["tool_s"] is not None]
    sp = []
    for a in W:
        for t in a["turns"]:
            if t["ncalls"] == k and k >= 2:
                ls = [c["lat"] for c in t["calls"] if c["lat"] is not None]
                if len(ls) == k:
                    sp.append(max(ls) - min(ls))
    P("| %d | %d | %.2f | %.2f | %s |" % (k, len(ts_), med(ts_), pct(ts_, .9), "%.2f" % med(sp) if sp else "-"))
P("")

# ---------------------------------------------------------------- calls per message
P("## tool calls per assistant message (one message = one API request)")
P("")
P("| set | requests | 0 calls | 1 call | 2 calls | 3-4 | 5+ | calls | calls per request | share of requests with 1 call among those with >=1 | share of calls sent in a multi-call message |")
P("|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for name, S in (("workers w4", [a for a in W if a["label"] == "w4"]), ("workers w5", [a for a in W if a["label"] == "w5"]), ("workers w6", [a for a in W if a["label"] == "w6"]), ("workers all", W),
                ("PI w4", [a for a in PI if a["label"] == "w4"]), ("PI w5", [a for a in PI if a["label"] == "w5"]), ("PI w6", [a for a in PI if a["label"] == "w6"])):
    c = collections.Counter(min(t["ncalls"], 5) if t["ncalls"] < 3 else (3 if t["ncalls"] <= 4 else 5) for a in S for t in a["turns"])
    n = sum(c.values()); calls = sum(t["ncalls"] for a in S for t in a["turns"])
    multi_calls = sum(t["ncalls"] for a in S for t in a["turns"] if t["ncalls"] >= 2)
    with1 = c[1] + c[2] + c[3] + c[5]
    P("| %s | %d | %d | %d | %d | %d | %d | %d | %.2f | %.1f%% | %.1f%% |" % (name, n, c[0], c[1], c[2], c[3], c[5], calls, calls / n, 100 * c[1] / with1, 100 * multi_calls / calls))
P("")
# by tool name
cn = collections.Counter(); cn_multi = collections.Counter()
for a in W:
    for t in a["turns"]:
        for c in t["calls"]:
            cn[c["name"]] += 1
            if t["ncalls"] >= 2:
                cn_multi[c["name"]] += 1
P("calls by tool (workers): " + ", ".join("%s %d (%.0f%% in multi-call messages)" % (k, v, 100 * cn_multi[k] / v) for k, v in cn.most_common(12)))
P("")

# ---------------------------------------------------------------- batching
CAP = 8


def merge_walk(a, strict):
    """Greedy: absorb a turn into the batch before it when both are read-only (or both file writes to different paths)
    and no call of the absorbed turn first met a token in a result of the batch (loose); strict also needs every call of the
    absorbed turn to name at least one specific token and no unseen token. Returns list of dicts, one per absorbed turn."""
    T = a["turns"]
    s = None  # batch start index into T
    batch_cls = None; batch_paths = set(); batch_calls = 0; batch_tool = 0.0
    absorbed = []
    for j, t in enumerate(T):
        classes = {c["name"] if c["cls"] == "F" else c["cls"] for c in t["calls"]}
        kind = None
        if t["ncalls"] > 0:
            ks = {c["cls"] for c in t["calls"]}
            kind = ks.pop() if len(ks) == 1 else "mixed"
        ok_start = kind in ("R", "F")
        can = False
        if s is not None and j > 0 and ok_start and kind == batch_cls and t["wait_s"] is None and not t["new_prompt"]:
            prev = T[j - 1]
            if prev["ncalls"] > 0 and prev["missing_results"] == 0 and not any(c["err"] for tt in T[s:j] for c in tt["calls"]) and batch_calls + t["ncalls"] <= CAP:
                dep = any(d >= s for c in t["calls"] for d in c["dep_idx"]) or any(c["jac"] >= 0.6 for c in t["calls"])   # a call needing a schema a ToolSearch of the batch loads, or a near-copy of the previous call (a retry or refinement)
                if not dep:
                    if kind == "F":
                        ps = [c["path"] for c in t["calls"]]
                        can = all(p and p not in batch_paths for p in ps) and len(set(ps)) == len(ps)
                    else:
                        can = True
                    if can and strict:
                        can = all(c["ntok"] >= 1 and c["n_unseen"] == 0 for c in t["calls"])
        if can:
            absorbed.append(dict(j=j, turn=t, overlap=min(t["tool_s"] or 0.0, batch_tool)))
            batch_calls += t["ncalls"]; batch_tool = max(batch_tool, t["tool_s"] or 0.0)
            batch_paths |= {c["path"] for c in t["calls"]}
        else:
            if ok_start:
                s = j; batch_cls = kind; batch_calls = t["ncalls"]; batch_tool = t["tool_s"] or 0.0
                batch_paths = {c["path"] for c in t["calls"]}
            else:
                s = None
    return absorbed


def saving(absorbed, a):
    """(requests, floor s, mid s, high s, overlap s, USD reads, USD reads+output) of the absorbed turns. floor = FIX_FLOOR per request;
    mid = time to first block + client gap of the request itself (floor when the wave has no request timestamps); high = the whole request
    (model time + client gap; wave 4: model + gap together); overlap = tool phase that runs under the batch's longest one."""
    req = len(absorbed)
    floor = mid = high = ov = 0.0
    usd_lo = usd_hi = 0.0
    for x in absorbed:
        t = x["turn"]; p = price(t["model"])
        floor += FIX_FLOOR
        if t["ttfb_s"] is not None and t["gap_prev_s"] is not None:
            g = t["gap_prev_s"] if t["gap_prev_s"] < 5 else 0.0
            mid += max(FIX_FLOOR, t["ttfb_s"] + g); high += t["model_s"] + g
        else:
            mid += FIX_FLOOR; high += t["pre_s"] if t["pre_s"] is not None else FIX_FLOOR
        ov += x["overlap"] if x["overlap"] <= LONG else 0
        lo = (t["cr"] * p[2] + t["inp"] * p[0]) / 1e6
        usd_lo += lo; usd_hi += lo + t["out"] * p[1] / 1e6
    return req, floor, mid, high, ov, usd_lo, usd_hi


P("## requests that independent calls could have saved (ESTIMATE; heuristic dependency test)")
P("")
P("Rule: consecutive turns merge into one message when the absorbed turn's calls are all read-only (Read, Glob, Grep, ToolSearch, colgrep, Bash with only read-only words and no redirect) like the batch before them, or all file Write/Edit to distinct paths; no call of the absorbed turn contains a path-like token that first appeared in a tool result of the batch; no call a near-copy (word overlap 0.6 or more) of the previous turn's call (a refinement), none needing the schema of a deferred tool that a ToolSearch of the batch loads; no error result in the batch; no message arrived in between; at most %d calls per message. `strict` also needs each absorbed call to name at least one path-like token and none unseen anywhere before. Fixed cost of a request: see the line above." % CAP)
P("")
mt = open(os.path.join(outdir, "merges.tsv"), "w")
mt.write("label\tagent\tname\tturn\tkind\tn_calls\ttool_names\tfloor_s\tstrict\n")
res = {}
for mode in ("loose", "strict"):
    for a in W:
        ab = merge_walk(a, mode == "strict")
        res[(mode, a["label"], a["agent"])] = (ab, saving(ab, a))
for (mode, lab, ag), (ab, sv) in res.items():
    if mode == "loose":
        a = next(x for x in W if x["label"] == lab and x["agent"] == ag)
        strict_set = {x["j"] for x in res[("strict", lab, ag)][0]}
        for x in ab:
            mt.write("%s\t%s\t%s\t%d\t%s\t%d\t%s\t%.2f\t%d\n" % (lab, ag, a["name"], x["j"], "R" if x["turn"]["calls"][0]["cls"] == "R" else "F", x["turn"]["ncalls"], ",".join(c["name"] + (":" + c["cmd0"] if c["cmd0"] else "") for c in x["turn"]["calls"]), 0.0, int(x["j"] in strict_set)))
mt.close()
P("| wave | mode | workers' requests | requests saved | share | seconds floor | seconds mid | seconds high | + tool overlap | USD (cache reads of the saved requests) | USD (+ their output tokens) | worker wall (s) | mid share of wall |")
P("|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for mode in ("loose", "strict"):
    for lab in ("w4", "w5", "w6", "all"):
        S = [a for a in W if lab == "all" or a["label"] == lab]
        nreq = sum(len(a["turns"]) for a in S)
        tot = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for a in S:
            sv = res[(mode, a["label"], a["agent"])][1]
            tot = [x + y for x, y in zip(tot, sv)]
        wall = sum(r["wall"] for r in rows if r["agent"] != "PI" and (lab == "all" or r["label"] == lab))
        P("| %s | %s | %d | %d | %.1f%% | %.0f | %.0f | %.0f | %.0f | %.2f | %.2f | %.0f | %.1f%% |" % (lab, mode, nreq, tot[0], 100 * tot[0] / nreq, tot[1], tot[2], tot[3], tot[4], tot[5], tot[6], wall, 100 * tot[2] / wall))
P("")
tot_usd = sum(r["usd"] for r in rows if r["agent"] != "PI")
P("workers' list-price spend in the same transcripts: USD %.2f; formula for the USD columns: sum over saved requests of (cache_read_tokens x read price + uncached input tokens x input price) / 1e6 (output tokens are kept in the merged message for the `+output` column they are saved). Prices from scripts/lab_status.py PRICES at the model of the request." % tot_usd)
P("")
# what pairs get merged
pc = collections.Counter()
for (mode, lab, ag), (ab, sv) in res.items():
    if mode != "loose":
        continue
    a = next(x for x in W if x["label"] == lab and x["agent"] == ag)
    for x in ab:
        T = a["turns"]
        pc[(",".join(sorted({c["name"] + (":" + c["cmd0"] if c["name"] == "Bash" else "") for c in T[x["j"] - 1]["calls"]})), ",".join(sorted({c["name"] + (":" + c["cmd0"] if c["name"] == "Bash" else "") for c in x["turn"]["calls"]})))] += 1
P("most common (previous turn's calls -> absorbed turn's calls), loose:")
P("")
P("| previous | absorbed | n |")
P("|:--|:--|--:|")
for (p_, q_), n in pc.most_common(12):
    P("| %s | %s | %d |" % (p_, q_, n))
P("")

# ---------------------------------------------------------------- per worker table
with open(os.path.join(outdir, "per_worker.tsv"), "w") as fh:
    fh.write("label\tname\ttype\trequests\tcalls\tcalls_per_req\twall_s\tusd\tmodel_first_s\tgap_s\tpre_s\ttool_s\tlong_s\twait_s\tsaved_loose\tsaved_strict\tmid_s_loose\n")
    for r in sorted(rows, key=lambda r: (r["label"], r["name"])):
        if r["agent"] == "PI":
            continue
        ab, sv = res[("loose", r["label"], r["agent"])]
        ab2, sv2 = res[("strict", r["label"], r["agent"])]
        fh.write("\t".join(str(x) for x in (r["label"], r["name"], r["type"], r["n"], r["calls"], "%.2f" % (r["calls"] / r["n"]), "%.0f" % r["wall"], "%.2f" % r["usd"], "%.0f" % (r["first"] + r["model"]), "%.0f" % r["gap"], "%.0f" % r["pre"], "%.0f" % r["tool"], "%.0f" % r["long"], "%.0f" % r["wait"], sv[0], sv2[0], "%.1f" % sv[2])) + "\n")
Wr = [r for r in rows if r["agent"] != "PI"]
P("## per worker task")
P("")
P("| set | workers | requests per worker (median / p90 / max) | calls per worker (median / p90 / max) | wall s (median / p90 / max) | USD (median / max) |")
P("|:--|--:|:--|:--|:--|:--|")
for lab in ("w4", "w5", "w6", "all"):
    S = [r for r in Wr if lab == "all" or r["label"] == lab]
    P("| %s | %d | %d / %d / %d | %d / %d / %d | %.0f / %.0f / %.0f | %.2f / %.2f |" % (lab, len(S), med([r["n"] for r in S]), pct([r["n"] for r in S], .9), max(r["n"] for r in S),
        med([r["calls"] for r in S]), pct([r["calls"] for r in S], .9), max(r["calls"] for r in S), med([r["wall"] for r in S]), pct([r["wall"] for r in S], .9), max(r["wall"] for r in S), med([r["usd"] for r in S]), max(r["usd"] for r in S)))
P("")
P("by agent type (all waves): " + "; ".join("%s: n=%d, median requests %d, median wall %.0f s, median calls/request %.2f" % (
    ty, len(S), med([r["n"] for r in S]), med([r["wall"] for r in S]), med([r["calls"] / r["n"] for r in S])) for ty in sorted({r["type"] for r in Wr if r["type"]}) for S in [[r for r in Wr if r["type"] == ty]]))
P("")
P("### every worker (seconds; saved = requests merged, loose / strict)")
P("")
P("| wave | name | type | requests | calls | calls/req | wall | USD | model+first | gap | pre | tool | long tool | wait | saved loose | saved strict |")
P("|:--|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for r in sorted(Wr, key=lambda r: (r["label"], r["name"])):
    ab, sv = res[("loose", r["label"], r["agent"])]
    ab2, sv2 = res[("strict", r["label"], r["agent"])]
    P("| %s | %s | %s | %d | %d | %.2f | %.0f | %.2f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %d | %d |" % (r["label"], r["name"], (r["type"] or "").replace("murmuration:", ""), r["n"], r["calls"], r["calls"] / r["n"], r["wall"], r["usd"], r["first"] + r["model"], r["gap"], r["pre"], r["tool"], r["long"], r["wait"], sv[0], sv2[0]))
P("")

# ---------------------------------------------------------------- cache gaps for workers
P("## cache re-writes after gaps over 300 s (workers' 5-minute cache)")
P("")
P("| wave | requests after a gap over 300 s | misses (read under half of previous context) | tokens not read | USD over a read (tokens x (cache-write-5m - read price)) | longest gap s | share of worker spend |")
P("|:--|--:|--:|--:|--:|--:|--:|")
gaps_all = []
for lab in ("w4", "w5", "w6", "all"):
    n = nm = lost_t = 0; usd_x = 0.0; mx = 0; spend = 0.0
    for a in W:
        if lab != "all" and a["label"] != lab:
            continue
        spend += sum(t["usd"] for t in a["turns"])
        T = a["turns"]
        for k in range(1, len(T)):
            start = T[k]["R"] or T[k]["first"]
            g = start - T[k - 1]["E"] - (T[k - 1]["tool_s"] or 0)
            gap = start - T[k - 1]["E"]
            # a long tool phase is not an idle gap for the cache: the cache is refreshed only by requests, so use time between requests
            if T[k - 1]["R"] is not None and T[k]["R"] is not None:
                gap = T[k]["R"] - T[k - 1]["R"]
            if gap > 300:
                ctx_prev = T[k - 1]["cr"] + T[k - 1]["cw5"] + T[k - 1]["cw1"] + T[k - 1]["inp"]
                n += 1
                mx = max(mx, gap)
                if T[k]["cr"] < 0.5 * ctx_prev:
                    p = price(T[k]["model"]); lost = max(0, ctx_prev - T[k]["cr"])
                    nm += 1; lost_t += lost; usd_x += lost * (p[3] - p[2]) / 1e6
                    if lab == "all":
                        gaps_all.append((a["name"], a["label"], gap, ctx_prev, T[k]["cr"], T[k]["tool_s"], T[k - 1]["tool_s"]))
    P("| %s | %d | %d | %d | %.2f | %.0f | %.1f%% |" % (lab, n, nm, lost_t, usd_x, mx, 100 * usd_x / spend if spend else 0))
P("")
P("(gap = time between two requests of one worker, waves 5-6 from request timestamps; wave 4 has none, so its gap is the time between the previous message's last block and this message's first block)")
P("")
P("gaps behind misses (all waves): " + "; ".join("%s %s gap %.0f s, tool phase before it %s s" % (g[0], g[1], g[2], "%.0f" % g[6] if g[6] is not None else "-") for g in gaps_all[:12]))
P("")

# ---------------------------------------------------------------- large tool outputs
# calibration: tokens per character from context growth after single-call turns
xs, ys = [], []
for a in W:
    T = a["turns"]
    for k in range(len(T) - 1):
        if T[k]["ncalls"] == 1 and T[k]["calls"][0]["chars"] < 60000 and T[k + 1]["wait_s"] is None:
            c0 = T[k]["cr"] + T[k]["cw5"] + T[k]["cw1"] + T[k]["inp"]; c1 = T[k + 1]["cr"] + T[k + 1]["cw5"] + T[k + 1]["cw1"] + T[k + 1]["inp"]
            if c1 > c0 and T[k]["calls"][0]["chars"] > 0:
                xs.append(T[k]["calls"][0]["chars"]); ys.append(c1 - c0 - T[k]["out"])
sl, ic = np.polyfit(xs, ys, 1)
P("## tool outputs that every later request re-reads")
P("")
P("calibration: growth of context (cache read + write + input) from one request to the next, minus the assistant's output tokens, against the result's characters, single-call turns, n = %d: tokens = %.0f + %.3f x chars (so %.2f chars per token)." % (len(xs), ic, sl, 1 / sl))
P("")
big = []
tot_cr_usd = 0.0
for a in W:
    T = a["turns"]
    n = len(T)
    for t in T:
        p = price(t["model"]); tot_cr_usd += t["cr"] * p[2] / 1e6
    for k, t in enumerate(T):
        for c in t["calls"]:
            tok = c["chars"] * sl
            later = n - 1 - k
            p = price(t["model"])
            big.append((a["label"], a["name"], c["name"] + (":" + c["cmd0"] if c["cmd0"] else ""), c["chars"], tok, later, tok * later * p[2] / 1e6, c["head"]))
with open(os.path.join(outdir, "big_results.tsv"), "w") as fh:
    fh.write("label\tname\tcall\tchars\test_tokens\tlater_requests\treread_usd\thead\n")
    for b in sorted(big, key=lambda b: -b[6])[:60]:
        fh.write("\t".join(str(x) if not isinstance(x, float) else "%.3f" % x for x in b) + "\n")
P("| size class (chars) | results | estimated tokens | USD of re-reads by later requests (tokens x later requests x read price) | share of workers' cache-read USD (USD %.2f) |" % tot_cr_usd)
P("|:--|--:|--:|--:|--:|")
for lo, hi in ((0, 2000), (2000, 5000), (5000, 20000), (20000, 10 ** 9)):
    S = [b for b in big if lo <= b[3] < hi]
    P("| %d-%s | %d | %.0f | %.2f | %.1f%% |" % (lo, hi if hi < 10 ** 9 else "+", len(S), sum(b[4] for b in S), sum(b[6] for b in S), 100 * sum(b[6] for b in S) / tot_cr_usd))
P("")
P("five costliest re-reads: " + "; ".join("%s %s %s %d chars, %d later requests, USD %.3f" % (b[0], b[1], b[2], b[3], b[5], b[6]) for b in sorted(big, key=lambda b: -b[6])[:5]))
P("")

# ---------------------------------------------------------------- denials, errors, hooks
P("## errors, denials, hook time visible in the records")
P("")
P("| wave | tool results with is_error | calls rejected (decision reject) | requests with no assistant message | PreToolUse hook timeouts | SubagentStart hook records (sum ms / max ms) | PostToolBatch records (n, sum ms) |")
P("|:--|--:|--:|--:|--:|--:|--:|")
for lab in ("w4", "w5", "w6"):
    S = [a for a in W if a["label"] == lab]
    err = sum(1 for a in S for t in a["turns"] for c in t["calls"] if c["err"])
    rej = sum(1 for a in S for t in a["turns"] for c in t["calls"] if c["pd"] and c["pd"].startswith("reject"))
    nre = sum(a["n_requests_no_assistant"] for a in S)
    h = [x for a in S for x in a["hooks"]]
    to = sum(1 for x in h if x["timed_out"] == "True")
    ss = [x["ms"] for x in h if x["event"] == "SubagentStart"]
    pb = [x["ms"] for x in h if x["event"] == "PostToolBatch"]
    P("| %s | %d | %d | %d | %d | %d / %d | %d, %d |" % (lab, err, rej, nre, to, sum(ss), max(ss or [0]), len(pb), sum(pb)))
P("")
nrq = sum(len(a["turns"]) for a in W); ncalls = sum(t["ncalls"] for a in W for t in a["turns"])
P("workers: %d requests, %d tool calls. Hook durations in the records cover only SubagentStart and PostToolBatch (and one cancelled PreToolUse); PreToolUse/PostToolUse successes carry no record in these transcripts." % (nrq, ncalls))
P("")
# retry after error
rt = collections.Counter()
for a in W:
    T = a["turns"]
    for k in range(len(T) - 1):
        if any(c["err"] for c in T[k]["calls"]):
            rt[a["label"]] += 1
P("requests that follow a turn with at least one error result (a retry or a reaction): " + ", ".join("%s %d" % kv for kv in sorted(rt.items())))
P("")

# ---------------------------------------------------------------- by type, and where the tool time goes
P("## by agent type (all waves, workers): shares of wall")
P("")
P("| type | workers | wall s | requests | model+first | gap | pre (w4 only) | tool <=120 s | long tool | wait | requests saved (loose) |")
P("|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for ty in sorted({r["type"] for r in Wr if r["type"]}):
    S = [r for r in Wr if r["type"] == ty]
    wl = sum(r["wall"] for r in S)
    f = lambda k: sum(r[k] for r in S)
    sv_ = sum(res[("loose", r["label"], r["agent"])][1][0] for r in S)
    P("| %s | %d | %.0f | %d | %.1f%% | %.1f%% | %.1f%% | %.1f%% | %.1f%% | %.1f%% | %d |" % (ty.replace("murmuration:", ""), len(S), wl, f("n"), 100 * (f("first") + f("model")) / wl, 100 * f("gap") / wl, 100 * f("pre") / wl, 100 * f("tool") / wl, 100 * f("long") / wl, 100 * f("wait") / wl, sv_))
P("")
P("## where the tool phases go (workers, single-call turns, by tool and first word of a Bash command)")
P("")
P("| call | n | sum s (all phases) | sum s in phases over %d s | n over %d s | median s | share of all tool-phase seconds |" % (LONG, LONG))
P("|:--|--:|--:|--:|--:|--:|--:|")
agg = collections.defaultdict(list)
for a in W:
    for t in a["turns"]:
        if t["ncalls"] == 1 and t["tool_s"] is not None:
            c = t["calls"][0]
            agg[c["name"] if c["name"] != "Bash" else "Bash " + c["cmd0"]].append(t["tool_s"])
totall = sum(sum(v) for v in agg.values())
for k, v in sorted(agg.items(), key=lambda kv: -sum(kv[1]))[:14]:
    P("| %s | %d | %.0f | %.0f | %d | %.2f | %.1f%% |" % (k, len(v), sum(v), sum(x for x in v if x > LONG), sum(1 for x in v if x > LONG), med(v), 100 * sum(v) / totall))
P("")
P("Bash single-call latency by wave (classifier-decided, result under 3000 chars, first word in the trivial set): " + "; ".join(
    "%s n=%d median %.2f s p90 %.2f s" % (lab, len(v), med(v), pct(v, .9)) for lab in ("w4", "w5", "w6") for v in [[c["lat"] for a in W if a["label"] == lab for t in a["turns"] if t["ncalls"] == 1 for c in t["calls"] if c["name"] == "Bash" and c["pd"] and c["pd"].endswith("classifier") and c["cmd0"] in ("ls", "cat", "head", "tail", "wc", "git", "grep", "sed", "echo", "date", "pwd", "stat", "test", "cd") and c["chars"] < 3000 and c["lat"] is not None]]))
P("")
P("Read single-call latency (no classifier context in the record): median %.2f s, n %d; ToolSearch %.2f s, Write %.2f s." % (med(lat_single["Read"]), len(lat_single["Read"]), med(lat_single["ToolSearch"]), med(lat_single["Write"])))
nb = sum(1 for a in W for t in a["turns"] for c in t["calls"] if c["name"] == "Bash" and c["pd"] and c["pd"].endswith("classifier"))
P("")
P("classifier-decided Bash calls in the workers' records: %d (w4 %d, w5 %d, w6 %d). At the earlier measured 0.45-0.75 s each that is %.0f-%.0f s; at the trivial-call median above minus the Read median it is about %.0f s. Worker wall over all waves: %.0f s." % (
    nb, cl_count["w4"], cl_count["w5"], cl_count["w6"], 0.45 * nb, 0.75 * nb, nb * (med(triv["classifier"]) - med(lat_single["Read"])), sum(r["wall"] for r in Wr)))
P("")

# ---------------------------------------------------------------- batching inside one Bash call, thinking, errors, chunked waits
P("## calls already batched inside one Bash command; thinking time; what the errors were")
P("")
nb = [c["nseg"] for a in W for t in a["turns"] for c in t["calls"] if c["name"] == "Bash"]
P("Bash calls by number of statements (split on && ; newline): 1 statement %d, 2 %d, 3-5 %d, 6+ %d; share with 2 or more: %.1f%% of %d Bash calls; mean statements %.2f. (A statement chain is one tool call, one classifier call, one request.)" % (
    sum(1 for x in nb if x <= 1), sum(1 for x in nb if x == 2), sum(1 for x in nb if 3 <= x <= 5), sum(1 for x in nb if x >= 6), 100 * sum(1 for x in nb if x >= 2) / len(nb), len(nb), sum(nb) / len(nb)))
P("")
th = sum(t["think_ms"] for a in W for t in a["turns"] if t["model_s"] is not None) / 1000
ms_ = sum(t["model_s"] for a in W for t in a["turns"] if t["model_s"] is not None)
nthink = sum(1 for a in W if a["label"] != "w4" for t in a["turns"] if t["think_ms"] > 0)
P("thinking: %d of %d worker requests (waves 5-6) carry a thinking block with a recorded duration; thinkingDurationMs sums to %.0f s against %.0f s of model time (%.1f%%); wave 6 alone: %.0f s of %.0f s (%.1f%%)." % (
    nthink, sum(len(a["turns"]) for a in W if a["label"] != "w4"), th, ms_, 100 * th / ms_,
    sum(t["think_ms"] for a in W if a["label"] == "w6" for t in a["turns"]) / 1000, sum(t["model_s"] for a in W if a["label"] == "w6" for t in a["turns"] if t["model_s"] is not None),
    100 * sum(t["think_ms"] for a in W if a["label"] == "w6" for t in a["turns"]) / 1000 / sum(t["model_s"] for a in W if a["label"] == "w6" for t in a["turns"] if t["model_s"] is not None)))
P("")
eh = collections.Counter()
for a in W:
    for t in a["turns"]:
        for c in t["calls"]:
            if c["err"]:
                eh[(a["label"], c["name"], c["errh"][:45])] += 1
P("worker tool results with is_error, by wave, tool and first 45 characters (top 14):")
P("")
P("| wave | tool | start of the error text | n |")
P("|:--|:--|:--|--:|")
for (lab, nm_, h), n in eh.most_common(14):
    P("| %s | %s | %s | %d |" % (lab, nm_, h.replace("|", "/"), n))
P("")
ru = collections.defaultdict(lambda: [0, 0.0, 0.0]); allusd = collections.defaultdict(float); allreq = collections.Counter()
for a in W:
    T = a["turns"]
    allusd[a["label"]] += sum(t["usd"] for t in T); allreq[a["label"]] += len(T)
    for k in range(len(T) - 1):
        if any(c["err"] for c in T[k]["calls"]) and T[k + 1]["wait_s"] is None:
            ru[a["label"]][0] += 1; ru[a["label"]][1] += T[k + 1]["usd"]
            ru[a["label"]][2] += (T[k + 1]["model_s"] or T[k + 1]["pre_s"] or 0.0) + ((T[k + 1]["gap_prev_s"] or 0.0) if (T[k + 1]["gap_prev_s"] or 0) < 5 else 0.0)
P("requests that directly follow a turn with an error result (retry or reaction), and their cost: " + "; ".join("%s: %d of %d requests (%.1f%%), USD %.2f of %.2f (%.1f%%), %.0f s of model+gap time" % (
    lab, ru[lab][0], allreq[lab], 100 * ru[lab][0] / allreq[lab], ru[lab][1], allusd[lab], 100 * ru[lab][1] / allusd[lab], ru[lab][2]) for lab in ("w4", "w5", "w6")))
P("")
# chunked waits: a miss whose preceding tool phase was most of the gap
tot_save = 0.0; nn = 0; tot_miss = 0.0; allm = 0
for a in W:
    T = a["turns"]
    for k in range(1, len(T)):
        if T[k - 1]["R"] is not None and T[k]["R"] is not None:
            gap = T[k]["R"] - T[k - 1]["R"]
        else:
            gap = (T[k]["R"] or T[k]["first"]) - T[k - 1]["E"]
        if gap > 300:
            ctx_prev = T[k - 1]["cr"] + T[k - 1]["cw5"] + T[k - 1]["cw1"] + T[k - 1]["inp"]
            if T[k]["cr"] < 0.5 * ctx_prev:
                p = price(T[k]["model"]); extra = ctx_prev * (p[3] - p[2]) / 1e6
                tot_miss += extra; allm += 1
                if (T[k - 1]["tool_s"] or 0) >= 0.8 * gap and T[k - 1]["ncalls"] == 1:
                    chunks = int(gap // 270)
                    cost = chunks * (ctx_prev * p[2] / 1e6 + 150 * p[1] / 1e6)
                    tot_save += max(0.0, extra - cost); nn += 1
P("cache misses after a gap over 300 s: %d, USD %.2f over a read. Of them %d follow a single long tool call that filled at least 80%% of the gap; if each such wait had been cut into tool calls of 270 s (one extra request per 270 s: previous context at the read price + 150 output tokens), the saving would be USD %.2f (ESTIMATE; assumes the waiting command can be split, and that the model's extra requests are as small as 150 output tokens, which the Bash timeout of 270 s lets it be)." % (allm, tot_miss, nn, tot_save))
P("")

# ---------------------------------------------------------------- PI
P("## PI main thread, same split (seconds)")
P("")
P("| wave | requests | calls | 0 / 1 / 2+ calls | wall | first | model | gap | pre | tool <=120 s | long tool | wait (idle until next message) | USD |")
P("|:--|--:|--:|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
for r in rows:
    if r["agent"] == "PI":
        P("| %s | %d | %d | %d / %d / %d | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.2f |" % (r["label"], r["n"], r["calls"], r["zero"], r["one"], r["multi"], r["wall"], r["first"], r["model"], r["gap"], r["pre"], r["tool"], r["long"], r["wait"], r["usd"]))
P("")
for a in PI:
    ab, sv = res.get(("loose", a["label"], a["agent"]), (None, None)) if False else (None, None)
pires = {}
for mode in ("loose", "strict"):
    for a in PI:
        ab = merge_walk(a, mode == "strict"); pires[(mode, a["label"])] = (ab, saving(ab, a))
P("PI batching (same rule, PI turns): " + "; ".join("%s %s: %d of %d requests, seconds floor/mid/high %.0f/%.0f/%.0f, USD %.2f (reads) to %.2f (+output)" % (a["label"], mode, pires[(mode, a["label"])][1][0], len(a["turns"]), pires[(mode, a["label"])][1][1], pires[(mode, a["label"])][1][2], pires[(mode, a["label"])][1][3], pires[(mode, a["label"])][1][5], pires[(mode, a["label"])][1][6]) for mode in ("loose", "strict") for a in PI))
P("")
P("PI tool-phase latency (single-call turns): " + "; ".join("%s: median %.2f s, n %d" % (k, med(v), len(v)) for k, v in sorted(((nm_, [c["lat"] for a in PI for t in a["turns"] if t["ncalls"] == 1 for c in t["calls"] if (c["name"] if c["name"] != "Bash" else "Bash") == nm_ and c["lat"] is not None]) for nm_ in ("Bash", "Read", "Agent", "SendMessage", "Edit", "Write")), key=lambda kv: -len(kv[1])) if len(v) >= 3))
P("")
open(os.path.join(outdir, "tables.md"), "w").write("\n".join(OUT) + "\n")
print("\n".join(OUT))
