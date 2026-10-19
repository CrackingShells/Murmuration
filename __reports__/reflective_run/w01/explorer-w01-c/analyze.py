#!/usr/bin/env python3
"""Tables for explorer-w01-c.  Input: tool_calls.csv + agents.csv (from extract_calls.py).
Run: python3 -I analyze.py <dir>      Output CSVs are written into <dir>.
Dedup rule: a tool_use_id that appears in several transcripts (forked sessions copy their parent's history) is counted
once, attributed to the first session in the order genesis, design, 3ccc590f, 2947f9dc, this run."""
import csv
import collections
import re
import sys

D = sys.argv[1]
rows = list(csv.DictReader(open(D + "/tool_calls.csv")))
seen = {}
for r in rows:
    seen.setdefault(r["tool_use_id"], r)
rows = list(seen.values())
print("raw", len(list(csv.DictReader(open(D + "/tool_calls.csv")))), "unique", len(rows))


def group(r):
    s, t = r["session"], r["agent_type"]
    pre = {"genesis_566fa912": "genesis", "design_82e8a947": "design", "s3ccc590f": "s3ccc590f",
           "s2947f9dc": "s2947f9dc", "thisrun_ab96c5ed": "thisrun"}[s]
    if t == "main":
        return pre + "/PI"
    if t.startswith("murmuration:"):
        return pre + "/explorer(shipped)"
    return pre + "/worker(general-purpose)"


# ---- outcome classifier (text based; is_error alone misses MCP content-level failures)
def outcome(r):
    h, e, tool = r["res_head"], r["is_error"], r["tool"]
    mcp = tool.startswith("mcp__")
    if tool == "Bash" and e != "1" and not h.startswith("<persisted-output>"):
        return "ok"          # Bash output may quote error strings (e.g. while reading transcripts); only is_error counts
    if e == "1" and "InputValidationError" in h:
        return "wrong_arguments"
    if "exceeds maximum allowed tokens" in h or h.startswith("<persisted-output>"):
        return "size_overflow"
    if mcp and "rsync version" in h:
        return "server_host_dependency"
    if mcp and ("HTTP 429" in h or "429 Unknown Error" in h):
        return "upstream_429"
    if mcp and "403 Forbidden" in h:
        return "upstream_403"
    if tool.startswith("mcp__ddg__search") and h.startswith('{"result":"No results were found'):
        return "empty_result"
    if mcp and "timed out" in h[:60]:
        return "timeout"
    if "hook error" in h[:80]:
        return "hook_block"
    if "auto mode classifier" in h:
        return "classifier_denial"
    if h.startswith("<tool_use_error>Blocked:"):
        return "platform_block(sleep)"
    if "not found in storage" in h:
        return "wrong_order(arxiv read before download)"
    if tool == "Read" and "does not exist" in h:
        return "path_missing"
    if e == "1" and h.startswith("Exit code"):
        return "bash_nonzero_exit"
    if "denied or failed" in h:
        return "denied_or_failed"
    if e == "1":
        return "other_error"
    return "ok"


for r in rows:
    r["group"] = group(r)
    r["outcome"] = outcome(r)
    r["tool_short"] = r["tool"] if r["server"] == "builtin" else r["server"] + "::" + r["tool"].split("__")[-1]

