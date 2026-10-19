# Hand-backs of wave-01-author-w01-6

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T11:57:46+09:00 | agent_id=aa70e320bd52db2dd type=murmuration:author event=PostToolUse status=delivered bytes=10351 sha256=95bca8451f1f
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

author-w01-6: w01-c6 and w01-c7 are filed, with proposed diffs and replay scripts, nothing applied or committed. Both are labelled CONJECTURE. The counts inside them are MEASURED, and every classification and counterfactual is one rater's reading.

Files (absolute paths; the Write tool did not refuse any file):
- Claim heads: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__pondus__/w01-c6.md` and `.../__pondus__/w01-c7.md`
- Puzzles: `.../__scrupuli__/wave-01-author-w01-6.md`. It has 9 puzzles and a `## symbols` section: E1–E5 (the elements of the close message), the four habit verdicts, and Y/P/N pre-emption.
- Work folder: `.../__reports__/reflective_run/w01/author-w01-6/`. It holds:
  - the diffs `c6-contract.diff`, `c6-optional-lab-status.diff`, `c7-asking-habit.diff`
  - the scripts and outputs `c6_replay.py`, `c7_replay.py`, `extract_prev.py`, `make_diffs.py`, `*_summary.txt`, `*.csv`, `prev_pi.json`
  - `diff_cost.txt` and `headless_init.jsonl`
  - All three diffs pass `git apply --check` on b497813.
- Commands, no tokens, seconds:
  - c6 full: `python3 -I extract_prev.py && python3 -I c6_replay.py > c6_summary.txt`; quick: `c6_replay.py --quick`.
  - c7 full: `python3 -I c7_replay.py > c7_summary.txt`; quick: `c7_replay.py --quick`.
  - Diffs: `python3 -I make_diffs.py`.
  - All run from the `author-w01-6` folder.
- Headless probe: one `claude -p` model call, USD 0.0714, 2.7 s.

## w01-c6 (human-facing close-message contract)

**Result.**
- Of the 55 research prompts, the contract would clearly pre-empt 1 (d10ebf86, "I don't even understand whether the hypothesis are verified") and partly pre-empt 5 (8af30fe6, 9cd91bd9, 83e43ba0, 939bea68, 3959fc84). The other 49 are decisions, new directions, button gates, process instructions or facts only the human held, and no wording changes them.
- The element that matters is the scope sentence (what a result closes, plus one thing outside it). A verdict table alone is not enough. 83e43ba0 ("maybe an artifact of this model family?") came right after a PI message that already had the question first and a hypothesis table with verdicts.
- It would not touch the headline-scope complaint at 2947f9dc:1254, because that was a slide (an artifact for outsiders), not a chat message.

**Corrections to your hunch.**
- "Never opens files" is true only of claim, puzzle and wave files, because none existed in those sessions. The human did open a findings report, the framing and the knowledge-transfer report. He opened the report because the chat message before it (about git config) carried no verdicts. That supports a chat message, not a file, as the carrier.
- Quote-replies: 12 of 55 prompts start with ">" and 13 contain a quoted line. Of the 9 corrections, 6 start with ">" and 7 contain one, so "7 of 9" holds only under the wider test.
- 0 of 55 prompts use a plugin label or verdict word.
- Cost unit: I changed USD to "the budget's own unit". In this run the human accepted a token budget ("6 M tokens ... That's reasonable"), and USD appears once, as a per-session cap (201e1cdd). The attention-hours figure comes from a scheduler prompt outside the 55.

**Supported versus extrapolated** (full table in the claim head).
- Supported: question first, plain-word verdicts, sentences that survive quoting, scope.
- Extrapolation, with no human prompt asking for it: label shown to the human, USD, a "what needs you" list, a `## For the user` block in the wave note, `/lab-status` in the same order.
- Thin: terms glossed on first use (one prompt in the 55, plus a topic-specific fork where he asked for more explanation).
- The `/lab-status` change is a separate optional diff because no human run of it is observable.

