---
type: findings
wave: wave-05
author: explorer-w05-a
date: 2026-10-21
version: v0
decision-required: none
---

# Where wave 4's wall-clock time went: findings (v0)

Stayed inside the brief. One scope note: the harness log's `end` events, the transcripts and the headless `meta.json` files were all read; the headless meta files are in the Trash folder `~/.Trash/murmuration-w04-raw-runs-2026-10-20/` (the PI trashed the run folders at 10:54, wave 4), read-only, only `meta.json` (`wall_s`, `turns`, mtime).

## Result

Wave 4 (09:27:19 to 10:55:24 JST, 88.1 min) was a sequence of one PI preface (7.5 min), a longest author-to-verifier chain (78.8 min, all of it one author, author-w04-2, plus the verifiers that followed it), and a close (1.8 min). MEASURED: the PI's own turns were 22% of the wall, its tool calls 2.7%, and 75% was the PI waiting for a hand-back; the PI answered every hand-back in a median of 4 s and never held up a worker by more than 59 s, so on the critical path the PI owns only 7.5 + 1.8 + about 1.7 = about 11 min (12.5%); the other 77 min are an author running headless `claude -p` experiments in 10 serial stages (67.5% of that chain was cells in flight). ESTIMATE: the three item chains were balanced (78.8, 73.4, 66.6 min), so shortening only the critical one saves at most 5.4 min; the single largest cheap win is 4.1 min of PI probing that sat before the first dispatch.

## Table

