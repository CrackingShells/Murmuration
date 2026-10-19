#!/usr/bin/env python3
"""Read the cells under <scratch>/runs/ and print one table of what the hooks did. Read-only; stdlib only.

usage: analyze.py <scratch> [--tsv FILE]
Inputs per cell: meta.json, stdout.jsonl (stream, with hook events), lab/__statera__/harness.jsonl, handbacks/, lab/__reports__/,
and the subagent transcript under ~/.claude/projects/*-runs-<cell>-lab/ (read only). No raw payload is copied to the output."""
import collections, glob, hashlib, json, os, re, shutil, statistics, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
import budget  # noqa: E402  (the shipped script: the same reader the hook uses)

S = os.path.abspath(sys.argv[1])
TSV = sys.argv[sys.argv.index("--tsv") + 1] if "--tsv" in sys.argv else None


def requests_of(path):
    """Subagent transcript as a list of (requestId, [content blocks]) in order, streamed records merged."""
    out, idx = [], {}
    for line in open(path, encoding="utf-8", errors="replace"):
        r = json.loads(line)
        if r.get("type") != "assistant":
            continue
        k = r.get("requestId") or r["message"]["id"]
        if k not in idx:
            idx[k] = len(out); out.append((k, []))
        out[idx[k]][1].extend(r["message"].get("content") or [])
    return out


