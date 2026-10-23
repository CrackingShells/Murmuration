# Builds the source-class shares, the costliest documents and scripts, duplicate-read and cap/section counterfactual tables from items.tsv of w08a_cost.py; input: items.tsv; outputs: tables.md, by_class.tsv, top_refs.tsv in the same folder. Usage: w08a_tables.py FOLDER_WITH_items.tsv
import sys, os, csv, collections, re

folder = sys.argv[1]
R = list(csv.DictReader(open(os.path.join(folder, "items.tsv")), delimiter="\t"))
for r in R:
    for f in ("chars", "est_tokens", "later_requests", "entered_at_request", "first_write_usd", "read_usd", "rewrite_usd", "n_rewrites"):
        r[f] = float(r[f])
    r["usd"] = r["first_write_usd"] + r["read_usd"] + r["rewrite_usd"]
TOT = sum(r["usd"] for r in R)

def base_kind(k):
    return re.sub(r" \(section\)", "", k.split(" via ")[0])

def source(r):
    c, k = r["cls"], r["kind"]
    if c == "script":
        return "lab script output (scripts/, __instrumenta__/)" if (k.startswith("scripts/") or k.startswith("__instrumenta__/")) else "worker's own code run (scratch script, inline python)"
    if c == "readdoc": return "Read of a lab document" if base_kind(k) != "other document" else "Read of a non-lab document"
    if c == "bashdoc": return "cat/sed/head/tail of a document in Bash"
    if c == "readsrc": return "Read of source code"
    if c == "bashsrc": return "cat/sed/head/tail of source code in Bash"
    if c == "git": return "git output"
    if c == "search": return "search results (colgrep, grep, find)"
    if c == "web": return "web or MCP results"
    if c == "hook": return "hook-injected text (additionalContext, total_tokens reminders)"
    if c == "brief": return "the brief (first prompt)"
    if c == "msg": return "messages, resume prompts, task notices"
    if c == "harness": return "harness text at start (instructions, session context, tool lists)"
    if c == "base": return "system prompt and tool schemas (base)"
    if c == "asst": return "the agent's own turns: " + k.replace("the agent's ", "")
    if k.startswith("ToolSearch"): return "ToolSearch results (tool schemas)"
    return "other tool results (edits, ToolSearch, mkdir, ls ...)"

for r in R:
    r["src"] = source(r)
TOOLRES = lambda r: r["tool"] not in ("attachment", "prompt", "") and r["cls"] not in ("asst", "base")

out = []
P = out.append
def money(x): return "%.2f" % x

