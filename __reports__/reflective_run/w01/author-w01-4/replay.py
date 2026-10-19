#!/usr/bin/env python3
"""Replay the prompts of real transcripts through the shipped rule and the patched rule.

Why a script: the question is a count over ~10^3 records of JSONL; the rules are the real
functions (imported, not re-implemented), so the numbers cannot drift from the code.

Usage:  python3 -I replay.py [--quick]      (--quick: only this run's transcript and 3ccc590f)
Output: table on stdout, per-turn rows in replay_rows.tsv next to this file.
No network, no writes outside this folder, ~2 s.

A hook-time `prompt` is rebuilt from a transcript record as the Desktop sends it: text blocks joined
with "\n" (MEASURED in explorer-w01-f run4); a slash command record becomes "/name args" (ASSUMPTION,
not checked: no slash command of the five transcripts is a lab command).
Which records fire UserPromptSubmit: human user records (certain), mid-turn typed prompts stored as
`queued_command` attachments (MEASURED here, case7), scheduled prompts (MEASURED here, case8),
platform "finished a turn" notices (UNVERIFIED; counted separately), task notifications and peer
messages (skipped by both rules; not counted).
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "patched", "scripts"))
import user_words as new  # noqa: E402
OLD_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts"))
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("user_words_shipped", os.path.join(OLD_PATH, "user_words.py"))
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)

PROJ = os.path.expanduser("~/.claude/projects")
COMB = PROJ + "/-Users-hacker-Documents-explore-combinatorics-on-binary/"
THIS = PROJ + "/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/"
FILES = [COMB + "566fa912-7009-421a-9d79-11145e2b8db9.jsonl", COMB + "82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl",
         COMB + "3ccc590f-0187-4f79-b7af-4955944f1374.jsonl", COMB + "2947f9dc-1c3a-452b-97a5-39d4510a1271.jsonl",
         THIS + "ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl"]
if "--quick" in sys.argv:
    FILES = [FILES[2], FILES[4]]


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")


def hook_prompt(content):
    t = text_of(content)
    if t.startswith("<command-message>"):
        name = re.search(r"<command-name>([^<]*)</command-name>", t)
        args = re.search(r"<command-args>(.*?)</command-args>", t, re.S)
        n = name.group(1) if name else ""
        return ((n if n.startswith("/") else "/" + n) + " " + (args.group(1) if args else "")).strip()
    return t


def events(path):
    """(class, hook prompt) in file order. Sidechains and tool results are not user prompts."""
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("isSidechain"):
            continue
        if r.get("type") == "user" and r.get("toolUseResult") is None:
            kind = (r.get("origin") or {}).get("kind")
            t = text_of(r["message"]["content"])
            if t.startswith(("[Request interrupted", "[Image:")):
                continue
            if kind == "human" and not r.get("isMeta"):
                yield "human", hook_prompt(r["message"]["content"])
            elif kind is None and r.get("turnOrigin") == "scheduled":
                yield "scheduled", t
            elif kind is None and r.get("turnOrigin") == "sdk" and not r.get("isMeta"):
                yield "platform_notice", t
        elif r.get("type") == "attachment":
            a = r.get("attachment") or {}
            if a.get("type") == "queued_command" and a.get("commandMode") == "prompt" \
                    and (a.get("origin") or {}).get("kind") == "human":
                yield "human_midturn", text_of(a.get("prompt"))


def old_entry(prompt):
    if not old.is_genuine(prompt) or not prompt.strip() or old.is_lab_command(prompt) or old.is_bare_command(prompt):
        return None
    return prompt.rstrip("\n")


def new_entry(prompt):
    p = new.strip_leading(prompt)   # the same order as handle(): command tests before the paste wrapper is removed
    if not new.is_genuine(p) or not p.strip() or new.is_lab_command(p) or new.is_bare_command(p):
        return None
    w = new.unwrap_pasted(p)
    return w.rstrip("\n") if w.strip() else None


def why(prompt, o, n):
    tags = []
    if re.match(r"\s*<system-reminder>\n", prompt):
        tags.append("leading_reminder")
    if re.search(r"<artifact-view-context\b", prompt):
        tags.append("view_context")
    if "<pasted_content id=" in prompt:
        tags.append("pasted_wrapper")
    if o is not None and n is None:
        tags.append("DROPPED(not user text)")
    if o is None and n is not None:
        tags.append("ADDED")
    return "+".join(tags) or "other"


def main():
    rows = []
    total = {}
    for path in FILES:
        sid = os.path.basename(path)[:8]
        for cls, prompt in events(path):
            o, n = old_entry(prompt), new_entry(prompt)
            rows.append((sid, cls, o is not None, n is not None, o != n, why(prompt, o, n), len(o or ""), len(n or ""),
                         (prompt[:60]).replace("\n", "\\n")))
    with open(os.path.join(HERE, "replay_rows.tsv"), "w") as fh:
        fh.write("session\tclass\tcurrent_stores\tnew_stores\tdiffer\treason\tcurrent_chars\tnew_chars\tprompt_head\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    print("session   class            fired  current  new   differ  | reasons among differing")
    for sid in dict.fromkeys(r[0] for r in rows):
        for cls in ("human", "human_midturn", "scheduled", "platform_notice"):
            sel = [r for r in rows if r[0] == sid and r[1] == cls]
            if not sel:
                continue
            rs = {}
            for r in sel:
                if r[4]:
                    rs[r[5]] = rs.get(r[5], 0) + 1
            print("%-9s %-16s %5d  %7d %4d  %6d  | %s" % (sid, cls, len(sel), sum(r[2] for r in sel), sum(r[3] for r in sel),
                                                         sum(r[4] for r in sel), rs))
    print()
    for label, classes in (("human (typed: user records + mid-turn)", ("human", "human_midturn")),
                           ("non-human that fire the hook (scheduled + platform notice)", ("scheduled", "platform_notice")),
                           ("all", ("human", "human_midturn", "scheduled", "platform_notice"))):
        sel = [r for r in rows if r[1] in classes]
        print("%-62s fired %3d  current stores %3d  new stores %3d  entries that differ %3d  chars current %7d new %7d"
              % (label, len(sel), sum(r[2] for r in sel), sum(r[3] for r in sel), sum(r[4] for r in sel),
                 sum(r[6] for r in sel), sum(r[7] for r in sel)))
    h = [r for r in rows if r[1] in ("human", "human_midturn")]
    print("typed turns whose current entry starts with a platform reminder: %d of %d" %
          (sum("leading_reminder" in r[5] for r in h), len(h)))
    # quote-reply: entries (new rule) that start with a '> ' quote, and the share of their text that is the quote
    q = n_q = 0
    qbytes = tot = 0
    for path in FILES:
        for cls, prompt in events(path):
            if cls not in ("human", "human_midturn"):
                continue
            e = new_entry(prompt)
            if e and e.startswith("> "):
                m = re.match(r"((?:>.*\n?)+)", e)
                q += 1
                qbytes += len(m.group(1))
                tot += len(e)
    print("typed entries (new rule) that open with a '> ' quote block: %d; quote chars %d of %d chars in those entries" % (q, qbytes, tot))
    # fidelity: the shipped rule on this run's two real prompts vs what the hook stored (main checkout, read only)
    main_words = "/Users/hacker/Documents/src/CrackingShells/Murmuration/__statera__/user_words.md"
    if os.path.exists(main_words) and FILES[-1].endswith("ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl"):
        stored = re.split(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}\n\n", open(main_words, encoding="utf-8").read(), flags=re.M)[1:]
        stored = [s.rstrip("\n") for s in stored][-2:]
        mine = [old_entry(p) for c, p in events(FILES[-1]) if c == "human"][:2]
        print("fidelity (shipped rule on this run's records == bytes stored by the hook): %s" %
              [a == b for a, b in zip(stored, mine)])


if __name__ == "__main__":
    main()