def cell(name):
    base = os.path.join(S, "runs", name)
    meta = json.load(open(os.path.join(base, "meta.json")))
    B = float(meta["B"]) if meta.get("B") not in (None, "", "none") else None
    lab = os.path.join(base, "lab")
    if B is None:   # the budget came from the hook's default (a scaled test copy), not from the brief: read it from the log
        lp = os.path.join(lab, "__statera__", "harness.jsonl")
        starts = [json.loads(x) for x in open(lp) if '"start"' in x] if os.path.exists(lp) else []
        B = starts[0]["B"] if starts else None
    row = dict(cell=name, time_min=meta.get("time") or None, plugin=meta["plugin"], type=meta["type"], B=B, wall_s=meta["wall_s"], total_usd=meta["usd"],
               worker_usd=meta["model_usd"].get("claude-sonnet-5-5"))
    log = []
    p = os.path.join(lab, "__statera__", "harness.jsonl")
    if os.path.exists(p):
        log = [json.loads(x) for x in open(p)]
    ev = collections.defaultdict(list)
    for x in log:
        ev[x["event"]].append(x)
    row.update({"n_" + k: len(ev[k]) for k in ("start", "note", "stop", "halt", "end", "deny")})
    sid = next(json.loads(l)["session_id"] for l in open(os.path.join(base, "stdout.jsonl")) if '"session_id"' in l)
    tdirs = glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents/agent-*.jsonl" % sid))
    assert len(tdirs) == 1, (name, tdirs)
    tx = tdirs[0]
    reqs = requests_of(tx)
    seen = budget.scan(tx)
    row["requests"] = len(reqs)
    # what the platform recorded as delivered to the worker (attachment records of its own transcript)
    att = [json.loads(l)["attachment"] for l in open(tx, encoding="utf-8", errors="replace") if '"attachment"' in l and "Lab harness" in l]
    row["note_delivered"] = sum(x.get("type") == "hook_additional_context" and "Lab harness note" in json.dumps(x) for x in att)
    row["stop_delivered"] = sum(x.get("type") == "hook_blocking_error" and "Call SubagentHandback now" in json.dumps(x) for x in att)
    recs_all = [json.loads(l) for l in open(tx, encoding="utf-8", errors="replace")]
    first_stop = next((i for i, x in enumerate(recs_all) if x.get("type") == "attachment" and x["attachment"].get("type") == "hook_blocking_error"
                       and "Call SubagentHandback now" in json.dumps(x["attachment"])), None)
    if first_stop is not None:
        row["stop_before_handback"] = not any(b.get("type") == "tool_use" and b.get("name") == "SubagentHandback"
                                              for x in recs_all[:first_stop] if x.get("type") == "assistant" for b in x["message"]["content"])
        row["tool_calls_after_first_stop"] = ",".join(b["name"] for x in recs_all[first_stop:] if x.get("type") == "assistant"
                                                      for b in x["message"]["content"] if b.get("type") == "tool_use")
        row["first_stop_frac"] = next(e["frac"] for e in ev["stop"])
    row["halt_delivered"] = sum("more than used up" in json.dumps(x) for x in att)
    row["recorded_usd"] = round(seen["usd_recorded"], 4)
    row["est_usd"] = round(seen["usd"], 4)
    row["exact_over_B"] = round(row["worker_usd"] / B, 3) if B else None
    row["recorded_share_of_exact"] = round(seen["usd_recorded"] / row["worker_usd"], 3)

    def reads(lo, hi):   # `cat fNN.txt` calls in requests lo < index <= hi (1-based)
        got = []
        for i, (_, blocks) in enumerate(reqs, 1):
            if lo < i <= hi:
                for b in blocks:
                    if b.get("type") == "tool_use" and b.get("name") == "Bash":
                        m = re.search(r"cat (f\d\d)\.txt", (b.get("input") or {}).get("command", ""))
                        got += [m.group(1)] if m else []
        return got
    total_reads = reads(0, len(reqs))
    row["files_read"] = len(set(total_reads))
    # where the marks 0.8 B and 1.0 B fall in the transcript, on each basis, by replaying prefixes of it through the shipped reader
    if B:
        recs = [json.loads(l) for l in open(tx, encoding="utf-8", errors="replace")]
        ids = list(collections.OrderedDict((r.get("requestId") or r["message"]["id"], 1) for r in recs if r.get("type") == "assistant"))
        mark = {}
        for n in range(1, len(ids) + 1):
            keep = set(ids[:n])
            tmp = os.path.join(base, "_prefix.jsonl")
            with open(tmp, "w") as fh:
                for r in recs:
                    if r.get("type") != "assistant" or (r.get("requestId") or r["message"]["id"]) in keep:
                        fh.write(json.dumps(r) + "\n")
            sc = budget.scan(tmp)
            for basis, v in (("est", sc["usd"]), ("rec", sc["usd_recorded"])):
                for m, f in (("note", 0.8), ("stop", 1.0)):
                    mark.setdefault((basis, m), n if v >= f * B else None)
                    if mark[(basis, m)] is None and v >= f * B:
                        mark[(basis, m)] = n
        os.remove(os.path.join(base, "_prefix.jsonl"))
        for (basis, m), n in mark.items():
            row["%s_mark_%s_at_request" % (basis, m)] = n
    row["est_share_of_exact"] = round(seen["usd"] / row["worker_usd"], 3)
    if ev["start"]:
        row["T_min"] = ev["start"][0].get("T")
    for k in ("note", "stop"):
        if ev[k]:
            row[k + "_which"], row[k + "_t_frac"] = ev[k][0].get("which"), ev[k][0].get("t_frac")
    if ev["end"]:
        row["end_elapsed_s"], row["end_t_frac"] = ev["end"][-1]["elapsed_s"], ev["end"][-1].get("t_frac")
    for k in ("note", "stop"):
        if ev[k]:
            e = ev[k][0]
            row[k + "_at_request"], row[k + "_frac"], row[k + "_elapsed_s"] = e["requests"], e["frac"], e["elapsed_s"]
            row["reads_after_" + k] = len(reads(e["requests"], len(reqs)))
    if ev["end"]:
        row["end_frac_recorded"] = ev["end"][-1]["frac"]
    if ev["note"]:
        row["post_note_usd_est"] = round(row["est_usd"] - ev["note"][0]["used"], 4)   # list price after the note, on the hook's basis
    if ev["stop"]:
        row["post_stop_usd_est"] = round(row["est_usd"] - ev["stop"][0]["used"], 4)
    # the hand-back
    hb = glob.glob(os.path.join(lab, "__statera__", "handbacks", "*.md"))
    sent = None
    for _, blocks in reqs:
        for b in blocks:
            if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                sent = (b.get("input") or {}).get("message")
    text = open(hb[0], "rb").read() if hb else b""
    row["handback_sections"] = text.count(b"\n## hand-back ")
    row["handback_saved_verbatim"] = bool(sent) and sent.encode() in text
    row["handback_mentions_gap"] = bool(sent) and bool(re.search(r"not (read|covered|reached)|NOT|did not|unread|partial|remaining|stopped|budget", sent, re.I))
    mentioned = set(re.findall(r"\bf(\d\d)\b", sent or ""))
    rp = glob.glob(os.path.join(lab, "__reports__", "**", "*.md"), recursive=True)
    row["report_files"] = len(rp)
    row["report_at_convention"] = os.path.exists(os.path.join(lab, "__reports__", "wave-02", meta["name"], "00-findings_v0.md"))
    for f in rp:
        mentioned |= set(re.findall(r"\bf(\d\d)\b", open(f, encoding="utf-8", errors="replace").read()))
    row["files_named_in_handback_or_report"] = len(mentioned)
    row["asked_files"] = meta["files"]
    # platform: hook events in the stream
    hc, bad = collections.Counter(), 0
    for line in open(os.path.join(base, "stdout.jsonl")):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("subtype") == "hook_started":
            hc[r.get("hook_event")] += 1
        if r.get("subtype") == "hook_response" and r.get("exit_code") not in (0, None):
            bad += 1
    row["hook_processes"], row["hook_nonzero_exit"] = sum(hc.values()), bad
    row["worker_calls"] = sum(1 for _, bl in reqs for b in bl if b.get("type") == "tool_use")
    return row, tx


