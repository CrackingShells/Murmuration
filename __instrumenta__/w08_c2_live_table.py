# Tabulates the live cells of protocol P2 (w08-c2) from their run folders: per cell, the deny lines and markers the hook left, every SubagentHandback call of the worker (length, whether it was denied), the hand-back the PI would have received (bytes recorded by the hook), which ground-truth items of the first message are in a file the worker wrote, the worker's measured usage re-priced at Sonnet list price, and for the on/off pairs the paired net; inputs: S (the live folder with runs/<cell>/), OUTDIR; outputs: OUTDIR/live_within.tsv, OUTDIR/live_cells.tsv, OUTDIR/live_calls.tsv, OUTDIR/live_pairs.tsv, OUTDIR/live_deny_texts.txt (lengths, counts and USD; no model text).
# usage: w08_c2_live_table.py S OUTDIR
import json, os, sys, glob, re, hashlib, statistics as st
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lab_status as L

S, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
LONG, FRAME, U = 5000, 1276, 1.2255e-5   # N; the median characters the harness adds around a hand-back in a PI transcript; the median PI-context USD per character (w08_c2_pi_side.tsv)
SKIP = ('{"type": "api-request',)
cells = sorted(d for d in os.listdir(S + "/runs") if os.path.exists(S + "/runs/%s/meta.json" % d))
cellrows = [["cell", "role", "arm", "mode", "files", "worker_requests", "calls", "call_chars", "calls_denied", "deny_lines", "deny_cause", "deny_chars", "markers", "recorded_handbacks", "recorded_bytes",
             "pi_chars_delivered", "first_items_total", "first_items_in_worker_files", "first_items_written_before_first_call", "first_items_moved_after_first_call", "second_items_total", "worker_usd_all_sonnet", "worker_usd_after_first_call_sonnet", "cell_usd_haiku", "wall_s", "deny_names_path"]]
callrows = [["cell", "call", "chars", "sha12", "result_chars", "result_is_deny", "result_names_path"]]
info = {}
denytexts = []
for c in cells:
    base = S + "/runs/" + c
    spec, meta = json.load(open(base + "/spec.json")), json.load(open(base + "/meta.json"))
    ground = json.load(open(base + "/ground.json"))
    lab = base + "/lab"
    log = lab + "/__statera__/harness.jsonl"
    deny = [json.loads(x) for x in open(log).read().splitlines() if '"deny"' in x] if os.path.exists(log) else []
    mk = lab + "/__statera__/.harness"
    markers = sorted(x for x in os.listdir(mk) if x != ".gitignore") if os.path.isdir(mk) else []
    secs = []
    for f in glob.glob(lab + "/__statera__/handbacks/*.md"):
        for m in re.finditer(r"^## hand-back (\d+) \| \S+ \| agent_id=\S+ type=\S+ event=(\S+) status=(\S+) bytes=(\d+) sha256=(\w+)$", open(f, errors="replace").read(), re.M):
            secs.append((m.group(2), m.group(3), int(m.group(4)), m.group(5)))
    tf = glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents/agent-*.jsonl" % meta["session"]))
    calls, results, usage, order, req_of_call = [], {}, {}, [], {}
    wbefore, wafter = [], []   # the inputs of Write, Edit and Bash calls (what the worker put into files) before and after its first SubagentHandback call
    for f in tf:
        for line in open(f, encoding="utf-8", errors="replace"):
            if line.startswith(SKIP):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            m = r.get("message") or {}
            if r.get("type") == "assistant" and m.get("model") != "<synthetic>":
                if m.get("id") not in usage:
                    order.append(m.get("id"))
                L.merge_usage(usage.setdefault(m.get("id"), {}), m.get("usage") or {})
                for b in m.get("content") or [] if isinstance(m.get("content"), list) else []:
                    if b.get("type") == "tool_use" and b.get("name") in ("Write", "Edit", "Bash", "NotebookEdit"):
                        (wafter if calls else wbefore).append(json.dumps(b.get("input") or {}, ensure_ascii=False))
                    if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                        calls.append((b["id"], (b.get("input") or {}).get("message") or ""))
                        req_of_call[b["id"]] = m.get("id")
            elif r.get("type") == "user" and isinstance(m.get("content"), list):
                for b in m["content"]:
                    if b.get("type") == "tool_result":
                        x = b.get("content")
                        results[b.get("tool_use_id")] = x if isinstance(x, str) else "".join(y.get("text", "") for y in x or [] if isinstance(y, dict))
    price = lambda mid: L.message_usd("claude-sonnet-5-5", usage[mid])   # measured tokens, Sonnet list price
    tot = sum(price(m) for m in order)
    after = 0.0
    if calls:
        k = order.index(req_of_call[calls[0][0]])
        after = sum(price(m) for m in order[k + 1:])
    names = 0
    denied = 0
    for i, (tid, msg) in enumerate(calls):
        res = results.get(tid, "")
        isd = "Lab harness check" in res
        denied += isd
        path = bool(re.search(r"(__reports__|__pondus__|__scrupuli__)/", res)) if isd else False
        names += path
        if isd:
            denytexts.append("%s call %d: %s" % (c, i + 1, res))   # the hook's own words (the agent's name and a path it wrote are the only model text in it)
        callrows.append([c, i + 1, len(msg), hashlib.sha256(msg.encode("utf-8", "replace")).hexdigest()[:12], len(res), int(isd), int(path)])
    # ground items: founder, population and station of each file, found in the first message and in files the worker wrote
    items = [(f, k, str(v[k])) for f, v in ground.items() for k in ("station", "founder", "population")]
    wfiles = ""
    for p in glob.glob(lab + "/**", recursive=True):
        rel = os.path.relpath(p, lab)
        if os.path.isfile(p) and not re.match(r"f\d{3}\.txt$", rel) and not rel.startswith(("__statera__", ".claude", ".ignore")) and not rel.startswith("__design__"):
            wfiles += open(p, errors="replace").read()
    first = calls[0][1] if calls else ""
    second = calls[-1][1] if len(calls) > 1 else ""
    f_in = [it for it in items if it[2] in first]
    f_file = [it for it in f_in if it[2] in wfiles]
    s_in = [it for it in items if it[2] in second]
    wb, wa = "".join(wbefore), "".join(wafter)
    # the json encoding of a number or name is the plain text; names have no escapes
    moved = [it for it in f_in if it[2] not in wb and it[2] in wa]
    before = [it for it in f_in if it[2] in wb]
    delivered = [x for x in secs if x[1].startswith("delivered")]
    last_bytes = delivered[-1][2] if delivered else 0
    cellrows.append([c, spec["role"], spec["arm"], spec["mode"], spec["files"], len(order), len(calls), "|".join(str(len(m)) for _, m in calls), denied, len(deny), "|".join(d.get("cause", "report") for d in deny),
                     "|".join(str(d.get("chars", "")) for d in deny), "|".join(markers), len(delivered), "|".join(str(x[2]) for x in delivered), last_bytes + FRAME if delivered else "", len(f_in), len(f_file), len(before), len(moved), len(s_in),
                     "%.4f" % tot, "%.4f" % after, "%.4f" % (meta.get("usd") or 0), meta.get("wall_s"), names])
    info[c] = dict(spec=spec, bytes=last_bytes, tot=tot, delivered=len(delivered), after=after, first=len(calls[0][1]) if calls else 0, last=len(calls[-1][1]) if calls else 0, ncalls=len(calls))
