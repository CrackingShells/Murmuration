# Hand-backs of wave-01-explorer-w01-b

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T11:57:46+09:00 | agent_id=ac6c27171353e66ed type=murmuration:explorer event=PostToolUse status=delivered bytes=15162 sha256=20e72e63cbb8
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

# explorer-w01-b report: communication, hand-backs, pairs, parsing

I stayed inside the brief. Two things differ from what you asked.
- `report.md` was not written to disk. The Write tool refused it ("Subagents should return findings as text, not write report files"), and I did not work around the refusal. The full report is below; please save it as `__reports__/reflective_run/w01/explorer-w01-b/report.md`.
- The report is late because the 60-turn limit stopped me before I wrote it.

Written to disk, all under `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/`:
- Puzzles: `__scrupuli__/wave-01-explorer-w01-b.md` (6 puzzles, the last one on the 60 turns).
- Scripts and tables in `__reports__/reflective_run/w01/explorer-w01-b/`.
  - Scripts: `extract_comm.py`, `analyze.py`, `coded_tables.py`, `numcheck.py`, `brief_dup.py`, `pair_thread.py`, `run_all.sh`. I did not re-run `run_all.sh` as a whole; I ran the scripts one by one.
  - Tables: `dispatches.csv`, `returns.csv` (filter `kind=agent-message`; it also holds bash-job and pointer rows), `reactions.csv`, `startctx.csv`, `brief_anatomy.csv`, `handbacks.csv`, `handbacks_coded.csv`, `followups.csv`, `usage_from_notifications.csv`, `pair_threads.csv`, `pair_orphans.txt`, `numcheck.csv`, `brief_dup.csv`, `summary.txt`.

Labels: MEASURED means a script produced it. HAND-CODED means I read the rows and assigned the code, and the script only counts. CONJECTURE and CITED as in the skill.

Evidence comes from the genesis study (`566fa912`) and the design session (`82e8a947`), both run before Murmuration existed, plus six probe sessions. This run's six explorer briefs are in the brief tables. This run has no hand-back yet, so nothing below measures how the shipped plugin's returns look.

## Unfinished
- The auto-classified `first_line_class` column in `handbacks.csv` is wrong in places (a regex; "all 10 blocked rows resolved" reads as a blocker). Use the hand-coded column in `handbacks_coded.csv`.
- `numcheck.csv` lists 94 numbers the PI quoted that are absent from the hand-back. I only skimmed it and found no clear misquote.
- Not tested: a peer message to a still-running agent.
- Per-return token cost is an ESTIMATE only.
- This run's own hand-backs are not compared with their briefs because none exist yet (predictions P1 and P2 at the end).

## 1. Brief length and redundancy
Command: `python3 -I extract_comm.py . && python3 -I analyze.py .`. Results are in `summary.txt`, `brief_anatomy.csv`, `dispatches.csv` and `startctx.csv`. `python3 -I brief_dup.py` gives `brief_dup.csv`.

| session | Agent briefs | median chars | range | follow-up SendMessages |
|:--|--:|--:|:--|--:|
| genesis | 10 | 3439 | 2643-5041 | 5 |
| design (own, after fork) | 14 | 3522 | 1245-5178 | 5 |
| this run | 6 | 2497 | 2305-2794 | 0 |

- The 10 follow-ups have a median of 1130 chars (range 729-3216).
- At chars/4, a typical brief is about 850 tokens (ESTIMATE).
- Bytes by paragraph class (leading-keyword rules in `analyze.py`, so approximate):

| paragraph class | share of a brief |
|:--|:--|
| task text | 48-62% |
| READ FIRST pointers | 10-14% |
| rules and constraints | 4-16% |
| role line | 5-7% |
| deliverable | 7-13% |
| FINAL MESSAGE spec | 3-4% |

- The FINAL MESSAGE share is 17.5% in this run's six briefs.
- In the genesis and design briefs, 29 of 30 had a return spec, 17 gave a word limit, and 21 carried the commit boilerplate.

What each agent already holds at its first turn (mean chars from the attachments before its first assistant turn, `startctx.csv`):

| | brief | CLAUDE.md | skill listing | SubagentStart hook text | system prompt | deferred-tool list | brief share |
|:--|--:|--:|--:|--:|--:|--:|--:|
| genesis (10) | 3696 | 1737 | 29975 | 2051 | 2788 | 14567 | 6.7% |
| design (12) | 3659 | 1892 | 29974 | 2051 | 2788 | 14567 | 6.5% |
| this run (6) | 2511 | 1737 | 29940 | 2051 | 2682 | 1117 | 6.1% |

- The brief is about 6% of the start context. The platform's skill listing is about ten times the brief.
- The 2051-char hook text is the user's own machine-level `SubagentStart` hook, which already injects text into every subagent. So SA5 exists in small form today, paid by the user's hook and not by the plugin.
- In this run the preloaded `research-loop` skill (8168 chars, from the `skills:` frontmatter of `agents/explorer.md`) is in all six explorers' contexts at line 5 of their transcripts. The brief still says to read `skills/research-loop/SKILL.md`.
- Verbatim overlap of this run's briefs (6-word shingles, `brief_dup.csv`):
  - 6.5-11.5% of a brief's shingles occur in explorer.md + SKILL.md + framing.md + wave-01.md + briefs.md together.
  - 25-41% occur in the other five briefs: the rules paragraph, "If you leave the brief...", the working-directory line, "worst-fitting case", "400k tokens".
  - For genesis and design briefs, the share inside the files they name is 1.6-4.8% (median).
