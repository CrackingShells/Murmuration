# Aggregates the per-request and per-item TSVs of w08d_pi_context.py into tables.md (spend split, source attribution, ten costliest items, pause pattern, lever estimates) and top_items.tsv, source_usd.tsv in one folder.
# usage: python3 -I w08d_pi_tables.py <folder holding sN_*_requests.tsv and sN_*_items.tsv>
import csv, sys, os, glob, re, statistics, collections

D = sys.argv[1]
OPUS = dict(inp=4.0, out=20.0, rd=0.20, w5=5.0, w1=8.0)
SONNET = dict(inp=2.0, out=10.0, rd=0.10, w5=2.5, w1=4.0)
labels = sorted({os.path.basename(f)[:-len("_requests.tsv")] for f in glob.glob(os.path.join(D, "*_requests.tsv"))})
SESS = {}
for lab in labels:
    rq = list(csv.DictReader(open(os.path.join(D, lab + "_requests.tsv")), delimiter="\t"))
    it = list(csv.DictReader(open(os.path.join(D, lab + "_items.tsv")), delimiter="\t"))
    for r in rq:
        for c in ("start", "end", "ctx", "cr", "cw5", "cw1", "inp", "out", "usd_read", "usd_cw5", "usd_cw1", "usd_inp", "usd_out", "rewrite_tok", "rewrite_usd", "rewrite_premium_usd"):
            r[c] = float(r[c])
        r["k"] = int(r["k"]); r["reset"] = int(r["reset"])
        r["gap"] = float(r["gap_s"]) if r["gap_s"] != "" else None
    for i in it:
        for c in ("step", "chars", "tokens", "n_reads", "usd_write_fresh", "usd_read", "usd_rewrite"):
            i[c] = float(i[c])
        i["step"] = int(i["step"])
        i["usd"] = i["usd_write_fresh"] + i["usd_read"] + i["usd_rewrite"]
    SESS[lab] = (rq, it)

out = []
def P(s=""):
    out.append(s)

def usd(x):
    return "%.2f" % x

def table(head, rows):
    P("| " + " | ".join(head) + " |")
    P("|" + "|".join(":--" if j == 0 else "--:" for j in range(len(head))) + "|")
    for r in rows:
        P("| " + " | ".join(str(x) for x in r) + " |")
    P()

# ---------------------------------------------------------------- 1 spend split per session
P("## 1 spend per request, split (list price, Opus 5.5: input 4, output 20, read 0.20, write 5 min 5, write 1 h 8 USD per million)")
P()
rows = []
T = collections.Counter()
for lab, (rq, it) in SESS.items():
    miss = [r for r in rq if r["k"] > 0 and not r["reset"] and r["cr"] < 0.5 * rq[r["k"] - 1]["ctx"]]
    rw_miss = sum(r["rewrite_usd"] for r in miss)
    rw_all = sum(r["rewrite_usd"] for r in rq)
    row = dict(n=len(rq), rd=sum(r["usd_read"] for r in rq), w5=sum(r["usd_cw5"] for r in rq), w1=sum(r["usd_cw1"] for r in rq), inp=sum(r["usd_inp"] for r in rq),
               out=sum(r["usd_out"] for r in rq), rw_miss=rw_miss, rw_noise=rw_all - rw_miss, nmiss=len(miss), cw1t=sum(r["cw1"] for r in rq), cw5t=sum(r["cw5"] for r in rq))
    row["tot"] = row["rd"] + row["w5"] + row["w1"] + row["inp"] + row["out"]
    row["fresh"] = row["w5"] + row["w1"] + row["inp"] - rw_all
    wall = rq[-1]["end"] - rq[0]["start"]
    row["wall"] = wall
    row["model"] = sorted({r["model"] for r in rq})[0]
    for k, v in row.items():
        if isinstance(v, (int, float)):
            T[k] += v
    SESS[lab] = SESS[lab] + (row,)
    rows.append([lab, row["n"], "%.1f h" % (wall / 3600), usd(row["tot"]), usd(row["rd"]), usd(row["fresh"]), usd(rw_all), usd(row["out"]), usd(row["inp"]), "%.0f%%" % (100 * row["rd"] / row["tot"]), "%.0f%%" % (100 * row["fresh"] / row["tot"]),
                 "%.0f%%" % (100 * rw_all / row["tot"]), "%.0f%%" % (100 * row["out"] / row["tot"]), "%.2f M / %.2f M" % (row["cw1t"] / 1e6, row["cw5t"] / 1e6)])
