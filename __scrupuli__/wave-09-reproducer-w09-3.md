## S-w09-reproducer-w09-3-1
The head of w09-c6 says "one 626-character criterion" for both judges, but only safeguard got the 626-character text; Granite got a 352-character wording without the allow clause. Cross-judge comparison therefore mixes judge and wording.
refs: __instrumenta__/w09c_judge.py (SHORT, GRANITE_SHORT), __instrumenta__/w09c6v_rescore.py

## S-w09-reproducer-w09-3-2
Granite's refusal-side 74.6% and its natural-allow block share 59.8% are close; "agrees on refusals" does not say the judge separates the two sides. A discrimination figure (block rate on refusals vs on allows, or an AUC from a score) is not in the rows, since Granite's yes/no is the only output stored.
refs: __reports__/wave-09/explorer-w09-c/results/granite_short.jsonl

## S-w09-reproducer-w09-3-3
"Natural" (user's own sessions) in w09-c6 means non-arena; 41% of its weight is the murmuration-lab project and 77% subagent calls, so it is not the user's hand-driven traffic. Cuts in `__instrumenta__/w09c6v_cuts.py` output: lab 68.9%, other natural 53.4%, natural main-thread 46.8% blocked.
refs: /private/tmp/murmuration-w09/explorer-w09-c/allowed_sample.jsonl (project_group, sub), __instrumenta__/w09c6v_cuts.py

## S-w09-reproducer-w09-3-4
The allow population is 30,663 classifier_allow rows dated 2026-10-08 to 2026-10-25 UTC (30,508 up to 10-24); the head states 10-24. Possibly a local-time vs UTC cut, not checked.
refs: /private/tmp/murmuration-w09/explorer-w09-c/classified.jsonl (ts), allowed_sample.jsonl

## S-w09-reproducer-w09-3-5
safeguard is not exactly repeatable at temperature 0 (author's spot check: one refusal flipped), yet its refusal-side 8 of 67 is a single run. The size of the run-to-run variation on 67 refusals is unknown; I did not re-run safeguard.
refs: __reports__/wave-09/author-w09-3/spotcheck.md
