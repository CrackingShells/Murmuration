## S-w08-reproducer-w08-6-1
The head of w08-c6 lists explorer-w08-h as the possible sixth "with" row and gives a median of about 2,040; the sixth row is reproducer-w08-3 (1,835) and the six-row median is 1,952. The title is right; the body is stale. Also two "with" briefs (explorer-w08-e, -f) were dispatched in the same second as author-w08-2, a "without", so "dispatched later" does not hold for all six.
refs: __instrumenta__/w08_v6_brief_check.py output (dispatch timestamps); __reports__/wave-08/research-pi/handback_len.tsv

## S-w08-reproducer-w08-6-2
The SKILL.md line tells explorers "at most about 1,500 characters", while the six rows with that line all exceeded it (309–949 over). The skill states a limit the measured workers did not meet; whether a limit of 1,000 would give 1,500 is not tested.
refs: __reports__/wave-08/research-pi/handback_len.tsv

## S-w08-reproducer-w08-6-3
waves.md gives a reason for installing the binary before the merge ("so that a reload of the hooks does not find it missing") that no run in the wave shows. I found no artifact for it and my questions to main got no answer before hand-back.
refs: `git diff claude/murmuration-wave-8-928ebd...w08-c6-pi-practice -- skills/research-loop/references/waves.md`; __statera__/wave-08.md lines 217-226

## S-w08-reproducer-w08-6-4
In my first selftest rerun I extracted only `scripts` and `bin` from the commit and got FileNotFoundError (no hooks.json): the selftest reads `../hooks/hooks.json`, so it depends on the tree outside `scripts/`. The manifest hash covers scripts only. Not a defect, but a landing step "run every --selftest on the merged tree" needs the whole tree.
refs: scripts/budget.py line 851
