## S-w08-explorer-w08-h-1
The PI's per-wave spend in wave 7's map (10.51, 11.90, 16.06, 15.86) is the PI to the wave's close, but explorer-w08-d's session totals are 10.50, 18.08, 23.08, 27.14: the PI sessions run on after each close by USD 6.18, 7.02 and 11.28 (waves 5-7). Cutting d's request tables at the close times gives 11.30 (wave 5, map 11.90), 15.19 (wave 6, map 16.06) and 15.86 (wave 7, exact). So the map's wave 5 and 6 figures are not reproduced by the close times I used, and "a wave's cost" depends on whether the PI's close-out work belongs to it.
refs: `__reports__/wave-08/explorer-w08-d/s3_w5_requests.tsv`, `s4_w6_requests.tsv`, `s5_w7_requests.tsv`; `__reports__/wave-07/research-pi/lab_cost_map.html` (spend array); close commits 4a6a533..347a7c3.

## S-w08-explorer-w08-h-2
The PI's 1-hour cache is worth USD 43.6 over three sessions in explorer-w08-c (net, waves 5-7) and USD 104.0 over six in explorer-w08-d (119.07 counterfactual re-writes minus a 15.08 premium). The first counts about 31 events (7.0 per 100 requests); the second 61 hits. I did not find which of the two counts what, only that the denominators differ (session 1 is huge in d, absent in c).
refs: `__reports__/wave-08/explorer-w08-c/00-findings_v0.md` table 3 and (a); `__reports__/wave-08/explorer-w08-d/tables.md` section 4.

## S-w08-explorer-w08-h-3
Wave 7's map had authors' R/W at 0.30-0.51 and a net of −2.15 to +3.31; explorer-w08-c finds a token share of 0.372 and a net of −0.02 per life. Both are on the page. The cause named by c (untimed wave-4 pauses and a misaligned tool_s) is c's own reading of w07's script, not a verdict; w07-c7 stays escalated, so the page has no label it may put on "authors should keep 1 hour".
refs: `__reports__/wave-08/explorer-w08-c/00-findings_v0.md` (puzzle 1); `__scrupuli__/wave-08-explorer-w08-c.md`; `__pondus__/w07-c7.md`.

## S-w08-explorer-w08-h-4
The report counts six decision rules, authors split 4 to 2; its table 4 has seven rows, of which authors take 5 minutes in five and 1 hour in two. The figure shows seven. The counts agree only if two rows (expected value and probability of gain) are one rule.
refs: `__reports__/wave-08/explorer-w08-c/00-findings_v0.md` Result paragraph "Rules choose differently" and table 4.

## S-w08-explorer-w08-h-5
Thinking share of worker context USD: 22.5% in explorer-w08-a (inferred from context growth), 18.9% in explorer-w08-f (signature fit applied to a's 2,905 turns; its own fit range is far from the lab's signatures). The map shows 22.5% as a and 18.9% as f's re-fit; the true value is somewhere in or beyond that, and the "effort" ceiling bar uses f's 15.8.
refs: `__reports__/wave-08/explorer-w08-f/apply_sigfit_to_w08a.txt`, `__reports__/wave-08/explorer-w08-a/tables.md`.

## S-w08-explorer-w08-h-6
The ladder's bases do not match: worker context USD 83.69 (input side only, waves 4-7), worker recorded cost 109.92 (waves 4-8, output at its stored, understated count), PI USD 144.47 (all six sessions). Rows from a and g are therefore not on one denominator, and the narrow-pool view reverses their order. I could not find one base the reports would all support.
refs: `__reports__/wave-08/explorer-w08-a/00-findings_v0.md` Not covered; `__reports__/wave-08/explorer-w08-g/00-findings_v0.md` table; `__reports__/wave-08/explorer-w08-d/00-findings_v0.md`.

## S-w08-explorer-w08-h-7
The PI's share of the lab: the wave note said 46% of priced spend; `lab_status.py --spend` now gives 148.16 of 405.34 total (37%) or of the 342.29 priced to agent rows (43%). Which denominator the wave note meant, and whether the headless and cost-state-only spend belong in it, is not stated.
refs: `__statera__/wave-08.md` ("46% of priced spend"); `python3 scripts/lab_status.py --spend`.

## S-w08-explorer-w08-h-8
Wave 8's headless spend is USD 19.91 so far (251 sessions), 8 times wave 7's whole 2.48 and 3 times wave 6's 7.54, mostly explorers' probes (haiku main threads 3.36 + 1.84, Sonnet effort arms about 1.4). No report says whether that is cost the lab wants to count against the levers it measured (explorer-w08-f alone 3.44, -g 1.45).
refs: `python3 scripts/lab_status.py --project /private/tmp/murmuration-w08 --spend`; `__reports__/wave-08/explorer-w08-f/00-findings_v0.md` Pointers; explorer-w08-g Method.

## S-w08-explorer-w08-h-9
The Rust budget row of wave 8's bar: 41 ms (wave 7) minus 9.0 ms in the platform gives 32; but w08-c4's own control row drifted −6.2 ms between arms, and the 9.0 ms is a pooled median with 10 of 12 pairs. The bar is arithmetic on two numbers whose own noise is of the same order as the difference; I drew it and labelled it ESTIMATE rather than leave wave 8 out of section 2.
refs: `__pondus__/w08-c4.md` title and scope; `__scrupuli__/wave-08-reproducer-w08-1.md` puzzle 1.