rows.append(["ALL", int(T["n"]), "%.1f h" % (T["wall"] / 3600), usd(T["tot"]), usd(T["rd"]), usd(T["fresh"]), usd(T["rw_miss"] + T["rw_noise"]), usd(T["out"]), usd(T["inp"]),
             "%.0f%%" % (100 * T["rd"] / T["tot"]), "%.0f%%" % (100 * T["fresh"] / T["tot"]), "%.0f%%" % (100 * (T["rw_miss"] + T["rw_noise"]) / T["tot"]), "%.0f%%" % (100 * T["out"] / T["tot"]), "%.2f M / %.2f M" % (T["cw1t"] / 1e6, T["cw5t"] / 1e6)])
table(["session", "requests", "wall", "USD total", "cache read (context already there)", "fresh write (new tokens)", "re-write (tokens already in context, not read)", "output (billed)", "uncached input", "read %", "fresh write %", "re-write %", "output %", "tokens written 1h / 5m"], rows)
P("Fresh write = write and input cost minus re-write cost. Re-write = tokens at positions below the previous request's context that were not read (positional model: the cache covers the first `cache_read` tokens). USD of misses (cache read under half the previous context, not a compaction) versus noise (small shortfalls at cache breakpoints):")
P()
table(["session", "misses", "USD re-written in misses", "USD re-written, small shortfalls"], [[lab, s[2]["nmiss"], usd(s[2]["rw_miss"]), usd(s[2]["rw_noise"])] for lab, s in SESS.items()] + [["ALL", int(T["nmiss"]), usd(T["rw_miss"]), usd(T["rw_noise"])]])

# ---------------------------------------------------------------- 2 source attribution
GROUP = [("tool result: Read of a document/code", lambda c: c.startswith("Read:")),
         ("tool result: Bash file view (cat/sed/head/tail)", lambda c: c.startswith("Bash: file view")),
         ("tool result: lab_status.py", lambda c: c == "Bash: lab_status.py"),
         ("tool result: git", lambda c: c.startswith("Bash: git")),
         ("tool result: search (Glob/Grep/colgrep, grep/ls/find/jq)", lambda c: c.startswith("search") or c.startswith("Bash: grep")),
         ("tool result: Bash python/script/gh/other/write", lambda c: c.startswith("Bash:")),
         ("tool result: Write/Edit echo", lambda c: c == "Write/Edit echo"),
         ("tool result: Agent/SendMessage (dispatch ack)", lambda c: c.startswith("Agent/SendMessage")),
         ("tool result: ToolSearch schemas", lambda c: c.startswith("ToolSearch")),
         ("tool result: other MCP/web/other tools", lambda c: c.startswith("other") or c.startswith("web") or c.startswith("Monitor")),
         ("worker hand-back messages (peer) ", lambda c: c.startswith("worker hand-back")),
         ("task notifications (worker done)", lambda c: c.startswith("task notification") or c.startswith("queued prompt")),
         ("injected: skill listing (re-entered)", lambda c: c == "injected: skill_listing"),
         ("injected: deferred tools / agent listing / MCP instructions", lambda c: c in ("injected: agent_listing_delta", "injected: deferred_tools_delta", "injected: mcp_instructions_delta")),
         ("child-session notes (a session the PI started finished a turn)", lambda c: c.startswith("child-session")),
         ("injected: invoked skill text", lambda c: c == "injected: skill text (invoked skill)"),
         ("injected: system reminders (linked sessions, total_tokens, silent turn)", lambda c: c.startswith("injected: system reminder") or c in ("injected: total_tokens_reminder", "injected: silent_turn_reminder")),
         ("injected: hooks, CLAUDE.md files, environment, other", lambda c: c.startswith("injected")),
         ("user messages", lambda c: c == "user message"),
         ("own output: Write/Edit content", lambda c: c == "own output: Write/Edit content"),
         ("own output: dispatch briefs and messages", lambda c: c.startswith("own output: dispatch")),
         ("own output: tool calls", lambda c: c.startswith("own output: tool calls")),
         ("own output: text", lambda c: c == "own output: text"),
         ("own output: recorded thinking text", lambda c: c.startswith("own output: thinking")),
         ("system prompt + tool definitions (prefix, not in transcript)", lambda c: c.startswith("system prompt")),
         ("post-compaction context (summary + prefix)", lambda c: c.startswith("COMPACTION")),
         ("own thinking carried in context (inferred: step residual, see section 2b)", lambda c: c.startswith("unattributed"))]

def group_of(c):
    for g, f in GROUP:
        if f(c):
            return g
    return "other: " + c

