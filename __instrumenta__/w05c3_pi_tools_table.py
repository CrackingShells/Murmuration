#!/usr/bin/env python3
"""Reads the stdout.jsonl and meta.json of wave-5 E6 cells (w05c3_pi_tools_cell.py runs) and prints one TSV row per cell: request-0 context (input+cache write+cache read of the first main-thread request), requests, tool names seen at init, the smoke steps present, refused/unknown tool results, cost; input: <scratch>/runs/<cell> folders named on the command line; output: TSV on stdout (and --tsv FILE).
usage: w05c3_pi_tools_table.py <scratch> <cell> [<cell> ...] [--tsv FILE]. Stdlib only."""
import json, os, sys
args = sys.argv[1:]; tsv = None
if "--tsv" in args:
    i = args.index("--tsv"); tsv = args[i + 1]; del args[i:i + 2]
scratch, cells = args[0], args[1:]
STEPS = [("Skill", "1skill"), ("Write", "2write"), ("Read", "3read"), ("Edit", "4edit"), ("Bash", "5bash"), ("ToolSearch", "6toolsearch"), ("Agent", "7agent")]
BAD = ("no such tool", "unknown tool", "not available", "permission to use", "was blocked", "refused", "inputvalidationerror", "not allowed", "doesn't want to take this action")
hdr = ["cell", "m1_ctx_req0", "in", "cache_write", "cache_read", "main_requests", "init_tools", "m2_steps_ok", "m3_bad_results", "m4_cost_usd", "wall_s", "toolsearch_found_NotebookEdit", "explorer_reply_has_beta", "final_text"]
rows = []
for c in cells:
    d = os.path.join(scratch, "runs", c); meta = json.load(open(os.path.join(d, "meta.json")))
    reply = ""; init_tools = []; first = None; nreq = 0; uses = {}; results = {}; bad = []; final = ""
    for l in open(os.path.join(d, "stdout.jsonl")):
        try:
            r = json.loads(l)
        except ValueError:
            continue
        if r.get("type") == "system" and r.get("subtype") == "init":
            init_tools = r.get("tools", [])
        if r.get("type") == "assistant" and r.get("parent_tool_use_id"):
            for b in r["message"]["content"]:
                if b.get("type") == "tool_use" and b["name"] == "SubagentHandback":
                    reply += json.dumps(b["input"])
        if r.get("type") == "assistant" and not r.get("parent_tool_use_id"):
            u = r["message"]["usage"]; nreq += 1
            if first is None:
                first = (u["input_tokens"], u["cache_creation_input_tokens"], u["cache_read_input_tokens"])
            for b in r["message"]["content"]:
                if b.get("type") == "tool_use":
                    uses[b["id"]] = (b["name"], b.get("input"))
                if b.get("type") == "text":
                    final = b["text"]
        if r.get("type") == "user" and not r.get("parent_tool_use_id"):
            cont = r["message"].get("content")
            if isinstance(cont, str) and "SubagentHandback" in cont:
                reply += cont
            if isinstance(cont, list):
                for b in cont:
                    if b.get("type") == "text" and "SubagentHandback" in b.get("text", ""):
                        reply += b["text"]
                for b in cont:
                    if b.get("type") == "tool_result":
                        txt = b.get("content"); txt = txt if isinstance(txt, str) else json.dumps(txt)
                        results[b["tool_use_id"]] = (bool(b.get("is_error")), txt)
                        if any(k in txt.lower() for k in BAD) or b.get("is_error"):
                            bad.append((uses.get(b["tool_use_id"], ("?",))[0], txt[:80].replace("\n", " ")))
    names = [uses[i][0] for i in uses]
    ok = []
    for tool, tag in STEPS:
        hit = [i for i in uses if uses[i][0] == tool or (tool == "Agent" and uses[i][0] in ("Agent", "Task"))]
        good = [i for i in hit if i in results and not results[i][0]]
        ok.append(tag if good else "MISSING-" + tag)
    ts = [results[i][1] for i in uses if uses[i][0] == "ToolSearch" and i in results]
    ag = [results[i][1] for i in uses if uses[i][0] in ("Agent", "Task") and i in results] + [reply]
    row = [c, sum(first or (0, 0, 0)), *(first or ("", "", "")), nreq, len(init_tools), ",".join(ok), json.dumps(bad), meta.get("total_cost_usd"), meta.get("wall_s"),
           any("NotebookEdit" in t for t in ts), any("beta" in t.lower() for t in ag), final.replace("\n", " ")[:40]]
    rows.append([str(x) for x in row])
out = "\t".join(hdr) + "\n" + "\n".join("\t".join(r) for r in rows) + "\n"
sys.stdout.write(out)
if tsv:
    open(tsv, "w").write(out)
