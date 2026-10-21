#!/usr/bin/env python3
"""Counts the tools called by the main thread of every research-pi session (transcripts whose first agent-setting record names research-pi, in the Murmuration worktree project dirs) and, for the first such session per dir, the deferred names per MCP server in its first deferred_tools_delta; input: ~/.claude/projects/*/*.jsonl; output: TSV of tool, calls, sessions on stdout, then the deferred-name table by server for the newest PI session and for a headless w07e base cell if its transcript path is given as argv[1].
Read-only; no credentials printed."""
import glob, json, os, sys, collections, re
root = os.path.expanduser("~/.claude/projects"); calls = collections.Counter(); sess = collections.defaultdict(set); n = 0; newest = None
for f in glob.glob(os.path.join(root, "*", "*.jsonl")):
    proj = f.split(os.sep)[-2]
    if not ("claude-worktrees-Murmuration" in proj and "---" not in proj and "-runs-" not in proj and "scratch" not in proj): continue
    ispi = False; used = collections.Counter()
    for l in open(f):
        if '"agent-setting"' in l and not ispi:
            try: r = json.loads(l)
            except ValueError: continue
            ispi = "research-pi" in json.dumps(r)
            if not ispi: break
            continue
        if ispi and '"tool_use"' in l:
            r = json.loads(l)
            if r.get("type") == "assistant" and not r.get("isSidechain"):
                for b in r["message"].get("content", []):
                    if isinstance(b, dict) and b.get("type") == "tool_use": used[b["name"]] += 1
    if ispi:
        n += 1
        for k, v in used.items(): calls[k] += v; sess[k].add(f)
        if newest is None or os.path.getmtime(f) > os.path.getmtime(newest): newest = f
print("PI sessions", n)
print("tool\tcalls\tsessions")
for k, v in calls.most_common(): print("%s\t%d\t%d" % (k, v, len(sess[k])))
def deferred(f):
    for l in open(f):
        if '"deferred_tools_delta"' in l:
            r = json.loads(l)
            if r.get("type") == "attachment" and r["attachment"].get("type") == "deferred_tools_delta":
                names = r["attachment"]["addedNames"]; c = collections.Counter(); ch = collections.Counter()
                for x in names:
                    s = re.match(r"mcp__(.+?)__", x); s = s.group(1) if s else "builtin"; c[s] += 1; ch[s] += len(x) + 1
                return c, ch
for lab, f in (("newest PI session", newest), ("headless base cell", sys.argv[1] if len(sys.argv) > 1 else None)):
    if not f: continue
    c, ch = deferred(f); print("\n# deferred names by server,", lab, "total", sum(c.values()), "names", sum(ch.values()), "chars"); print("server\tnames\tchars")
    for k, v in ch.most_common(): print("%s\t%d\t%d" % (k, c[k], v))