# ---- 1. share by source class
agg = collections.OrderedDict()
for r in sorted(R, key=lambda r: -r["usd"]):
    a = agg.setdefault(r["src"], [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    a[0] += 1; a[1] += r["est_tokens"]; a[2] += r["first_write_usd"]; a[3] += r["read_usd"]; a[4] += r["rewrite_usd"]; a[5] += r["usd"]
    a[6] += r["n_rewrites"]
P("## 1. Worker context USD by source class (68 workers, waves 4-7)\n")
P("Context USD = cache reads + cache writes (5 min and 1 hour rates as recorded) + uncached input, at list price, of every request; output tokens are left out (the transcripts hold the output count at the start of the stream, so it is not usable). Total USD %s. Each element's USD is the sum over the requests that carried it (see the method in the report).\n" % money(TOT))
P("| source class | elements | est. tokens | first write | reads | re-writes after a pause | total USD | share |")
P("|:--|--:|--:|--:|--:|--:|--:|--:|")
with open(os.path.join(folder, "by_class.tsv"), "w") as fh:
    fh.write("source_class\telements\test_tokens\tfirst_write_usd\tread_usd\trewrite_usd\ttotal_usd\tshare\n")
    for k, a in agg.items():
        P("| %s | %d | %s | %s | %s | %s | %s | %.1f%% |" % (k, a[0], "{:,.0f}".format(a[1]), money(a[2]), money(a[3]), money(a[4]), money(a[5]), 100 * a[5] / TOT))
        fh.write("%s\t%d\t%.0f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\n" % (k, a[0], a[1], a[2], a[3], a[4], a[5], a[5] / TOT))
tool_tot = sum(r["usd"] for r in R if TOOLRES(r))
P("\nOf the total, tool results (all rows whose tool is a call, not the base, the agent's own output, hook text, messages) are USD %s (%.1f%%); re-writes after a pause are USD %s (%.1f%% of all)." % (money(tool_tot), 100 * tool_tot / TOT, money(sum(r["rewrite_usd"] for r in R)), 100 * sum(r["rewrite_usd"] for r in R) / TOT))

# ---- by wave
P("\n## 1b. By wave (USD, share of that wave's context USD)\n")
waves = sorted({r["wave"] for r in R})
srcs = list(agg.keys())
P("| source class | " + " | ".join(waves) + " |")
P("|:--|" + "--:|" * len(waves))
wt = {w: sum(r["usd"] for r in R if r["wave"] == w) for w in waves}
for s in srcs:
    P("| %s | " % s + " | ".join("%s (%.0f%%)" % (money(sum(r["usd"] for r in R if r["wave"] == w and r["src"] == s)), 100 * sum(r["usd"] for r in R if r["wave"] == w and r["src"] == s) / wt[w]) for w in waves) + " |")
P("| total | " + " | ".join(money(wt[w]) for w in waves) + " |")

# ---- 2. documents by kind and route
P("\n## 2. Lab documents by kind and route (Read vs Bash cat/sed/head/tail)\n")
dk = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0.0, 0.0, 0])
for r in R:
    if r["cls"] in ("readdoc", "bashdoc"):
        k = base_kind(r["kind"]); route = "Read" if r["cls"] == "readdoc" else "Bash"
        d = dk[(k, route)]
        d[0] += 1; d[1] += r["est_tokens"]; d[2] += r["usd"]
        d[3] += 1 if "(section)" in r["kind"] else 0
dsum = sum(v[2] for v in dk.values())
P("| document kind | route | results | est. tokens (mean per result) | USD | share of all context USD | read in part (offset/limit) |")
P("|:--|:--|--:|--:|--:|--:|--:|")
for (k, route), v in sorted(dk.items(), key=lambda kv: -kv[1][2]):
    P("| %s | %s | %d | %s | %s | %.1f%% | %d |" % (k, route, v[0], "{:,.0f}".format(v[1] / v[0]), money(v[2]), 100 * v[2] / TOT, v[3]))
P("| all documents | | %d | | %s | %.1f%% | |" % (sum(v[0] for v in dk.values()), money(dsum), 100 * dsum / TOT))
# Bash route details: which command word
bw = collections.defaultdict(lambda: [0, 0.0])
for r in R:
    if r["cls"] == "bashdoc":
        w = r["kind"].split(" via ")[-1]
        bw[w][0] += 1; bw[w][1] += r["usd"]
P("\nBash document reads by command word: " + "; ".join("%s %d results USD %s" % (w, v[0], money(v[1])) for w, v in sorted(bw.items(), key=lambda kv: -kv[1][1])))

# ---- 3. top 20 documents and scripts
def refkey(r):
    if r["cls"] == "script":
        return ("script", r["kind"])
    if r["cls"] in ("readdoc", "bashdoc"):
        ref = r["ref"] or "(path not in lab dirs)"
        ref = re.sub(r"wave-\d+\.md", "wave-NN.md", ref) if base_kind(r["kind"]) == "wave note" else ref
        return ("document", base_kind(r["kind"]) + " | " + ref)
    return None
tr = collections.defaultdict(lambda: [0, 0.0, 0.0, 0.0, set()])
for r in R:
    k = refkey(r)
    if k is None: continue
    t = tr[k]
    t[0] += 1; t[1] += r["est_tokens"]; t[2] += r["usd"]; t[3] += r["rewrite_usd"]; t[4].add(r["agent_id"])