P("## 2 what put the context there: USD over each item's life (fresh write + every later cache read + re-writes)")
P()
G = collections.defaultdict(lambda: collections.Counter())
for lab, (rq, it, row) in SESS.items():
    for i in it:
        g = group_of(i["cat"])
        G[g]["n"] += 1
        G[g]["tok"] += i["tokens"]
        G[g]["w"] += i["usd_write_fresh"]
        G[g]["r"] += i["usd_read"]
        G[g]["rw"] += i["usd_rewrite"]
        G[g]["usd"] += i["usd"]
        G[g]["reads"] += i["n_reads"] * i["tokens"]
        G["~" + lab][g] += i["usd"]
G["billed output (all sessions)"]["usd"] = T["out"]
G["billed output (all sessions)"]["n"] = int(T["n"])
G["uncached input (all sessions)"]["usd"] = T["inp"]
tot_all = T["tot"]
rows = []
order = sorted([g for g in G if not g.startswith("~")], key=lambda g: -G[g]["usd"])
for g in order:
    c = G[g]
    rows.append([g, int(c["n"]), "%.0fk" % (c["tok"] / 1e3) if c["tok"] else "", usd(c["w"]), usd(c["r"]), usd(c["rw"]), usd(c["usd"]), "%.1f%%" % (100 * c["usd"] / tot_all)])
rows.append(["TOTAL", "", "", "", "", "", usd(sum(G[g]["usd"] for g in order)), "100%% of %s" % usd(tot_all)])
table(["source", "items", "tokens entered", "USD write (fresh)", "USD later reads", "USD re-writes", "USD total", "share of PI spend"], rows)
P("Items sum plus billed output plus uncached input equals the usage-based total of section 1 by construction (the model prices each position of the context at each request). The prefix and the step residuals are not in the transcript as text.")
P()

FAM = [("the PI's own words (billed output + carried tool calls, briefs, Write/Edit content, text, thinking)", lambda g: g.startswith("own ") or g.startswith("billed output")),
       ("tool results (reading, git, lab_status, search, acks)", lambda g: g.startswith("tool result")),
       ("workers' hand-backs, task notifications, child-session notes", lambda g: g.startswith("worker hand-back") or g.startswith("task notifications") or g.startswith("child-session")),
       ("injected text and the prefix (skill listing, tool/agent lists, hooks, reminders, system prompt)", lambda g: g.startswith("injected") or g.startswith("system prompt")),
       ("post-compaction context", lambda g: g.startswith("post-compaction")),
       ("user messages", lambda g: g.startswith("user messages")),
       ("uncached input", lambda g: g.startswith("uncached"))]
rows = []
for name, f in FAM:
    u = sum(G[g]["usd"] for g in order if f(g))
    rows.append([name, usd(u), "%.1f%%" % (100 * u / tot_all)])
P("### 2a roll-up")
P()
table(["family", "USD", "share of PI spend"], rows)
# by session, group shares
P("### by session (USD)")
P()
gl = [g for g in order if not g.startswith("billed") and not g.startswith("uncached")]
head = ["source"] + list(SESS)
rows = []
for g in gl[:16]:
    rows.append([g] + [usd(G["~" + lab][g]) for lab in SESS])
table(head, rows)


P("### 2b checks on the attribution")
P()
rows = []
for lab, (rq, it, row) in SESS.items():
    res = {i["step"]: i["tokens"] for i in it if i["tool"] == "residual"}
    vis = collections.defaultdict(float)
    for i in it:
        if i["tool"] == "assistant" and not i["cat"].startswith("own output: thinking"):
            vis[i["step"]] += i["tokens"]
    xs = [rq[k - 1]["out"] - vis.get(k, 0) for k in range(1, len(rq))]
    ys = [res.get(k, 0) for k in range(1, len(rq))]
    n = len(xs)
    if n < 5:
        continue
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys)); vx = sum((a - mx) ** 2 for a in xs); vy = sum((b - my) ** 2 for b in ys)
    sk = [i for i in it if i["cat"] == "injected: skill_listing"]
    rows.append([lab, "%.0fk" % (sum(ys) / 1e3), "%.0fk" % (sum(xs) / 1e3), "%.0fk" % (sum(r["out"] for r in rq) / 1e3), "%.2f" % (cov / (vx * vy) ** .5) if vx and vy else "", "%.2f" % (cov / vx) if vx else "", len(sk), usd(sum(i["usd"] for i in sk))])
table(["session", "sum of step residual tokens", "sum of (billed output - estimated visible output) of the previous request", "billed output tokens", "correlation per step", "slope", "skill-listing injections", "USD of those"], rows)
P("MEASURED: the step residual (tokens the context grew by that no recorded text explains) tracks the previous request's billed output minus its visible text, correlation 0.85-0.94, slope about 1. CONJECTURE: the residual is the model's thinking blocks, which stay in the context although the transcript stores them empty (thinking text is 0-466 characters in the records); the residual also holds per-step framing and reminders.")
P()
# ---------------------------------------------------------------- 3 ten costliest items
allit = []
for lab, (rq, it, row) in SESS.items():
    for i in it:
        allit.append((i["usd"], lab, i))
