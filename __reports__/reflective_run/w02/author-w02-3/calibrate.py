#!/usr/bin/env python3
"""The calibration of CHARS_PER_TOKEN in scripts/budget.py: content characters against the exact output tokens of each worker run.

usage: calibrate.py <runs dir>      (the pilot set: <scratch>/pilot/runs_v1, 7 cells)
Per cell: the sonnet `outputTokens` of the run's `modelUsage` (exact), the output count the transcript records, and the characters of
the worker's messages (text, thinking, and the JSON of tool inputs, as `budget.block_text` counts them). Read-only; stdlib only."""
import glob, json, os, statistics, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "scripts"))
import budget

ratios = []
for d in sorted(glob.glob(os.path.join(sys.argv[1], "*", "stdout.jsonl"))):
    cell = os.path.basename(os.path.dirname(d))
    lines = [json.loads(l) for l in open(d) if l.startswith("{")]
    sid = next(r["session_id"] for r in lines if "session_id" in r)
    exact = [r for r in lines if r.get("type") == "result"][-1]["modelUsage"]["claude-sonnet-5-5"]["outputTokens"]
    f = glob.glob(os.path.expanduser("~/.claude/projects/*/%s/subagents/agent-*.jsonl" % sid))[0]
    out, blocks = {}, {}
    for l in open(f):
        r = json.loads(l)
        if r.get("type") == "assistant":
            k = r["requestId"]
            out[k] = max(out.get(k, 0), r["message"]["usage"]["output_tokens"])
            blocks.setdefault(k, set()).update(budget.block_text(b) for b in r["message"]["content"])
    chars = sum(len(b) for bl in blocks.values() for b in bl)
    ratios.append(chars / exact)
    print("%-3s exact output tokens %5d  recorded %4d (%2d%%)  content chars %5d  chars per exact token %.2f" % (cell, exact, sum(out.values()), 100 * sum(out.values()) / exact, chars, chars / exact))
print("median chars per exact token %.2f, range %.2f to %.2f over %d runs" % (statistics.median(ratios), min(ratios), max(ratios), len(ratios)))
