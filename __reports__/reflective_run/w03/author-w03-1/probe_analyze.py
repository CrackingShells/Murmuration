#!/usr/bin/env python3
"""Summarise the PostToolBatch probe cells under <scratch>/runs: per agent, the hook events against the batches the transcript shows.
usage: probe_analyze.py <scratch> [--tsv FILE]    Stdlib only."""
import glob, json, os, sys, collections
S = os.path.abspath(sys.argv[1]); rows = []
for meta in sorted(glob.glob(os.path.join(S, "runs", "*", "meta.json"))):
    m = json.load(open(meta)); base = os.path.dirname(meta)
    if not os.path.exists(os.path.join(base, "events.jsonl")) or "mode" not in m:
        continue   # an end-to-end cell or a message probe, not a PostToolBatch probe cell
    ev = []
    for l in open(os.path.join(base, "events.jsonl")):
        r = json.loads(l)
        if "full" not in r: ev.append(r)
    # transcripts: the subagent's own file
    subs = glob.glob(os.path.expanduser("~/.claude/projects/*%s*/%s/subagents/agent-*.jsonl" % (os.path.basename(base), m["session"])))
    # the cell's lab folder is runs/<cell>/lab, so the project folder name ends with '-<cell>-lab'
    subs = glob.glob(os.path.expanduser("~/.claude/projects/*-runs-%s-lab/%s/subagents/agent-*.jsonl" % (m["cell"], m["session"])))
    tx = subs[0] if subs else None
    txt = open(tx).read() if tx else ""
    # batches in the transcript: distinct assistant message ids that carry tool_use blocks
    msgs = collections.OrderedDict()
    if tx:
        for l in open(tx):
            r = json.loads(l)
            if r.get("type") == "assistant":
                mid = (r.get("message") or {}).get("id")
                for b in (r["message"].get("content") or []):
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        msgs.setdefault(mid, set()).add(b["id"])
    by = collections.defaultdict(lambda: collections.Counter())
    sizes = collections.defaultdict(list)
    for r in ev:
        a = r["agent_id"] or "main"
        by[a][r["kind"]] += 1
        if r["kind"] == "PostToolBatch":
            sizes[a].append(len(r["batch"] or []))
    sub_id = next((a for a in by if a != "main"), None)
    c = by.get(sub_id, collections.Counter()); c0 = by.get("main", collections.Counter())
    tx_sizes = [len(v) for v in msgs.values()]
    ids_tx = set().union(*msgs.values()) if msgs else set()
    ids_batch = {b["tool_use_id"] for r in ev if r["kind"] == "PostToolBatch" and r["agent_id"] for b in (r["batch"] or [])}
    ids_use = {r["tool_use_id"] for r in ev if r["kind"] == "PostToolUse" and r["agent_id"]}
    ags = [r for r in ev if r["kind"] == "PostToolUse" and r["tool_name"] == "Agent"]
    stops = [r for r in ev if r["kind"] == "SubagentStop"]
    starts = [r for r in ev if r["kind"] == "SubagentStart"]
    actual_fg = bool(ags and starts and ags[0]["t"] >= starts[0]["t"])   # the Agent call returned after the worker started: it ran in the foreground
    att = collections.Counter()
    if tx:
        for l in open(tx):
            r = json.loads(l)
            if r.get("type") == "attachment":
                att[r["attachment"].get("type")] += 1
    handback = any(r["kind"] == "PostToolUse" and r["tool_name"] == "SubagentHandback" and r["agent_id"] for r in ev)
    rows.append(dict(cell=m["cell"], asked_bg=m.get("bg", True), fg=actual_fg, mode=m["mode"], usd=round(m["usd"] or 0, 3),
                     ctx_att=att["hook_additional_context"], stopped_att=att["hook_stopped_continuation"], handback_post=handback,
                     sub_pre=c["PreToolUse"], sub_use=c["PostToolUse"], sub_batch=c["PostToolBatch"], tx_batches=len(msgs),
                     batch_sizes=sizes.get(sub_id, []), tx_sizes=tx_sizes, calls_tx=len(ids_tx), calls_in_batch=len(ids_batch), calls_in_use=len(ids_use),
                     batch_ids_eq_tx=ids_batch == ids_tx, main_batch=c0["PostToolBatch"], main_use=c0["PostToolUse"],
                     ))
cols = list(rows[0]) if rows else []
for r in rows:
    print(" ".join("%s=%s" % (k, r[k]) for k in cols))
if "--tsv" in sys.argv:
    with open(sys.argv[sys.argv.index("--tsv") + 1], "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows: fh.write("\t".join(str(r[k]) for k in cols) + "\n")

# totals over the cells whose hook only logged or added context (the block cells stop the worker at its first batch: counted apart)
tot = {}
for r in rows:
    if r["mode"] == "block":
        k = "block cells (PostToolBatch decision block)"
    else:
        k = "foreground cells" if r["fg"] else "background cells"
    d = tot.setdefault(k, collections.Counter())
    d["cells"] += 1; d["transcript batches"] += r["tx_batches"]; d["PostToolBatch events"] += r["sub_batch"]
    d["batches with the same tool_use ids"] += r["batch_ids_eq_tx"] and r["tx_batches"]
    d["batches with 2 or more calls"] += sum(1 for x in r["tx_sizes"] if x > 1)
    d["... of them with the same size in PostToolBatch"] += sum(1 for a, b in zip(r["tx_sizes"], r["batch_sizes"]) if a > 1 and a == b)
    d["tool calls"] += r["calls_tx"]; d["calls in PostToolBatch"] += r["calls_in_batch"]; d["calls with a PostToolUse"] += r["calls_in_use"]
    d["hook_additional_context attachments in the worker transcript"] += r["ctx_att"]
for k, d in tot.items():
    print("TOTAL", k, dict(d))
