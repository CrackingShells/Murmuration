# Scores PI-like compaction runs of w08_c3_run.py (stream.jsonl, debug.log, truth.json, meta.json) into one tsv row per run on stdout: items correct Q1..Q5, compaction request and context numbers, re-reads after the boundary, hook time, spend re-priced at Opus 5.5 list.
"""usage: w08_c3_score.py RUNS_DIR [NAME ...]   (RUNS_DIR = S/runs; default: every run folder with a final answer). Prints no transcript text; the final answer is scored by regular expressions against truth.json.
Prices per million tokens, Opus 5.5 list (scripts/lab_status.py PRICES): input 4, output 20, cache read 0.20, cache write 5 min 5, 1 h 8 (output of the compaction request: usage of the forked agent, debug.log).
Columns: run arm model seed reports boundary_at pre post comp_s comp_usd next_write q1 q1_lenient q2 q3 q4 q5 reread_calls reread_tok reread_files hook_ms total_usd_opus55 cost_reported ctx_last sum_chars s_sentence s_names s_next s_labels s_q5."""
import glob, json, os, re, sys

PR = dict(i=4.0, o=20.0, r=0.20, w5=5.0, w1=8.0)
def norm(t): return re.sub(r"\s+", " ", re.sub(r"[`*‘’“”\"']", "", t)).strip().lower()

def sections(text):
    marks = list(re.finditer(r"(?m)^\s*(?:[#>*\-\s]*)\(?([1-5])[\).:]\s|^\s*\*\*\(?([1-5])[\).:]", text))
    out = {}
    for n, m in enumerate(marks):
        k = int(m.group(1) or m.group(2))
        if k in out: continue
        out[k] = text[m.end():marks[n + 1].start()] if n + 1 < len(marks) else text[m.end():]
    return out

def score(text, t):
    sec = sections(text); whole = text
    ok_sec = all(k in sec for k in (1, 2, 3, 4, 5))
    s = lambda k: sec.get(k, whole)
    s1 = s(1); names = list(t["in_flight"])
    def has_pair(sx, n, cid):
        i = sx.find(n)
        return i >= 0 and cid in sx[i:i + 160]
    pairs = all(has_pair(s1, n, c) for n, c in t["in_flight"].items())
    q1_len = pairs
    q1 = pairs and not any(e in s1 for e in t["ended"])
    q2 = norm(t["sentence"]) in norm(whole)
    na = t["next_action"]; s3 = s(3)
    q3 = all(x in s3 for x in (na["worker"], na["claim"], na["label"], na["restate_by"], na["dispatch"], na["gap_claim"]))
    s4 = s(4); q4 = True
    for cid, lab in t["labels"].items():
        i = s4.find(cid); seg = s4[i:i + 220] if i >= 0 else ""
        good = bool(re.search(r"below MEASURED|restate", seg)) if lab.startswith("below") else bool(re.search(r"THEOREM[^\n]{0,40}gap|gap[^\n]{0,40}THEOREM|SOUND WITH GAP", seg, re.I))
        q4 = q4 and good
    s5 = s(5); q5 = t["q5"]["g"] in s5 and bool(re.search(r"k\s*=\s*%d\b" % t["q5"]["k"], s5))
    return dict(q1=q1, q1_lenient=q1_len, q2=q2, q3=q3, q4=q4, q5=q5, sectioned=ok_sec)

def summary_flags(name, t):
    """Booleans on the compaction summary (the isCompactSummary record of the run's session transcript; the text is never printed): chars, sentence verbatim, both in-flight names, next-step names, both labels, q5 value."""
    fs = glob.glob(os.path.expanduser("~/.claude/projects/*author-w08-3-runs-%s-lab/*.jsonl" % name.replace("_", "-")))
    if not fs: return ["-"] * 6
    text = ""
    for l in open(fs[0], errors="replace"):
        if '"isCompactSummary":true' in l.replace(" ", ""):
            try: d = json.loads(l)
            except ValueError: continue
            c = d["message"]["content"]; text = c if isinstance(c, str) else " ".join(b.get("text", "") for b in c)
            break
    if not text: return ["-"] * 6
    n = norm(text); na = t["next_action"]
    return [len(text), int(norm(t["sentence"]) in n), int(all(norm(x) in n for x in t["in_flight"])), int(all(norm(x) in n for x in (na["restate_by"], na["dispatch"], na["worker"]))),
            int(all(norm(x) in n for x in t["labels"]) and "below measured" in n), int(t["q5"]["g"] in n)]