pairs = [["pair", "pi_chars_on", "pi_chars_off", "chars_saved", "pi_saving_usd_at_u", "worker_usd_on_sonnet", "worker_usd_off_sonnet", "worker_extra_usd", "net_usd", "sign"]]
for a, b in (("e_on_auto", "e_off_auto"), ("a_on_auto", "a_off_auto")):
    if a in info and b in info and info[a]["delivered"] and info[b]["delivered"]:
        on, off = info[a]["bytes"] + FRAME, info[b]["bytes"] + FRAME
        sv = (off - on) * U
        ex = info[a]["tot"] - info[b]["tot"]
        pairs.append([a + " vs " + b, on, off, off - on, "%.4f" % sv, "%.4f" % info[a]["tot"], "%.4f" % info[b]["tot"], "%.4f" % ex, "%.4f" % (sv - ex), "+" if sv - ex > 0 else "-"])
within = [["cell", "calls", "first_message_chars", "delivered_chars", "chars_saved_vs_first", "pi_saving_usd_at_u", "worker_usd_after_first_call_sonnet", "net_usd_within_run", "sign"]]
for c, i in info.items():
    if i["spec"]["arm"] == "on" and i["ncalls"]:
        sv = (i["first"] - i["last"]) * U
        within.append([c, i["ncalls"], i["first"], i["last"], i["first"] - i["last"], "%.4f" % sv, "%.4f" % i["after"], "%.4f" % (sv - i["after"]), "+" if sv - i["after"] > 0 else ("0" if i["after"] == 0 else "-")])
open(os.path.join(OUT, "live_deny_texts.txt"), "w").write("\n\n".join(denytexts) + "\n")
for name, rows in (("live_within.tsv", within), ("live_cells.tsv", cellrows), ("live_calls.tsv", callrows), ("live_pairs.tsv", pairs)):
    open(os.path.join(OUT, name), "w").write("\n".join("\t".join(str(x) for x in r) for r in rows) + "\n")
    print("\n".join("\t".join(str(x) for x in r) for r in rows))
