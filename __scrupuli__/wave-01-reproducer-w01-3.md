## S-w01-reproducer-w01-3-1
Of 163 ended sessions, every cell where all messages carry a `stop_reason` reproduces `cost-state` USD; every cell with an unfinished subagent message misses, and the miss is output tokens only. Nothing in the transcript tells whether the final output count is ever written later; the 70 messages whose records show a growing `output_tokens` suggest the stored value is the last streamed chunk, but no one checked whether the missing output is recoverable from another record type (e.g. `iterations` in `usage`).
refs: __reports__/reflective_run/w01/reproducer-w01-3/cells.py, __reports__/reflective_run/w01/author-w01-3/validate_cells.csv

## S-w01-reproducer-w01-3-2
Sessions whose `cwd` is this run's scratchpad (`/private/tmp/claude-501/...scratchpad...`, 12 sessions, 8 project folders, `cost-state` USD 0.111) are this run's own headless probes yet appear in no scan, because the scan keys on the repository family. The run's own agents create them by writing to a scratchpad; a lab-level total would need a rule for them.
refs: __reports__/reflective_run/w01/reproducer-w01-3/ (inline check in the transcript of this verification), ~/.claude/projects/-private-tmp-claude-501--Users-hacker-Documents-tmp-claude-worktrees-Murmuration-*

## S-w01-reproducer-w01-3-3
The scan counts 30 sessions below the main checkout that are probe sessions of the plugin's own build (USD 1.11 `cost-state`) in the "lab's" TOTAL; the table separates them but the TOTAL does not. A human reading TOTAL gets build-time spend mixed with this run's spend unless `--since` is passed. Which date is a lab's start?
refs: __reports__/reflective_run/w01/author-w01-3/human_main_checkout.txt

## S-w01-reproducer-w01-3-4
The R1 head figure moves with live data (52/54 at 11:30, 105/107 at 11:55, my 99/101): all three give the same two Haiku misses. A MEASURED claim whose headline denominator grows between runs has no fixed number to reproduce; only the exception set is stable. Should the claim carry the exception set, not the ratio?
refs: __reports__/reflective_run/w01/author-w01-3/validate.txt, __reports__/reflective_run/w01/reproducer-w01-3/cells.py

## S-w01-reproducer-w01-3-5
Helper-model (Haiku) calls exist only in `cost-state` (566fa912 Haiku: 29,584 input tokens, no transcript message). If a session never ends cleanly (crash, kill), there is no `cost-state`, and the helper spend is invisible even to the "exact" figure. How many of the 163 session folders lack a `cost-state` and have no live process? Not measured.
refs: __reports__/reflective_run/w01/reproducer-w01-3/cells.py