rows, txs = [], {}
for d in sorted(os.listdir(os.path.join(S, "runs"))):
    if os.path.exists(os.path.join(S, "runs", d, "meta.json")):
        r, tx = cell(d)
        rows.append(r); txs[d] = tx
cols = sorted({k for r in rows for k in r}, key=lambda k: (list(rows[0]).index(k) if k in rows[0] else 99, k))
for r in rows:
    print(json.dumps(r, sort_keys=True))
if TSV:
    with open(TSV, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join("" if r.get(c) is None else str(r.get(c)) for c in cols) + "\n")

# the counts the claim quotes
for r in rows:
    assert r.get("plugin", "").startswith("nohooks") or (r["note_delivered"] == r["n_note"] and r["stop_delivered"] == r["n_stop"]), \
        ("the log and the worker's transcript disagree", r["cell"], r["n_note"], r["note_delivered"], r["n_stop"], r["stop_delivered"])
timed = [r for r in rows if r.get("time_min")]
rows = [r for r in rows if not r.get("time_min")]   # the time cells have their own lines below
quiet = [r for r in rows if r["plugin"] == "smallquiet"]   # start note and the platform's tracker, no notices
hooked = [r for r in rows if not r["plugin"].startswith("nohooks") and r["plugin"] != "smallquiet"]
def med(xs):
    xs = sorted(x for x in xs if x is not None)
    return xs[len(xs) // 2] if xs else None
print("AGG cells with notices: %d; start-note-only cells: %d; no-hooks controls: %d" % (len(hooked), len(quiet), len(rows) - len(hooked) - len(quiet)))
print("AGG start note and tracker only (no 0.8 note, no stop): %s" % [(r["cell"], r["files_read"], r["exact_over_B"]) for r in quiet])
noted = [r for r in hooked if r.get("n_note")]
print("AGG note: fired in %d; reads after the note = 0 in %d; frac at the note (min, max) = %s" % (
    len(noted), sum(r["reads_after_note"] == 0 for r in noted), (min(r["note_frac"] for r in noted), max(r["note_frac"] for r in noted)) if noted else None))
stopped = [r for r in hooked if r.get("n_stop")]
print("AGG stop notice arrived before any hand-back call (a real test of obedience) in: %s" % [r["cell"] for r in stopped if r.get("stop_before_handback")])
print("AGG stop (block at 1.0 B): fired in %d; reads after it = 0 in %d; hand-back saved in %d" % (
    len(stopped), sum(r["reads_after_stop"] == 0 for r in stopped), sum(r["handback_saved_verbatim"] for r in stopped)))
halted = [r for r in hooked if r.get("n_halt")]
print("AGG halt (continue false): fired in %d: %s; hand-back saved in %d" % (len(halted), [r["cell"] for r in halted], sum(r["handback_saved_verbatim"] for r in halted)))
print("AGG hand-back saved verbatim in %d of %d cells with hooks" % (sum(r["handback_saved_verbatim"] for r in hooked), len(hooked)))
denied = [r for r in hooked if r.get("n_deny")]
print("AGG deny: fired once in %d (n_deny sum %d); report at the convention path in %d" % (len(denied), sum(r["n_deny"] for r in denied), sum(r["report_at_convention"] for r in denied)))
print("AGG exact worker USD / B, cells with hooks: min %.2f median %.2f max %.2f; controls: %s" % (
    min(r["exact_over_B"] for r in hooked), med([r["exact_over_B"] for r in hooked]), max(r["exact_over_B"] for r in hooked),
    [(r["cell"], r["exact_over_B"]) for r in rows if r["plugin"].startswith("nohooks")]))
print("AGG USD after the note on the hook's basis: median %s, max %s; after the stop: median %s" % (
    med([r.get("post_note_usd_est") for r in hooked]), max([r.get("post_note_usd_est") or 0 for r in hooked]), med([r.get("post_stop_usd_est") for r in hooked])))
print("AGG recorded share of exact: min %.2f max %.2f; hook basis (est) share of exact: min %.2f max %.2f over %d cells" % (
    min(r["recorded_share_of_exact"] for r in rows), max(r["recorded_share_of_exact"] for r in rows),
    min(r["est_share_of_exact"] for r in rows), max(r["est_share_of_exact"] for r in rows), len(rows)))
print("AGG hook processes per worker tool call: %.2f (hook processes / worker calls, cells with hooks)" % (sum(r["hook_processes"] for r in hooked) / sum(r["worker_calls"] for r in hooked)))
for r in timed:
    print("AGG time cell %s (Time: min %s): note at t_frac %s by %s at %ss, stop notice at t_frac %s by %s at %ss; reads after note %s, after stop %s; "
          "ended at t_frac %s (%ss); hand-back saved %s; exact worker USD / default B %s" % (
              r["cell"], r["time_min"], r.get("note_t_frac"), r.get("note_which"), r.get("note_elapsed_s"), r.get("stop_t_frac"), r.get("stop_which"),
              r.get("stop_elapsed_s"), r.get("reads_after_note"), r.get("reads_after_stop"), r.get("end_t_frac"), r.get("end_elapsed_s"),
              r["handback_saved_verbatim"], r["exact_over_B"]))
print("AGG total USD of these cells (total_cost_usd): %.3f" % sum(r["total_usd"] for r in rows + timed))

# hook latency on a real transcript (the one with most requests), process start included, python3 as the hooks.json runs it
if rows and "--no-latency" not in sys.argv:
    best = max((r for r in rows if not r["plugin"].startswith("nohooks")), key=lambda r: r["requests"])["cell"]
    tx = txs[best]
    sess = os.path.dirname(os.path.dirname(tx))
    scratch = tempfile.mkdtemp()   # the benchmark writes state and log lines: never into a cell's own lab
    os.makedirs(os.path.join(scratch, "__statera__"))
    ev = dict(hook_event_name="PostToolUse", tool_name="Bash", agent_id=os.path.basename(tx)[6:-6], agent_type="murmuration:explorer",
              transcript_path=sess + ".jsonl", cwd=scratch, permission_mode="auto")
    out = {}
    for label, script, e in (("budget.py PostToolUse", "budget.py", ev), ("handback.py PreToolUse (explorer, first call: deny)", "handback.py", dict(ev, hook_event_name="PreToolUse", tool_name="SubagentHandback")),
                             ("python3 -c pass", None, None)):
        ts = []
        for _ in range(20):
            t = time.perf_counter()
            if script:
                subprocess.run([sys.executable, os.path.join(HERE, "..", "..", "..", "..", "scripts", script)], input=json.dumps(e), capture_output=True, text=True)
            else:
                subprocess.run([sys.executable, "-c", "pass"])
            ts.append((time.perf_counter() - t) * 1000)
        out[label] = (round(statistics.median(ts), 1), round(max(ts), 1))
    shutil.rmtree(scratch)
    print("latency ms (median, max of 20) on the %d-request transcript of %s: %s" % (len(requests_of(tx)), best, out))
