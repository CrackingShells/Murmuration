## S-w04-reproducer-w04-8-1
The rule's "template shape" criterion reads as a test of whether the explorer follows an instruction, but only 1 of the 6 B' and A runs after a deny ever opened the template: e1b-b2 has a Read of plugin_Bp/skills/research-loop/templates/report_findings.md; e1b-b1, e1b-b3 and e1b-a1..a3 did not (the deny text in scripts/handback.py line 202 names the template, yet no A run opened it). The rule therefore measures "found and opened a file whose path the line does not give", not "follows the template". A line with a path, or the headings inline, was not run.
refs: /private/tmp/murmuration-w04/author-w04-2/runs/e1b-*/ transcripts at ~/.claude/projects/*-runs-e1b-*-lab/*/subagents/agent-*.jsonl; __instrumenta__/w04c8_rederive_e1b.py

## S-w04-reproducer-w04-8-2
The head's items-correct for e1b-a2 is 75; my grader gives 76 of 76. The head's parse_items takes the first line naming an fNNN with four digits, and a prose line "Moormere f005/f019 ..." in A2's report (with the population 20347) is taken as the row of f005. A grader artifact of one item, no effect on the rule.
refs: __instrumenta__/budget_arms_analyze.py parse_items; runs/e1b-a2/lab/__reports__/wave-04/explorer-w04-e1ba2/00-findings_v0.md line 4

## S-w04-reproducer-w04-8-3
The brief says "Write it in your hand-back", but in the final hand-backs the list is present in 0 of 3 A and 1 of 3 B' runs (the report carries it). The deny sends the list to a report file in A; the line sends it there in B'. The claim counts report rows as delivered. Which place the PI actually reads (hand-back vs report) was not measured. In e1b-b2 the list is written twice (list.txt and the report).
refs: runs/e1b-*/lab/__statera__/handbacks/*.md; runs/e1b-b2/lab/__reports__/wave-04/explorer-w04-e1bb2/

## S-w04-reproducer-w04-8-4
A runs get the deny at 0.88 to 1.02 B and then overshoot by 0.12 to 0.23 B; the deny hook's cost is the report-writing after the first attempt. B' writes the report before the first attempt and lands at 0.93 to 1.00. Per-run totals are USD 0.26 to 0.40 and similar by arm (A 1.051, B' 0.970 total), so the overshoot is about 0.08 USD on a 0.30 budget; n = 3 cannot separate that from run noise (B'2 0.345 against A2 0.314).
refs: __reports__/reflective_run/w04/author-w04-2/derived2/cost_per_run_e1b_e2b.tsv

## S-w04-reproducer-w04-8-5
The restated E1 omits the uncapped exploratory ux-a1..2 (1 deny each); reproducer-w04-2 listed it. Also the run cost cap: head says 12 runs cost 4.5167 against a cap of 4.5 (exceeded by 0.017); the cap is the PI's, and the head discloses it.
refs: __pondus__/w04-c2.md (reproducer-w04-2 section, m1 line); __reports__/reflective_run/w04/author-w04-2/derived2/cost_per_run_e1b_e2b.tsv