allit.sort(key=lambda x: -x[0])
P("## 3 the ten costliest single items (all sessions)")
P()
rows = []
for u, lab, i in allit[:10]:
    rows.append([lab, i["step"], i["cat"], (i["label"] or "")[:70].replace("|", "/"), "%.0f" % i["chars"], "%.0fk" % (i["tokens"] / 1e3), int(i["n_reads"]), usd(i["usd_write_fresh"]), usd(i["usd_read"]), usd(i["usd_rewrite"]), usd(u)])
table(["session", "request", "source", "label (path or command head)", "chars", "tokens", "later requests that read it", "write", "reads", "re-writes", "USD"], rows)
with open(os.path.join(D, "top_items.tsv"), "w") as fh:
    fh.write("rank\tsession\tstep\tcat\tlabel\tchars\ttokens\tn_reads\tusd_write\tusd_read\tusd_rewrite\tusd\n")
    for n, (u, lab, i) in enumerate(allit[:60], 1):
        fh.write("\t".join(str(x) for x in (n, lab, i["step"], i["cat"], i["label"], int(i["chars"]), int(i["tokens"]), int(i["n_reads"]), round(i["usd_write_fresh"], 4), round(i["usd_read"], 4), round(i["usd_rewrite"], 4), round(u, 4))) + "\n")
P("Top 10 together: USD %s of %s (%.1f%%). Next, the ten costliest items excluding the system prefix, residuals and post-compaction context:" % (usd(sum(x[0] for x in allit[:10])), usd(tot_all), 100 * sum(x[0] for x in allit[:10]) / tot_all))
P()
real = [x for x in allit if not (x[2]["cat"].startswith("system prompt") or x[2]["cat"].startswith("unattributed") or x[2]["cat"].startswith("COMPACTION"))]
rows = []
for u, lab, i in real[:10]:
    rows.append([lab, i["step"], i["cat"], (i["label"] or "")[:70].replace("|", "/"), "%.0fk" % (i["tokens"] / 1e3), int(i["n_reads"]), usd(u)])
table(["session", "request", "source", "label", "tokens", "later reads", "USD"], rows)
with open(os.path.join(D, "source_usd.tsv"), "w") as fh:
    fh.write("source\titems\ttokens\tusd_write\tusd_read\tusd_rewrite\tusd\n")
    for g in order:
        c = G[g]
        fh.write("%s\t%d\t%d\t%.4f\t%.4f\t%.4f\t%.4f\n" % (g, c["n"], c["tok"], c["w"], c["r"], c["rw"], c["usd"]))


P("### 2c the preface: what the PI has bought before its first dispatch")
P()
rows = []
for lab, (rq, it, row) in SESS.items():
    disp = [i["step"] for i in it if i["cat"].startswith("own output: dispatch")]
    if not disp:
        continue
    f = min(disp)
    pre = sum(r["usd_read"] + r["usd_cw5"] + r["usd_cw1"] + r["usd_inp"] + r["usd_out"] for r in rq[:f + 1])
    rows.append([lab, f, "%dk" % (rq[0]["ctx"] / 1e3), "%dk" % (rq[f]["ctx"] / 1e3), usd(pre), "%.1f%%" % (100 * pre / row["tot"]), "%.1f%%" % (100 * sum(i["usd"] for i in it if i["step"] <= f) / row["tot"])])
table(["session", "first dispatch at request", "context at request 0", "context at the first dispatch", "USD of requests up to and including it", "share of the session's USD", "share of the session's USD that items entering up to then cost over the whole session"], rows)

