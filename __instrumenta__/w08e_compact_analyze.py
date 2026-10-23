# Summarises one headless compaction run of w08e_compact_run.py (stream.jsonl, debug.log, hooks.log, summary.txt, stream_resume.jsonl) into a markdown block on stdout: compaction events, the compaction requests' own usage and Opus-5.5 list price, visible vs total usage, fact survival, resume-brief injection size.
"""usage: w08e_compact_analyze.py RUNDIR   (prints markdown; reads only the files named above; never prints transcript text, only counts and booleans)
Opus 5.5 list price per million tokens (scripts/lab_status.py PRICES): input 4, output 20, cache read 0.20, cache write 5 min 5, 1 h 8. A compaction request's `input` is uncached input (priced 4), `cacheCreate` is a write (priced 8, 1 h tier assumed)."""
import json, os, re, sys

D = sys.argv[1]
OP = dict(i=4.0, o=20.0, r=0.20, w=8.0)
def opus(i, o, r, w): return (i * OP["i"] + o * OP["o"] + r * OP["r"] + w * OP["w"]) / 1e6

def jl(path):
    out = []
    if not os.path.exists(path): return out
    for ln in open(path, errors="replace"):
        try: out.append(json.loads(ln))
        except ValueError: pass
    return out

st = jl(os.path.join(D, "stream.jsonl"))
req = {}
order = []
for d in st:
    if d.get("type") == "assistant":
        m = d["message"]; u = m.get("usage") or {}
        if m["id"] not in req: order.append(m["id"])
        req[m["id"]] = (u.get("input_tokens", 0), u.get("output_tokens", 0), u.get("cache_read_input_tokens", 0), u.get("cache_creation_input_tokens", 0))
res = [d for d in st if d.get("type") == "result"]
mu = list(res[0]["modelUsage"].values())[0] if res else {}
tot = (mu.get("inputTokens", 0), mu.get("outputTokens", 0), mu.get("cacheReadInputTokens", 0), mu.get("cacheCreationInputTokens", 0))
vis = tuple(sum(req[k][j] for k in req) for j in range(4))
bnd = [d.get("compact_metadata") for d in st if d.get("type") == "system" and d.get("subtype") == "compact_boundary"]
print("## run %s" % os.path.basename(D.rstrip("/")))
print("visible requests %d, compact_boundary events %d, turns %s, total_cost_usd (haiku list) %s, wall in meta %s s" % (
    len(req), len(bnd), res[0].get("num_turns") if res else None, res[0].get("total_cost_usd") if res else None, json.load(open(os.path.join(D, "meta.json")))["wall_s"]))
print("\ncontext per visible request (input+read+write): " + ", ".join(str(sum(req[k][j] for j in (0, 2, 3))) for k in order))
print("\n| compaction | trigger | pre_tokens | post_tokens | duration_ms |\n|--:|:--|--:|--:|--:|")
for n, b in enumerate(bnd, 1):
    print("| %d | %s | %d | %d | %d |" % (n, b.get("trigger"), b.get("pre_tokens", 0), b.get("post_tokens", 0), b.get("duration_ms", 0)))
dbg = open(os.path.join(D, "debug.log"), errors="replace").read()
fa = re.findall(r"Forked agent \[([\w-]+)\] finished: (\d+) messages.*?totalUsage: input=(\d+) output=(\d+) cacheRead=(\d+) cacheCreate=(\d+)", dbg)
print("\n| compaction request | agent | input (uncached) | output | cache read | cache write | USD at Opus 5.5 list |\n|--:|:--|--:|--:|--:|--:|--:|")
sums = [0, 0, 0, 0]
for n, (a, _m, i, o, r, w) in enumerate(fa, 1):
    i, o, r, w = int(i), int(o), int(r), int(w)
    for j, v in enumerate((i, o, r, w)): sums[j] += v
    print("| %d | %s | %d | %d | %d | %d | %.3f |" % (n, a, i, o, r, w, opus(i, o, r, w)))
print("\nreconciliation (input, output, read, write): total from result %s; visible requests %s; difference %s; sum of forked-agent lines %s" % (
    tot, vis, tuple(t - v for t, v in zip(tot, vis)), tuple(sums)))
