#!/usr/bin/env python3
"""Lists the tool calls of every transcript of one session in time order, with the start of each input; input: a session folder (its .jsonl beside it), output: lines on stdout.

    python3 -I list_tool_calls.py SESSION_DIR [WIDTH]
"""
import glob
import json
import os
import re
import sys


def calls(path):
    name = os.path.basename(path)[:22]
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        c = (r.get("message") or {}).get("content")
        if r.get("type") == "user" and isinstance(c, str):
            m = re.search(r"Your name is ([a-z0-9-]+)", c)
            if m:
                name = m.group(1)
        if r.get("type") == "assistant" and isinstance(c, list):
            for b in c:
                if b.get("type") == "tool_use":
                    yield r.get("timestamp", ""), b["name"], b.get("input", {})
    yield "~", "END", {"agent": name}


def main(argv):
    d, width = argv[0].rstrip("/"), int(argv[1]) if len(argv) > 1 else 160
    for f in [d + ".jsonl"] + sorted(glob.glob(d + "/subagents/*.jsonl")):
        name, rows = os.path.basename(f)[:22], []
        for ts, tool, inp in calls(f):
            if tool == "END":
                name = inp["agent"]
                continue
            rows.append((ts, tool, json.dumps(inp)[:width].replace("\\n", " ")))
        print("== %s (%d calls)" % (name, len(rows)))
        for ts, tool, s in rows:
            print("%s %-12s %s" % (ts[11:19], tool[:12], s))


if __name__ == "__main__":
    main(sys.argv[1:])