Time base: JST, 2026-10-20. "Model" = previous record to assistant record; "tool" = tool_use to tool_result; "idle" = no turn running. Figure: `wave4_gantt.png`.

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Wave length | 09:27:19 to 10:55:24 = 5285 s (88.1 min); first dispatch 09:34:50; last verdict 10:53:38 | MEASURED | `intervals/PI.tsv`, `chain_ends.txt` |
| PI thread split | model 1176 s (22.3%), tool 145 s (2.7%), idle waiting 3960 s (75.0%); 114 model requests, mean about 10 s each | MEASURED | `intervals/PI.tsv`, `pi_turns_after_idle.tsv` |
| PI response to a hand-back | first assistant record 2 to 20 s after (median 4 s); first dispatch needing a decision 4 to 61 s after (E3b/E1b pre-registration writes account for the 42 and 45 s) | MEASURED | `pi_response_lag.tsv` |
| PI-owned time on the critical path | preface 7.5 min (09:27:19 to 09:34:50), handoffs about 1.7 min (57, 18, 8, 16 s on author-w04-2's chain plus gaps), close 1.8 min | MEASURED / sum is ESTIMATE | `pi_events.txt`, `chain_ends.txt` |
| Preface content | reading 1.2 min; item-1 probing (hook probe, `ps`, Desktop log, probe subagent) 4.1 min (09:28:30 to 09:32:34); pre-registration and wave note 1.4 min; four briefs 50 s | MEASURED | `pi_events.txt` lines 5 to 67 |
| Chain ends (from first dispatch 09:34:50) | C12 (items 8 and 10: author-w04-2 then reproducer-w04-2/3/8/9) 10:53:38 = 78.8 min; C5 (item 9: author-w04-4, reproducer-w04-5) 10:48:13 = 73.4; C11 (item 11: author-w04-3, reproducers 4/7/10) 10:41:28 = 66.6; C1 17.6; C6 7.2 | MEASURED | `chain_ends.txt` |
| Worker time (15 runs) | model 6337 s, tool under 45 s 1837 s, tool 45 s or longer 8724 s, not running between resumes 3153 s; active total 16898 s = 3.2 times the wall clock | MEASURED | `lane_shares.tsv` |
| Consistency check | per-run `model + tool` equals the harness `active_s` (author-w04-2: 1057 + 173 + 3041 = 4271 against 4272.6) | CHECKED | `lane_shares.tsv`, `__statera__/harness.jsonl` (wave-4 worktree) |
| Calls of 45 s or longer | authors 32 calls, 6713 s (13 wait loops 4021 s; 19 other, 2692 s); reproducers 21 calls, 2009 s (13 wait loops 1223 s; 8 other, 786 s); PI none | MEASURED (regex classing of the command text) | `long_tool_calls.tsv` |
| author-w04-2 chain | 50 headless cells in 10 serial stages (stage lengths in s: 323, 340, 409, 339, 337, 559, 84, 339, 199, 265); union 3194 s = 53.2 of the chain's 78.8 min; cell wall median 296 s (min 80, max 559); at most 9 cells at once | MEASURED | `headless_cells.tsv` |
| Stage cause: confound rework | 20 first-run cells carried `--max-budget-usd 1.5`; the platform then shows the worker a budget attachment in every request (the author's own finding); the 9 pre-registered cells were repeated uncapped (stage `u` 337 s) and the exploratory X cells again (stage `ux` 559 s): 896 s = 14.9 min of the chain is repeat of earlier cells | MEASURED (stage times); cause is the author's account in `__pondus__/w04-c2.md` line 15 (CITED to that file) | `headless_cells.tsv`, w04-c2 head (wave-4 worktree) |
| Stage cause: batch width | stage widths 2, 6, 9, 3, 9, 4, 2, 9, 3, 3; no stage above 9; 12-cell E1b+E2b ran as 9 + 3 (second stage 199 s plus 38 s gap) | MEASURED; "9 is a chosen cap" is CONJECTURE | `headless_cells.tsv` |
| Message to a busy agent | question to author-w04-2 at 10:28:02 and 10:28:32, answered 10:33:23 and 10:33:28 (321 s, 296 s), author-w04-3 asked 10:13:15 answered 10:16:42 (207 s); questions to an idle (finished) author: 15 to 75 s (9 cases) | MEASURED | SendMessage listing in "Pointers" |
| Verifier polling after the answer | reproducer-w04-3 sent its question 10:28:32, polled `timeout N tail -f /dev/null` with N = 50, 90, 120, 150; the answer was queued 10:33:31 and read at its next tool round 10:35:59 (151 s after); reproducer-w04-2 read at 10:35:01 (98 s after 10:33:23) | MEASURED | `__instrumenta__/wave_worker_events.py` on both agents |
| Cache after idle | PI turns after idle gaps of 450 s (10:00:26 to 10:07:56) and 16 min (09:52:29 to 10:08:09) re-created 3585 tokens against 221392 read | CHECKED (one run) | `pi_turns_after_idle.tsv` rows 10:08:09 |
| PI context | 75k tokens at 09:27 to 361k at 10:55 (cache read plus create, per request) | MEASURED | `pi_turns_after_idle.tsv` |
| Brief streaming | four Agent calls in one message: briefs took 09:34:00 to 09:34:50; all four workers started within 1.3 s of 09:34:50, so author-w04-1 (written at 09:34:13) waited 37 s | MEASURED | `pi_events.txt`, `__statera__/harness.jsonl` |
| Hook time in the PI thread | no per-hook durations recorded on the 25 Stop summaries; SessionStart hooks 818 ms total over 2 calls | MEASURED | PI transcript, count only |

### ESTIMATE: what would have shortened the wave

Model: wave = pre + max over chains(chain length) + close, with pre = 7.5, chains 78.8 / 73.4 / 66.6, close = 1.8 (min). Base 7.5 + 78.8 + 1.8 = 88.1. Each row changes one input; the "saves" column is the change in wave length, not in the chain. Labelled ESTIMATE: these are formula evaluations on the measured segments, not runs.

| Change | Formula | Wave (min) | Saves (min) | Condition not tested |
|:--|:--|:--|:--|:--|
| S1: dispatch independent authors before item-1 probing | pre − 4.1 | 84.0 | 4.1 (4.6%) | authors of items 8, 9, 10, 11 do not need item 1's result; the pre-registration was needed (user's rule), item 1's probe was not |
| S2: no confound rework in the critical chain (stages u and ux) | C12 − 14.9 = 63.9, so max is C5 = 73.4 | 82.7 | 5.4 (6.1%) | would need the budget-attachment confound seen before the 20 first-run cells (CONJECTURE: those 20 are the 2 pilots, 6 e1, 3 e2-c and 9 x cells by count, so the pilots carried the flag; I did not read the launch commands) |
| S3: S2 plus no 9-cell cap (E1b and E2b in one stage; X-c stage merged) | C12 − 14.9 − 4.0 − 5.9 = 54.0; max is still C5 | 82.7 | 5.4 | wide batches fail to log in sometimes: 4 of 12 and 1 of 9 parallel launches returned "Not logged in" in author-w04-3's runs (S-w04-author-w04-3-7) |
| S4: all three chains cut to the shortest item chain (C11) | pre + 66.6 + close | 75.9 | 12.2 (13.9%) | requires work on C12 and C5 at once |
| S1 + S4 | 3.4 + 66.6 + 1.8 | 71.8 | 16.3 (18.5%) | as above |
| Verifier does not poll after its question (answer read within 15 s) | affects reproducer-w04-2/3 only; they ended 10:35:34 and 10:36:29; author-w04-2 was running E2b-a cells until 10:36:17 | 88.1 | about 0 | off the critical path in wave 4; the loss is the verifiers' own 98 to 151 s each |
| Brief streaming (start the first worker when its Agent call is written) | 37 s once, 15 s and 7 s on later batches | 87.3 | about 0.8 | platform runs parallel tool calls after the message ends; not controllable by the lab |

## Worst-fitting case

The story that fits best is C12: one author, an experiment of serial headless stages, 53 of 79 min in cells in flight, a 15-min repeat caused by a confound, and a PI who answered in seconds. It fits the title "the lab waits for runs, not for the PI".

The case that fits worst is C5 (item 9, author-w04-4 and reproducer-w04-5). It has one headless cell of 91 s, no repeat stage, a 54.2-min author run (harness `t_frac` 0.90 of its 60-min limit) whose time was model 1476 s, tool 45 s or longer 1434 s (its own timing loops), idle 1531 s after hand-back; then 18.7 min of verification that was itself a 420-pair re-measurement. It finished 5.4 min before C12, so a lab that removed all of C12's headless waiting would still run 73.4 min on C5, where the cost is the author's (and the verifier's) own measurement design, not run-waiting. The headless-wait story explains the longest chain, not the second.

Second worst fit: the 98 to 151 s a verifier lost polling after its answer was in the queue is a real defect of the exchange (a queued message waits for the next tool round, and a polling call is a tool round of 50 to 150 s), but it was off the critical path in wave 4, so it does not lengthen the wave in this record.

For prior work: none cited.

## Not covered

- Model time inside worker runs is only "previous record to assistant record"; I did not split API latency, streaming and thinking. A cheaper model per request (`explorer` and `reproducer` model choice) was not tested.
- Whether 9 is an API or login ceiling or the author's choice: no wave-4 evidence beyond S-w04-author-w04-3-7; nothing here ran headless cells.
- C5's author time (model 1476 s of 3250 s, 122 requests) was not traced to its causes; nor was C11's (66.6 min, 15 long calls).
- What a worker costs in tokens: no spend figures quoted, per the brief; request counts are in `__statera__/harness.jsonl`.
- The wave-4 transcripts record no user turn after 09:27:20 (checked in `pi_events.txt`), so user waiting is zero here; later waves may differ.
- Cross-checking `lab_status.py`'s parser: I wrote new helpers rather than extend it, because it reports spend and labels, not intervals.

## Steering questions

- [now] Should wave 5's dispatch order be "write pre-registration, dispatch independent authors, then do item-1-style PI probes"? S1 is 4.1 min of 88 and costs nothing but order.
- [now] Do you want one probe that raises the headless batch width past 9 (10 to 30 parallel `claude -p` cells with the same credentials) to see whether "Not logged in" returns? S3's saving needs it.
- [later] Should a verifier that has sent its question end its run and be resumed by the author's reply (the PI already resumes finished agents by `SendMessage`) instead of polling? CONJECTURE: removes 98 to 151 s of polling per exchange; untested.

## Pointers

All under `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/lab-system-optimization-1aa673/`. Helpers cited as `__instrumenta__/<file>@4b7cd79`. Raw inputs (read only): PI transcript `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-wave-4-3417be/c533f1c6-c56e-4c8d-b6ff-e90c3ddea2f4.jsonl` (called `$S.jsonl`), its folder `$S/subagents/`, `murmuration-wave-4-3417be/__statera__/harness.jsonl`, `~/.Trash/murmuration-w04-raw-runs-2026-10-20/`. Python run as `python3 -I`; no seeds; quick command is the same (the full set runs in about 20 s).

| Artifact | Command |
|:--|:--|
| `__reports__/wave-05/explorer-w05-a/wave4_gantt.png`, `lane_shares.tsv` | `python3 -I __instrumenta__/wave_gantt.py __reports__/wave-05/explorer-w05-a/intervals __reports__/wave-05/explorer-w05-a/headless_cells.tsv wave4_gantt.png > lane_shares.tsv` (`__instrumenta__/wave_gantt.py@4b7cd79`) |
| `intervals/PI.tsv`, `intervals/<agent>.tsv` | `python3 -I __instrumenta__/wave_timeline_pi.py <transcript.jsonl> <out.tsv>` for the PI file and each `$S/subagents/agent-*.jsonl` (`__instrumenta__/wave_timeline_pi.py@4b7cd79`) |
| `headless_cells.tsv` | `python3 -I __instrumenta__/wave_headless_cells.py ~/.Trash/murmuration-w04-raw-runs-2026-10-20 headless_cells.tsv` (`__instrumenta__/wave_headless_cells.py@4b7cd79`) |
| `long_tool_calls.tsv` | `python3 -I __instrumenta__/wave_long_tool_calls.py $S.jsonl $S/subagents 45 long_tool_calls.tsv` (`__instrumenta__/wave_long_tool_calls.py@4b7cd79`) |
| `chain_ends.txt` | `python3 -I __instrumenta__/wave_chain_ends.py <harness.jsonl> 092719 105524 C12=reproducer-w04-8 C5=reproducer-w04-5 C11=reproducer-w04-10,author-w04-3 C1=reproducer-w04-1 C6=reproducer-w04-6` (`__instrumenta__/wave_chain_ends.py@4b7cd79`) |
| `pi_response_lag.tsv` | `python3 -I __instrumenta__/wave_pi_response_lag.py $S.jsonl` (`__instrumenta__/wave_pi_response_lag.py@4b7cd79`) |
| `pi_events.txt`, `pi_turns_after_idle.tsv` | `python3 -I __instrumenta__/wave_pi_event_list.py $S.jsonl > pi_events.txt` and `... --usage > pi_turns_after_idle.tsv` (`__instrumenta__/wave_pi_event_list.py@9c478fb`) |
| Worker event lists (reproducer-w04-2/3 polling; author-w04-2 stages) | `python3 -I __instrumenta__/wave_worker_events.py $S/subagents/agent-<id>.jsonl` (`__instrumenta__/wave_worker_events.py@4b7cd79`); agent ids in `$S/subagents/*.meta.json` |
| SendMessage latencies | inline `python3 -I` over all transcripts listing each `SendMessage` tool_use and its result with JST times; question to answer: reproducer-w04-1 to author-w04-1 09:50:38 to 09:51:25 (47 s), reproducer-w04-6 09:40:53 to 09:41:29 (36), reproducer-w04-4 to author-w04-3 10:13:15 to 10:16:42 (207), reproducer-w04-2 10:28:02 to 10:33:23 (321), reproducer-w04-3 10:28:32 to 10:33:28 (296), reproducer-w04-7 10:31:54 to 10:32:09 (15), reproducer-w04-10 10:39:55 to 10:40:27 (32), reproducer-w04-9 10:40:43 to 10:41:58 (75), reproducer-w04-8 10:41:03 to 10:42:03 (60) and 10:51:02 to 10:51:26 (24), reproducer-w04-5 10:45:37 to 10:45:58 (21) |