**What goes where** (`c6-contract.diff`).
- A "Tell the user" step in the wave-closing section of `waves.md`, plus a one-clause change to the final-synthesis paragraph.
- A `## For the user (at close)` block in the wave template.
- One voice sentence in `agents/research-pi.md`.

**Cost.**
- Net words: waves.md +111, wave template +37, research-pi.md +42, total +190. The optional `/lab-status` diff adds +23.
- The research-pi.md sentence is +13% of the file that is in context on every PI turn.
- Token estimates: 250–410 input tokens per session. A 355-word close message is about 460–760 output tokens, roughly 0.01% of a 6 M token budget.
- Those ranges use 1.3–2.15 tokens per word. 2.15 is the measured median over 42 PI messages and may include hidden reasoning, so I give ranges (puzzle 8).
- Leanness tension: the contract fixes order and scope, not length. The reacted-to PI messages have a median of 337 words, against a modelled contract message of 355. The human's request for MORE explanation in the fork 3ccc590f stays a chat-on-request matter.

**Headless (`claude -p` 2.1.302, MEASURED).**
- The init tool list has 30 tools and none of `mcp__ccd_turn__wrap_up`, `update_plan`, `mark_chapter` or `AskUserQuestion`. So:
  - There are no buttons, so "needs you" is text with a default that nobody can veto.
  - There is no quote-reply channel.
  - Earlier wave-close messages exist only in the transcript, which is why the same text must go into the wave note.
- `PushNotification`, `ScheduleWakeup` and `RemoteTrigger` do appear in the headless tool list. I did not call `PushNotification`.
- UNVERIFIED: what `PushNotification` does without a destination, and whether a Desktop-spawned background session carries the ccd tools.

**Design rule** ("identity in prose, no rule saying when to decide what" in `research-pi.md`).
- It respects the rule: the procedure lives in `waves.md`, which is where procedures belong, and the research-pi.md sentence is about voice.
- The ordering clause ("their question first, then ...") is borderline. If you read it as a rule, drop that one sentence and keep the `waves.md` step. Coverage then falls to messages at wave close only.

## w01-c7 (asking habit in `working_defaults.md`)

**Result.** Verdicts are CONJECTURE; counts and outcomes are MEASURED.
- Of 19 asks: 4 removed, 4 shortened, 2 at risk, 9 unchanged. Against explorer-w01-d's 6 redundant, I agree on 4 and move 2 to at-risk. Ask 5 is a write into the human's own scheduler, so the existing ask-first rule applies. Ask 14 is the "Start wave 1" ask, below.
- Of 55 prompts: 5 removed, 7 if two conditional cases hold (9.1% to 12.7%); 3 shortened; 1 at risk. Explorer-w01-d's S+W count was 12 of 55. The gap is the six waiting-artefact (W) prompts, mostly the design-gate holds, which the habit does not remove.
- Of the 6 S-class prompts: 2 removed, 2 conditional, 2 untouched (29aad9e7 and 6ee68017 are first statements, so nothing earlier exists to find).

**The 479 minutes.**
- The 479 minutes is the human's absence, not a system cost. After the click at 00:24:46 the agent had about 1.5 minutes of work in total (55 s and 48 s), separated by the human's 17-minute reply.
- The habit would remove one click and nothing else of weight.
- Across all four removable asks the person was present for 4.7 idle minutes. Of the asks counted at risk or shortened, 25.3 more minutes were with the person present.

**Design gates (the five asks).**
- All five were declined. "State the default and carry on" is wrong for them unless the PI correctly sees that the build depends on the answer.
- Three of the five repeat an earlier decline readable in his words. I count those as shortened (open prompt in place of click then question), not removed.

