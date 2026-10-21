## S-w04-reproducer-w04-10-1
The pass rests on one run. The rule (at least 4 of 6) is met by exactly 4, and the fourth hit is pt2r2, the only near-fit hit. Take pt2r2 away and the result is 3 of 6, which is neither "works" (4 or more) nor "fails" (2 or fewer). The three fit runs hit because the file name repeats the task's words ("substrings", "distinct"), so the near fit is the informative arm, and it reads 1 of 3.
refs: /private/tmp/murmuration-w04/author-w04-3/runs_c/pt2r2/run.jsonl (call 1: `ls | grep -i -E "collatz|peak|max"`, call 3: cat of the near fit); __reports__/reflective_run/w04/author-w04-3/e3c/e3c_runs_table.tsv

## S-w04-reproducer-w04-10-2
s7 counts "name in a command", not "name seen". pt2r3 and pt2r2 both had the near fit's name in the output of their grep; pt2r3 saw it and chose two other Collatz scripts (the shorter ones, whose first line says "one start value"). Is that a find failure or a judgement that the name did not match the task? The table cannot tell; the s7 flag gives no "seen but not opened" column.
refs: runs_c/pt2r3/run.jsonl call 1 (res includes steps_longest_collatz_stopping_time_below_limit.py)

## S-w04-reproducer-w04-10-3
`ls | grep -i` is the method in 5 of 6 runs although the shipped paragraph does not tell workers to do it. Where do workers get it from? In all 6 runs the first call was `ls __instrumenta__ ... | head -30/50`, and the second a keyword grep; this looks like a habit of the model, not of the plugin. Whether it holds on the other models/versions (2.1.304 only) is not tested.
refs: runs_c/*/run.jsonl call 0 and call 1

## S-w04-reproducer-w04-10-4
Init records have no `agent` field (version 2.1.304), so the arm cannot be read from the run record; only the command line in `e3_run_workers.py` line 74 (`--agent murmuration:author`) and the behaviour (workers file a w04-c9 claim head) show it. Not a doubt about the result, a gap in the audit trail.
refs: runs_c/pt1r1/run.jsonl line 1; __instrumenta__/e3_run_workers.py:74

## S-w04-reproducer-w04-10-5
Workers leave the lab. pt1r1 (calls 3-5) read the research-loop skill from the PI's scratchpad `.../ab96c5ed-.../scratchpad/rep8x/B2c/skills/research-loop`, found by `find / -path "*research-loop*"`; pt2r2 and pt2r3 read the skill from the plugin cache or the author's export. None touched the target names, but the labs are not sealed from the host file system; the skill text they read is from different versions (cache 0.1.0 vs export vs PI scratch copy), which is a small uncontrolled variable across runs.
refs: runs_c/pt1r1/run.jsonl calls 2-5; runs_c/pt2r2/run.jsonl call 3; runs_c/pt2r3/run.jsonl call 5

## S-w04-reproducer-w04-10-6
The lab in the run folders holds 430 files in `__instrumenta__` (429 + the worker's own script) and `.ignore`/colgrep index per run; colgrep was available (9 tools in the init) and still 0 of 6 calls. In w04-c7 1 of 6 called `search`. With 0/6 vs 1/6 the rate of colgrep use is not distinguishable from the same value; the claim says "never by colgrep", which is true of these 6 runs only.
refs: runs_c/pt1r1/run.jsonl init record (`tools`); w04-c7 claim file