# ---------------------------------------------------------------- 4 pauses
P("## 4 pauses: gap from the end of one response to the start of the next request")
P()
rows = []
GP = []
for lab, (rq, it, row) in SESS.items():
    gaps = [r for r in rq if r["gap"] is not None]
    g300 = [r for r in gaps if r["gap"] > 300]
    g3600 = [r for r in gaps if r["gap"] > 3600]
    g300_1h = [r for r in g300 if r["gap"] <= 3600]
    hit = [r for r in g300_1h if r["cr"] >= 0.5 * rq[r["k"] - 1]["ctx"]]
    miss = [r for r in g300 if r["cr"] < 0.5 * rq[r["k"] - 1]["ctx"] and not r["reset"]]
    rw = sum(r["rewrite_usd"] for r in miss)
    rwp = sum(r["rewrite_premium_usd"] for r in miss)
    # counterfactual 5-minute cache: every gap in (300, 3600] that hit would have re-written the previous context at the 5-minute rate
    cf5 = sum(rq[r["k"] - 1]["ctx"] * (OPUS["w5"] - OPUS["rd"]) / 1e6 for r in hit)
    prem1h = row["cw1t"] * (OPUS["w1"] - OPUS["w5"]) / 1e6
    GP.append((lab, len(gaps), len(g300), len(g300_1h), len(hit), len(g3600), len(miss), rw, rwp, cf5, prem1h))
    rows.append([lab, len(gaps), len(g300), len(g300_1h), len(hit), len(g3600), len(miss), usd(rw), usd(rwp), usd(cf5), usd(prem1h)])
rows.append(["ALL"] + [sum(g[j] for g in GP) if j < 6 else usd(sum(g[j] for g in GP)) for j in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)])
table(["session", "requests with a gap", "gaps > 5 min", "of them 5 min to 1 h", "of those: 1 h cache hit", "gaps > 1 h", "misses (read < half previous context)", "USD re-written in misses", "of it: premium over a read", "counterfactual: USD a 5-minute cache would have re-written for the 5 min - 1 h hits", "USD extra paid for writing at the 1 h rate instead of 5 min (tokens x (8-5))"], rows)
P("Gap = start of request k minus end of response k-1 (the cache clock restarts at each request). Hits and misses are tested on the cache read of the request that follows the gap.")
P()
# who ended each long gap
P("### what ended the gaps over 5 minutes")
P()
cause = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
for lab, (rq, it, row) in SESS.items():
    for r in rq:
        if r["gap"] is not None and r["gap"] > 300:
            c = cause[r["gap_cause"]]
            c[0] += 1
            c[1] += r["gap"] > 3600
            c[2] += r["gap"]
            c[3] += r["rewrite_usd"] if (r["cr"] < 0.5 * rq[r["k"] - 1]["ctx"] and not r["reset"]) else 0
table(["what arrived first", "gaps > 5 min", "of them > 1 h", "summed gap (h)", "USD re-written in the miss"], [[k, v[0], v[1], "%.1f" % (v[2] / 3600), usd(v[3])] for k, v in sorted(cause.items(), key=lambda kv: -kv[1][0])])
# distribution of gaps
allg = [r["gap"] for rq, it, row in SESS.values() for r in rq if r["gap"] is not None]
allg.sort()
def pc(p):
    return allg[min(len(allg) - 1, int(p * len(allg)))]
P("Gap percentiles over %d requests: median %.1f s, p75 %.1f s, p90 %.1f s, p95 %.0f s, p99 %.0f s, max %.0f s. Share of requests with a gap > 60 s: %.1f%%; > 300 s: %.1f%%; > 3600 s: %.1f%%." % (len(allg), pc(.5), pc(.75), pc(.9), pc(.95), pc(.99), allg[-1], 100 * sum(g > 60 for g in allg) / len(allg), 100 * sum(g > 300 for g in allg) / len(allg), 100 * sum(g > 3600 for g in allg) / len(allg)))
P()
# which requests cost most, by what woke the PI
P("### what woke the PI: requests by trigger (the first thing that arrived after the previous response)")
P()
trig = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0, 0.0])
for lab, (rq, it, row) in SESS.items():
    for r in rq:
        c = trig[r["gap_cause"] or "first request"]
        c[0] += 1
        tot = r["usd_read"] + r["usd_cw5"] + r["usd_cw1"] + r["usd_inp"] + r["usd_out"]
        c[1] += tot
        c[2] += r["usd_read"]
        c[3] += (r["tools"].split("|")[0] == "")
        c[5] += (tot if r["tools"].split("|")[0] == "" else 0)
        c[4] += (r["tools"].split("|")[0] == "" and r["out"] < 200)
table(["trigger", "requests", "USD", "of it cache read", "requests with no tool call", "USD of those", "of them output < 200 tokens"], [[k, v[0], usd(v[1]), usd(v[2]), v[3], usd(v[5]), v[4]] for k, v in sorted(trig.items(), key=lambda kv: -kv[1][1])])

# ---------------------------------------------------------------- 5 levers
P("## 5 what each lever would have saved (ESTIMATE; formulas below each table)")
P()
rd_price = OPUS["rd"]

def items_where(pred, labs=None):
    for lab, (rq, it, row) in SESS.items():
        for i in it:
            if pred(lab, i):
                yield lab, i

