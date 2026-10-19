#!/usr/bin/env python3
"""w02-c2: replay the prompts of five real transcripts through the shipped hook before and after the text rule.

Why a script: the question is a count over ~10^4 JSONL records, and `handle()` itself must run on each prompt,
so the counts cannot drift from the code.

Usage:  python3 -I replay.py [--quick]
          --quick  only 3ccc590f and this run (about 0.2 s)
Reads (read only): the five transcripts named in __design__/framing.md. Writes only replay_rows.tsv here.
No network, no seeds (deterministic), about 3 s. Each file is read up to a pinned line count (PINS) so
the numbers hold while this run's transcript keeps growing; the prefix hash is checked.

"Stores" = what `handle()` appends to a lab's user_words.md, measured by running `handle()` in a temporary lab:
  after  = scripts/user_words.py of this worktree (the text rule applied)
  before = baseline_user_words.py here (scripts/user_words.py of commit a8b5d5d, byte copy)
  no_side = after, with the third leading block (`<side-sessions-event>`) removed from LEADING_BLOCKS
A hook-time `prompt` is rebuilt from a record as text blocks joined with "\n" (measured by explorer-w01-f run4;
byte-checked here on this run's two earliest entries against the main checkout's user_words.md);
a slash-command record is rebuilt as "/name args" (ASSUMED).
"""
import collections
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PROJ = os.path.expanduser("~/.claude/projects")
COMB = PROJ + "/-Users-hacker-Documents-explore-combinatorics-on-binary/"
THIS = PROJ + "/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/"
# (path, pinned line count, sha256 of those lines)
PINS = [
    (COMB + "566fa912-7009-421a-9d79-11145e2b8db9.jsonl", 2149, "b5bd8ef66362"),
    (COMB + "82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl", 2375, "1a684a91ab18"),
    (COMB + "3ccc590f-0187-4f79-b7af-4955944f1374.jsonl", 467, "af62f33255d7"),
    (COMB + "2947f9dc-1c3a-452b-97a5-39d4510a1271.jsonl", 1875, "dfce400aa013"),
    (THIS + "ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl", 1527, "76ccc36d1b36"),
]
QUICK = "--quick" in sys.argv
if QUICK:
    PINS = [PINS[2], PINS[4]]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


after = load("uw_after", os.path.join(ROOT, "scripts", "user_words.py"))
before = load("uw_before", os.path.join(HERE, "baseline_user_words.py"))
no_side = load("uw_noside", os.path.join(ROOT, "scripts", "user_words.py"))
no_side.LEADING_BLOCKS = no_side.LEADING_BLOCKS[:2]
HEADING = re.compile(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}\n\n", re.M)


