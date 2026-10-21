"""Tabulates the platform's own record of hook runs (`attachment.type == hook_success|hook_cancelled`, field durationMs) in session transcripts, per hook event and command label: n, median, p90, sum.

usage: hook_platform_durations.py MAIN.jsonl [MAIN2.jsonl ...]  (each main's subagents under <id>/subagents/ are read too). Only hooks that wrote stdout or failed leave such a record, so silent PostToolUse/PreToolUse runs are absent: the table is a lower bound on counts and a sample of durations of the noisy ones.
Output: markdown table on stdout; the `command` field holds the hook's statusMessage when it has one.
"""
import json, sys, glob, collections, statistics as st
d = collections.defaultdict(list)
for main in sys.argv[1:]:
    for f in [main] + sorted(glob.glob(main[:-6] + "/subagents/**/agent-*.jsonl", recursive=True)):
        for line in open(f, encoding="utf-8", errors="replace"):
            if '"hook_' not in line: continue
            try: r = json.loads(line)
            except ValueError: continue
            a = r.get("attachment") if r.get("type") == "attachment" else None
            if a and a.get("type") in ("hook_success", "hook_cancelled", "hook_non_blocking_error", "hook_blocking_error") and a.get("durationMs") is not None:
                d[(a.get("hookEvent") or a.get("hookName", "?").split(":")[0], a["type"], str(a.get("command"))[:60])].append(a["durationMs"])
print("| event | record | command label / status message | n | median ms | p90 ms | sum s |\n|:--|:--|:--|--:|--:|--:|--:|")
for (ev, ty, cmd), v in sorted(d.items(), key=lambda kv: -sum(kv[1])):
    v = sorted(v); print("| %s | %s | %s | %d | %.0f | %.0f | %.1f |" % (ev, ty, cmd, len(v), st.median(v), v[int(.9 * (len(v) - 1))], sum(v) / 1000))