def one(RD, name):
    D = os.path.join(RD, name); t = json.load(open(os.path.join(D, "truth.json"))); m = json.load(open(os.path.join(D, "meta.json")))
    rows = []
    for l in open(os.path.join(D, "stream.jsonl")):
        try: rows.append(json.loads(l))
        except ValueError: pass
    # usage per message id, max over rows; context per request
    use = {}; order = []
    for d in rows:
        if d.get("type") == "assistant":
            mm = d["message"]; u = mm.get("usage") or {}
            if mm["id"] not in use: use[mm["id"]] = {}; order.append(mm["id"])
            c = use[mm["id"]]
            for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"): c[k] = max(c.get(k, 0), u.get(k, 0) or 0)
            cc = u.get("cache_creation") or {}
            c["w1"] = max(c.get("w1", 0), cc.get("ephemeral_1h_input_tokens", 0) or 0); c["w5"] = max(c.get("w5", 0), cc.get("ephemeral_5m_input_tokens", 0) or 0)
    usd = 0.0
    for k in order:
        u = use[k]; w1, w5 = u["w1"], u["w5"]
        if w1 + w5 < u["cache_creation_input_tokens"]: w5 += u["cache_creation_input_tokens"] - w1 - w5
        usd += (u["input_tokens"] * PR["i"] + u["output_tokens"] * PR["o"] + u["cache_read_input_tokens"] * PR["r"] + w1 * PR["w1"] + w5 * PR["w5"]) / 1e6
    dbg = open(os.path.join(D, "debug.log"), errors="replace").read()
    fa = re.findall(r"Forked agent \[([\w-]+)\] finished: \d+ messages.*?totalUsage: input=(\d+) output=(\d+) cacheRead=(\d+) cacheCreate=(\d+)", dbg)
    comp_usd = sum((int(a) * 4 + int(b) * 20 + int(c) * 0.2 + int(d) * 8) / 1e6 for _, a, b, c, d in fa)
    usd += comp_usd
    hooks = re.findall(r"hooks module [\w@.\-]+ classic\.PreCompact settled in ([\d.]+)ms", dbg)
    bidx = [i for i, d in enumerate(rows) if d.get("type") == "system" and d.get("subtype") == "compact_boundary"]
    pre = post = comp_s = ""; nextw = ""; summ = ""
    if bidx:
        cm = rows[bidx[0]]["compact_metadata"]; pre, post, comp_s = cm["pre_tokens"], cm["post_tokens"], round(cm["duration_ms"] / 1000, 1)
        for d in rows[bidx[0]:]:
            if d.get("type") == "assistant":
                u = d["message"]["usage"]; nextw = u.get("cache_creation_input_tokens"); break
    # re-reads: tool calls after the first boundary; a Read of the turn's own report is not a re-read
    turn = -1; calls = []; tu = {}
    for i, d in enumerate(rows):
        if d.get("type") == "system" and d.get("subtype") == "init": turn += 1
        if bidx and i > bidx[0]:
            if d.get("type") == "assistant":
                for b in d["message"]["content"]:
                    if b.get("type") == "tool_use":
                        inp = b.get("input") or {}; tgt = inp.get("file_path") or inp.get("command") or inp.get("pattern") or ""
                        own = 1 <= turn <= len(t["reports"]) and (t["reports"][turn - 1] in tgt) and b["name"] == "Read"
                        tu[b["id"]] = (b["name"], tgt, own)
            elif d.get("type") == "user" and isinstance(d["message"].get("content"), list):
                for b in d["message"]["content"]:
                    if b.get("type") == "tool_result" and b.get("tool_use_id") in tu:
                        c = b.get("content"); L = len(c) if isinstance(c, str) else len(json.dumps(c))
                        n, tgt, own = tu[b["tool_use_id"]]
                        if not own: calls.append((n, os.path.basename(tgt.split()[-1]) if tgt else "", L))
    final = ""
    for d in rows:
        if d.get("type") == "result": final = d.get("result") or final
    sc = score(final, t) if m.get("final_sent") else dict(q1="", q1_lenient="", q2="", q3="", q4="", q5="", sectioned="")
    cost = [d.get("total_cost_usd") for d in rows if d.get("type") == "result"]
    ctxs = [use[k]["input_tokens"] + use[k]["cache_read_input_tokens"] + use[k]["cache_creation_input_tokens"] for k in order]
    return [name, m["arm"], m["model"], m["seed"], m["reports_read"], m["after_boundary_at_report"], pre, post, comp_s, "%.3f" % comp_usd, nextw,
            *[int(bool(sc[k])) if sc[k] != "" else "" for k in ("q1", "q1_lenient", "q2", "q3", "q4", "q5")],
            len(calls), round(sum(c[2] for c in calls) / 2.4), re.sub(r"[^\w.;-]", "", ";".join(sorted({c[1] for c in calls})))[:60] or "-", ",".join(hooks), "%.2f" % usd, "%.3f" % (cost[-1] if cost else 0), ctxs[-1] if ctxs else "", *summary_flags(name, t)]

if __name__ == "__main__":
    RD = sys.argv[1]; names = sys.argv[2:] or sorted(os.path.basename(p) for p in glob.glob(os.path.join(RD, "*")) if os.path.exists(os.path.join(p, "meta.json")))
    print("\t".join("run arm model seed reports boundary_at pre post comp_s comp_usd next_write q1 q1_lenient q2 q3 q4 q5 reread_calls reread_tok reread_files hook_ms total_usd_opus55 cost_reported ctx_last sum_chars s_sentence s_names s_next s_labels s_q5".split()))
    for n in names:
        try: print("\t".join(("-" if x in ("", None) else str(x)) for x in one(RD, n)))
        except Exception as e: print(n, "ERROR", repr(e)[:100])
