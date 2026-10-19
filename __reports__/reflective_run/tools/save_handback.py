#!/usr/bin/env python3
"""Save the last hand-back of a named agent from a session transcript to a file.

Usage: save_handback.py <transcript.jsonl> <agent-name> <out.md>

Hand-backs land in several record kinds (user messages, queue-operation, attachment), so every
string field of every record is searched; the longest occurrence wins (some records hold truncated renderings). Prototype for a SubagentStop
hook that would persist `last_assistant_message` (research-pi, reflective run wave 1).
"""
import json, sys

def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)

path, name, out = sys.argv[1:4]
key = '<agent-message from="%s">' % name
best = (None, None)
for i, line in enumerate(open(path, encoding="utf-8"), 1):
    if name not in line:
        continue
    for s in strings(json.loads(line)):
        if key in s and "[Subagent hand-back]" in s:
            t = s[s.index(key):]
            if best[1] is None or len(t) > len(best[1]):
                best = (i, t)
if best[1] is None:
    sys.exit("no hand-back from %s" % name)
with open(out, "w", encoding="utf-8") as fh:
    fh.write("<!-- Saved by research-pi with __reports__/reflective_run/tools/save_handback.py from %s line %d: the Write tool refused the agent's own report file. Text unchanged. -->\n\n" % (path.rsplit("/", 1)[-1], best[0]))
    fh.write(best[1])
print(out, best[0], len(best[1]))
