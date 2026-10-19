# Wave 01

opened: 2026-10-19

## The user's sentence this wave serves

> Search how the system should optimize itself, starting mostly from the elements we considered
> adding but set aside as over-engineering for now. Each of them may come back, change shape, or
> stay out, depending on what the evidence shows.

(2026-10-19 10:56; earlier, 09:25: "run Murmuration on itself first, using the genesis study's
transcripts and files as data.")

## What does not add up

Both reviews cut v5 on the argument that its machinery served a diagnosis (carriage) that wave 1
had overturned (uptake). That argument is about the *research* failure. It says nothing about the
user's three axes: whether the team can run *on its own*, whether its behaviour and cost are
*logged*, and whether a human can *review* it. Several cut elements (the ledger SA3, the friction
hooks SA8, the SubagentStop close SA6, the questions to the human SA13) were never judged on
those axes. Meanwhile the very first minutes of this run already turned up three faults in what
shipped, all in exactly those axes: the prompt hook stored platform text as the user's words, the
lab was invisible from the worktree the app opened, and spend tracking found nothing because the
transcript sits under a different project path (S-w01-research-pi-1..3). So the cut may have
removed things that were needed and kept things that are fragile. This wave is a portfolio of cheap
probes over the transcripts to find where the evidence actually is, before any claim.

Budget for the study, set by the PI because the prompt left it open (`Budget: [state it, …]`):
about **6 M tokens of team spend over at most three waves**, wave 1 about 2.5 M (six Sonnet
explorers at about 400 k each). Proposed by the PI because the prompt left it open; confirmed by
the user at 11:04 ("That's reasonable, actually.").

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w01-a | explorer | Spend and behaviour profile per agent run from transcripts; what a ledger (SA3, SA6) would hold that post-hoc parsing cannot || yes, 299k tok, 13 min; report saved by PI from hand-back (`w01/explorer-w01-a/report.md`) |
| explorer-w01-b | explorer | Communication: briefs, hand-backs, pair messages, and what the PI did with returns (SA4, SA5, SA16; parsing of outputs) || after a 60-turn stop and resume; 317k tok; report saved by PI (`w01/explorer-w01-b/report.md`) |
| explorer-w01-c | explorer | Tools and MCP servers: reached for, lacked, failed, discovery overhead, against the allowlists (SA15, SA8) || after a 60-turn stop and resume; 296k tok; report saved by PI (`w01/explorer-w01-c/report.md`) |
| explorer-w01-d | explorer | Every human intervention: what it was, what triggered it, what the team would have needed to act alone (SA13, SA9) | after a 60-turn stop and resume; 307k tok; report saved by PI (`w01/explorer-w01-d/report.md`) |
| explorer-w01-e | explorer | Human review UX: what humans read, what confused them, established UX for reviewing agent runs (axis 3) || yes, 219k tok, 8 min; wrote `w01/explorer-w01-e/report.md` itself via Bash |
| explorer-w01-f | explorer | Platform capabilities for logging and cost now (hooks on 2.1.302, OpenTelemetry, status line, transcripts) || yes, 319k tok, 12 min; report saved by PI (`w01/explorer-w01-f/report.md`) |
| author-w01-1 | author | w01-c1: persist hand-backs by hook; stop asking workers for report files | |
| author-w01-2 | author | w01-c2: which source gives exact per-subagent spend (explorers a and f disagree) | |
| author-w01-3 | author | w01-c3: fix `/lab-status` spend (worktrees, forks, USD); hook run index or scan | |
| author-w01-4 | author | w01-c4: fix user-words capture (system-reminder blocks; worktree root) | |
| author-w01-5 | author | w01-c5: turn limits per role (3 of 6 explorers stopped at 60) | |
| author-w01-6 | author | w01-c6: human-facing report contract; w01-c7: asking habit for the PI | |

## Claims of this wave

| Claim | Statement (short) | Current label |
|:--|:--|:--|
| w01-c1 | Hand-back hook (first statement) | superseded by w01-c14 |
| w01-c2 | Per-subagent output in transcripts is exact except in `auto`/`plan` modes (and rarely otherwise); detector; OTel exact | escalated → used at MEASURED by PI decision (statement restated, see Notes) |
| w01-c3 | `/lab-status` spend: dedupe by sessionId, find worktree sessions, USD from cost-state; no hook needed (this machine, 2.1.299) | MEASURED |
| w01-c4 | User-words capture fix (first statement) | superseded by w01-c9, w01-c10 |
| w01-c5 | Turn-limit stops (first statement) | superseded by w01-c8 |
| w01-c6 | Human-facing close-message contract | below CONJECTURE: restate (verifier: none clearly pre-empted; 3 of 55 at wave close) |
| w01-c7 | Asking habit for the PI | below CONJECTURE: restate (verifier: removes 1–2 of 19 asks) |
| w01-c8 | Turn-limit stops cost no cache rewrite when resumed within ~5 min; 0 of 38 notices waited > 300 s; per-role limits (CONJECTURE) | escalated → used at MEASURED by PI decision |
| w01-c9 | User-words text rule: 72 typed prompts kept, 51 cleaned, 0 dropped | below MEASURED: restate (numbers reproduced; title broader than run) |
| w01-c10 | User-words root rule (cwd first) | below CONJECTURE: restate (regression found; Desktop unobserved) |
| w01-c11, w01-c12 | Set-aside verdict table, first two statements | superseded by w01-c13 |
| w01-c13 | Set-aside verdict table: 8 examined, SA6 back if w01-c14 holds, SA3 changed shape, 6 stay out, 9 not examined | CONJECTURE (SUPPORTED) |
| w01-c14 | Hand-back hook, headless, saves every hand-back verbatim, drafts/gaps marked; recovery aid only | MEASURED |

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|
| S-w01-author-w01-1-1 | followed: w01-c1 |
| S-w01-author-w01-1-2 | followed: w01-c1 |
| S-w01-author-w01-1-3 | followed: w01-c1 |
| S-w01-author-w01-1-4 | followed: w01-c1 |
| S-w01-author-w01-1-5 | followed: w01-c1 |
| S-w01-author-w01-1-6 | followed: w01-c1 |
| S-w01-author-w01-1-7 | parked: SA6's presence gate was not tested; no evidence for or against — open item |
| S-w01-author-w01-1-8 | parked: leanness probe (can a plugin shorten the skill listing for workers?) not run in wave 1 for budget — open item |
| S-w01-author-w01-1-9 | followed: w01-c1 |
| S-w01-author-w01-1-10 | parked: cause found (the worktree's .claude/settings.local.json is picked up by headless runs below it); cleaning the registry is the user's call — open item |
| S-w01-author-w01-1-11 | followed: w01-c1 |
| S-w01-author-w01-2-1 | followed: w01-c2 |
| S-w01-author-w01-2-2 | followed: w01-c2 |
| S-w01-author-w01-2-3 | followed: w01-c2 |
| S-w01-author-w01-2-4 | parked: cause found (the worktree's .claude/settings.local.json is picked up by headless runs below it); cleaning the registry is the user's call — open item |
| S-w01-author-w01-2-5 | followed: w01-c2 |
| S-w01-author-w01-2-6 | followed: w01-c2 |
| S-w01-author-w01-3-1 | parked: subagent prompt-cache lifetime (5 min vs 1 h for the main thread) is the reflective_run tuning target `cacheTtl`; not tested — open item |
| S-w01-author-w01-3-2 | followed: w01-c3 |
| S-w01-author-w01-3-3 | followed: w01-c3 |
| S-w01-author-w01-3-4 | followed: w01-c10 |
| S-w01-author-w01-3-5 | followed: w01-c3 |
| S-w01-author-w01-3-6 | followed: w01-c2 |
| S-w01-author-w01-3-7 | followed: w01-c3 |
| S-w01-author-w01-4-1 | followed: w01-c10 |
| S-w01-author-w01-4-2 | parked: cause found (the worktree's .claude/settings.local.json is picked up by headless runs below it); cleaning the registry is the user's call — open item |
| S-w01-author-w01-4-3 | followed: w01-c9 |
| S-w01-author-w01-4-4 | followed: w01-c9 |
| S-w01-author-w01-4-5 | followed: w01-c9 |
| S-w01-author-w01-4-6 | followed: w01-c9 |
| S-w01-author-w01-4-7 | followed: w01-c9 |
| S-w01-author-w01-4-8 | parked: leanness probe (can a plugin shorten the skill listing for workers?) not run in wave 1 for budget — open item |
| S-w01-author-w01-5-1 | followed: w01-c8 |
| S-w01-author-w01-5-2 | parked: whether maxTurns restarts on resume is not testable from transcripts; needs a probe — open item |
| S-w01-author-w01-5-3 | followed: w01-c8 |
| S-w01-author-w01-5-4 | parked: subagent prompt-cache lifetime (5 min vs 1 h for the main thread) is the reflective_run tuning target `cacheTtl`; not tested — open item |
| S-w01-author-w01-5-5 | parked: leanness probe (can a plugin shorten the skill listing for workers?) not run in wave 1 for budget — open item |
| S-w01-author-w01-5-6 | followed: w01-c8 |
| S-w01-author-w01-5-7 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-author-w01-5-8 | followed: w01-c2 |
| S-w01-author-w01-5-9 | followed: w01-c8 |
| S-w01-author-w01-6-1 | followed: w01-c6 |
| S-w01-author-w01-6-2 | followed: w01-c6 |
| S-w01-author-w01-6-3 | followed: w01-c7 |
| S-w01-author-w01-6-4 | followed: w01-c7 |
| S-w01-author-w01-6-5 | followed: w01-c7 |
| S-w01-author-w01-6-6 | followed: w01-c7 |
| S-w01-author-w01-6-7 | followed: w01-c6 |
| S-w01-author-w01-6-8 | followed: w01-c6 |
| S-w01-author-w01-6-9 | parked: where a rule that crosses labs lives (user scope vs lab framing) is a design question for the user — open item |
| S-w01-explorer-w01-a-1 | followed: w01-c2 |
| S-w01-explorer-w01-a-2 | followed: w01-c3 |
| S-w01-explorer-w01-a-3 | followed: w01-c2 |
| S-w01-explorer-w01-a-4 | followed: w01-c8 |
| S-w01-explorer-w01-a-5 | followed: w01-c3 |
| S-w01-explorer-w01-a-6 | parked: minor record-format oddities with no cost found in this study |
| S-w01-explorer-w01-b-1 | followed: w01-c13 |
| S-w01-explorer-w01-b-2 | parked: status-vs-verdict wording in hand-backs: no cost observed (the PI relayed correctly in case C) |
| S-w01-explorer-w01-b-3 | followed: w01-c1 |
| S-w01-explorer-w01-b-4 | followed: w01-c1 |
| S-w01-explorer-w01-b-5 | parked: word limits exceeded without a cost observed; no proposal |
| S-w01-explorer-w01-b-6 | followed: w01-c8 |
| S-w01-explorer-w01-c-1 | followed: w01-c13 |
| S-w01-explorer-w01-c-2 | followed: w01-c13 |
| S-w01-explorer-w01-c-3 | followed: w01-c13 |
| S-w01-explorer-w01-c-4 | followed: w01-c1 |
| S-w01-explorer-w01-c-5 | followed: w01-c8 |
| S-w01-explorer-w01-d-1 | followed: w01-c7 |
| S-w01-explorer-w01-d-2 | followed: w01-c6 |
| S-w01-explorer-w01-d-3 | followed: w01-c7 |
| S-w01-explorer-w01-d-4 | followed: w01-c7 |
| S-w01-explorer-w01-d-5 | followed: w01-c7 |
| S-w01-explorer-w01-d-6 | followed: w01-c7 |
| S-w01-explorer-w01-d-7 | followed: w01-c9 |
| S-w01-explorer-w01-d-8 | followed: w01-c7 |
| S-w01-explorer-w01-d-9 | followed: w01-c8 |
| S-w01-explorer-w01-e-1 | followed: w01-c6 |
| S-w01-explorer-w01-e-2 | followed: w01-c6 |
| S-w01-explorer-w01-e-3 | followed: w01-c3 |
| S-w01-explorer-w01-e-4 | followed: w01-c7 |
| S-w01-explorer-w01-e-5 | followed: w01-c6 |
| S-w01-explorer-w01-e-6 | followed: w01-c6 |
| S-w01-explorer-w01-e-7 | followed: w01-c6 |
| S-w01-explorer-w01-f-1 | parked: resolved: framing corrected (Desktop runs 2.1.299; CLI 2.1.302); all platform claims now name their binary |
| S-w01-explorer-w01-f-2 | followed: w01-c2 |
| S-w01-explorer-w01-f-3 | followed: w01-c9 |
| S-w01-explorer-w01-f-4 | followed: w01-c3 |
| S-w01-explorer-w01-f-5 | followed: w01-c13 |
| S-w01-explorer-w01-f-6 | followed: w01-c13 |
| S-w01-explorer-w01-f-7 | followed: w01-c13 |
| S-w01-reproducer-w01-1-1 | followed: w01-c1 |
| S-w01-reproducer-w01-1-2 | followed: w01-c1 |
| S-w01-reproducer-w01-1-3 | parked: cause found (the worktree's .claude/settings.local.json is picked up by headless runs below it); cleaning the registry is the user's call — open item |
| S-w01-reproducer-w01-1-4 | followed: w01-c1 |
| S-w01-reproducer-w01-1-5 | followed: w01-c1 |
| S-w01-reproducer-w01-1-6 | followed: w01-c1 |
| S-w01-reproducer-w01-1-7 | followed: w01-c1 |
| S-w01-reproducer-w01-1-8 | followed: w01-c1 |
| S-w01-reproducer-w01-2-1 | followed: w01-c2 |
| S-w01-reproducer-w01-2-2 | followed: w01-c2 |
| S-w01-reproducer-w01-2-3 | followed: w01-c2 |
| S-w01-reproducer-w01-2-4 | parked: handled: identifier-bearing run files untracked and local commits rebuilt (S-w01-research-pi-16); deleting runs/ is the user's call — open item |
| S-w01-reproducer-w01-2-5 | parked: cause found (the worktree's .claude/settings.local.json is picked up by headless runs below it); cleaning the registry is the user's call — open item |
| S-w01-reproducer-w01-2-6 | parked: handled: identifier-bearing run files untracked and local commits rebuilt (S-w01-research-pi-16); deleting runs/ is the user's call — open item |
| S-w01-reproducer-w01-3-1 | followed: w01-c3 |
| S-w01-reproducer-w01-3-2 | followed: w01-c3 |
| S-w01-reproducer-w01-3-3 | followed: w01-c3 |
| S-w01-reproducer-w01-3-4 | followed: w01-c3 |
| S-w01-reproducer-w01-3-5 | followed: w01-c3 |
| S-w01-reproducer-w01-4-1 | followed: w01-c9 |
| S-w01-reproducer-w01-4-2 | followed: w01-c10 |
| S-w01-reproducer-w01-4-3 | parked: auto-mode classifier refusal of a bypass launch: platform behaviour, no plugin change proposed |
| S-w01-reproducer-w01-4-4 | parked: cause found (the worktree's .claude/settings.local.json is picked up by headless runs below it); cleaning the registry is the user's call — open item |
| S-w01-reproducer-w01-4-5 | followed: w01-c9 |
| S-w01-reproducer-w01-5-1 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-reproducer-w01-5-2 | followed: w01-c8 |
| S-w01-reproducer-w01-5-3 | followed: w01-c8 |
| S-w01-reproducer-w01-5-4 | followed: w01-c8 |
| S-w01-reproducer-w01-5-5 | followed: w01-c8 |
| S-w01-reproducer-w01-6-1 | followed: w01-c6 |
| S-w01-reproducer-w01-6-2 | followed: w01-c6 |
| S-w01-reproducer-w01-6-3 | followed: w01-c6 |
| S-w01-reproducer-w01-6-4 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-reproducer-w01-6-5 | followed: w01-c6 |
| S-w01-reproducer-w01-7-1 | followed: w01-c7 |
| S-w01-reproducer-w01-7-2 | followed: w01-c7 |
| S-w01-reproducer-w01-7-3 | followed: w01-c7 |
| S-w01-reproducer-w01-7-4 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-reproducer-w01-7-5 | followed: w01-c7 |
| S-w01-reproducer-w01-7-6 | followed: w01-c7 |
| S-w01-reproducer-w01-8-1 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-reproducer-w01-8-2 | followed: w01-c8 |
| S-w01-reproducer-w01-8-3 | followed: w01-c8 |
| S-w01-reproducer-w01-8-4 | followed: w01-c8 |
| S-w01-reproducer-w01-9-1 | followed: w01-c9 |
| S-w01-reproducer-w01-9-2 | followed: w01-c9 |
| S-w01-reproducer-w01-9-3 | followed: w01-c9 |
| S-w01-reproducer-w01-9-4 | followed: w01-c9 |
| S-w01-reproducer-w01-9-5 | followed: w01-c9 |
| S-w01-reproducer-w01-9-6 | parked: auto-mode classifier denial of a transcript listing: platform behaviour, no plugin change proposed |
| S-w01-reproducer-w01-10-1 | followed: w01-c10 |
| S-w01-reproducer-w01-10-2 | followed: w01-c10 |
| S-w01-reproducer-w01-10-3 | followed: w01-c10 |
| S-w01-reproducer-w01-10-4 | followed: w01-c10 |
| S-w01-reproducer-w01-11-1 | followed: w01-c13 |
| S-w01-reproducer-w01-11-2 | followed: w01-c13 |
| S-w01-reproducer-w01-11-3 | followed: w01-c13 |
| S-w01-reproducer-w01-11-4 | parked: open-puzzle counts move as files are added; the close count is the one in this note |
| S-w01-reproducer-w01-11-5 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-reproducer-w01-11-6 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-reproducer-w01-11-7 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-reproducer-w01-11-8 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-research-pi-1 | followed: w01-c9 |
| S-w01-research-pi-2 | followed: w01-c10 |
| S-w01-research-pi-3 | followed: w01-c3 |
| S-w01-research-pi-4 | followed: w01-c8 |
| S-w01-research-pi-5 | followed: w01-c10 |
| S-w01-research-pi-6 | followed: w01-c2 |
| S-w01-research-pi-7 | parked: resolved by explorer-w01-d's definition (31 genesis, 37 design); the PI's loose count of 69 is withdrawn |
| S-w01-research-pi-8 | followed: w01-c8 |
| S-w01-research-pi-9 | parked: leanness probe (can a plugin shorten the skill listing for workers?) not run in wave 1 for budget — open item |
| S-w01-research-pi-10 | parked: cause found (the worktree's .claude/settings.local.json is picked up by headless runs below it); cleaning the registry is the user's call — open item |
| S-w01-research-pi-11 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-research-pi-12 | followed: w01-c6 |
| S-w01-research-pi-13 | followed: w01-c1 |
| S-w01-research-pi-14 | followed: w01-c10 |
| S-w01-research-pi-15 | parked: research-loop protocol proposal (claim-head versioning before verification; late PI answers; derived-table lossiness) not hardened in this study — open item |
| S-w01-research-pi-16 | parked: handled: identifier-bearing run files untracked and local commits rebuilt (S-w01-research-pi-16); deleting runs/ is the user's call — open item |

## Notes

- The worktree branch `claude/murmuration-system-optimization-8cff9e` was fast-forwarded to
  `roadmap/reflective_run` (79fb6cf) so the lab is visible here (S-w01-research-pi-2). The hook keeps writing the user's prompts to the
  main checkout; the PI copies them over verbatim with `cp` until that is fixed (S-w01-research-pi-5).

- explorer-w01-d's definition of a genuine prompt (`origin.kind == human`, not meta, not a tool
  result; reminder blocks stripped) gives 31 (genesis) and 37 (design, 28 after the fork); the PI's 69
  was a loose filter and is withdrawn (S-w01-research-pi-7).
- **Budget unit corrected.** The "6 M tokens" budget was sized on the platform's `subagent_tokens`
  figures (about 300 k per explorer), which are the size of a run's last request, not its spend
  (explorer-w01-f §3; author-w01-3 puzzle -3). It has no checkable unit. Re-stated in USD, the unit
  the user budgets in (explorer-w01-e §1.2): at 11:4x the study had spent USD 28.23 to 36.16 by
  author-w01-3's prototype reader (`lab_spend.py --root .`; ESTIMATE for this open session: list
  price, subagent output a lower bound), of which the PI is about 6.3. The same intent (three waves
  of this size) is about **USD 70 to 90 in all**. Proposed to the user; not yet confirmed.
- **PI decision on the ESCALATE of w01-c5** (reproducer-w01-5): w01-c5 is not used at its label.
  As filed it states an ESTIMATE (the 0.65–0.70 USD exposure) and an inferred TTL rule as MEASURED,
  and its Result 3 did not reproduce with its own command until fixed. The restatement the author
  asked for is filed as w01-c8 (`supersedes: w01-c5`), now 0 of 32 notices after the reproducer's
  second catch (genesis notices double-counted through the fork). w01-c8 stands or falls on
  reproducer-w01-8's verdict.
- **PI decision on the ESCALATE of w01-c8** (reproducer-w01-8): the substance reproduced; only the
  title was stale. The author's pending restatement is accepted as the statement, because the
  verifier's independent result gives exactly its figures (0 of 38 distinct worker notices over
  300 s; of 17 resumes, cold in all 7 with gap ≥ 284.9 s and warm in all 10 with gap ≤ 282.0 s;
  the 5-minute window CONJECTURE). w01-c8 is used at MEASURED with that statement; the per-role
  `maxTurns` values inside it stay CONJECTURE.
- **PI decision on the coming ESCALATE of w01-c4** (author's own proposal): split into w01-c9 (the
  text rule, MEASURED) and w01-c10 (the root rule; headless facts MEASURED, Desktop CONJECTURE),
  both `supersedes: w01-c4`. The PI added an observation for w01-c10: both prompts of this run were
  written to the main checkout's lab while the session ran in the worktree.
- **No further restatement rounds for w01-c6 and w01-c7.** Both are OVERSTATED (below CONJECTURE:
  restate). Their verifiers' own re-ratings are recorded in their verdict sections (w01-c6: none
  clearly, 3 of 55 plausibly at wave close, 5 under the broad reading). Given the remaining budget
  (spent USD 43.19 at least, ESTIMATE about 55 at 12:1x) and the small effect, they go to the user
  at their current state rather than through another author–verifier round.
- **PI decision on the ESCALATE of w01-c2** (reproducer-w01-2): the narrowed title is accepted as
  the statement, because the verifier's independent result gives its figures (detector agrees in
  199 of 199 cells; auto 29/29 and plan 10/10 inexact on output; other modes 4/160 inexact, all
  background + short final message + thinking off; 4 new runs agree; this run's real subagent files
  0 of 23 all-final). Scope stays headless haiku, one subagent at a time; the cause of the auto/plan
  truncation is not found. w01-c2 is used at MEASURED with that statement.
- **w01-c11 → w01-c12 → w01-c13** (PI's set-aside verdict table): two OVERSTATED rounds, then
  SUPPORTED on w01-c13 (reproducer-w01-11).
- **Commit hygiene:** two local commits that included 422 identifier-bearing raw run files were
  rebuilt without them (S-w01-research-pi-16); nothing was pushed.
- Token figures in the Returned column are the platform's `subagent_tokens`, which is the size of
  the last request, not spend (explorer-w01-f §3, explorer-w01-a §3); kept only as a size marker.
- My puzzle S-w01-research-pi-6 read the notification's usage block as a free ledger line. That
  reading is wrong: the block is the last request's context size (explorer-w01-f §3).
- The Write tool refused `report.md` from subagents five times (agents a, b, c, f: "Subagents should
  return findings as text, not write report files"); e and d wrote theirs through Bash heredocs
  instead. Checked in the subagent transcripts by the PI. Reports a, b, c, f were saved from the
  hand-backs with `__reports__/reflective_run/tools/save_handback.py`.

- At close: 168 open puzzles, each disposed above. Spend: USD 60.56 at least, ESTIMATE about 75.65
  (author-w01-3's `lab_spend.py`, 12:4x; open session at list price, subagent output a lower bound).

closed: 2026-10-19
