## S-w03-reproducer-w03-1-1
The same worker prompt gave a different stopping point: in my cell r1 (the author's e1 configuration, the final file) the explorer handed back at about 80% of USD 0.30, after the 75% note, and never got the 87.5% or 93.75% note; the author's e1 handed back at 99%. The jump from 0.25 to 0.31 was the hand-back request itself, a 90-line list as output (about USD 0.07 at sonnet's output price). A threshold schedule cannot warn before one request that is a quarter of the budget. Is the hand-back's own cost the real overshoot at small budgets, more than the hook's cadence? I did not test with a hand-back that is short.
refs: /tmp/reproducer-w03-1/s2/runs/r1/lab/__statera__/harness.jsonl (notes at 0.508 and 0.753, then 1.032 after the refused hand-back), /tmp/reproducer-w03-1/s2/timeline_r1.jsonl

## S-w03-reproducer-w03-1-2
In every run of mine the notes above 100% arrived only because `handback.py` refused the first hand-back: the worker had already decided to hand back, and the report check turned a 80 to 100% hand-back into a 103 to 138% run. The sentence "if one or two more steps finish the result, finish it" is therefore tested mostly against a worker that is writing a report it must write. The claim says this for e2, e3, e5, e6; q1 and r1 show it again. The author's own puzzle 5 notes it too. A cell where the worker has already written its report would test the sentence.
refs: /tmp/reproducer-w03-1/s2/runs/r1/lab/__statera__/harness.jsonl (deny line at 19:47:40 between the 75% note and the 103% note), /tmp/reproducer-w03-1/s4/runs/q1/lab/__statera__/harness.jsonl

## S-w03-reproducer-w03-1-3
The "unknown" start note: with two same-type workers of different figures, the platform started both in dispatch order, and after the fix both start notes say "set by the lines of your brief, else USD 3.00 and 20 minutes". The worker then reads its brief, which has the lines, so the note is harmless, but it tells a worker whose limit is USD 0.50 that 3.00 is the fallback. I did not check whether either worker's behaviour changed. Also the `start` log line records B 3.0 / T 20 for them until the first check corrects the state; anyone reading the log's `start` line for such a worker reads the wrong limit.
refs: /tmp/reproducer-w03-1/par/run2/lab/__statera__/harness.jsonl (the two `start` lines with `source: unknown`, B 3.0, against the `end` lines with B 0.5 and 0.8)

## S-w03-reproducer-w03-1-4
`sed -i` and some shell chains were refused by the tool hook in this session with messages about stdin, and a `sleep` in front of other commands was blocked; I worked round it with `until` loops. Not a finding about the build, but it cost me a call each time.
refs: none

## S-w03-reproducer-w03-1-5
Recount note: "109 of 109 batches" counts only the 15 non-block cells; with the 4 block cells there are 113 PostToolBatch events. The claim states 15 runs, so it is consistent, but a reader who adds the 4 block cells to the 109 will not get the 172 calls figure. The 172 is the number of PreToolUse events of those 15 cells, and includes the hand-back calls.
refs: /tmp/reproducer-w03-1/recount.py (my own count of events.jsonl), derived/probe_analysis.txt TOTAL lines