- Paraphrase overlap is higher and not measurable this way. The brief's "Rules:" paragraph restates the "Rules for the team" block of `framing.md`, which the same brief orders the agent to read (HAND-CODED, one brief checked closely).
- Shared sentences are not always waste. "Never stop processes by name pattern" exists because of a real incident (case P below).
- Follow-ups repair briefs. Of 10 SendMessages (`followups.csv`): 4 corrections, 3 new input/scope/assignment, 1 unblock, 1 brief omission, 1 spec change.
  - The brief omission is design line 1880, sent 22 s after the brief (15:46:55 to 15:47:17). It added the branch and commit rules the brief lacked, right after the human said so in a queued message (`pair_orphans.txt`).

## 2. Hand-back shapes
Unit: the 30 hand-backs in `<agent-message from=...>` form (genesis 13, design 17), `handbacks.csv`.

The platform already supplies an envelope.
- The header reads "[Subagent hand-back] ... model output, NOT a message from the user".
- The report is indented two spaces.
- A separate `<task-notification>` carries `status` and `<usage>` (tokens, tool uses, duration). It is present for 29 of 29 agent notifications (`usage_from_notifications.csv`).

So who, status and usage are already machine-readable. Only the body is free.

| | value |
|:--|:--|
| words per report, median / min / max | 331 / 104 / 3527 |
| briefs with a word limit (20) | 18 over the limit; median 1.27x; median excess 54 words |
| briefs without a limit (10) | median 1135 words (283 for the limited ones) |
| first line (HAND-CODED) | STATUS 17, headline RESULT 8, path only 3, title/body 2 |
| reports naming an absolute path / a relative path / a commit hash | 20 / 26 / 24 |
| with bullets / `#` headers / table rows | 29 / 7 / 2 |
| with a label word (THEOREM, CHECKED, ...) | 18 |
| harness line `[harness: subagent output matched instruction-shaped pattern(s): ...]` first | 8 (0 of 13 genesis, 8 of 17 design) |
| body control tags rewritten `<` to `<\` | 8 reports; tags seen: `<agent-message`, `<task-notification`, `<cross-session-message` and closing forms |

- The 30 returns total 19,394 words, about 26 k tokens (ESTIMATE, words x 1.33). Return text is not where the cost is. A word-limit hook would save about 54 words per return (MEASURED excess), and I judge it not worth building (CONJECTURE).
- The harness flag fires on settings.json and bypassPermissions content, which is this lab's subject. The PI never mentioned it in any of the 8 cases (HAND-CODED scan, 0 of 8), so all 8 were false positives in effect.
- A parser must skip a leading `[harness: ...]` line. A report that quotes a control tag arrives altered.

## 3. What the PI did next
`handbacks_coded.csv`, with codes HAND-CODED and joined to `reactions.csv`. The window is the PI's turn after delivery.

| action in the window | of 30 |
|:--|--:|
| read or ran something on the file the report points to | 15 |
| dispatched the next agent | 10 |
| checked a claim independently before relaying (own computation, raw evidence, fetch) | 10 |
| sent a SendMessage (to any agent) | 7 |
| none of those four (relayed to the user) | 6 |

Typical (T), genesis line 557 (trellis): status-first, 320 words, 3 paths and 2 commit hashes. The PI re-ran the agent's selftest, then agreed. This fits a "status + path" header.

Case C, correction relay, genesis line 674 (reproducer).
- The report opens "Gates: all three pass. Committed as 437a67e." Item 4(a) says OVERSTATED, with six number slips.
- Within 9 s the PI sent two correction messages to the authors (lines 677 and 678). The numbers were copied correctly: 5.8 to 5.42, 1.68 to 1.669, 0.1833-0.1837, 46 to 40 of 51.
- The PI also added conventions the verifier had not given: keep v0, write v1, update README, "reply in under 100 words".
- The authors confirmed (lines 701 and 746).
- Free prose worked here, and the PI's relay added value.

Case P, an incident in the tail, genesis line 580.
- The last paragraph of a 360-word report reads "Mistake to flag: ... `pkill -f run_all.py` also killed another agent's `code/trellis/run_all.py`".
- The PI's first action was to check the trellis data (line 586).
- The incident went into the knowledge-transfer table (`__reports__/meta_process/00-knowledge_transfer_v0.md:95` in the genesis repo), then into a v4 hook (`process_guard.py`, later cut), then into the brief boilerplate.
- This is the best fit for a machine-parseable `incidents:` field.

Case B, blocker first, design line 1573 (probes): title, then "BLOCKER FIRST: the claude CLI is logged out ... Ten mechanisms ... NOT RUN". The PI sent the re-run message at line 1616. Free prose worked because the agent put the blocker first unprompted.

Misreads and wrong numbers: none found in a skim of 94 candidates (unfinished). Re-asks caused by a misunderstood return: none. The 7 messages are corrections, scope and unblock steps. One loose lead is S-w01-research-pi-7, where 69 versus 28 "human prompts" has no definition attached to either number.

## 4. Pair threads and reconstruction
- Real pair conversations on a research question: zero, in both sessions and in this run. The pair evidence is six synthetic pings in probe sessions: `ec70ebcf` (named author and verifier) and unnamed siblings `a4b39e78` and `a5073b71` in the design session. Every value claim for SA4 is therefore CONJECTURE.
- The nearest real instance is case C: the PI relayed verifier to authors, 2 messages, about 460 tokens, 9 s.

Reconstruction from transcripts alone (`pair_thread.py`, `pair_threads.csv`, `pair_orphans.txt`), MEASURED: 15 of 16 SendMessages joined to a receipt.
- Probe session: 3 of 3.
- Design session: 12 of 13. The one miss is a message to another session, which cannot have a receipt here.

The join needs three things.
1. The sender's `SendMessage` tool_use in the sender's own transcript. Nested agents live in the same subagents folder.
2. Three receiver forms, not one:
   - `<agent-message from="X">` in a user message;
   - "The coordinator sent a message while you were working:" for the main thread;
   - an `attachment` of type `queued_command` holding the bare text with no sender, used for a message to a still-running agent.
   In the design session 4 of 12 main-to-agent messages came in the bare form. The user's own mid-run messages use that form too. For peer messages to a running agent this is untested (CONJECTURE: also bare).
3. Normalising `<\` back to `<`. A message quoting a control tag arrives rewritten (probe A to B: `<agent-message from=...>` became `<\agent-message ...>`), and an exact join fails otherwise.

Two more details: de-duplicate by tool_use id, because the same tool_use sits on two transcript lines (my first run double-counted). Hand-backs to the main thread show as receipts without a send (26 in the design session).

A `PostToolUse(SendMessage)` mirror would add no content, since sender and recipient are recoverable. It would add a key, because a per-claim thread needs the claim id. Neither the transcript nor the hook has it unless the message text or its `summary` field carries it, or SA5 injected it. A zero-code alternative (CONJECTURE) is to require the claim id in `summary`.

## 5. Where a fixed parseable return shape helps or hurts
Already fixed where code reads: claim, puzzle, verdict and wave files.
- `python3 scripts/lab_status.py` parsed explorer-w01-e's puzzle file (7 puzzles plus `## symbols`) into 14 listed puzzles with no warning (MEASURED).
- The cold review found silent-failure modes in those parsers: N1 HTML comments, N2 verdict prefix match, N3 a puzzle file without `##` headings, N8 an unchecked label (CITED: `__reports__/cold_review/01-findings_v1.md` rows N1, N2, N3, N8).