# (a) reading by section
doc = lambda lab, i: (i["cat"].startswith("Read:") or i["cat"].startswith("Bash: file view")) and i["tokens"] > 1500
big = list(items_where(doc))
tot_doc = sum(i["usd"] for _, i in big)
tot_read_all = sum(i["usd"] for _, i in items_where(lambda l, i: i["cat"].startswith("Read:") or i["cat"].startswith("Bash: file view")))
P("### (a) read by section")
P()
rows = []
for f in (0.5, 0.25):
    rows.append(["keep %d%% of each document read over 1,500 tokens" % (100 * f), len(big), usd(tot_doc), usd(tot_doc * (1 - f)), "%.1f%%" % (100 * tot_doc * (1 - f) / tot_all)])
table(["scenario", "items", "USD those items cost over their life", "saving", "share of PI spend"], rows)
P("Formula: saving = (1 - f) x sum of USD(write + reads + re-writes) over Read and `cat/sed/head/tail` items with more than 1,500 tokens. f is a stated assumption, not measured; the all-sizes total for these two sources is USD %s." % usd(tot_read_all))
# duplicates
dup = collections.defaultdict(list)
for lab, (rq, it, row) in SESS.items():
    for i in it:
        if i["cat"].startswith("Read:") and i["label"]:
            dup[(lab, i["label"])].append(i)
dn = dsum = 0
dl = []
for k, v in dup.items():
    if len(v) > 1:
        for i in v[1:]:
            dn += 1; dsum += i["usd"]
        dl.append((sum(i["usd"] for i in v[1:]), k, len(v)))
dl.sort(reverse=True)
P()
P("MEASURED: %d Reads of a path already Read earlier in the same session (%d paths read twice or more); the later copies cost USD %s over their lives (an upper bound of the saving from not re-reading; a file may have changed in between). Costliest: %s." % (dn, sum(1 for v in dup.values() if len(v) > 1), usd(dsum), "; ".join("%s x%d USD %s" % (k[1].split("/")[-1][:40], n, usd(u)) for u, k, n in dl[:4])))
P()

# (b) delegate orientation reads
P("### (b) delegate orientation reads to a Sonnet worker that returns a short summary")
P()
rows = []
tot_sav = 0
for lab, (rq, it, row) in SESS.items():
    disp = [i["step"] for i in it if i["cat"].startswith("own output: dispatch")]
    first = min(disp) if disp else None
    if first is None:
        rows.append([lab, "no dispatch", "", "", "", "", "", ""])
        continue
    ori = [i for i in it if i["step"] <= first and (i["cat"].startswith("Read:") or i["cat"].startswith("Bash:") or i["cat"].startswith("search") or i["cat"].startswith("other") or i["cat"].startswith("ToolSearch"))]
    T_tok = sum(i["tokens"] for i in ori)
    cost = sum(i["usd"] for i in ori)
    nreads = (sum(i["n_reads"] * i["tokens"] for i in ori) / T_tok) if T_tok else 0
    SUM_TOK = 1500
    # summary enters at the step of the last orientation item, carried as long as the replaced items on average
    last_step = max([i["step"] for i in ori], default=first)
    later = len(rq) - last_step - 1
    wr = OPUS["w1"]
    summ = SUM_TOK * (wr + later * rd_price) / 1e6
    # worker: reads T_tok tokens in n_w requests of a growing context, writes them once at the Sonnet 1 h-free 5-minute rate, outputs 1,500 tokens
    n_w = 15
    worker = (T_tok * SONNET["w5"] + n_w * (T_tok / 2) * SONNET["rd"] + SUM_TOK * SONNET["out"] + 20000 * SONNET["w5"]) / 1e6
    sav = cost - summ - worker
    tot_sav += max(sav, 0)
    rows.append([lab, first, len(ori), "%.0fk" % (T_tok / 1e3), usd(cost), usd(summ), usd(worker), usd(sav)])
table(["session", "first dispatch at request", "orientation items before it", "tokens", "USD they cost over their life", "USD of a 1,500-token summary carried to the end", "USD of the Sonnet worker", "saving"], rows)
P("Formula: orientation items = tool results (Read, Bash, search, MCP, ToolSearch) entering at or before the request of the PI's first dispatch (an Agent or SendMessage input). saving = cost(items) - summary - worker. summary = 1,500 x (8 + L x 0.20) / 1e6 with L the number of later requests; worker = (T x 2.5 + 15 x T/2 x 0.10 + 1,500 x 10 + 20,000 x 2.5) / 1e6 for T orientation tokens (15 requests, a 20k-token worker prefix; both ESTIMATE). Sum of positive savings: USD %s. It assumes the PI would not read the same documents again after the summary; a PI that does loses the saving, and the orientation reads that decide a brief may not delegate." % usd(tot_sav))
P()

