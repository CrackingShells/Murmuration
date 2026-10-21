# per worker transcript (subagents/agent-*.jsonl + .meta.json): splits requests, list-price USD, tokens and active time into phases (preamble, orientation, work, deliver, exchange, resumes), counts failed/repeated calls, re-reads and large tool outputs; inputs: a subagents folder (+ optional harness.jsonl); outputs: a CSV (one row per worker) and a JSON detail file
import json, glob, os, re, sys, importlib.util, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("lab_status", os.path.join(HERE, "..", "scripts", "lab_status.py"))
LS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LS)  # reuse PRICES and message_usd (list price, same table as /lab-status)

SCRATCH_OK = ("/private/tmp/", "/tmp/")
DOC_PAT = re.compile(r"(framing\.md|/agents/|^agents/|/skills/|^skills/|synthesis\.md|wave-0\d\.md|briefs\.md|user_words|README|AGENTS\.md|CLAUDE\.md|__scrupuli__|working_defaults|waves\.md|references/)")
DELIV_PAT = re.compile(r"(__pondus__|__reports__|__scrupuli__)")
RUN_PAT = re.compile(r"(python3?\b|\bpytest\b|\bbash\b|\bsh\b |claude -p|\./|node |make |colgrep|jq |sqlite3)")
LOOK_PAT = re.compile(r"^\s*(cd [^;&|]+(&&|;)\s*)?(ls|cat|sed|head|tail|git (log|show|diff|status|rev-parse|branch)|grep|rg|wc|diff|stat|file|find|nl|awk|echo|pwd|test|date|git -C)\b")


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def text_of(content):
    if isinstance(content, str):
        return content
    out = []
    for b in content or []:
        if isinstance(b, dict):
            if b.get("type") == "text":
                out.append(b.get("text", ""))
            elif b.get("type") == "tool_result":
                out.append(text_of(b.get("content")))
    return "\n".join(out)


def categorize(name, inp, cwd):
    """One tool call -> category. Order of strength is in PRIORITY."""
    if name == "SubagentHandback":
        return "handback"
    if name == "SendMessage":
        return "exchange"
    if name in ("ToolSearch", "Glob") or name.startswith("mcp__plugin_colgrep"):
        return "search"
    if name in ("Monitor", "TaskOutput", "TaskStop"):
        return "wait"
    if name in ("Write", "Edit"):
        p = inp.get("file_path", "")
        return "deliver" if DELIV_PAT.search(p) else "write-other"
    if name == "Read":
        p = inp.get("file_path", "")
        if DOC_PAT.search(p):
            return "doc"
        if not p.startswith(cwd) and not p.startswith(SCRATCH_OK):
            return "outside"
        return "look"
    if name == "Bash":
        c = inp.get("command", "")
        if re.search(r"git commit", c):
            return "deliver"
        if re.search(r"(cat|tee)\s+>>?\s*\S*(__pondus__|__reports__|__scrupuli__)", c) or re.search(r">>?\s*\S*(__pondus__|__reports__|__scrupuli__)", c):
            return "deliver"
        if re.search(r"(cat|tee)\s+>>?\s*\S+", c) and "<<" in c:
            return "write-other"
        if RUN_PAT.search(c) and not LOOK_PAT.match(c):
            return "run"
        paths = re.findall(r"(/Users/hacker/[^\s'\"<>|;&)]*|~/\.claude[^\s'\"<>|;&)]*)", c)
        if any(not p.startswith(cwd) and not p.startswith(SCRATCH_OK) for p in paths):
            return "outside"
        if DOC_PAT.search(c):
            return "doc"
        if LOOK_PAT.match(c):
            return "look"
        return "run"
    return "other"


PRIORITY = ["handback", "exchange", "deliver", "run", "write-other", "outside", "doc", "search", "wait", "look", "other"]