print("autocompact lines: " + ", ".join(sorted(set(re.findall(r"autocompact: tokens=\S+ level=(\w+) effectiveWindow=(\d+)", dbg) and ["level=%s window=%s" % x for x in re.findall(r"autocompact: tokens=\S+ level=(\w+) effectiveWindow=(\d+)", dbg)]))))
print("routing: " + str(sorted(set(re.findall(r"autocompact: routing through (\w+) \(thresholdSource=(\w+)\)", dbg)))))
print("bail lines: %d (\"no assistant messages in summarize set\")" % dbg.count("no assistant messages in summarize set"))
inj = re.findall(r"Hook SessionStart:(\w+) \(SessionStart\) success:\\n# Lab brief[^\n]*", dbg)
lens = [len(m) for m in re.findall(r"Hook SessionStart:compact \(SessionStart\) success:\\n(# Lab brief[^\n]*)", dbg)]
print("resume_brief output on SessionStart:compact: %d injections, escaped-line lengths (chars) %s" % (len(lens), lens))
if os.path.exists(os.path.join(D, "debug_resume.log")):
    d2 = open(os.path.join(D, "debug_resume.log"), errors="replace").read()
    l2 = [len(m) for m in re.findall(r"Hook SessionStart:resume \(SessionStart\) success:\\n(# Lab brief[^\n]*)", d2)]
    print("resume_brief output on SessionStart:resume: %d injections, lengths %s" % (len(l2), l2))
facts = {"number 48213": "48213", "path /opt/zeta/config.toml": "/opt/zeta/config.toml", "quote (heron ... blue ink)": "heron files its taxes in blue ink", "audit code KX-9917": "KX-9917"}
hl = jl(os.path.join(D, "hooks.log"))
print("hooks.log events: " + ", ".join("%s/%s" % (h["event"], h.get("trigger") or h.get("source")) for h in hl))
sp = os.path.join(D, "summary.txt")
summ = open(sp, errors="replace").read() if os.path.exists(sp) else ""
print("\nlast PostCompact summary: %d chars; facts present verbatim: %s" % (len(summ), {k: (v in summ) for k, v in facts.items()}))
rs = jl(os.path.join(D, "stream_resume.jsonl"))
txt = "\n".join(c.get("text", "") for d in rs if d.get("type") == "assistant" for c in d["message"]["content"] if c.get("type") == "text")
print("after --resume, model's answer (facts named verbatim): %s" % {k: (v in txt) for k, v in facts.items()} if rs else "no resume run")

# ref codes: which of the per-file codes the model could still give exactly after --resume, by the number of compactions that came after the file was read
cp = os.path.join(D, "codes.json")
if os.path.exists(cp) and rs:
    codes = json.load(open(cp)); epoch = 0; read_epoch = {}
    for d in st:
        if d.get("type") == "system" and d.get("subtype") == "compact_boundary": epoch += 1
        if d.get("type") == "assistant":
            for c in d["message"]["content"]:
                if c.get("type") == "tool_use" and c.get("name") == "Read":
                    m = re.search(r"/fill/f(\d+)\.txt", c["input"].get("file_path", ""))
                    if m: read_epoch.setdefault(int(m.group(1)), epoch)
    got = dict((int(a), b) for a, b in re.findall(r"\bf(\d+)\s*=\s*([A-Z]+|UNKNOWN)", txt))
    print("\nref codes after --resume (files read: %d, total compactions %d)" % (len(read_epoch), epoch))
    print("| compactions after the file was read | files | exact code given | UNKNOWN | wrong code |\n|--:|--:|--:|--:|--:|")
    for k in range(epoch + 1):
        fs = [n for n, e in read_epoch.items() if epoch - e == k]
        ok = sum(1 for n in fs if got.get(n) == codes[str(n)]); unk = sum(1 for n in fs if got.get(n, "UNKNOWN") == "UNKNOWN")
        print("| %d | %d | %d | %d | %d |" % (k, len(fs), ok, unk, len(fs) - ok - unk))
    sm = open(sp, errors="replace").read() if os.path.exists(sp) else ""
    print("codes present verbatim in last PostCompact summary: %d of %d" % (sum(1 for c in codes.values() if c in sm), len(codes)))
