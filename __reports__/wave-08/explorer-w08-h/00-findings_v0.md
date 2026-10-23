---
type: findings
wave: wave-08
author: explorer-w08-h
date: 2026-10-24
version: v0
decision-required: none
---

# The lab's cost map after wave 8 (so far): lever ladder, PI against workers, cache-lifetime choice (findings v0)

Stayed inside the brief. The map is `__reports__/wave-08/explorer-w08-h/lab_cost_map.html`, built from wave 7's file (`__reports__/wave-07/research-pi/lab_cost_map.html`) by `__instrumenta__/w08h_build_cost_map.py` (fragments in `__instrumenta__/w08h_frag/`); sections 1, 2, 4, 5 and 6 keep their look and are updated, section 3 (spend) and 3b (cache) are rebuilt as B and C, and A is new. One departure: wave 8 was still moving while I wrote (w08-c3, w08-c6, w08-c8 got verdicts and landed; explorers i and j were dispatched), so figures are those of 01:25 to 01:45 JST on 2026-10-24, and I read only the reports named in the brief, not explorers i and j.

## Result

MEASURED/ESTIMATE as labelled in the map: the ladder holds 16 levers. By central value, as a share of the spend each acts on: the PI's 1-hour cache (already on, 30-72% of PI spend, ESTIMATE) and PI compaction near 250k tokens (22-31%, ESTIMATE; the window key is yours to write) are an order of magnitude above everything else; the next group is 2-10% (skills listing, hand-backs, documents by section, rtk, orientation reads); everything the workers' side offers is under 2.5% of worker USD (script cap 0.1-1.4%, batching 0.2-2.1%, effort inside noise). The PI is USD 148.16 of the lab's USD 405.34 (37%). A worker's own earlier turns are 41.6% of its context USD and no lever on them has been tried. [source: `__reports__/wave-08/explorer-w08-h/lab_cost_map.html`, section A and the table at its end]