P("\n## 3. The 20 costliest documents and scripts (aggregated over workers; wave notes merged into one row, kind | path)\n")
P("| rank | type | what | results | workers | mean est. tokens | USD | share | of which re-writes |")
P("|--:|:--|:--|--:|--:|--:|--:|--:|--:|")
with open(os.path.join(folder, "top_refs.tsv"), "w") as fh:
    fh.write("type\twhat\tresults\tworkers\tmean_est_tokens\tusd\tshare\trewrite_usd\n")
    for i, (k, t) in enumerate(sorted(tr.items(), key=lambda kv: -kv[1][2])):
        fh.write("%s\t%s\t%d\t%d\t%.0f\t%.4f\t%.4f\t%.4f\n" % (k[0], k[1], t[0], len(t[4]), t[1] / t[0], t[2], t[2] / TOT, t[3]))
        if i < 20:
            P("| %d | %s | %s | %d | %d | %s | %s | %.1f%% | %s |" % (i + 1, k[0], k[1], t[0], len(t[4]), "{:,.0f}".format(t[1] / t[0]), money(t[2]), 100 * t[2] / TOT, money(t[3])))
P("\nSeparately, the 10 costliest lab scripts only:\n")
P("| rank | script | results | workers | mean est. tokens | USD | share of lab-script USD |")
P("|--:|:--|--:|--:|--:|--:|--:|")
sc = [(k, t) for k, t in tr.items() if k[0] == "script" and (k[1].startswith("scripts/") or k[1].startswith("__instrumenta__/"))]
sct = sum(t[2] for k, t in sc)
for i, (k, t) in enumerate(sorted(sc, key=lambda kv: -kv[1][2])[:10]):
    P("| %d | %s | %d | %d | %s | %s | %.1f%% |" % (i + 1, k[1], t[0], len(t[4]), "{:,.0f}".format(t[1] / t[0]), money(t[2]), 100 * t[2] / sct))
P("\nLab-script USD in all: %s over %d results (%.1f%% of all context USD)." % (money(sct), sum(t[0] for k, t in sc), 100 * sct / TOT))

# ---- 4. counterfactual caps
P("\n## 4. ESTIMATE: ceiling saving if each output were capped, or a document read by section only\n")
P("Formula: for an element with t tokens and context USD c (first write + reads + re-writes), a cap of K tokens leaves c x min(1, K/t), because every later request carries the element, so its whole cost is proportional to its tokens (same position in the life of the worker, same pauses). Saving = sum over capped elements of c x max(0, 1 - K/t). It is a ceiling: it assumes the cut text was not needed, that no extra call is made to get it, and that the worker's answer does not change. 'By section only' is the same formula with K = the section size read (a Read with offset and limit).\n")
groups = [("lab script output", lambda r: r["src"].startswith("lab script")),
          ("documents, Read", lambda r: r["cls"] == "readdoc"),
          ("documents, Bash cat/sed/head/tail", lambda r: r["cls"] == "bashdoc"),
          ("all documents (Read + Bash)", lambda r: r["cls"] in ("readdoc", "bashdoc")),
          ("lab scripts + all documents", lambda r: r["cls"] in ("readdoc", "bashdoc") or r["src"].startswith("lab script")),
          ("source code (Read + Bash)", lambda r: r["cls"] in ("readsrc", "bashsrc")),
          ("every tool result", TOOLRES)]
