#!/usr/bin/env python3
"""Task 2 check: every AskUserQuestion answer in the five transcripts, run through ask_capture.handle().

For each dialog result (tool_result of an AskUserQuestion call) the hook payload is rebuilt as
{tool_name, tool_input: {questions}, tool_response: <record's toolUseResult>} (the shape the headless
host test showed, see notes in the claim) and run in a temporary lab. Checks: the entry holds every
answer text verbatim; and how often the model-facing string of the tool result loses that
(multi-select answers joined by a bare comma).
Usage: python3 -I replay_asks.py      (about 1 s, read only)
"""
import glob
import json
import os
import tempfile

import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ask_capture", os.path.join(HERE, "ask_capture.py"))
ac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ac)
P = os.path.expanduser("~/.claude/projects/")
FILES = sorted(glob.glob(P + "-Users-hacker-Documents-explore-combinatorics-on-binary/*.jsonl")) + [
    P + "-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl"]
os.environ.pop("CLAUDE_PROJECT_DIR", None)
seen, n_dialogs, n_answers, n_ok, n_list, n_lossy, n_multi = set(), 0, 0, 0, 0, 0, 0
for path in FILES:
    uses = {}
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        c = (r.get("message") or {}).get("content")
        if not isinstance(c, list):
            continue
        for b in c:
            if b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion":
                uses[b["id"]] = b["input"]
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in uses and b["tool_use_id"] not in seen:
                seen.add(b["tool_use_id"])
                tur = r.get("toolUseResult")
                if not isinstance(tur, dict) or "answers" not in tur:
                    print(os.path.basename(path)[:8], "dialog without answers:", repr(b.get("content"))[:80])
                    continue
                n_dialogs += 1
                with tempfile.TemporaryDirectory() as tmp:
                    os.makedirs(os.path.join(tmp, "__statera__"))
                    ac.handle({"tool_name": "AskUserQuestion", "cwd": tmp, "tool_input": uses[b["tool_use_id"]], "tool_response": tur})
                    entry = open(os.path.join(tmp, "__statera__", "user_words.md"), encoding="utf-8").read()
                for q, a in tur["answers"].items():
                    for item in (a if isinstance(a, list) else [a]):
                        n_answers += 1
                        n_ok += item in entry
                    if isinstance(a, list):
                        n_list += 1
                        # the model-facing string joins a list with a bare comma: ambiguous when an item has a comma
                        n_multi += len(a) > 1
                        n_lossy += len(a) > 1 and any("," in item for item in a)
                assert all(q in entry for q in tur["answers"]), "a question text is missing"
print("dialogs with answers: %d; answer texts: %d; found verbatim in the stored entry: %d" % (n_dialogs, n_answers, n_ok))
print("list answers: %d; with 2 or more items: %d; of these with a comma inside an item (the comma-joined string cannot be split back): %d" % (n_list, n_multi, n_lossy))