# (c) shorter hand-backs
P("### (c) shorter hand-back messages")
P()
hb = list(items_where(lambda l, i: i["cat"].startswith("worker hand-back")))
rows = []
for cap in (1000, 2000, 3000):
    sv = 0
    for lab, i in hb:
        if i["chars"] > cap:
            sv += i["usd"] * (1 - cap / i["chars"])
    rows.append(["cap at %d characters" % cap, len(hb), "%.0fk" % (sum(i["chars"] for _, i in hb) / 1e3), usd(sum(i["usd"] for _, i in hb)), usd(sv), "%.1f%%" % (100 * sv / tot_all)])
table(["scenario", "hand-back messages", "characters", "USD they cost over their life", "saving", "share of PI spend"], rows)
if hb:
    ch = sorted(i["chars"] for _, i in hb)
    P("Hand-back size: n = %d, median %d chars, p90 %d, max %d." % (len(ch), ch[len(ch) // 2], ch[int(.9 * len(ch))], ch[-1]))
P("Formula: saving = sum over hand-backs longer than the cap of USD(item) x (1 - cap / chars). Task notifications (about 900 characters each) are not counted here; they are in the table of section 2.")
P()

# (d) compaction
P("### (d) compaction, or a new session, when the context passes a threshold")
P()
S_AFTER = 91500   # observed post-compaction context, s1 request 276 (MEASURED)
def simulate(rq, trig):
    drop = 0.0
    sav = 0.0
    cost = 0.0
    nc = 0
    for r in rq:
        k = r["k"]
        if r["reset"]:
            drop = 0.0   # a real compaction occurred; stop simulating beyond it
            continue
        ctx = r["ctx"] - drop
        prev = rq[k - 1]["ctx"] if k else 0
        miss = k > 0 and r["cr"] < 0.5 * prev
        rate = OPUS["w1"] if miss else OPUS["rd"]
        sav += drop * rate / 1e6
        if ctx > trig:
            d = ctx - S_AFTER
            C = ctx * OPUS["rd"] / 1e6 + 8000 * OPUS["out"] / 1e6 + 41000 * OPUS["w1"] / 1e6
            cost += C
            drop += d
            nc += 1
    return sav, cost, nc
rows = []
for trig in (200000, 300000):
  for S_AFTER_ in (91500, 136500):
    S_AFTER = S_AFTER_
    tsv = tcv = tn = 0
    cell = []
    for lab, (rq, it, row) in SESS.items():
        s_, c_, n_ = simulate(rq, trig)
        tsv += s_; tcv += c_; tn += n_
        cell.append((lab, s_, c_, n_))
    rows.append(["trigger %dk, compact to %dk" % (trig // 1000, S_AFTER // 1000), tn, usd(tsv), usd(tcv), usd(tsv - tcv), "%.1f%%" % (100 * (tsv - tcv) / tot_all), "; ".join("%s %s/%d" % (l, usd(s_ - c_), n_) for l, s_, c_, n_ in cell if n_)])
S_AFTER = 91500
table(["scenario", "compactions", "USD saved on later requests", "USD of the compactions", "net", "share of PI spend", "net per session / compactions"], rows)
P("Formula: when the context of a request exceeds the trigger, compact to 91,500 tokens (the post-compaction context the lab measured at request 276 of s1, 966,526 -> 91,499 tokens) or, as a variant, to 136,500 (the same plus about 45k tokens the PI re-reads after the compaction, the median orientation size of table (b)); every later request then carries `drop` fewer tokens, saving drop x 0.20 / 1e6 (x 8 / 1e6 where the request was a cache miss, as the tokens would have been re-written). One compaction costs ctx x 0.20 + 8,000 output x 20 + 41,000 written x 8, all / 1e6 (the 41,043 written tokens of request 276; the 8,000-token summary is an assumption). Information lost by compaction is not priced. Sessions s2-s6 are one wave each, so for them the trigger acts inside a wave; a new session at a wave boundary is a trigger at the start of the next wave and is bounded by what the PI must re-read." % ())
P()
# context at start and end per session
rows = []
for lab, (rq, it, row) in SESS.items():
    rows.append([lab, "%dk" % (rq[0]["ctx"] / 1e3), "%dk" % (rq[-1]["ctx"] / 1e3), "%dk" % (max(r["ctx"] for r in rq) / 1e3), "%.0fk" % (statistics.mean(r["ctx"] for r in rq) / 1e3), "%.2f" % (sum(r["usd_read"] for r in rq) / len(rq))])
table(["session", "context at request 0", "at the last request", "max", "mean over requests", "mean cache-read USD per request"], rows)

# (e) fewer requests per dispatch batch
P("### (e) fewer requests per dispatch batch")
P()
rows = []
tsave = 0
nrun = nabs = 0
runlens = collections.Counter()
for lab, (rq, it, row) in SESS.items():
    runs = []
    cur = []
    for r in rq:
        nag = int(r["tools"].split("|")[1]) + int(r["tools"].split("|")[2])
        if nag > 0:
            cur.append(r)
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    ab = [r for run in runs for r in run[1:]]
    sv = sum(r["usd_read"] + (r["rewrite_premium_usd"] if r["rewrite_tok"] > 0.5 * rq[r["k"] - 1]["ctx"] else 0) for r in ab)
    tsave += sv
    nrun += len(runs); nabs += len(ab)
    for run in runs:
        runlens[len(run)] += 1
    rows.append([lab, sum(len(x) for x in runs), len(runs), len(ab), usd(sv)])
rows.append(["ALL", "", nrun, nabs, usd(tsave)])
table(["session", "requests that dispatch (Agent or SendMessage)", "runs of consecutive dispatching requests", "requests absorbed if each run were one", "USD saved (their cache reads, and re-write premium after a miss)"], rows)
P("Run lengths (consecutive requests each carrying an Agent or SendMessage call, nothing between): %s." % ", ".join("%d: %d" % (k, v) for k, v in sorted(runlens.items())))
P("Formula: absorbed request = every request of a run after its first; saving = its cache-read USD (the new tokens are still written once; its own output is still produced). It is an upper bound, since a dispatch may depend on the result of the previous one.")
P()

P("### (f) compact right before a pause that turns out to be longer than an hour")
P()
rows = []
tsv_ = 0
for lab, (rq, it, row) in SESS.items():
    for r in rq:
        if r["k"] > 0 and not r["reset"] and r["cr"] < 0.5 * rq[r["k"] - 1]["ctx"] and r["rewrite_usd"] > 0.5:
            prev = rq[r["k"] - 1]["ctx"]
            comp = prev * OPUS["rd"] / 1e6 + 8000 * OPUS["out"] / 1e6 + 41000 * OPUS["w1"] / 1e6
            after = 91500 * OPUS["w1"] / 1e6
            net = r["rewrite_usd"] - after - comp
            tsv_ += net
            rows.append([lab, r["k"], "%.0f min" % (r["gap"] / 60), "%dk" % (prev / 1e3), usd(r["rewrite_usd"]), usd(comp), usd(after), usd(net)])
rows.append(["ALL", "", "", "", "", "", "", usd(tsv_)])
table(["session", "request after the pause", "gap", "context before", "USD re-written", "USD of compacting before the pause", "USD of writing the compacted 91.5k after it", "net saving"], rows)
P("Formula: net = re-write USD - (ctx x 0.20 + 8,000 x 20 + 41,000 x 8) / 1e6 - 91,500 x 8 / 1e6. It assumes the PI knew the pause was coming; it can know only at the end of a wave or when it hands a decision to the user.")
P()
P("### (e2) dispatch bursts: dispatching requests within 120 s of each other, other requests between them counted")
P()
rows = []
tot_span = 0.0
for lab, (rq, it, row) in SESS.items():
    disp = [r for r in rq if int(r["tools"].split("|")[1]) + int(r["tools"].split("|")[2]) > 0]
    bursts = []
    cur = []
    for r in disp:
        if cur and r["start"] - cur[-1]["start"] > 120:
            bursts.append(cur); cur = []
        cur.append(r)
    if cur:
        bursts.append(cur)
    span = 0.0; nsp = 0
    for b in bursts:
        if len(b) > 1:
            inside = [r for r in rq if b[0]["k"] < r["k"] <= b[-1]["k"]]
            nsp += len(inside)
            span += sum(r["usd_read"] for r in inside)
    tot_span += span
    ag = [int(r["tools"].split("|")[1]) for r in disp]
    rows.append([lab, len(disp), sum(ag), len(bursts), sum(1 for b in bursts if len(b) > 1), nsp, usd(span)])
rows.append(["ALL", "", "", "", "", "", usd(tot_span)])
table(["session", "dispatching requests", "Agent calls", "bursts", "bursts with 2+ dispatching requests", "requests inside those bursts after the first", "USD of their cache reads (upper bound of the saving if each burst were one request)"], rows)
P("Upper bound: it counts every request from the second to the last dispatching request of a burst, including requests that wrote the briefs or read results the next dispatch depends on.")
P()
open(os.path.join(D, "tables.md"), "w").write("\n".join(out) + "\n")
print("wrote tables.md, %d lines" % len(out))