caps = [1000, 2500, 5000, 10000]
P("| group | elements | USD now | share | " + " | ".join("saving at cap %s tokens" % "{:,}".format(c) for c in caps) + " | elements above 2,500 tokens |")
P("|:--|--:|--:|--:|" + "--:|" * len(caps) + "--:|")
for name, f in groups:
    S = [r for r in R if f(r)]
    cu = sum(r["usd"] for r in S)
    cells = []
    for K in caps:
        sv = sum(r["usd"] * max(0.0, 1 - K / r["est_tokens"]) for r in S if r["est_tokens"] > 0)
        cells.append("%s (%.1f%% of all)" % (money(sv), 100 * sv / TOT))
    P("| %s | %d | %s | %.1f%% | " % (name, len(S), money(cu), 100 * cu / TOT) + " | ".join(cells) + " | %d |" % sum(1 for r in S if r["est_tokens"] > 2500))

# ---- 5. duplicates and early reads
P("\n## 5. Duplicate reads of one document by one worker (ceiling saving: every read after the first is not needed)\n")
seen = collections.defaultdict(list)
for r in R:
    if r["cls"] in ("readdoc", "bashdoc") and r["ref"]:
        seen[(r["agent_id"], r["ref"])].append(r)
dup_n = dup_usd = 0
dup_by = collections.Counter()
for (a, ref), L_ in seen.items():
    if len(L_) > 1:
        L_.sort(key=lambda r: r["entered_at_request"])
        for r in L_[1:]:
            dup_n += 1; dup_usd += r["usd"]; dup_by[base_kind(r["kind"])] += r["usd"]
P("Repeat reads (same worker, same path, route Read or Bash): %d results, USD %s (%.1f%% of all context USD): %s." % (dup_n, money(dup_usd), 100 * dup_usd / TOT, "; ".join("%s %s" % (k, money(v)) for k, v in dup_by.most_common())))
# same lab document read by many workers (wave note per wave)
P("\n## 6. Position in the worker's life\n")
early = sum(r["usd"] for r in R if r["cls"] in ("readdoc", "bashdoc") and r["entered_at_request"] <= 3)
P("Document results that entered in the first 4 requests: USD %s (%.1f%% of all context USD; %.0f%% of document USD)." % (money(early), 100 * early / TOT, 100 * early / dsum))
# per-worker distribution
pw = collections.defaultdict(float); pwd = collections.defaultdict(float)
for r in R:
    pw[r["agent_id"]] += r["usd"]
    if r["cls"] in ("readdoc", "bashdoc"): pwd[r["agent_id"]] += r["usd"]
P("Per worker: total context USD median %s, mean %s, max %s; document share of a worker's USD median %.0f%%." % (money(sorted(pw.values())[len(pw) // 2]), money(TOT / len(pw)), money(max(pw.values())), 100 * sorted(pwd[a] / pw[a] for a in pw)[len(pw) // 2]))


P("\n## 7. USD per 1,000 tokens of one tool result, by the request at which it entered (all tool results)\n")
P("| entered at request | results | mean later requests | USD per 1,000 tokens (mean of sums) | of which re-write share |")
P("|:--|--:|--:|--:|--:|")
for lo, hi in ((1, 3), (4, 10), (11, 30), (31, 60), (61, 1000)):
    S = [r for r in R if TOOLRES(r) and lo <= r["entered_at_request"] <= hi and r["est_tokens"] > 0]
    if S:
        P("| %d-%d | %d | %.0f | %.4f | %.0f%% |" % (lo, hi, len(S), sum(r["later_requests"] for r in S) / len(S), 1000 * sum(r["usd"] for r in S) / sum(r["est_tokens"] for r in S), 100 * sum(r["rewrite_usd"] for r in S) / sum(r["usd"] for r in S)))
P("\nA document of 23,000 tokens read at request 2 would, at the first bucket's rate, cost USD %.2f in the life of one worker (ESTIMATE: tokens x USD per token of the bucket)." % (23 * 1000 * sum(r["usd"] for r in R if TOOLRES(r) and 1 <= r["entered_at_request"] <= 3 and r["est_tokens"] > 0) / sum(r["est_tokens"] for r in R if TOOLRES(r) and 1 <= r["entered_at_request"] <= 3 and r["est_tokens"] > 0)))

open(os.path.join(folder, "tables.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
