## symbols
- `__instrumenta__/`: the lab folder for helper scripts, one file each, created by `/lab`.
- `.ignore`: the file `/lab` writes at the lab root; colgrep, ripgrep and fd skip the paths it lists.

## S-w03-author-w03-2-1
The instruction to search `__instrumenta__/` before writing was read by every worker (the note and the agent file are in the transcripts of all three) and in the headless lab 0 of 3 called colgrep; two ran `ls` on an empty folder and one did not look. In the six one-agent probes 1 called `search` with `paths` and `limit: 5` and the rest used `ls` and `head`. With 3 files in the folder `ls` is the cheaper search; I do not know where it stops being enough, and the lab was too small to show it. A lab with 30 scripts is the missing case.
refs: /tmp/author-w03-2/run1.jsonl (raw); __reports__/reflective_run/w03/author-w03-2/run1_measure.json; __reports__/reflective_run/w03/author-w03-2/author_probe_runs.json

## S-w03-author-w03-2-2
The proof-adversary wrote its own check without looking in `__instrumenta__/`, and its agent file says to write code that does not import the author's. That is right for independence, but it makes verifiers the one role that never reuses a script. The reproducer's file says to run or read the author's instruments; that was not exercised (no reproducer in the headless lab).
refs: __reports__/reflective_run/w03/author-w03-2/list_tool_calls.py on the session `59b76b3e-7639-4bf2-9993-852668550e4e`; agents/proof-adversary.md, agents/reproducer.md

## S-w03-author-w03-2-3
The heredoc share of output characters went up in the headless lab (72% of the workers' output, 55% before) while inline Python went to 0. Writing a script, a report or a verdict is a heredoc, so that share cannot tell "code run inline" from "files saved". The figure to watch is the inline-Python count (715 of 967 heredocs before). The PI's baseline name, "heredocs", mixes the two.
refs: __reports__/reflective_run/w03/author-w03-2/baseline.json; run1_measure.json

## S-w03-author-w03-2-4
The main-thread author, asked for one line of arithmetic with the extra sentence "No claim file is needed", ran it as `python3 -c` and wrote no file; asked the same without that sentence, 6 of 6 wrote a file. Neither had a start note (the hook's note reaches subagents only), so the sentence in the prompt is the one difference I know of, from one run against six. A prompt that says no claim is needed seems to tell the agent that nothing is to be kept.
refs: /tmp/author-w03-2/probe_main.jsonl (raw); __reports__/reflective_run/w03/author-w03-2/author_probe_runs.json

## S-w03-author-w03-2-5
A CLI `colgrep search` with a path argument, in a folder with no indexed ancestor, builds a separate index of that path. Three such searches on this worktree made three sub-indexes (`probes`, `scripts`, `reflective_run`) in my scratch store. Whoever searches a subfolder of a lab that was never indexed leaves one index per subfolder, in the user's store. This is the stale-index source the user described; `/lab` building the root index first prevents it for labs, not for other folders. Separately, some session has indexed `/private/tmp` as a whole project (`tmp-a825743a`): a lab made under `/tmp` without its own `COLGREP_DATA_DIR` would fold into it; not tested.
refs: /tmp/author-w03-2/wt-index/ (three folders); ~/Library/Application Support/colgrep/indices/tmp-a825743a/project.json

## S-w03-author-w03-2-6
colgrep `search -l -k 50` listed fewer files than the index holds (a file whose text had nothing to do with the query was missing in two probe runs; `colgrep` printed "indexed 703 files" while 578 were listed for a broad query with `-k 100000`). I used a query that matches every probe file's text to compare setups, so the table is sound, but a file list from `-l` is a ranked list, not the index content.
refs: __reports__/reflective_run/w03/author-w03-2/colgrep_scope_probe.py; /tmp/author-w03-2/wt_indexed_files.txt

## S-w03-author-w03-2-7
The `.ignore` file also hides paths from ripgrep and fd, and perhaps from Claude Code's Glob tool, which is the documented fallback for reading `__instrumenta__/`. The fallback folder is not in the block, but I did not test Glob on a hidden path (no Glob tool in this agent's tool list). The block also hides every `*.json` and `*.txt` of the lab from the semantic index, including a JSON config an instrument might need.
refs: scripts/lab_init.py (IGNORE_BLOCK); __reports__/reflective_run/w03/author-w03-2/colgrep_scope_probe.json

## S-w03-author-w03-2-8
I held myself to the practice and slipped twice: I ran the first probe lab, the category counts and one tally as inline heredocs before writing them as files (`ignore_effect_counts.py`, `colgrep_scope_probe.py`), and the scoped searches I made before writing each script found nothing that fitted except a close neighbour (`extract_calls.py`, which has fixed session paths). The search returned five hits each time and I wrote a new file each time; whether that is reuse failing or the scripts being too specific I cannot say.
refs: __reports__/reflective_run/w01/explorer-w01-c/extract_calls.py; __reports__/reflective_run/w03/author-w03-2/

## S-w03-author-w03-2-9
The PI's baseline of 42 workers and 1,811 Bash calls changes while wave 3 runs (the folder now holds 43 transcripts without mine, then more). The filter that gives a fixed set is `--exclude-name w03` (40 workers, 1,703 Bash calls), which also drops the two wave-3 workers present when the PI counted. The PI's 598 shell searches and 238 file-walking Python heredocs are the rules "grep, rg or find as a word anywhere in the command" and "python and `glob` in the command"; the narrower rules I wrote (heredoc bodies removed; `glob` as a word plus `os.walk`, `listdir`, `rglob`, `iterdir`, `scandir`) give 504 and 136. Which one the user means by "searched by hand" is the PI's call.
refs: __reports__/reflective_run/w03/author-w03-2/baseline.json; scratchpad/heredoc_measure.py

## S-w03-author-w03-2-10
After the PI's restatement (folders-only `.ignore`), the Grep probe returned 6 of 10 needle files as intended. To run it I had to pass `--tools Grep`: a headless session with `--setting-sources project,local` has no Glob or Grep tool at all, so which tools a session carries depends on the user settings, and the verifier's earlier probes (Grep present with only built-in plugins) must have had them some other way. I do not know which setting adds them. Also: the PI's list of folders (hand-backs, `raw/`, `runs/`) did not name `generated/`; I kept `**/generated/` because the user asked for an index free of generated code, and dropped `*.min.js` as a file pattern. Say if `generated/` should go.
refs: __reports__/reflective_run/w03/author-w03-2/ignore_grep_probe.py, ignore_grep_probe.json; scripts/lab_init.py (IGNORE_BLOCK)
