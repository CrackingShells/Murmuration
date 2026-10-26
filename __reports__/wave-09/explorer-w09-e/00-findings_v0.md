---
type: findings
wave: wave-09
author: explorer-w09-e
date: 2026-10-25
version: v0
decision-required: confirm
---

# PreCompact digest at a real PI's size: what is re-read after a compaction (findings v0)

Stayed inside the brief, with four scope notes. (1) The "digest" arms put the digest in two places, not one: H = the PreCompact hook's stdout (the user's location, it passes through the summarizer); HP = the same digest as a second `SessionStart` row with matcher `compact` (reaches the context verbatim after the summary). I added HP because `resume_brief.py` already uses that channel. (2) Hooks of the runs were trimmed to the compaction rows (no Rust guard, no budget hooks). (3) Six Opus cells, not one pair: the cells cost USD 1.2-1.7 each, not the 3-4 I priced, because the compaction request ran on a cold cache and the later requests were few. (4) The first Opus cell (`OP_B1_pilot6q`) used six questions and was kept as a pilot row; the five other cells use eight.

## Result

**The route works and is cheap.** A real PI transcript cut after record 788 (wave 8's PI main thread, context 216,872 tokens at 01:11 JST on 2026-10-24, last record an assistant `end_turn`), a clone of the repository at the commit the transcript itself shows (104666a), the real `harness.jsonl` cut at the same second (3 workers in flight) and the 7 hand-back files on disk at that second, resumed with `claude -p --resume <id> --fork-session` and compacted on the first request (window 230,000, threshold 197,000, `thresholdSource=env`; boundary `pre_tokens` 219,478-222,058). [MEASURED, source: `runs_scored.tsv`, `debug.log` of each run]

**At this size, with the lab's existing state only (B1), the PI kept every thread** (6 of 6 in the pilot, 8 of 8 in two cells) and re-read 5.3k-8.6k tokens (ESTIMATE, result characters / 3.6) in 2-3 tool calls; the context grew by 15.3k-25.0k tokens between the first and last request after the compaction (MEASURED from usage). The wave-8 floor of 91k that wave 8 feared is not what is re-read: the PI re-reads what the summary lost (details of reports), plus the lab's status table.

**With the digest, re-reads were about half, answers were the same.** H (PreCompact): 1 cell, 2 calls, 3.8k tokens, growth 12.2k. HP (digest after the summary): 2 cells, 3.0k and 3.3k tokens, 1-2 calls, growth 11.0k and 14.4k. All three digest cells answered 8 of 8 (my reading; see the worst-fitting case for the scorer's two false flags). n is 2 against 1 against 2 and the tool-call habit of the model moves the number more than the arm may: this is a pilot reading, CONJECTURE for the difference. [source: `runs_scored.tsv`, `calls_after_boundary.tsv`]

**"Re-read nothing" did not hold in any arm.** The summaries (10.2k-14.1k characters) held no number of the two detail questions (1,123 requests; 15 of 23) in any of the four summaries I extracted, so every PI opened a file for questions 7 and 8; the digest cells opened the hand-back files named in the digest (`__statera__/handbacks/wave-08-explorer-w08-d.md`), the B1 cells grepped the reports' folders. The digest made the PI skip `lab_status` in 1 of 3 cells (HP_2 and HP_3 ran no `lab_status` call; H_2 ran one filtered call of 719 characters) against 3 of 3 B1 cells running it (results of 17.4k + 1.7k, 13.5k + 3.0k and 13.7k characters in the pilot, B1_2 and B1_3). [source: `calls_after_boundary.tsv`]

**What the digest costs and carries.** The digest is 5,366 characters (about 1.5k tokens) built in 0.12 s (offline `time`; the platform's PreCompact step settled in 242 ms in the H run). Through the summarizer it survived whole in H on Opus: 13 of 13 wave-note map entries, 17 of 17 read ranges and the user's words verbatim were in the summary; the summary was larger (14,065 characters, 5,990 output tokens against 10,154-12,265 characters and 4,031-4,762 tokens). The line pointers were exact (wave-08.md lines 161-163 are the three in-flight dispatch rows; `evidence:` is line 5 of `w08-c1.md`). [MEASURED, source: `summary_flags.tsv`, `digest_at_cut.txt`, a check against the lab files]

**Money (ESTIMATE).** The difference in tokens carried is about 12k per compaction. With explorer-w08-e's net table (R = 10k: USD 42.15; R = 45k: 31.27 over six PI sessions, 14-17 compactions) the slope is about USD 0.31 per 1k of R, so 12k of R is about USD 3.7 of a 31-45 saving [source: `__reports__/wave-08/explorer-w08-e/00-findings_v0.md`, "Result" (4); my slope]. The cell-to-cell spread of one arm's re-read (B1: 5.3k, 7.7k, 8.6k) is as large as a third of that difference.

## Table

| Cell | Arm | Q (items right) | Calls after boundary | Result chars | Re-read tokens (ESTIMATE) | Context growth (MEASURED) | Compaction request USD | After-boundary requests USD | Reported cell USD |
|:--|:--|:--|--:|--:|--:|--:|--:|--:|--:|
| OP_B1_pilot6q | B1 | 6 of 6 | 2 | 19,110 | 5,308 | 15,273 | 0.772 | 0.473 | 1.286 |
| OP_B1_2 | B1 | 8 of 8 | 3 | 27,738 | 7,705 | 24,034 | 0.773 | 0.499 | 1.324 |
| OP_B1_3 | B1 | 8 of 8 | 2 | 31,011 | 8,614 | 25,022 | 0.771 | 0.574 | 1.393 |
| OP_H_2 | H (PreCompact) | 8 of 8 | 2 | 13,586 | 3,774 | 12,193 | 0.807 | 0.414 | 1.246 |
| OP_HP_2 | HP (digest after) | 8 of 8 (scorer: 7) | 2 | 10,744 | 2,984 | 10,958 | 0.758 | 0.395 | 1.190 |
| OP_HP_3 | HP (digest after) | 8 of 8 (scorer: 7) | 1 | 11,897 | 3,305 | 14,445 | 0.768 | 0.515 | 1.703 |

All rows MEASURED as to tokens and answers; USD re-priced at Opus 5.5 list (input 4, output 20, read 0.20, 1-hour write 8 per million) from the stream and the forked agent's `totalUsage` in `debug.log`; the last column is the run's own `total_cost_usd`. Command and quick command: see Pointers. Seeds: none (one cut, one lab; the model is not deterministic).

The questions (`questions3.txt`, eight): workers in flight with claim ids; the user's instruction quoted; labels of w08-c1 and w08-c2 as the lab's rules give them; what the PI decided about each and what it waits for; how many claims are escalated and which are of waves 5-7 (truth 9: w05-c1, w07-c7); the commit w08-c1's evidence cites for `rust/src/budget.rs` and the line of that `evidence:` field (bfbcc96, line 5); two numbers from hand-backs in context before the cut (explorer-w08-d: 7 sessions, 1,123 requests, costliest read 33k characters at USD 0.80; explorer-w08-b: 15 and 17 of 23). Truths come from the lab files at the cut.

Other numbers [MEASURED, source: `runs_scored.tsv`, hook events in `stream.jsonl`]: compaction request 168,357 uncached input tokens + 20,706 cached, 4.0k-6.0k output tokens, 38.7-50.2 s; the first request after the boundary holds 37.4k-43.1k tokens of context; `resume_brief.py` printed 31,844 characters (about 9k tokens, the wave note of 12,983 characters plus 50 open puzzles) in every arm, more than the summary.

## Worst-fitting case

The story "a digest spares re-reads without losing the thread" fits worst in three places.

1. **The digest did not spare the detail re-read.** Questions 7 and 8 were answered by opening files in every cell. HP_3 answered all eight with one call, but that call was the `cat` of two hand-back files: 11.9k characters. The digest made the PI's route short (the right files named), not absent. [source: `calls_after_boundary.tsv`]
2. **Trust is partial.** H_2 had the escalated-claims count in its digest and still ran `lab_status.py | grep` to check it (719 characters); HP_2 and HP_3 answered Q5 from the digest and said so ("this count comes from the lab's digest ... I have not re-run lab_status"). One cell trusting, one verifying: no pattern at n = 3.
3. **A cost outlier on the digest side:** HP_3 reported USD 1.703 against 1.190 for HP_2: 94.9k cache-creation tokens against 46.7k, 201k input against 168k, i.e. a cache miss on its second request (two runs of the replicate were launched at the same time). My per-message sum for the same run is 1.283, so the stream's total and the sum of its requests disagree by USD 0.42 only here (the other cells differ by 0.03-0.05). [source: `runs_scored.tsv` columns `total_usd`, `cost_reported`; modelUsage in the result line]

Scorer disagreement: `w09e_score.py` flags Q3 as wrong in HP_2 and HP_3 because its answer to item 3 does not name the claim ids; the answer says "Both are unverified MEASURED", which is the truth; I count them right (the flag stays in `runs_scored.tsv`).

Where the story fits best: HP_2, 2 calls and 3.0k tokens, 8 of 8, cell USD 1.19, the lowest of six.

Replay artifacts that touch the arms equally: (a) on resume the platform emits a `task_notification` for each unfinished background agent ("didn't finish before the previous session ended", with the agent's description), so Q1's names reach every arm by another route, and every answer adds that nothing is running now [source: `stream.jsonl` of `OP_B1_2`, `system/task_notification`]; (b) the compaction request ran on a cold cache (the resumed context is not cached), so it paid input price for 168k tokens: USD 0.76-0.81 here against the USD 0.126-0.157 that explorer-w08-e measured for a live compaction [source: its report, "Result" (2)]. The cell dollars are not the cost of a live compaction; the re-read tokens are not affected.

A pilot haiku cell (cut at record 117, context 76k, window 100,000) with the PreCompact digest copied the user's words into its summary with one sentence dropped ("... progressively optimize murmuration. You are Murmuration ..." lost "by using it yourself."), although the digest asked for them word for word; the Opus summaries kept them verbatim. [source: `/private/tmp/murmuration-w09/explorer-w09-e/pilot/runs/P1`, session file of the run; n = 1, model not the PI's]

## Not covered

- A hardened comparison: n is 1-2 per arm on one cut; the questions were written by me, together with the digest, so Q5 and Q6 fit the digest's structure (a generic map of claim head fields, but the `evidence:` line is one of them). No blind scoring beyond my reading.
- One cut point (a PI waiting for a worker, wave 8, record 788). The second transcript (`70daedf1`, a fork of the same session) and cuts at other moments (mid-dispatch, 300k, a later wave with a 45k-character wave note) were not run.
- A live compaction (no resume, warm cache), the Desktop route, `autoCompactWindow` from a project file: the run used the environment variable.
- The thread beyond answers: the PI was not asked to carry on the work (write the next wave-note entry, dispatch the next worker) after the compaction, so "without losing the thread" is shown for recall, not for action.
- colgrep hits as pointers: the colgrep tools were allowed and no cell called them (Bash `cat`, `sed`, `grep` every time). The markdown hit does not show where it matched (wave 8's explorer-w08-b), so a digest that hands colgrep hits to the PI was not built.
- Auto-generated "next step" and decisions: the digest lifts the PI's last words and last `update_plan`; the plan in this transcript was stale (set at 15:11Z, before the wave began), which the digest labels "may be stale".
- Haiku PI-like cells at this size, Opus beyond the six cells (the budget of USD 10 is spent).

## Steering questions

- [now] Is the pilot's reading ("the digest halves the re-read, 8 of 8 either way, and the dollar difference is about USD 3.7 of 31-45") enough to leave the PreCompact hook out of `main`, or does the user want the hardened test (see below, about USD 20)?
- [now] A hardened claim would need: at least 5 cells per arm over at least 3 cuts (the PI at 150k, 217k, 300k of wave 8; one of wave 7), the questions frozen by another agent before the digest is built, blind scoring, one live (non-resume) session per arm for the cold-cache and `task_notification` artifacts, and detail questions graded by the share that needed a file. About 15-18 cells at USD 1.2-1.4 is USD 18-25 (ESTIMATE from this report's cells).
- [later] Should the digest carry the hand-back files' headline numbers (the details every summary lost), since those are what the re-reads were for?

## Pointers

Scratch (not committed; transcripts and hook payloads carry account identifiers): `/private/tmp/murmuration-w09/explorer-w09-e/` (`lab/` the scratch lab, `main/` the cut and the runs, `pilot/` the haiku pilots).

- Route: `python3 -I __instrumenta__/w09e_cut_session.py <PI transcript> 788 <lab> <out>` (cut, path rewrite, install under `~/.claude/projects/<encoded lab>/<new id>.jsonl`; never writes the original) then `python3 __instrumenta__/w09e_run.py S NAME --arm B1|H|HP --session-id <id> --lab <lab> --export <plugin dir> --questions <file> --model opus --window 230000 --max-usd 5 --perm auto`. Lab: `git clone` of this repository, `git checkout -B claude/murmuration-wave-8-928ebd 104666a`, remote and other branches removed, `harness.jsonl` cut at `t <= 2026-10-24T01:11:15`, hand-backs with mtime up to the cut, the worktree path rewritten in the hand-backs.
- Quick command (haiku route check, USD 0.02): cut the same transcript at record 117 (`... 117 <lab> <out>`), then `w09e_run.py ... --arm H --model haiku --window 100000 --questions q.txt`.
- Score and tables: `python3 -I __instrumenta__/w09e_score.py S/runs OP_B1_pilot6q OP_B1_2 OP_H_2 OP_HP_2 OP_B1_3 OP_HP_3 [--show]` gives `runs_scored.tsv`; `calls_after_boundary.tsv` and `summary_flags.tsv` come from short inline extractions of `stream.jsonl` and of the compaction summary in the forked session file (commands in this session, same fields as in the tsv header).
- Derived files in `__reports__/wave-09/explorer-w09-e/`: `runs_scored.tsv`, `calls_after_boundary.tsv`, `summary_flags.tsv`, `digest_at_cut.txt` (the digest as built at the cut, 5,366 characters).
- Scripts: `__instrumenta__/w09e_cut_session.py@832716a`, `w09e_digest.py@832716a`, `w09e_run.py@832716a`, `w09e_score.py@832716a`. Prior scripts reused as models: `w08_c3_run.py`, `w08_c3_score.py`. Hook modelled on `scripts/precompact_state.py` of branch `w08-c3-compaction`.
- Prior results used (CITED to the repository, not to outside literature): `__pondus__/w08-c3.md` (small-lab result), `__reports__/wave-08/explorer-w08-e/00-findings_v0.md` (settings key, compaction cost, net table), `__reports__/wave-08/research-pi/02-wave09_handoff_v0.md` (direction 3).
- Processes: the six Opus cells and the three haiku pilot runs ran in the foreground or as background jobs with recorded pids (`main/OP_*.job.pid`); all gone at hand-back (checked with `kill -0`).
