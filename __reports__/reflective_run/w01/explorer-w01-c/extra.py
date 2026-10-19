#!/usr/bin/env python3
"""Extra measurements for explorer-w01-c.  Run: python3 -I extra.py <dir>   (reads calls_dedup_classified.csv, transcripts read-only)
Outputs: t6_bash_commands.csv, t7_toolsearch_context_delta.csv, t8_prefix_toolnames.csv, t9_bash_shell_search.csv"""
import csv, glob, json, os, re, sys, collections
D = sys.argv[1]
HOME = os.path.expanduser("~/.claude/projects")
rows = list(csv.DictReader(open(D + "/calls_dedup_classified.csv")))

# t6: what Bash was used for (first word / python vs wolframscript), per group
def kind(cmd):
    c = cmd
    if re.search(r"wolframscript|wolfram", c): return "wolframscript"
    if re.search(r"python3?\b", c): return "python"
    if re.search(r"\bcargo\b|\brustc\b", c): return "cargo/rust"
    if re.search(r"\bgit\b", c): return "git"
    if re.search(r"\bjq\b", c): return "jq"
    if re.search(r"\b(ssh|scp|rsync)\b", c): return "ssh/rsync"
    if re.search(r"\b(grep|rg|egrep)\b", c): return "grep/rg"
    if re.search(r"\b(ls|cat|head|tail|wc|sed|awk|find|mkdir|cp|mv|echo|cd)\b", c): return "shell-basic"
    return "other"
t6 = collections.Counter()
for r in rows:
    if r["tool"] == "Bash":
        try: cmd = json.loads(r["input_head"] + ('"}' if not r["input_head"].endswith("}") else "")).get("command", "")
        except Exception: cmd = r["input_head"]
        t6[(r["group"], kind(cmd))] += 1
with open(D + "/t6_bash_commands.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["group", "bash_kind", "calls"])
    for (g, k), n in sorted(t6.items()): w.writerow([g, k, n])

# t9: shell corpus search attempts (the pattern the colgrep hook denies)  -- uses the transcript text directly
pat = re.compile(r"(grep\s+-[a-zA-Z]*r|grep\s+--recursive|\brg\b|find\b[^|;]*-exec\s+grep|xargs\s+grep)")
t9 = collections.Counter(); blocked = collections.Counter()
for r in rows:
    if r["tool"] == "Bash" and pat.search(r["input_head"]):
        t9[r["group"]] += 1
        if "hook error" in r["res_head"][:80] or "COLGREP_BYPASS" in r["res_head"]: blocked[r["group"]] += 1
with open(D + "/t9_bash_shell_search.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["group", "bash_calls_with_recursive_grep_or_rg", "of_which_hook_blocked"])
    for g in sorted(t9): w.writerow([g, t9[g], blocked[g]])

# t8: tool names that were loaded (non-deferred) at agent start, from prefix.json; Glob/Grep presence
t8 = []
for base in glob.glob(HOME + "/-Users-hacker-Documents-explore-combinatorics-on-binary/*/subagents/*.prefix.json"):
    d = json.load(open(base)); names = d["state"]["toolNames"]
    t8.append((os.path.basename(base)[6:-12], len(names), "Glob" in names, "Grep" in names, "Monitor" in names, "SendMessage" in names, "ToolSearch" in names, d["state"].get("anyDeferLoading")))
seen = set(); out = []
for x in t8:
    if x[0] in seen: continue
    seen.add(x[0]); out.append(x)
with open(D + "/t8_prefix_toolnames.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["agent_key", "n_tools_loaded_at_start", "Glob", "Grep", "Monitor", "SendMessage", "ToolSearch", "anyDeferLoading"]); w.writerows(out)

# t7: context growth across each ToolSearch call (upper bound on what loading schemas cost)
GEN = HOME + "/-Users-hacker-Documents-explore-combinatorics-on-binary"
RUN = HOME + "/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e"
tsids = {r["tool_use_id"]: r for r in rows if r["tool"] == "ToolSearch"}
res = []
paths = glob.glob(GEN + "/*.jsonl") + glob.glob(GEN + "/*/subagents/agent-*.jsonl") + glob.glob(RUN + "/*.jsonl") + glob.glob(RUN + "/*/subagents/agent-*.jsonl")
done = set()
for p in paths:
    last = None; pending = None
    for l in open(p, encoding="utf-8", errors="replace"):
        d = json.loads(l)
        if d.get("type") != "assistant": continue
        u = (d.get("message") or {}).get("usage") or {}
        tot = (u.get("input_tokens", 0) or 0) + (u.get("cache_creation_input_tokens", 0) or 0) + (u.get("cache_read_input_tokens", 0) or 0)
        if pending is not None and pending[0] not in done:
            res.append((pending[0], pending[1], tot - pending[2])); done.add(pending[0]); pending = None
        c = (d.get("message") or {}).get("content")
        if isinstance(c, list):
            for b in c:
                if b.get("type") == "tool_use" and b.get("name") == "ToolSearch" and b["id"] in tsids and b["id"] not in done:
                    pending = (b["id"], tsids[b["id"]]["tsq_query"][:80], tot)
with open(D + "/t7_toolsearch_context_delta.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["tool_use_id", "query", "context_growth_tokens_to_next_assistant_turn"])
    for r in res: w.writerow(r)
print("ok", len(res))