# ---- T1: calls by group x server
t1 = collections.Counter((r["group"], r["server"]) for r in rows)
groups = sorted({r["group"] for r in rows})
servers = sorted({r["server"] for r in rows})
with open(D + "/t1_calls_by_group_server.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["group"] + servers + ["total"])
    for g in groups:
        w.writerow([g] + [t1.get((g, s), 0) for s in servers] + [sum(t1.get((g, s), 0) for s in servers)])

# ---- T1b: calls by group x tool
t1b = collections.Counter((r["group"], r["tool_short"]) for r in rows)
with open(D + "/t1b_calls_by_group_tool.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["group", "tool", "calls"])
    for (g, t), n in sorted(t1b.items(), key=lambda x: (x[0][0], -x[1])):
        w.writerow([g, t, n])

# ---- T2: outcomes by server
t2 = collections.Counter((r["server"], r["outcome"]) for r in rows)
outs = sorted({r["outcome"] for r in rows})
with open(D + "/t2_outcomes_by_server.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["server"] + outs + ["total", "non_ok", "non_ok_pct"])
    for s in servers:
        tot = sum(t2.get((s, o), 0) for o in outs)
        bad = tot - t2.get((s, "ok"), 0)
        w.writerow([s] + [t2.get((s, o), 0) for o in outs] + [tot, bad, round(100.0 * bad / tot, 1) if tot else 0])

# ---- T2b: outcomes per MCP tool (only servers an agent could be asked to use)
t2b = collections.Counter((r["tool_short"], r["outcome"]) for r in rows if r["server"] != "builtin" and not r["server"].startswith("ccd_"))
with open(D + "/t2b_outcomes_by_mcp_tool.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tool"] + outs + ["total"])
    for t in sorted({k[0] for k in t2b}):
        w.writerow([t] + [t2b.get((t, o), 0) for o in outs] + [sum(t2b.get((t, o), 0) for o in outs)])

# ---- T3: discovery (ToolSearch) per agent
per = collections.defaultdict(lambda: dict(calls=0, ts=0, select=0, keyword=0, noresult=0))
for r in rows:
    k = (r["group"], r["session"], r["agent_key"], r["agent_desc"])
    per[k]["calls"] += 1
    if r["tool"] == "ToolSearch":
        per[k]["ts"] += 1
        q = r["tsq_query"]
        if q.startswith("select:"):
            per[k]["select"] += 1
        else:
            per[k]["keyword"] += 1
        if "tool_reference" not in r["res_head"]:
            per[k]["noresult"] += 1
with open(D + "/t3_toolsearch_per_agent.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["group", "session", "agent_key", "agent_desc", "calls", "toolsearch", "select_form", "keyword_form", "empty_result", "share_pct"])
    for k, v in sorted(per.items()):
        w.writerow(list(k) + [v["calls"], v["ts"], v["select"], v["keyword"], v["noresult"], round(100.0 * v["ts"] / v["calls"], 1)])

# ---- T3b: ToolSearch queries (the raw material)
with open(D + "/t3b_toolsearch_queries.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["group", "agent_key", "agent_desc", "ts", "query", "n_refs_returned"])
    for r in rows:
        if r["tool"] == "ToolSearch":
            w.writerow([r["group"], r["agent_key"], r["agent_desc"], r["ts"], r["tsq_query"][:300], r["res_head"].count("<tool_reference")])

# ---- T4: allowlist gap.  Role of a genesis/design worker is my reading of its description  [assumption]
ROLE_HINT = [("Adversarial", "proof-adversary"), ("Reproduce", "reproducer"), ("Verifier", "reproducer"), ("Cold review", "reproducer"),
             ("Wave 1: instrument", "reproducer"), ("Build final Wolfram", "author"), ("Build minimal lab", "author"), ]
BUILTIN = {
    "explorer": {"Read", "Glob", "Grep", "Bash", "Write", "Edit", "WebFetch", "WebSearch", "Skill", "ToolSearch"},
    "author": {"Read", "Glob", "Grep", "Bash", "Write", "Edit", "Skill", "ToolSearch", "SendMessage"},
    "reproducer": {"Read", "Glob", "Grep", "Bash", "Write", "Edit", "Skill", "ToolSearch", "SendMessage"},
    "proof-adversary": {"Read", "Glob", "Grep", "Bash", "Write", "Edit", "Skill", "ToolSearch", "SendMessage"},
}
MCP = {
    "explorer": {"WolframToolkit", "plugin_colgrep-mcp_colgrep", "arxiv", "context7"},
    "author": {"WolframToolkit", "plugin_colgrep-mcp_colgrep", "arxiv"},
    "reproducer": {"WolframToolkit", "plugin_colgrep-mcp_colgrep"},
    "proof-adversary": {"WolframToolkit", "plugin_colgrep-mcp_colgrep"},
}


def role_of(desc):
    for k, v in ROLE_HINT:
        if k.lower() in desc.lower():
            return v
    return "explorer"


def allowed(role, r):
    if r["server"] == "builtin":
        return r["tool"] in BUILTIN[role]
    return r["server"] in MCP[role]


gap = collections.Counter()
tot_by_role = collections.Counter()
for r in rows:
    if r["group"].endswith("worker(general-purpose)"):
        role = role_of(r["agent_desc"])
        tot_by_role[role] += 1
        if not allowed(role, r):
            gap[(role, r["tool_short"])] += 1
with open(D + "/t4_allowlist_gap_workers.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["assumed_role", "tool_not_in_allowlist", "calls", "role_total_calls"])
    for (role, t), n in sorted(gap.items(), key=lambda x: -x[1]):
        w.writerow([role, t, n, tot_by_role[role]])

# ---- T4b: the PI sessions (research-pi inherits everything: so only informational)
pi = collections.Counter((r["group"], r["tool_short"]) for r in rows if r["group"].endswith("/PI") and r["server"] != "builtin")
with open(D + "/t4b_pi_mcp_use.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["group", "mcp_tool", "calls"])
    for (g, t), n in sorted(pi.items()):
        w.writerow([g, t, n])

# ---- T5: allowlisted MCP servers: how often were they called by workers?
t5 = collections.Counter((r["server"], r["group"]) for r in rows if r["server"] in ("WolframToolkit", "plugin_colgrep-mcp_colgrep", "arxiv", "context7", "ddg") or r["tool"] in ("WebSearch", "WebFetch"))
with open(D + "/t5_allowlisted_server_use.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["server_or_tool", "group", "calls"])
    for (s, g), n in sorted(t5.items()):
        w.writerow([s, g, n])
for r in rows:
    pass
with open(D + "/calls_dedup_classified.csv", "w", newline="") as f:
    w = csv.DictWriter(f, ["group", "session", "agent_key", "agent_desc", "ts", "tool", "server", "tool_use_id", "outcome", "is_error", "res_len", "input_head", "res_head", "tsq_query"], extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
print("done")