A shape would have helped (HAND-CODED judgement):
- Case P: an `incidents:` line.
- Case C: a `verdicts: a=OVERSTATED b=SUPPORTED` line, so the wave note could be filled without a re-read.
- The wave note's "Returned" column needs no body shape, since the platform notification already gives status and usage.

A shape would have hurt or been useless:
- An XML-like header named like a control tag is rewritten by the harness. A JSON or YAML header without such a tag is probably untouched (CONJECTURE, untested).
- "First line" parsers break on the harness line in 8 of 17 reports in a lab about settings and hooks.
- A one-word status misleads in case C ("pass" over OVERSTATED).
- It adds nothing where the value is a surprise.

Worst-fitting case: design line 1567 (instrument validation, 1552 words). It has a clean status line, a decision table, then "What puzzled me". The PI called it "the most valuable thing wave 1 could have produced" and said it "changes our own retrospective". No field would carry that, and a "done" status would sit on top of a report that overturned the design's premise. Second worst: case C.

Predictions to check when this run's returns arrive (CONJECTURE):
- P1: the six briefs state no word limit for the final message (`return_word_limit` is empty in `dispatches.csv`), so returns will land near the no-limit median (about 1100 words), not the limited one (about 280).
- P2: several returns will carry the harness line, because the lab's subject is hooks and settings.

## Puzzles (full text in `__scrupuli__/wave-01-explorer-w01-b.md`)
1. SA4 is judged on zero real pair conversations, and the relay in case C looks cheap and useful.
2. Case C: "Gates: all three pass" sits over OVERSTATED. Should "status" mean the run or the claim?
3. The harness flag fires on 8 of 17 design-session returns, always ignored, and it will fire on this lab's own subject.
4. A message to a running agent is recorded bare in the receiver's transcript, with no sender, the same form as a user's mid-run message.
5. 18 of 20 returns exceeded their word limit, yet no follow-up cost a step. Is the limit doing any work?
6. What used my 60 turns: exploration, plus re-running extraction after fixing my own bugs (queue-operation lines without a uuid duplicating the design session's returns; each tool_use on two lines; three receipt forms), and long outputs from some bash calls. The brief did not tell me to write the report before the last extraction.