**Worst case: ask 14, "Start wave 1".**
- It looks redundant against "open its roadmap from v4", but the human's typed answer added that other sessions were running in the repo.
- My added first paragraph (the existing ask-first rule now also covers the person's other sessions, accounts and schedules) helps only if the PI sees that the action touches them. Nothing in the text makes it see that, so the risk stays open.
- Near miss for keyword matching: ask 0, "Try Greek", overlaps the human's earlier "Greek root or Latin", which was about method, not a choice.

**Wording changes versus your hunch.**
- "Search" became "read the last entries". For asks 13 and 17 the settling prompt ranks 30th of 39 and 47th of 55 by word overlap, with overlap 0.0. It sits 2–3 prompts back, and the whole file for 55 prompts is 2,474 words.
- "Continue independent work" became "carry on with what does not depend on the answer". 17 of 19 asks were issued with no subagent running, and `wrap_up` ends the turn.

**Cost.**
- +127 words in working_defaults.md (+49% of that file, read at every session start), about 165–280 input tokens.
- Reading the whole user-words file costs 3.2k–5.3k tokens; at 19 asks that is about 100k tokens (under 2% of the 6 M budget), and the PI already reads the last entries at session start.
- Risk of not asking when it should: the failure I can measure is the false positive (a sentence read as settling something it does not). I found one near miss and one real exposure (ask 14). A shallow read fails safe, because the PI just asks as it does today.
- A wrong rule written into the framing's "Rules for the team" propagates to every brief; the mitigation is "in their words", and the human does open the framing.

**Design rule.**
- As placed, it respects the rule. `research-pi.md` is untouched, and the text sits in `working_defaults.md`, which already holds a when-to-ask rule.
- It would break the rule if moved into `research-pi.md`.

**Headless.**
- The habit fits better there than buttons do. The default taken must be recorded where the person will see it (the c6 note).
- The "rule stated once" bullet has one prompt and nothing to carry.
- UNVERIFIED: whether the UserPromptSubmit hook fires and writes user_words.md under `-p`.

**Scope.** c6 does not close whether the contract lowers corrections in a real run. c7 does not decide where a rule that must cross labs lives (puzzle 9: the commit rule was stated in one project and repeated while building another repository).

**Caveats a verifier should probe.**
- One rater classified all 55 prompts and 19 asks. The `why` columns in `c6_replay.csv` and `c7_asks_replay.csv` are where to disagree.
- The "prompts avoided" counts depend on my settling-prompt picks for asks 13 and 17.
- The tokens-per-word range is wide (puzzle 8).

## hand-back 2 | 2026-10-19T11:57:46+09:00 | agent_id=aa70e320bd52db2dd type=murmuration:author event=PostToolUse status=delivered bytes=5171 sha256=3623f192ce46
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

author-w01-6: I answered both verifiers' questions, and the corrected counts are lower than my first report. In both claim heads a "CORRECTIONS AFTER THE EXCHANGE" block now sits at the end and is current where it disagrees with the text above it. The titles and labels (CONJECTURE) are unchanged, and I propose restatements that I did not apply, since changing what a claim states goes to the PI.

**Cause: `prompts.csv` caps `human_text` near 420 characters.**
- It cut 18 of the 55 prompts, and both verifiers caught it; I had not known.
- My word checks, rank figures and token estimates had all run on the capped text.
- I added `fulltext.py`, which reads the full prompt text from the transcripts, and re-ran everything on it.
- Five prompts have no transcript text found and keep the capped text, so word and character totals are lower bounds.
- `full_text_check.py` re-runs the word checks on the full text.

**w01-c6 after the exchange with reproducer-w01-6**
- Counts of the 55 prompts the contract might have pre-empted:

  | Reading | Prompts |
  |:--|:--|
  | Clearly | 0 |
  | Partly, if the research-pi.md voice sentence is read as applying to every message | 5 |
  | Partly, close-of-wave messages only | 3 |

- d10ebf86 reacted to the findings file, and no line of `c6-contract.diff` regulates a report file, so it moved from Y to P.
- 3959fc84 moved from P to N: a scope sentence helps only if the PI already knows what to name as outside.
- The 3 close-only prompts are 9cd91bd9, 83e43ba0 and 939bea68, using the verifier's indices. 8af30fe6 reacted to a mid-wave reply.
- Proposed restatement: "plausibly pre-empts 3 of 55 at wave close, 5 if the voice sentence applies to every message; none clearly".
- Word checks on the full text: 6 prompts name a cost word (not 4), USD appears only in 201e1cdd, and no prompt uses a plugin label or verdict word (3 ordinary-verb hits). 12 of 55 prompts start with ">", and 6 of the 9 corrections do.
- The headless probe was weaker than I claimed. Re-run with the default MCP configuration (USD 0.0865): 132 tools, 99 of them MCP, none `mcp__ccd_*`, no `AskUserQuestion`. So MEASURED now: a terminal `claude -p` 2.1.302 has neither. Whether a Desktop-spawned background session has them is UNVERIFIED.
- I dropped the ordering clause of the research-pi.md sentence at the verifier's suggestion. It now reads "You write to the person as to a colleague who reads one sentence at a time and quotes it back." The diff is +168 words net and passes `git apply --check`.

**w01-c7 after the exchange with reproducer-w01-7**

| Item | First report | Corrected |
|:--|:--|:--|
| Asks removed | 4 | 2 (asks 1 and 17; only 17 has a settling prompt) |
| Asks shortened | 4 | 4 (asks 10, 11, 13, 16) |
| Asks at risk | 2 | 2 (asks 2, 14) |
| Asks unchanged | 9 | 11 |
| Prompts removed, of 55 | 5 | 2 |
| Prompts removed, with conditional cases | 7 | 4 (3.6% to 7.3%) |
| S-class prompts removed | 2 (2 conditional) | 0 (2 conditional, 4 untouched) |

- Ask 13 moved to shortened: it bundles creating the repo with opening the roadmap from v4, a gate the human had declined three times.
- Ask 2 moved to at risk: the PI had already looked on disk, and the LM Studio folder was the human's knowledge.
- Ask 3 moved to kept: nothing shows the PI would have read the prior art unasked.
- Ask 5 moved to kept: under the diff's own first paragraph, schedules still wait for a yes.
- Finder numbers, tie-aware:

  | Item | Value |
  |:--|:--|
  | Ask 17 settling prompt rank | 4th of 55 (10 tied), overlap 0.17 |
  | Ask 13 settling prompt rank | 13th (+26 tied) of 39, overlap 0.0 |
  | Best-overlapping prompt | never the settling one (0.5 for asks 10, 11, 17) |
  | Highest overlap among KEEP and AT_RISK asks | 0.5 (ask 18) |

  I retracted "shares no content word", and word overlap is still not a reliable finder.
- Whole user-words file: at least 27,494 characters, 4,717 words, so 6.1k to 10.1k tokens per read and 117k to 193k over 19 asks. That is 2 to 3% of the 6 M budget.
- The 479 minutes still recovers only about 1.5 minutes of agent work.
- Proposed restatement, with a range: removes 1 to 2 of 19 asks and 2 to 4 of 55 prompts, shortens 4, leaves 2 at risk, does not recover the 479 minutes.

**Files, all in `__reports__/reflective_run/w01/author-w01-6/`.**
- Claim heads (`/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/`): `__pondus__/w01-c6.md`, `__pondus__/w01-c7.md`.
- Puzzles: `__scrupuli__/wave-01-author-w01-6.md`. It still has 9 puzzles; I did not add the truncation problem as a puzzle.
- New this round: `fulltext.py`, `full_text_check.py` and `full_text_check.txt`, `headless_init_default_mcp.jsonl`.
- Re-run outputs: `c6_summary.txt`, `c6_replay.csv`, `c7_summary.txt`, `c7_asks_replay.csv` (adds a `settle_ties` column), `c7_s_prompts.csv`.
- Diffs: `c6-contract.diff` (+168 words), `c6-optional-lab-status.diff` (+23), `c7-asking-habit.diff` (+127). All three pass `git apply --check`; nothing is applied or committed.
- Reproduce: `python3 -I c6_replay.py`, `python3 -I c7_replay.py`, `python3 -I make_diffs.py`, `python3 -I full_text_check.py`.
