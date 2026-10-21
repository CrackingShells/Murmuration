## S-w06-author-w06-7-1
The saving is small and not where the brief expected. Of the guard's 65 ms start (through `sh`), 31 ms is `sh` itself and 22 ms is the interpreter (`python3 -S -I -c pass` 53 ms total); `-S -I` bought 6.6 ms, import laziness nothing (the 5 ms of imports are `json` and `re`, both needed by the module), bytecode caching at most 2.2 ms. The 131 to 150 ms that reproducer-w06-8 read in the debug file under a live session is about twice what the command costs here, so most of it lies in the platform's hook start or in load, not in the script. A further saving would have to come from fewer starts (the Bash row has no `if`), not from a faster start; that is a decision about the guard's scope (it needs the whole text to judge) and is not taken here.
refs: /private/tmp/murmuration-w06/author-w06-7.bench.out, /private/tmp/murmuration-w06/reproducer-w06-8/runs/ordinary_auto/dbg.log

## S-w06-author-w06-7-2
The "0 changes" replays (decide_diff, the recorded-call replay) run `decide()` in process and could not fail for a change that only touches the command string or the docstring; the check that can fail is the end-to-end one through `sh -c` (`w06c14_cmd_equal.py`), and I put it first in the claim for that reason. What it still cannot see: a `python3` on another machine whose `-I` or `-S` differs, or whose standard library sits in a place only `site` finds (a broken venv). The old command had the same dependence on `python3`, but not on `-S`.
refs: __instrumenta__/w06c14_cmd_equal.py, /private/tmp/murmuration-w06/author-w06-7.equal.out

## S-w06-author-w06-7-3
The two other rows that still start plain `python3` (`user_words.py` on UserPromptSubmit and `resume_brief.py` on SessionStart resume|compact, at the head of `hooks/hooks.json`) were left alone: the brief names the guard only. `user_words.py` runs on every user prompt, `resume_brief.py` on resume or compact; whether they read the environment or import siblings (and so cannot take `-I`) I did not check.
refs: hooks/hooks.json lines 4-25

## S-w06-author-w06-7-4
In the live unreadable run the tool result begins `PreToolUse:Bash hook error: [python3 -S -I "..."]: python3: can't open file` and then the platform's own text; it blocks, as c13's h4 found. The model sees the flags in the message, which is harmless, but a reader grepping for the old command string in logs will no longer find it (reproducer-w06-8's `Hooks: PreToolUse:Bash [python3 ".../permission_guard.py"]` greps change).
refs: /private/tmp/murmuration-w06/author-w06-7/live/unreadable/stream.jsonl
