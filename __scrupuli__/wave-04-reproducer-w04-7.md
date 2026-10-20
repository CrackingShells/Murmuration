## S-w04-reproducer-w04-7-1
The folder at 429 scripts does not test search at all for either task: `collatz_longest_stopping_time.py` is entry 9 and `binary_max_distinct_substrings_bruteforce.py` entry 3 of the sorted listing, so the first call of every run (`ls | head -30..100`) showed both names. The precondition (ls at least 3x one colgrep search) is a statement about the full listing, which no worker printed in full. A fair precondition would include a target placed after the cut workers use (about 30 to 100 names).
refs: /private/tmp/murmuration-w04/author-w04-3/lab420_scripts (ls | grep -n collatz), /private/tmp/murmuration-w04/reproducer-w04-7/dump.txt call 0 of each run

## S-w04-reproducer-w04-7-2
Folder names do not match their content: `lab420_scripts` holds 429 scripts and `lab300_scripts` holds 336. A reader of the scripts folder under /private/tmp/murmuration-w04/author-w04-3/ would take the wrong set (my first run used `lab_scripts`, 46 files, and the dump looked as if every run had 380 new files).
refs: /private/tmp/murmuration-w04/author-w04-3/lab420_scripts, lab300_scripts

## S-w04-reproducer-w04-7-3
The claim head states claude 2.1.302; the E3b runs and probes report claude_code_version 2.1.304 (E3 runs were 2.1.302). The binary changed between E3 and E3b, so the "same as w04-c4" comparison (5 of 9 adapted at 46 scripts against 0 of 6 at 429) is also across a version change, besides differing in folder size, task sampling and arms.
refs: /private/tmp/murmuration-w04/author-w04-3/runs_b/pt1r1/run.jsonl (claude_code_version), runs/ct1r1/run.jsonl

## S-w04-reproducer-w04-7-4
s3 is a count of whole tool results of calls that name the folder, so a `ls ... | head -30` that also prints `__design__` and framing.md and a `sed -i`/`git commit` call (31 characters, pt1r3) are in it. The effect here is small (framing.md is 447 characters), but the metric is an upper bound by construction, and with workers making only 4 to 6 calls the median of 6 moves with one extra `head` call. P's range (2,163 to 6,832) overlaps Q's (1,934 to 6,007); the rule looks only at medians.
refs: /private/tmp/murmuration-w04/reproducer-w04-7/dump.txt pt1r3 call 5; e3_measure.py search_kind

## S-w04-reproducer-w04-7-5
The 12 runs are 5 to 7 turns and USD 0.07 to 0.10 each, and the worker picks the fit script after one or two calls. This means "reuse" on t1 is mostly "the task equals the script", which any folder look would catch; the 3 of 6 strict reuse depends on that task design, not on the arms. The near-fit task (the part where search could matter) gives 0 of 6 in both arms and also in the 336 set.
refs: runs_b/*/run.jsonl num_turns; e3b_runs_table.tsv

## S-w04-reproducer-w04-7-6
The probe's ratio is query-dependent: 5,136 (binary query, author), 4,513 (the search pt2r2 made), 4,468 (my Collatz probe). The 429 threshold margin over 3 is 9% at the author's largest result; the 336 set missed it by a similar margin (2.45 to 2.70). A different `snippet_lines` or a longer query would move it. Headless search probes cost about USD 0.28 each, almost all of it the plugin load, not the search.
refs: __reports__/reflective_run/w04/author-w04-3/e3b/e3b_search_probe_429.json, /private/tmp/murmuration-w04/reproducer-w04-7/probe/probe.jsonl
