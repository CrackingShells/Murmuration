---
type: findings
wave: wave-09
author: explorer-w09-h
date: 2026-10-26
version: v0
decision-required: confirm
---

# Escalations decided without the claim file: did it matter, and what is the cheapest lever (v0)

## Result
- **Did it matter: not for the label, a little for the wording and follow-up.** For 13 of the 14 claims with a `verdict: ESCALATE` I located the wake or the decision; in 0 of 13 do I judge that the decision label (restate in place, supersede) would have differed had the PI read the section and exchange first [CONJECTURE; rests on the per-claim comparison in `01-escalation_table.md`: in 9 of 10 reproducer hand-backs the hand-back already carries the verifier's findings, the author's request and the proposed restatement; hand-back median 4,458 chars against a section median 6,929]. In 3 of 13 (w04-c4, w07-c7, w08-c9) the wake text is thinner than the file or the hand-back, and the decision section written 2 to 5 days later says more [CONJECTURE]. The one case where the PI did open the verdict section in the wake (w01-c5, `awk ... | cut -c1-500`) decided the same way as the others [MEASURED, transcript line 754 of `ab96c5ed`].
- **Fate of the 14 decisions.** 5 were "supersede with a new claim" at the wake (w01-c4, w01-c5, w06-c3, w08-c1, w08-c9) and `lab_status` shows `superseded by` for all 5; 9 were "restate in place" and show `MEASURED (PI decided: restated, not re-verified)`; reversed: 0 of 14 [MEASURED, `python3 -I scripts/lab_status.py`]. All 9 decision sections were written 2026-10-24, 2 to 5 days after the wakes, in two batches (82aa750: 4 sections; dd8357f: 5), none at the wake [MEASURED, `git log -S'## decision: research-pi'`]. Their `statement:` differs in substance from the wake text in 3 of 9 (w03-c2, w04-c4, w07-c7) [CONJECTURE, my reading].
- **The records undercount reads, and overcount none.** w09-c4's "0 of 10" holds for the 10 reproducer hand-backs delivered as messages (I re-ran: `opens_claim` is empty in the wake turn and the next in all 10) [MEASURED, `out/wakes.json`]. Four more escalations arrived as queued attachments (w01-c5, w05-c1, w08-c1) or in an order I could not place (w01-c8); the w09d parser has no turn for a queued hand-back. Of those, 1 of 3 examined (w01-c5) read the verdict section, 2 of 3 did not [MEASURED, transcript lines 754, 1425-1440, 384-420].
- **Cheapest lever that does not rely on PI memory (ESTIMATE, nothing built).** A synchronous `UserPromptSubmit` hook that, for a peer message from a reproducer or proof-adversary whose claim file ends its section with `verdict: ESCALATE`, returns the section as `additionalContext`. Adds per escalation: 98 chars for a pointer with line range (all 14: 98-101), 2,621 chars median for the exchange alone (1,629-4,629), 6,929 chars median for the whole verdict section (4,783-11,727; sum over the 14: 103,967) [MEASURED, `out/ranges.tsv`]. Sits in `rust/src/handback.rs` (new event kind next to `gate`, L331-362; emission pattern at `rust/src/budget.rs:708`), mirrored in `scripts/handback.py`, registered in `hooks/hooks.json`.