def analyse(path, harness_end):
    rows = [json.loads(l) for l in open(path)]
    meta = json.load(open(path[:-6] + ".meta.json"))
    cwd = next((r["cwd"] for r in rows if r.get("cwd")), "")
    # ---- requests: group assistant records by message id
    reqs, order = {}, []
    results = {}  # tool_use_id -> dict
    events = []   # (idx, kind, ts, info)
    pre_chars = collections.Counter()  # chars before the first assistant record, by kind
    seen_assistant = False
    for i, r in enumerate(rows):
        t = ts(r["timestamp"]) if r.get("timestamp") else None
        k = r.get("type")
        if k == "assistant" and isinstance(r.get("message"), dict):
            seen_assistant = True
            m = r["message"]
            key = m.get("id") or r.get("requestId") or r.get("uuid")
            if key not in reqs:
                reqs[key] = dict(model=m.get("model"), usage={}, t_first=t, t_last=t, idx=i, calls=[], prev_t=None, final=False)
                order.append(key)
            q = reqs[key]
            LS.merge_usage(q["usage"], m.get("usage") or {})
            if isinstance(m.get("usage", {}).get("cache_creation"), dict):
                q["usage"]["cache_creation"] = m["usage"]["cache_creation"]
            q["usage"]["speed"] = (m.get("usage") or {}).get("speed")
            q["t_last"] = t
            q["final"] = bool(m.get("stop_reason"))
            for b in m.get("content") or []:
                if b.get("type") == "tool_use":
                    q["calls"].append(dict(id=b["id"], name=b["name"], input=b.get("input") or {}))
                if b.get("type") == "text":
                    q["content_chars"] = q.get("content_chars", 0) + len(b.get("text", ""))
                elif b.get("type") == "tool_use":
                    q["content_chars"] = q.get("content_chars", 0) + len(json.dumps(b.get("input") or {}))
        elif k == "user" and isinstance(r.get("message"), dict):
            c = r["message"].get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        tx = text_of(b.get("content"))
                        results[b["tool_use_id"]] = dict(t=t, chars=len(tx), err=bool(b.get("is_error")), head=tx[:160].replace("\n", " "), idx=i)
            if not seen_assistant:
                pre_chars["user:brief+skill"] += len(json.dumps(c))
            o = r.get("origin")
            if o and seen_assistant:
                events.append((i, "resume-user", t, o))
        elif k == "attachment":
            a = r.get("attachment") or {}
            at = a.get("type")
            if not seen_assistant:
                pre_chars["attach:" + str(at)] += len(json.dumps(a))
            elif at == "queued_command":
                events.append((i, "queued", t, a.get("origin") or {}))
    # ---- request sequence with previous-record time
    seq = [reqs[k] for k in order]
    for q in seq:
        # time of the record immediately before this request's first record
        j = q["idx"] - 1
        while j >= 0 and not rows[j].get("timestamp"):
            j -= 1
        q["prev_t"] = ts(rows[j]["timestamp"]) if j >= 0 else q["t_first"]
        q["prev_type"] = rows[j].get("type")
    # resume boundaries: user rows with origin after first assistant, whose predecessor request ended with a handback
    resume_idx = [e for e in events if e[1] == "resume-user"]
    # the request index at which each run starts
    run_of = [0] * len(seq)
    bounds = []
    for (i, _, t, o) in resume_idx:
        bounds.append((i, t, o))
    for n, q in enumerate(seq):
        run_of[n] = sum(1 for b in bounds if b[0] < q["idx"])
    # ---- per-request cost, tokens, time, category
    out_reqs = []
    for n, q in enumerate(seq):
        u = q["usage"]
        # output tokens: the transcript keeps the start-of-stream count; same estimate as scripts/budget.py (max(recorded, chars / 1.3))
        u["output_tokens"] = max(int(u.get("output_tokens") or 0), int(q.get("content_chars", 0) / 1.3))
        usd = LS.message_usd(q["model"], u) or 0.0
        cw = int(u.get("cache_creation_input_tokens") or 0)
        cr = int(u.get("cache_read_input_tokens") or 0)
        inp = int(u.get("input_tokens") or 0)
        outt = int(u.get("output_tokens") or 0)
        cats = [categorize(c["name"], c["input"], cwd) for c in q["calls"]]
        cat = next((p for p in PRIORITY if p in cats), "none")
        tool_end = max([results[c["id"]]["t"] for c in q["calls"] if c["id"] in results and results[c["id"]]["t"]] or [q["t_last"]])
        tool_end = max(tool_end, q["t_last"])
        if n == 0:
            prev_end = ts(rows[0]["timestamp"])
        elif run_of[n] > run_of[n - 1]:
            prev_end = bounds[run_of[n] - 1][1]  # the resume message
        else:
            prev_end = out_reqs[n - 1]["end"]
        model_s = max(0.0, q["t_last"] - prev_end)
        tool_s = max(0.0, tool_end - q["t_last"])
        out_reqs.append(dict(end=tool_end, n=n, run=run_of[n], cat=cat, cats=cats, usd=usd, cw=cw, cr=cr, inp=inp, out=outt, ctx=inp + cw + cr, model_s=model_s, tool_s=tool_s, t=q["t_first"], calls=q["calls"]))
    # idle gaps: for the first request of a resumed run, prev_t is the resume message; the gap from the previous request's tool end to the resume message is idle
    idle_total = 0.0
    resume_rows = []
    for ridx in range(1, (max(run_of) if run_of else 0) + 1):
        first = next(x for x in out_reqs if x["run"] == ridx)
        prev = [x for x in out_reqs if x["run"] == ridx - 1]
        prev_end = max(seq[prev[-1]["n"]]["t_last"], max([results[c["id"]]["t"] for c in prev[-1]["calls"] if c["id"] in results] or [0])) if prev else None
        b = bounds[ridx - 1]
        gap = (b[1] - prev_end) if prev_end else 0
        idle_total += max(0, gap)
        runreq = [x for x in out_reqs if x["run"] == ridx]
        resume_rows.append(dict(run=ridx, origin=b[2].get("kind"), frm=b[2].get("from"), idle_s=round(gap, 1), first_cw=first["cw"], first_cr=first["cr"], first_ctx=first["ctx"],
                                first_usd=round(first["usd"], 4), requests=len(runreq), usd=round(sum(x["usd"] for x in runreq), 4),
                                active_s=round(sum(x["model_s"] + x["tool_s"] for x in runreq), 1)))
    # ---- phases
    # orientation prefix: requests before the first run/write/deliver/exchange/handback request
    first_act = next((x["n"] for x in out_reqs if x["cat"] in ("run", "write-other", "deliver", "exchange", "handback")), len(out_reqs))
    for x in out_reqs:
        x["prefix"] = x["n"] < first_act and x["run"] == 0
    # ---- tool-result sizes and carry cost
    p = LS.PRICES[re.sub(r"-\d{8}$", "", out_reqs[0]["model"] if False else (seq[0]["model"] or "claude-sonnet-5-5"))]
    carry = []
    for n, x in enumerate(out_reqs):
        for c in x["calls"]:
            r = results.get(c["id"])
            if not r:
                continue
            toks = r["chars"] / 4.0  # [assumption: 4 characters per token]
            later = len(out_reqs) - n - 1
            usd = toks * (p[3] + later * p[2]) / 1e6  # one cache write, then a cache read per later request
            carry.append(dict(n=n, name=c["name"], cat=categorize(c["name"], c["input"], cwd), chars=r["chars"], later=later, usd=usd, err=r["err"], head=r["head"], arg=(c["input"].get("command") or c["input"].get("file_path") or json.dumps(c["input"]))[:140].replace("\n", " ")))
    # ---- failed and repeated calls
    fails = [dict(n=n, name=c["name"], head=results[c["id"]]["head"], arg=(c["input"].get("command") or c["input"].get("file_path") or "")[:100].replace("\n", " ")) for n, x in enumerate(out_reqs) for c in x["calls"] if c["id"] in results and results[c["id"]]["err"]]
    reads = collections.Counter()
    for x in out_reqs:
        for c in x["calls"]:
            if c["name"] == "Read":
                reads[c["input"].get("file_path")] += 1
            elif c["name"] == "Bash":
                cm = c["input"].get("command", "")
                m = re.match(r"\s*(cat|head -\d+|sed -n '[^']*'|tail -\d+)\s+(\S+)\s*$", cm)
                if m:
                    reads[m.group(2)] += 1
    rereads = {k: v for k, v in reads.items() if v > 1}
    cmds = collections.Counter(c["input"].get("command", "")[:300] for x in out_reqs for c in x["calls"] if c["name"] == "Bash")
    repeats = {k: v for k, v in cmds.items() if v > 1 and len(k) > 25}
    # cache misses inside a run: ctx well above previous ctx but cache_read far below previous total
    misses = []
    for n in range(1, len(out_reqs)):
        a, b = out_reqs[n - 1], out_reqs[n]
        if b["run"] == a["run"] and b["cw"] > 0.5 * a["ctx"] and b["cr"] < 0.5 * a["ctx"]:
            misses.append(dict(n=n, gap_s=round(seq[n]["prev_t"] - seq[n - 1]["t_last"], 1), cw=b["cw"], usd_extra=round(b["cw"] * (p[3] - p[2]) / 1e6, 4)))
    return dict(path=path, meta=meta, cwd=cwd, reqs=out_reqs, resumes=resume_rows, carry=carry, fails=fails, rereads=rereads, repeats=repeats, misses=misses,
                pre_chars=dict(pre_chars), idle_total=idle_total, harness=harness_end.get(path.split("agent-")[1][:-6]), bounds=[(b[0], b[1], b[2].get("kind")) for b in bounds], prices=p, nqueued=sum(1 for e in events if e[1] == "queued"))


