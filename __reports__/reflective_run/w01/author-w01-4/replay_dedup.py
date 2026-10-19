#!/usr/bin/env python3
"""Replay.py's comparison, deduplicated: forks copy the first records of their parent session (same uuid), and the
hook fired once, in the original session. A user record is keyed by its uuid, a mid-turn prompt (queued_command
attachment) by its delivery_id. Writes the table to stdout and distinct rows to replay_dedup_rows.tsv.

Usage: python3 -I replay_dedup.py            (about 2 s, no network, writes only replay_dedup_rows.tsv here)
"""
import collections
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rp", os.path.join(HERE, "replay.py"))
rp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp)


def keyed(path):
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("isSidechain"):
            continue
        if r.get("type") == "user" and r.get("toolUseResult") is None:
            kind = (r.get("origin") or {}).get("kind")
            t = rp.text_of(r["message"]["content"])
            if t.startswith(("[Request interrupted", "[Image:")):
                continue
            if kind == "human" and not r.get("isMeta"):
                yield "human", ("u", r.get("uuid")), rp.hook_prompt(r["message"]["content"])
            elif kind is None and r.get("turnOrigin") == "scheduled":
                yield "scheduled", ("u", r.get("uuid")), t
            elif kind is None and r.get("turnOrigin") == "sdk" and not r.get("isMeta"):
                yield "platform_notice", ("u", r.get("uuid")), t
        elif r.get("type") == "attachment":
            a = r.get("attachment") or {}
            if a.get("type") == "queued_command" and a.get("commandMode") == "prompt" \
                    and (a.get("origin") or {}).get("kind") == "human":
                p = rp.text_of(a.get("prompt"))
                yield "human_midturn", ("q", a.get("delivery_id") or p), p


seen, rows, raw = set(), [], collections.Counter()
for path in rp.FILES:
    for cls, key, prompt in keyed(path):
        raw[cls] += 1
        if key in seen:
            continue
        seen.add(key)
        o, n = rp.old_entry(prompt), rp.new_entry(prompt)
        rows.append((os.path.basename(path)[:8], cls, o is not None, n is not None, o != n, rp.why(prompt, o, n),
                     len(o or ""), len(n or ""), prompt[:60].replace("\n", "\\n")))
with open(os.path.join(HERE, "replay_dedup_rows.tsv"), "w") as fh:
    fh.write("session\tclass\tcurrent_stores\tnew_stores\tdiffer\treason\tcurrent_chars\tnew_chars\tprompt_head\n")
    fh.writelines("\t".join(map(str, r)) + "\n" for r in rows)
print("class             fired(raw)  distinct  current stores  new stores  differ  dropped(typed)  chars current -> new")
for label, classes in (("typed (human + mid-turn)", ("human", "human_midturn")), ("not typed", ("scheduled", "platform_notice")),
                       ("all", ("human", "human_midturn", "scheduled", "platform_notice"))):
    s = [r for r in rows if r[1] in classes]
    drop = sum(1 for r in s if r[2] and not r[3]) if classes[0] == "human" and label.startswith("typed") else "-"
    print("%-24s %8d  %8d  %14d  %10d  %6d  %14s  %d -> %d" % (label, sum(raw[c] for c in classes), len(s),
          sum(r[2] for r in s), sum(r[3] for r in s), sum(r[4] for r in s), drop, sum(r[6] for r in s), sum(r[7] for r in s)))
