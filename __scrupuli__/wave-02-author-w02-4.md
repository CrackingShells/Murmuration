## symbols
- `new`, `ctl`, `old` (in w02-c4): the three plugin variants of the test: this worktree; the same with `Skill` back in the four workers' `tools:`; git HEAD before the change.

## S-w02-author-w02-4-1
All six lean explorers read the report template before writing (Read or `cat` of `report_findings.md`), though the preloaded skill only names its path; the two old-plugin runs, whose brief also asked for a findings report, wrote none at the convention path and put the findings into the hand-back text. So the template and the skill section, not the brief alone, decide whether the report exists. What I could not show is whether this survives a long brief with many other deliverables: sonnet obeyed the brief at n=6 here, and explorer-w02-b saw haiku decline on the platform's soft rule.
refs: __reports__/reflective_run/w02/author-w02-4/result.jsonl (`read_template`, `report_at_convention_path`), __reports__/reflective_run/w02/author-w02-4/example_new_a_00-findings_v0.md

## S-w02-author-w02-4-2
The hand-back should be short, but it ran 131 to 222 words in the lean runs, repeating most of the report's Result section. The explorer file says "a short hand-back message that points to it" and nothing about length. If the PI reads these in a batch, a cap in the explorer file (for example "the path, one sentence, and what is not covered") would cost a line; whether it should be added is the PI's call and I did not change it.
refs: result.jsonl; hand-back texts in the subagent transcripts of new_a..new_f (scratch folder, not copied)

## S-w02-author-w02-4-3
Four of six lean runs wrote the report with a shell heredoc even when the brief asked for the Write tool (new_d), so the platform's Write refusal is not what decides most report writes in practice; only a brief that forbids heredocs (new_e, new_f) forced Write, and Write accepted `00-findings_v0.md`. A hook or guard on the Write tool would therefore see only part of the report writes. Whether the report-name refusal also covers `cat > FINDINGS.md` through Bash is not tested here.
refs: result.jsonl (`write_tool_paths` for new_d, new_e, new_f); brief_d.txt, brief_e.txt

## S-w02-author-w02-4-4
In headless `-p` the main session's Agent tool took no `name` parameter (haiku said so for new_a), so the brief's "Your name is ..." is the only place a worker learns its name, and the transcripts carry no agent name. For the budget hook (author-w02-3) that matters: if it keys on `Budget: USD` in the prompt and on the agent id, a headless dispatch has no name to log. Outside the Desktop app only.
refs: __reports__/reflective_run/w02/author-w02-4/ (run.sh dispatch prompt); e_new_a.json `result` text in the scratch folder

## S-w02-author-w02-4-5
With the worktree's hooks loaded, 2 of 5 lean explorer runs skipped the report template and wrote their own headings and no front matter (new_a, new_d), against 0 of 7 without hooks. The only added `SubagentStart` context in those runs came from the user's own global hooks, which are in every run, and the plugin's budget hook injected nothing visible. Chance is possible at this n. If the new hooks (or their `PostToolUse` handling) change how the worker reads its skill, the shape guarantee of the report is lost and I cannot yet say why.
refs: __reports__/reflective_run/w02/author-w02-4/result_with_hooks.jsonl (`heads`, `read_template`); scratch folder author-w02-4-hooks

## S-w02-author-w02-4-6
The PI's message gave the hook's figure for the B3 author as "about 0.24 of B (about USD 0.20)". The `end` line says used 0.19777 USD, `frac` 0.4944 (USD) and `t_frac` 0.6017 (time) of B = 0.40. The 0.20 USD matches; 0.24 does not match either fraction, and I do not know which number it was meant to be. The explorer's table gives 0.494 and 0.602, as I do.
refs: __reports__/reflective_run/w02/author-w02-4/b3_selfreport_out.md; B3 `lab/__statera__/harness.jsonl` (author-w01-1 `end`)

## S-w02-author-w02-4-7
The harness `used` for the seven workers sums to 0.900 USD against 0.8655 exact, 4% high, while the explorer's table says the output estimate is 108% of exact in tokens. So the hook's USD figure is a good estimate here (n = 1 arm), and the self-report is not. Does the self-report error come from the worker adding the PI's or other workers' spend, or from guessing from token counts? The hand-back does not say.
refs: b3_selfreport_out.md; B3 handbacks/wave-01-author-w01-1.md line 29