## Table

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| What the map shows, A | 16 levers ranked, three unit views (share of the side's spend, share of the narrow pool, USD), status per lever, a second lane of ms saved per hook start | ESTIMATE (ceilings) except effort and the hook times, MEASURED | map section A; per-lever rows in the table view |
| What the map shows, B | spend per wave (waves 1-3 as one row, 4-8), PI to close and PI after close hatched, wave 8 so far PI 6.10 + workers 27.92 + headless 19.91 = at least 53.93; PI by price part and 21 sources; workers' context by 19 sources | MEASURED (spend), ESTIMATE (sources) | `wave8_spend_by_agent.tsv`; explorer-w08-d, -a |
| What the map shows, C | net per life of 1 hour over 5 minutes by type with 10th/median/90th, and a 7-rule by 4-type grid | ESTIMATE | explorer-w08-c tables 3, 4 |
| Wave 8 spend by agent | PI 6.10 (75 requests); authors 13.02; explorers 13.57 (this page's helper 0.65 in it); verifiers 1.33; list price, lower bound | MEASURED | `__reports__/wave-08/explorer-w08-h/wave8_spend_by_agent.tsv`, `python3 -I __instrumenta__/w08h_wave_spend.py <ad75be4f>.jsonl` |
| Numbers I computed, all arithmetic on reported ones | PI after-close spend 6.18/7.02/11.28 (session total minus wave figure); waves 1-3 rest 98.91 (162.14 − 63.23); PI share 37%; author-cache central point 14 × −0.02; narrow pools 10.44, 32.06; skills low end 2.90; PI cache lever 43.6 and 104.0 | ESTIMATE | map table rows marked "mine" |

## Worst-fitting case

The story is "the PI's cache and compaction dominate; the worker side is near its floor". It fits worst in three places.

1. The two top bars are the least comparable: the 1-hour cache for the PI is an avoided cost of a setting already on (USD 43.6 over three sessions by explorer-w08-c, 104.0 over six by explorer-w08-d, whose counterfactual counts 61 hits against about 31 events in c's model); compaction has one real compaction behind it and, until w08-c3's verdict, no outcome test. They are on one chart with levers whose ceilings are cleaner, which can read as more certainty than they have.
2. The worker-side rows share a base that does not fit the PI's: worker context USD 83.69 (waves 4-7, input side only) against worker recorded cost 109.92 (waves 4-8, output at stored count) against the PI's 144.47 (all six sessions). Share of the side's spend is therefore not the same fraction in any two rows; the narrow-pool view reverses the ranking (documents 48%, scripts 15%).
3. The authors' 1-hour cache: wave 7's map said "defensible for authors, a bet near break-even" (net −2.15 to +3.31 over waves 4-6); wave 8 on timed pauses says −0.02 ± 0.39 per life, 5 rules of 7 for 5 minutes. The map keeps both (the old figure under a fold) and does not decide.

## Not covered

- Waves 1-3 are one row with the rest of their worktree unsplit (workers and headless are not separated in any report I was told to read).
- Per-wave PI spend for waves 5-7 is the close-time figure of wave 7's map plus a difference to explorer-w08-d's session totals; I did not re-cut the PI's requests at the wave boundaries.
- Time levers are in ms, with no USD; the PI tool denylist and colgrep have no USD in the reports and are named below the ladder only.
- Explorers i and j, and w08-c6 and w08-c8 beyond their heads and verdict lines, were not read for numbers; w08-c6 appears as a landed card and a ladder status.
- Wave 8's final spend; the page says "so far" and a lower bound.
- I checked the page by headless Chrome screenshots (dark, light, the USD and zoom view) and `node --check` on its script; I did not click through every tooltip.

## Steering questions

- [now] The ladder puts a landed setting (the PI's 1-hour cache) and an estimated one (compaction) at the top. Do you want landed levers drawn apart from levers still to decide, so that the top of the chart is only decisions open?
- [later] Should `lab_status.py --spend` report spend per wave (a wave opening and close time in the wave note), so that the cost map's per-wave rows come from one script and the after-close PI spend stops being a hand difference?

## Pointers

- `__reports__/wave-08/explorer-w08-h/lab_cost_map.html` (self-contained; no network fetches; the three URLs in it are text in the source table). Rebuild: `python3 -I __instrumenta__/w08h_build_cost_map.py` (reads `__reports__/wave-07/research-pi/lab_cost_map.html` and `__instrumenta__/w08h_frag/*`).
- `__reports__/wave-08/explorer-w08-h/wave8_spend_by_agent.tsv`: `python3 -I __instrumenta__/w08h_wave_spend.py ~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-8-928ebd/ad75be4f-14dd-4dd8-90c7-fb175ed36239.jsonl`.
- Scripts cited as `__instrumenta__/w08h_wave_spend.py@<commit>`, `__instrumenta__/w08h_build_cost_map.py@<commit>` (commit of this report).
- Labels read from `python3 scripts/lab_status.py` at about 01:40 JST: w08-c3, w08-c4, w08-c6 MEASURED (SUPPORTED); w08-c2 unverified; w08-c8 CONJECTURE; w07-c1 and w07-c8 below MEASURED: restate; w07-c7 escalated.
- Spend: `python3 scripts/lab_status.py --spend` (USD 405.34 at least), `--project /private/tmp/murmuration-w08 --spend` (19.91 at least); waves 4-7 headless from `--project /private/tmp/murmuration-w0N --spend` (26.52, 18.20, 7.54, 2.48; wave 5 reads 18.20 against the map's 18.18).

## Refresh at the close of wave 8 (03:57 JST, 24 October; same file, updated in place)

- Spend (both lower bounds while the session is open): `lab_status.py --spend` USD 442.53 at least (PI 159.23, agent rows 379.47); wave 8 in this checkout PI 16.95 + 22 workers 53.28 (authors 25.93, explorers 20.48, verifiers 6.87) + headless 21.47 (`--project /private/tmp/murmuration-w08`, all ended) = at least 91.71 [source: `wave8_spend_by_agent.tsv`, MEASURED]. At 01:25 the same sum was 53.93.
- Labels from `lab_status.py`: w08-c3, c4, c6, c11, c12, c13 MEASURED (SUPPORTED); c8 CONJECTURE (SUPPORTED); c2 unverified, not landed; c1, c5, c7, c9, c10 superseded. The compaction row says the setting is the user's.
- New: a "safety and checking" lane in A (guard holes 1,515 of 2,259 flag/wrapper cases and 359 of 639 G3 write cases to 0, w08-c13; false denials 113 of 623 unchanged, explorer-w08-j; verification about 8% of spend, first verdict of 76 claims 38/25/13, explorer-w08-i), four landed cards (c13, c12, c11, c8) and one superseded card in section 4, and five source rows.
- The second implementation's size: w08-c12 gives none; the line counts (1,134 + 382 + 574) are from w08-c1's head, and c12 means a budget change is made in both implementations.
- Not refreshed: the PI-by-source and worker-by-source charts (explorer-w08-d's cut 00:17, explorer-w08-a's waves 4-7), the ladder's USD values (reports unchanged); the ladder's authors-cache and compaction rows keep their ESTIMATE labels.