def main():
    sub, outdir = sys.argv[1], sys.argv[2]
    harness = sys.argv[3] if len(sys.argv) > 3 else None
    hend = {}
    if harness:
        for l in open(harness):
            d = json.loads(l)
            if d.get("event") == "end":
                hend[d["agent_id"]] = d  # last end line wins (cumulative)
    os.makedirs(outdir, exist_ok=True)
    detail, rows = {}, []
    for f in sorted(glob.glob(os.path.join(sub, "agent-*.jsonl"))):
        a = analyse(f, hend)
        name = a["meta"].get("name") or os.path.basename(f)
        detail[name] = a
        R = a["reqs"]
        tot = lambda key, sel=lambda x: True: sum(x[key] for x in R if sel(x))
        total_usd = tot("usd")
        row = collections.OrderedDict(name=name, type=a["meta"].get("agentType", "").split(":")[-1], agent_id=os.path.basename(f)[6:-6], requests=len(R), runs=1 + len(a["resumes"]), usd_list=round(total_usd, 3),
                                      active_s_transcript=round(sum(x["model_s"] + x["tool_s"] for x in R), 0), active_s_harness=(a["harness"] or {}).get("active_s"), usd_harness=(a["harness"] or {}).get("used"))
        for c in PRIORITY + ["none"]:
            row["req_" + c] = sum(1 for x in R if x["cat"] == c)
            row["usd_" + c] = round(tot("usd", lambda x, c=c: x["cat"] == c), 4)
            row["s_" + c] = round(tot("model_s", lambda x, c=c: x["cat"] == c) + tot("tool_s", lambda x, c=c: x["cat"] == c), 0)
        row["req_prefix"] = sum(1 for x in R if x["prefix"])
        row["usd_prefix"] = round(tot("usd", lambda x: x["prefix"]), 4)
        row["s_prefix"] = round(tot("model_s", lambda x: x["prefix"]) + tot("tool_s", lambda x: x["prefix"]), 0)
        row["usd_first_request"] = round(R[0]["usd"], 4)
        row["first_ctx_tokens"] = R[0]["ctx"]
        row["usd_resume_runs"] = round(sum(r["usd"] for r in a["resumes"]), 3)
        row["resume_first_cw_tokens"] = sum(r["first_cw"] for r in a["resumes"])
        row["resume_first_usd"] = round(sum(r["first_usd"] for r in a["resumes"]), 4)
        row["failed_calls"] = len(a["fails"])
        row["rereads_extra"] = sum(v - 1 for v in a["rereads"].values())
        row["repeat_bash_extra"] = sum(v - 1 for v in a["repeats"].values())
        big = [c for c in a["carry"] if c["chars"] > 8000]
        row["results_over_8k"] = len(big)
        row["carry_usd_over_8k"] = round(sum(c["usd"] for c in big), 4)
        row["carry_usd_all"] = round(sum(c["usd"] for c in a["carry"]), 4)
        row["cache_miss_events"] = len(a["misses"])
        row["cache_miss_extra_usd"] = round(sum(m["usd_extra"] for m in a["misses"]), 4)
        rows.append(row)
    import csv
    with open(os.path.join(outdir, "worker_phase_table.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    slim = {}
    for name, a in detail.items():
        slim[name] = {k: v for k, v in a.items() if k not in ("reqs",)}
        slim[name]["reqs"] = [{k: v for k, v in x.items() if k != "calls"} | {"calls": [(c["name"], (c["input"].get("command") or c["input"].get("file_path") or "")[:160]) for c in x["calls"]]} for x in a["reqs"]]
    json.dump(slim, open(os.path.join(outdir, "worker_phase_detail.json"), "w"), indent=1, default=str)
    print("wrote", len(rows), "workers to", outdir)


if __name__ == "__main__":
    main()