class Lab:
    """A temporary lab: stores(mod, prompt) runs mod.handle() and returns the text it appended, or None."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.makedirs(os.path.join(self.tmp.name, "__statera__"))
        self.path = os.path.join(self.tmp.name, "__statera__", "user_words.md")
        os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def stores(self, mod, prompt):
        size = os.path.getsize(self.path) if os.path.exists(self.path) else 0
        mod.handle({"prompt": prompt, "cwd": self.tmp.name})
        if not os.path.exists(self.path) or os.path.getsize(self.path) == size:
            return None
        with open(self.path, encoding="utf-8", newline="") as fh:
            fh.seek(0)
            data = fh.read().encode("utf-8")[size:].decode("utf-8")
        return HEADING.split(data.lstrip("\n"), maxsplit=1)[-1].rstrip("\n")


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


def events(lines):
    """(class, key, hook prompt). Key: record uuid, or delivery_id for a mid-turn prompt; forks copy uuids."""
    for line in lines:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("isSidechain"):
            continue
        if r.get("type") == "user" and r.get("toolUseResult") is None:
            kind = (r.get("origin") or {}).get("kind")
            t = text_of(r["message"]["content"])
            if t.startswith("[Request interrupted"):
                yield "interrupt", ("u", r.get("uuid")), t
            elif t.startswith("[Image:"):
                continue
            elif kind == "human" and not r.get("isMeta"):
                yield "typed", ("u", r.get("uuid")), hook_prompt(r["message"]["content"])
            elif kind is None and r.get("turnOrigin") == "scheduled":
                yield "scheduled", ("u", r.get("uuid")), t
            elif kind is None and r.get("turnOrigin") == "sdk" and not r.get("isMeta"):
                yield "notice", ("u", r.get("uuid")), t
        elif r.get("type") == "attachment":
            a = r.get("attachment") or {}
            if a.get("type") == "queued_command" and a.get("commandMode") == "prompt" \
                    and (a.get("origin") or {}).get("kind") == "human":
                p = text_of(a.get("prompt"))
                yield "typed", ("q", a.get("delivery_id") or p), p


def main():
    lab = Lab()
    seen, rows, raw, files = set(), [], collections.Counter(), []
    for path, pin, digest in PINS:
        with open(path, "rb") as fh:
            lines = fh.read().split(b"\n")
        if lines and lines[-1] == b"":
            lines.pop()
        n = pin or len(lines)
        got = hashlib.sha256(b"\n".join(lines[:n])).hexdigest()[:12]
        assert digest is None or got == digest, "%s: the first %d lines changed (%s != %s)" % (path, n, got, digest)
        files.append((os.path.basename(path)[:8], n, got))
        for cls, key, prompt in events(l.decode("utf-8", "replace") for l in lines[:n]):
            raw[cls] += 1
            if key in seen:
                continue
            seen.add(key)
            b, a, ns = lab.stores(before, prompt), lab.stores(after, prompt), lab.stores(no_side, prompt)
            rows.append((files[-1][0], cls, b, a, ns, prompt))
    with open(os.path.join(HERE, "replay_rows.tsv"), "w") as fh:
        fh.write("session\tclass\tbefore_chars\tafter_chars\tno_side_chars\tdiffer\tprompt_head\n")
        for s, c, b, a, ns, p in rows:
            fh.write("%s\t%s\t%d\t%d\t%d\t%d\t%s\n" % (s, c, len(b or ""), len(a or ""), len(ns or ""), b != a,
                                                       p[:60].replace("\n", "\\n").replace("\t", " ")))
    print("files (lines read, sha256 prefix of those lines):", ", ".join("%s %d %s" % f for f in files))
    print("%-22s %6s %8s %7s %7s %8s %9s %s" % ("class", "fired", "distinct", "before", "after", "differ", "dropped", "chars before -> after"))
    for label, classes in (("typed", ("typed",)), ("not typed (notice+sched)", ("notice", "scheduled")),
                           ("interrupt records", ("interrupt",))):
        s = [r for r in rows if r[1] in classes]
        drop = sum(1 for r in s if r[2] is not None and r[3] is None) if label == "typed" else "-"
        print("%-22s %6d %8d %7d %7d %8d %9s %d -> %d" % (
            label, sum(raw[c] for c in classes), len(s), sum(r[2] is not None for r in s), sum(r[3] is not None for r in s),
            sum(r[2] != r[3] for r in s), drop, sum(len(r[2] or "") for r in s), sum(len(r[3] or "") for r in s)))
    print()
    # what the third block (<side-sessions-event>) changes: after vs after-without-it
    d = [r for r in rows if r[3] != r[4]]
    print("third block `<side-sessions-event>` changes the stored text of %d prompts: classes %s" %
          (len(d), dict(collections.Counter(r[1] for r in d))))
    for cls in ("typed", "notice", "scheduled"):
        s = [r for r in rows if r[1] == cls]
        print("   %-9s distinct %3d  stores without the third block %3d  with it %3d" % (
            cls, len(s), sum(r[4] is not None for r in s), sum(r[3] is not None for r in s)))
    # nothing is rewritten: the stored 'after' text is one contiguous piece of the rebuilt hook prompt
    typed = [r for r in rows if r[1] == "typed" and r[3] is not None]
    ok = sum(1 for r in typed if r[3].strip() in r[5])
    print("typed entries whose stored 'after' text is one contiguous piece of the prompt: %d of %d" % (ok, len(typed)))
    # fidelity of the rebuilt prompt: this run's first two typed records vs the last two entries of the
    # main checkout's user_words.md (written by the hook there; read only)
    main_words = "/Users/hacker/Documents/src/CrackingShells/Murmuration/__statera__/user_words.md"
    this = [r for r in rows if r[0] == "ab96c5ed" and r[1] == "typed"][:2]
    if os.path.exists(main_words) and len(this) == 2:
        stored = [s.rstrip("\n") for s in HEADING.split(open(main_words, encoding="utf-8").read())[1:]][-2:]
        print("fidelity: the shipped rule on this run's first two typed records == the last two entries stored by the hook in the main checkout: %s"
              % [a == r[2] for a, r in zip(stored, this)])

if __name__ == "__main__":
    main()
