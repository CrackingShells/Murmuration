## S-w08-author-w08-10-1
Three of the eight direct false allows of explorer-w08-j stay allowed after the change, and they are not of the two causes: c177 starts `"$BIN" -p ... --setting-sources project` (a variable is the program, inside a heredoc script), c202 puts the flag in a variable (`extra='--settings {"disableAllHooks":true}'` ... `$extra`), c203 gives `--settings nohooks.json` where the file written in the same call holds `disableAllHooks`. A worker who writes the natural launch form with a variable or a settings file still passes. Is the guard meant to see variables and files at all (its docstring says no), or should the rule be "a `claude` command line with a flag word and any non-literal word is denied"? I did not try that rule; it would deny c177, c202 and also every `"$CLAUDE" -p ...` in the lab's scripts.
refs: __reports__/wave-08/author-w08-10/frozen_compare.md, __reports__/wave-08/explorer-w08-j/guard_replay_v0.json (ids c177, c202, c203)

## S-w08-author-w08-10-2
A false denial that was already there stays, by construction: `echo "$(claude -p hi --setting-sources=user)"` (and `out="$(claude ... --setting-sources=user)"`) is denied by G2 on the old reading, where the segment ends in `)"` and the value becomes `user)"`. I kept every old reading so that nothing denied is allowed (the monotone argument), which keeps this denial too. Two of the 970 control cases show it. The change could drop the old reading of substitutions and lower the false denials, but then "nothing denied is allowed" would need a measurement instead of an argument.
refs: __reports__/wave-08/author-w08-10/cases_new.txt (control row), __instrumenta__/w08_c10_cases.py shapes claude_inside_dq_subst, claude_inside_dq_assign

## S-w08-author-w08-10-3
The count of recorded calls I can replay is 10,375 (folders `~/.claude/projects/*Murmuration*`, 401 of them), not the 20,896 of explorer-w08-j's collection and of my brief; explorer-w08-j's collect script takes folders of the Murmuration lab by another pattern (the 3,300 arena folders of the guard tests). I do not know which of the two `check_guard_equal.py` is meant to see by default; it uses the capitalised glob, so the arena folders are not in its default set. (c) is stated on the 10,375, and on the frozen set of 739 that holds the arena-denied cases.
refs: __reports__/wave-08/author-w08-10/recorded_diff.txt, scripts/check_guard_equal.py (recorded_events, default folders)

## S-w08-author-w08-10-4
The only new denial in the recorded calls that is not one of the five label-true hole calls is a PI heredoc that edits the wave note through `python3` and quotes the hole form in prose (`env -u VAR claude ... --setting-sources project`). It is a false denial by the labels (prose), but it is the same text as the hole form, and the plain prose form `claude ... --setting-sources project` was already denied at baseline (G2 false denials, 22 in the frozen set). The guard cannot tell prose from a command here; whoever writes the note has to word it as the explorer did before (S-w08-explorer-w08-j-1 refs). The cost of the change to ordinary writing is therefore one more phrase to avoid.
refs: __reports__/wave-08/author-w08-10/recorded_diff.json (id toolu_01Xp1p3ZrDZs4hNSLeHTBHw4)

## S-w08-author-w08-10-5
My own first helper call was denied live by G3: a python heredoc that patched a case list and named `settings.json` in a string next to `open(..., 'w')`. It did not touch any settings file. That is the false-denial class explorer-w08-j counted (G3, interpreter branch); I used the Edit tool instead. The rule cost me one call and some minutes in a task about this guard.
refs: none kept (the denied call is in this session's transcript)

## S-w08-author-w08-10-6
The option tables of the wrappers (which options of `env`, `timeout`, `ionice`, `stdbuf`, `xargs`, `caffeinate`, `sudo`, `time`, `exec` take a value) are from my memory of GNU and BSD usage; no man page was read (no downloads) and no wrapper was run. A letter missing from a table is a hole again; a letter wrongly present skips one word, which is never `claude` (the program word is kept when it is `claude`), so the worst case there is a missed program other than `claude` (a G3 target such as `cp` behind a skipped value). Nothing in the experiment can tell which table entries are wrong.
refs: scripts/permission_guard.py VALUE_OPTS, rust/src/guard.rs VALUE_OPTS

## S-w08-author-w08-10-7
Process substitution `<( )` / `>( )` was not in my protocol; I found it by thinking about "substitutions in other positions", added it, and the case generator's first run after that showed 12 allowed holes until I also fixed the early exit that looked only for `$(` and a backtick. The metamorphic generator found the bug at once, but I wrote its shapes after the first implementation, so the shapes I did not think of are the ones that stay open: `$'...'` words, `${var:-$(...)}` forms, here-strings, a substitution that is the flag itself (`"$(echo --bare)"`) are not in the 3,945 cases.
refs: __instrumenta__/w08_c10_cases.py SHAPES