## Table
Full table of the 14 claims: `__reports__/wave-09/explorer-w09-h/01-escalation_table.md`. Summary rows:

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Claims with an ESCALATE verdict line | 14 (w01-c2, c4, c5, c8; w02-c10; w03-c2; w04-c4, c7, c10; w05-c1; w06-c3; w07-c7; w08-c1, c9) | MEASURED | `__instrumenta__/w09h_extract.py` over `__pondus__/*.md` |
| Reproducer hand-backs located as messages | 10; hand-back chars min 2,033, median 4,458, max 6,036 | MEASURED | `out/wakes.json`, `out/coverage.tsv` |
| Other wakes | w01-c5 queued hb (4,527 chars after the frame), w05-c1 queued hb (4,657), w08-c1 queued hb (3,027); w01-c8 not placed | MEASURED | `__instrumenta__/w09h_find_mentions.py`, `w09h_pi_after.py` |
| Claim file opened before or in the wake turn | 0 of 10 messages; 1 of 3 queued (w01-c5, verdict section only, lines cut at 500 chars: 8,135 of 9,352 characters shown (87%), 4 of the 15 lines of the exchange part cut) | MEASURED | `out/wakes.json`; transcript lines 754, 1425-1440, 384-420 |
| Verdict section chars (14) | min 4,783, median 6,929, mean 7,426, max 11,727 | MEASURED | `out/ranges.tsv` |
| Exchange chars (14; `### exchange` to the end of the section) | min 1,629, median 2,621, mean 2,813, max 4,629 | MEASURED | `out/ranges.tsv` |
| Numeric tokens of the section found in the hand-back | median 0.59 (0.23 to 1.00; w04-c4 lowest, w04-c10 highest) over 10 | MEASURED (a crude proxy; most misses are probe paths and counts) | `out/coverage.tsv`, `__instrumenta__/w09h_coverage.py` |
| Decision label that a read would have changed | 0 of 13 | CONJECTURE | `01-escalation_table.md`, column "would a read have changed it" |
| Decision wording or follow-up that a read might have changed | 3 of 13 (w04-c4: the 4/3/1 breakdown in the verifier's suggested restatement; w07-c7: c3 limited to the 6-tool headless author, which the hand-back already says; w08-c9: 2 of 4 open items taken) | CONJECTURE | same |
| Decisions later superseded / restated / reversed | superseded 5 (at the wake, as decided); decision section added 9 (all 2 to 5 days later); reversed 0 | MEASURED | `lab_status.py`; `git log -S` |
| In-place restatement | the wake text of w04-c4 says "restate the head in place", w04-c7 "restate the claim in place", w04-c10 "restated in place"; reproducer-w08-9 counts 8 of the 9 decisions as the restated wording in place (w07-c7 the exception); the skill says the author's head is never edited and the decision goes in a section | MEASURED (PI wake text, three claims); the 8 of 9 is the verifier's count (CITED) | `01-escalation_table.md`; `__pondus__/w08-c9.md` independent result (2, content) |
| Lever P: pointer with line range in the notice | 98 chars median (98-101); the PI must still open the file | ESTIMATE (string built per claim) | `out/ranges.tsv` |
| Lever E: exchange verbatim | +2,621 chars median; +59% of the median hand-back (4,458) | ESTIMATE | `out/ranges.tsv` |
| Lever S: whole verdict section | +6,929 chars median; +155% of the median hand-back; about 1,700 tokens at 4 chars per token | ESTIMATE (the 4 chars per token is an assumption) | `out/ranges.tsv` |
| Hook latency per fire | about 100 ms (Rust, first hook 108 ms, warm 98 ms) on every hand-back prompt; 25 to 40 hand-back wakes per wave | CITED (`__reports__/wave-06/explorer-w06-a/00-findings_v0.md:20`, from the repo, not re-run); wake counts from `__reports__/wave-09/author-w09-2/counts.txt` | as given |

How the file "at that moment" was fixed. Claim files are append-only for verifiers and the PI, so the file when the PI decided is the prefix of today's file ending at the escalating verifier's last `verdict: ESCALATE` line; `w09h_extract.py` cuts it there (fenced blocks respected) [CHECKED on the 14: the cut is a prefix of today's file, and the verdict section equals, after trailing whitespace, the section in the first commit that holds `verdict: ESCALATE` (`git show <commit>:<path>`; commits e1014a0, 8ffd44e, d4fb928, 9e4bbac, 13fb81e, 0e9b3df, ca12ffd, 5986b88, 6b79137, 033e274, e688d43, 3e73bca). Those commits fall after the wakes I could time (e1014a0 at 19 12:03 against the wake at 12:00; 8ffd44e at 11:57 against the w01-c5 wake at 11:37), so what the PI could have read in the wake was this section or a prefix of it, not a longer one]. The heads in the cut are today's: authors edited heads after the wakes (the w04-c4, w04-c7, w04-c10 and w05-c1 heads differ from the verdict commit by 800 to 1,100 chars), so head comparisons in this report use the hand-back, not the cut.

### What would carry the information (no code written; each step labelled)
1. Trigger: exact, not prose: peer message prefix `<agent-message from=` (already in `scripts/user_words.py:42`, `NON_USER_PREFIXES`), the agent name begins `reproducer-` or `proof-adversary-`, claim id from the message; then read `__pondus__/<id>.md` and test that the last `verdict:` line of the last `## verdict: <that agent>` section is `ESCALATE`. A word match on "ESCALATE" in the body gives false hits (`w09c2_escalations.py` prints three blocks from explorers and authors).
2. Output: `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "<lines A-B of the claim file>"}}`, the shape `rust/src/budget.rs:708` already emits for other events.
3. Where: new branch in `rust/src/handback.rs::run` (L364) beside `gate` (L331-362, the deny-once pattern for explorers); the same in `scripts/handback.py` (`main`, selftest, equality checked by `scripts/check_guard_equal.py` style tests); one new entry under `UserPromptSubmit` in `hooks/hooks.json`, synchronous (the present `user_words.py` entry is `async: true`, so it cannot inject, and it may wait up to 3 s for the transcript record: `ORIGIN_WAIT`, so do not put the new logic in it).
4. Alternative on the verifier side: extend `gate()` to `murmuration:reproducer` and `murmuration:proof-adversary`: deny the first hand-back of a verifier whose section ends in ESCALATE unless the message contains the exchange. Costs the same characters but moves them into the hand-back (the verifier pays output tokens; the PI cannot miss it), and relies on a once-only deny that the explorer gate already uses.
5. Not verified, and decisive: whether `additionalContext` of a `UserPromptSubmit` hook reaches the model when the prompt is a peer message, and when the hand-back arrives as a `queued_command` attachment (w01-c5, w05-c1, w08-c1 did). `__reports__/wave-06/explorer-w06-b/00-findings_v0.md:36` says the hook "fires per user prompt and per queued task notification"; it does not say what the model then sees [CONJECTURE]. One headless test would settle it; I was told not to run one.

## Worst-fitting case
- **For "the PI should have read the file and the decision would be better": w02-c10 and w04-c10.** The hand-back carried the verifier's figures, the author's proposed narrowing and its open items; for w04-c10 the hand-back (4,476 chars) carries the data checks, the edge, the dependence on pt2r2 and the author's draft title that the section (4,783) holds. Reading the file would have cost 6,341 and 4,783 chars and told the PI nothing new that I found. Also w01-c5: the PI did read the verdict section 2 s after the hand-back and decided exactly as the PI that did not read.
- **For "the lever fixes the decisions": w07-c7.** The hand-back said the 1-hour result holds "only for the 6-tool, 12k-token headless author", that the author "never tested a resume", and that the money is "not determined"; the PI wrote "it lands by its registered rule" and merged. The ex-post decision section narrows to the 6-tool headless author and says "kept by risk attitude, not by a measured gain". The information was in the notice; the decision still went the other way first. A lever that adds the file adds nothing here [CONJECTURE].
- **Typical:** w01-c2, w02-c10, w04-c7, w04-c10, w05-c1: hand-back carries the content, the PI restates or accepts, no later change.
- **Where the file did hold something the hand-back did not:** w04-c4 (the verifier's full suggested restatement, only pointed to in the hand-back) and w08-c9 (items about the form of the PI's own decision records). w04-c4 gained a more detailed statement 5 days later in the decision section; w08-c9 was superseded (w08-c11).

## Not covered
- w01-c8: I did not place the wake of reproducer-w01-8's escalation (a hand-back of author-w01-5 at line 909 precedes "I've applied my decision"), so no judgement is given for it.
- I read the verdict section and exchange in full for 7 files (w01-c4, w01-c2, w02-c10, w03-c2, w04-c4, w04-c7, w08-c9); for w04-c10, w05-c1, w06-c3, w07-c7, w08-c1, w01-c5 I read the hand-back and the PI's turn and used only the numeric-token overlap and the head of the section; "would it have changed" is one reader's judgement (mine), 13 of 14 only.
- Whether the PI read a claim file in turns before the wake (w09-c4's claim; I only checked the wake turn and the next one).
- Hook behaviour: `additionalContext` for peer or queued prompts is untested (see above). Hook cost is cited, not re-measured.
- Dollar cost of the added characters: not computed; the hook is a read of one file and a string, no model call.
- Whether the three-line decision rules in the skill would be better enforced by a gate on writing the decision section (a `PreToolUse` check that the PI has read the section): not sized.

## Steering questions
- [now] Is the 3-of-13 "wording or follow-up" signal enough to build lever E or S, or is lever P (98 chars) the only one worth its hook?
- [now] May one headless run test whether `additionalContext` from `UserPromptSubmit` reaches the model for a peer-origin prompt and for a queued attachment?
- [now] Should in-place head restatement at the wake (8 of 9 by reproducer-w08-9's count) be named as a skill breach in the next brief, since the head is meant to stay as filed?

## Pointers
- Per-escalation table: `__reports__/wave-09/explorer-w09-h/01-escalation_table.md`.
- Extraction output: `__reports__/wave-09/explorer-w09-h/out/` (`wakes.json`, `claim_at_verdict/<id>.md`, `coverage.tsv`, `ranges.tsv`).
- Commands (from the worktree; P = `$HOME/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration`; six pairs as in `__pondus__/w09-c2.md` "method"):
  - `python3 -I __instrumenta__/w09h_extract.py __reports__/wave-09/explorer-w09-h/out w123=$P-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl w4=$P-murmuration-wave-4-3417be/c533f1c6-c56e-4c8d-b6ff-e90c3ddea2f4.jsonl w5=$P-lab-system-optimization-1aa673/6b0e1f2a-b6d1-40f5-840c-f38548cd357e.jsonl w6=$P-blissful-villani-34edd8/74fa512e-a149-4bbb-bd20-2d434b0f997f.jsonl w7=$P-xenodochial-franklin-bc67fb/f023f552-e4a3-4823-a275-6d98b51b849c.jsonl w8=$P-murmuration-wave-8-928ebd/70daedf1-41ec-46c0-baa6-6df7da82a7ae.jsonl`
  - `python3 -I __instrumenta__/w09h_coverage.py <out>`, `python3 -I __instrumenta__/w09h_ranges.py <out>`, `python3 -I __instrumenta__/w09h_show.py <out> <claim-id> [wake-index]`
  - `python3 -I __instrumenta__/w09h_find_mentions.py <transcript> <agent-name>` and `python3 -I __instrumenta__/w09h_pi_after.py <transcript> <line> <n>` for the queued wakes (w01-c5 line 750, w05-c1 line 1421, w08-c1 line 383).
- Scripts: `__instrumenta__/w09h_extract.py@aed13a4`, `w09h_show.py@aed13a4`, `w09h_coverage.py@aed13a4`, `w09h_ranges.py@aed13a4`, `w09h_find_mentions.py@aed13a4`, `w09h_pi_after.py@aed13a4`.
- Puzzles: `__scrupuli__/wave-09-explorer-w09-h.md`.
