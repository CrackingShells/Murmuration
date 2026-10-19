# Wave 02

opened: 2026-10-19

## The user's sentence this wave serves

The user answered the PI's decision questions through the Desktop question dialog (`AskUserQuestion`,
12:26 JST by the transcript; the PI first wrote 12:50, corrected per author-w02-2). These answers are not in `__statera__/user_words.md`, because they arrive as a
tool result and do not fire `UserPromptSubmit` (S-w02-research-pi-1). Quoted verbatim from the
tool result in this run's transcript:

> You are supposed to decide that based on experiment on the new architecture. or based on the
> logging you will be able to measure. This should be an informed decision. Although, something I
> can say is that:
> - P6 is strange. Your system is reasoning based on budget. So rather than a max turn, the unit is
>   token or time budget and that can be given to the agent through regular hooks without
>   triggering context or deadline anxiety
> - P1's direction to drop reports as deliverable is possible, why not. But I find it strange and
>   dangerous: after all, until now, reports had been the only way for agents to pass on, in a
>   structured repeatable format, findings, observations, notice, knowledge transfers, test
>   definitions, etc.. that's the point of using skills is that it standardizes agent's activity
>   (in this case the research activity).

> [Human-facing changes:] Neither for now

> I am updating the available budget: I will be gone for the next 6h. You can proceed and work on
> optimizing yourself until then.

## What does not add up

Wave 1 measured what shipped, mostly against transcripts of a pre-Murmuration study, and proposed
fixes that were checked one by one. None of them has run together in a lab, so whether the fixed
system is better in use is unmeasured. The user asks for that: decide from an experiment on the
new architecture, using the logging it can measure. Two of wave 1's directions are also wrong
against the user's reading:
- The worker limit is turns, while the lab reasons in budget (tokens or time). A budget given to
  the agent through hooks may replace `maxTurns`, if it can be done without causing anxiety. This
  is SA5 (SubagentStart injection) coming back in a new shape, and it is untested.
- The fix for refused report files drops structured reports. The user wants reports kept as the
  standard deliverable. The refusal covers only basenames starting REPORT, SUMMARY, FINDINGS or
  ANALYSIS (w01-c14), and the round-versioned report names of the writing-reports convention
  (`NN-<type>_vN.md`) start with digits, so they may pass untouched. Not tested.

Budget: about 6 hours of wall time from about 12:30 JST, set by the user. In USD the PI caps this
wave at about 60 more (study total about 135) and checks spend at each phase.
[assumption: the user gave hours, not USD; the cap keeps the wave at the size of wave 1]

## Plan (phases; each one a set of dispatches)

- A (parallel): apply the two measured fixes on this branch: `/lab-status` spend (w01-c3 plus the
  w01-c2 detector) and the prompt-text rule (w01-c9). Probe the platform for budget delivery by
  hook. Probe report naming against the Write refusal. Probe the skill listing and the subagent
  cache lifetime (O4, O5).
- B: build the budget mechanism and the report convention from what A finds.
- C: run a small real study with the changed plugin in a scratch lab outside this worktree, in
  `auto` permission mode, and measure it with the lab's own logging: spend per agent and whether
  it is exact, reports delivered and their format, budget notices and how agents reacted, stranded
  runs, the prompt record.
- D: decide what lands on the branch from C's measurements; write the synthesis.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| author-w02-1 | author | w02-c1: apply the measured `/lab-status` spend fix (w01-c3 + w01-c2 detector) to the shipped script | yes; landed as 2b8dda9 (SUPPORTED) |
| author-w02-2 | author | w02-c2: apply the prompt-text rule (w01-c9) to the shipped hook; prototype AskUserQuestion capture | yes; landed as 9b96ac0 (SUPPORTED) |
| reproducer-w02-1 | reproducer | verify w02-c1 | SUPPORTED |
| reproducer-w02-2 | reproducer | verify w02-c2 | SUPPORTED |
| explorer-w02-a | explorer | How a token/time budget can reach a running worker through hooks; presence gate; first look at "anxiety" | yes; USD 0.78, 82 headless haiku runs; wrote `00-findings_v0.md` itself (Write allowed) |
| explorer-w02-b | explorer | Report names vs the Write refusal; loading writing-reports; skill-listing size; subagent cache lifetime | after a 60-turn stop and resume; USD 0.26 |
| author-w02-3 | author | w02-c3: ship the budget hook (USD, 80% note, 100% stop) and the hand-back saver with a deny-once report check; later w02-c5, w02-c6, and the switch-off | yes; w02-c3 superseded by w02-c5; w02-c5 and w02-c6 SUPPORTED; budget part switched off (b14130f) |
| author-w02-4 | author | w02-c4: report templates in research-loop; workers without `Skill`; maxTurns as fallback 150; later w02-c10 | yes; w02-c4 OVERSTATED (restate); w02-c10 ESCALATE, decided below |
| reproducer-w02-3 | reproducer | verify w02-c3 | OVERSTATED; restated as w02-c5 |
| reproducer-w02-4 | reproducer | verify w02-c4 | SUPPORTED, then OVERSTATED with `changed_by:` |
| reproducer-w02-5 | reproducer | verify w02-c5 | SUPPORTED |
| reproducer-w02-6 | reproducer | verify w02-c6 | SUPPORTED |
| explorer-w02-c | explorer | measure arms A, B, B2, B3, B4 by the pre-registered metrics (`w02/explorer-w02-c/`) | yes; four findings reports |
| reproducer-w02-7 | reproducer | verify w02-c7 (README headless note; PI-authored) | OVERSTATED; head restated by PI decision |
| reproducer-w02-8 | reproducer | verify w02-c8 (the experiment; PI-authored) | OVERSTATED; head restated by PI decision; its finding switched the budget hook off |
| author-w02-1 (resumed) | author | w02-c9: `/lab-status` reads a verifier's latest verdict | yes; landed as b396fd1 |
| reproducer-w02-9 | reproducer | verify w02-c9 | SUPPORTED |
| reproducer-w02-10 | reproducer | verify w02-c10 | ESCALATE; narrowed by PI decision, landed as d4fb928 |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|
| w02-c1 | `/lab-status` spend in USD, every session of the lab, each message once | MEASURED |
| w02-c2 | prompt hook keeps only the user's text | MEASURED |
| w02-c3 | budget and hand-back hooks, first filing | superseded by w02-c5 |
| w02-c4 | report template, workers without `Skill`, `maxTurns` 150 | below MEASURED: restate |
| w02-c5 | budget notes obeyed in probes; hand-backs saved verbatim; deny-once report request | MEASURED (budget part switched off by the experiment rule) |
| w02-c6 | time budget on the same path; reaches background workers | MEASURED (switched off with the budget) |
| w02-c7 | README note on the headless background ceiling | below MEASURED: restate; head restated by PI decision |
| w02-c8 | the five-arm experiment | below MEASURED: restate; head restated by PI decision |
| w02-c9 | `/lab-status` reads the latest verdict | MEASURED |
| w02-c10 | spend figures only from the harness or `/lab-status` | escalated; MEASURED for the narrowed statement by PI decision |

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|
| S-w02-author-w02-1-1 | followed: w02-c1 |
| S-w02-author-w02-1-2 | followed: w02-c1 |
| S-w02-author-w02-1-3 | parked: accepted cost: the reader is +203 lines for exact USD and worktree discovery; leanness weighed in w02-c1 |
| S-w02-author-w02-1-4 | parked: decided: no uplift estimate and no wake-ups column; the lower-bound mark is enough |
| S-w02-author-w02-1-5 | parked: listed for the user as an open item in __statera__/synthesis.md |
| S-w02-author-w02-1-6 | parked: minor display question; no evidence of confusion |
| S-w02-author-w02-1-7 | parked: resolved: commits were staged by name |
| S-w02-author-w02-2-1 | parked: resolved: the wave note now says 12:26 |
| S-w02-author-w02-2-2 | parked: listed for the user as an open item in __statera__/synthesis.md |
| S-w02-author-w02-2-3 | followed: w02-c2 |
| S-w02-author-w02-2-4 | followed: w02-c2 |
| S-w02-author-w02-2-5 | parked: listed for the user as an open item in __statera__/synthesis.md |
| S-w02-author-w02-3-1 | followed: w02-c5 |
| S-w02-author-w02-3-2 | followed: w02-c5 |
| S-w02-author-w02-3-3 | followed: w02-c5 |
| S-w02-author-w02-3-4 | followed: w02-c5 |
| S-w02-author-w02-3-5 | parked: resolved: the budget hook is switched off (b14130f), so it no longer starts on main-thread calls |
| S-w02-author-w02-3-6 | followed: w02-c5 |
| S-w02-author-w02-3-7 | followed: w02-c5 |
| S-w02-author-w02-3-8 | followed: w02-c5 |
| S-w02-author-w02-3-9 | followed: w02-c5 |
| S-w02-author-w02-3-10 | followed: w02-c5 |
| S-w02-author-w02-3-11 | parked: budget overrun of USD 0.02 noted; no action |
| S-w02-author-w02-3-12 | followed: w02-c6 |
| S-w02-author-w02-3-13 | followed: w02-c6 |
| S-w02-author-w02-4-1 | followed: w02-c4 |
| S-w02-author-w02-4-2 | parked: listed for the user as an open item (hand-backs repeat the report) in __statera__/synthesis.md |
| S-w02-author-w02-4-3 | parked: no guard on the Write tool is proposed, so heredoc writes do not matter |
| S-w02-author-w02-4-4 | followed: w02-c5 |
| S-w02-author-w02-4-5 | followed: w02-c8 |
| S-w02-author-w02-4-6 | followed: w02-c10 |
| S-w02-author-w02-4-7 | followed: w02-c10 |
| S-w02-explorer-w02-a-1 | followed: w02-c5 |
| S-w02-explorer-w02-a-2 | followed: w02-c5 |
| S-w02-explorer-w02-a-3 | followed: w02-c5 |
| S-w02-explorer-w02-b-1 | followed: w02-c4 |
| S-w02-explorer-w02-b-2 | followed: w02-c4 |
| S-w02-explorer-w02-b-3 | followed: w02-c8 |
| S-w02-explorer-w02-c-1 | followed: w02-c8 |
| S-w02-explorer-w02-c-2 | followed: w02-c8 |
| S-w02-explorer-w02-c-3 | followed: w02-c8 |
| S-w02-explorer-w02-c-4 | parked: listed for the user as an open item (proof files in __pondus__ read as claims) in __statera__/synthesis.md |
| S-w02-explorer-w02-c-5 | followed: w02-c7 |
| S-w02-explorer-w02-c-6 | followed: w02-c10 |
| S-w02-explorer-w02-c-7 | parked: listed for the user as an open item (hook silent at three tool results in B4) in __statera__/synthesis.md |
| S-w02-explorer-w02-c-8 | followed: w02-c8 |
| S-w02-reproducer-w02-1-1 | followed: w02-c1 |
| S-w02-reproducer-w02-1-2 | followed: w02-c1 |
| S-w02-reproducer-w02-1-3 | followed: w02-c1 |
| S-w02-reproducer-w02-1-4 | parked: expected: an open session's figure grows while it runs |
| S-w02-reproducer-w02-1-5 | parked: process note: author addenda after a verdict are marked as such |
| S-w02-reproducer-w02-2-1 | followed: w02-c2 |
| S-w02-reproducer-w02-2-2 | followed: w02-c2 |
| S-w02-reproducer-w02-2-3 | followed: w02-c2 |
| S-w02-reproducer-w02-2-4 | followed: w02-c2 |
| S-w02-reproducer-w02-2-5 | parked: process: claim heads edited after an independent result; see S-w01-research-pi-11 (open item) |
| S-w02-reproducer-w02-3-1 | followed: w02-c5 |
| S-w02-reproducer-w02-3-2 | followed: w02-c5 |
| S-w02-reproducer-w02-3-3 | followed: w02-c5 |
| S-w02-reproducer-w02-3-4 | parked: resolved: quick runs now write summary_quick.tsv |
| S-w02-reproducer-w02-3-5 | parked: resolved: the hashes and commit are recorded in w02-c5 |
| S-w02-reproducer-w02-3-6 | followed: w02-c5 |
| S-w02-reproducer-w02-4-1 | followed: w02-c4 |
| S-w02-reproducer-w02-4-2 | followed: w02-c4 |
| S-w02-reproducer-w02-4-3 | followed: w02-c4 |
| S-w02-reproducer-w02-4-4 | parked: process: late answers from authors; see S-w01-research-pi-15 (open item) |
| S-w02-reproducer-w02-4-5 | parked: process: late answers from authors; see S-w01-research-pi-15 (open item) |
| S-w02-reproducer-w02-4-6 | followed: w02-c8 |
| S-w02-reproducer-w02-5-1 | followed: w02-c5 |
| S-w02-reproducer-w02-5-2 | followed: w02-c5 |
| S-w02-reproducer-w02-5-3 | followed: w02-c5 |
| S-w02-reproducer-w02-5-4 | followed: w02-c5 |
| S-w02-reproducer-w02-5-5 | parked: resolved: the evidence files were committed after the verdict (bb7f2ce) |
| S-w02-reproducer-w02-6-1 | followed: w02-c6 |
| S-w02-reproducer-w02-6-2 | followed: w02-c6 |
| S-w02-reproducer-w02-6-3 | followed: w02-c6 |
| S-w02-reproducer-w02-6-4 | followed: w02-c6 |
| S-w02-reproducer-w02-6-5 | followed: w02-c6 |
| S-w02-reproducer-w02-7-1 | followed: w02-c7 |
| S-w02-reproducer-w02-7-2 | followed: w02-c7 |
| S-w02-reproducer-w02-7-3 | followed: w02-c7 |
| S-w02-reproducer-w02-8-1 | followed: w02-c8 |
| S-w02-reproducer-w02-8-2 | followed: w02-c8 |
| S-w02-reproducer-w02-8-3 | followed: w02-c8 |
| S-w02-reproducer-w02-8-4 | followed: w02-c8 |
| S-w02-reproducer-w02-8-5 | followed: w02-c8 |
| S-w02-reproducer-w02-9-1 | parked: listed for the user as an open item (a verdict rule keyed on changed_by) in __statera__/synthesis.md |
| S-w02-reproducer-w02-9-2 | parked: resolved: the PI's briefs now say 'last' |
| S-w02-reproducer-w02-9-3 | parked: listed for the user as an open item (verdict template wording) in __statera__/synthesis.md |
| S-w02-reproducer-w02-10-1 | followed: w02-c10 |
| S-w02-reproducer-w02-10-2 | followed: w02-c10 |
| S-w02-reproducer-w02-10-3 | followed: w02-c10 |
| S-w02-research-pi-1 | parked: listed for the user as an open item (AskUserQuestion capture: prototype in w02-c2, Desktop test needed) in __statera__/synthesis.md |
| S-w02-research-pi-2 | followed: w02-c7 |
| S-w02-research-pi-3 | followed: w02-c9 |

Also: `__scrupuli__/wave-02-explorer-w02-b.md` has a puzzle under the heading "What used my 60 turns", which `/lab-status` does not track. It was read: it is the 60-turn stop that w02-c4 answers (`maxTurns` 150, lean workers).

## Notes

- **Experiment, arms A and B (14:45 JST; measured by explorer-w02-c, `w02/explorer-w02-c/00-findings_v0.md`).**
  Decisions by the pre-registered rules:
  - w02-c4 (report template, lean workers): **lands**. Worker first-request context is 42–44% smaller
    at every role (A 23.6–23.9k, B 13.3–13.8k tokens). Both explorer reports sit at the convention path
    with the template's front-matter keys and its six headings in order. The PI reads "template's
    shape" as the required headings in order, extra headings allowed; that is a reading, stated here.
  - Hand-back saver (part of w02-c5): **lands**. 18 of 18 murmuration hand-backs were saved; the
    built-in web-fetch agent's hand-back was saved too.
  - Deny-once check: not exercised (0 denies; both explorers wrote the report first). It stays on
    the strength of w02-c5's probe cells (13 of 13).
  - Budget note and stop: **undecided at real B**. No note or stop fired; the highest use was 0.28 B.
    The defaults (1.5–3 USD) are 3.5 to 150 times what the workers spent per run.
  - Outcome: no regression. B's synthesis is correct by brute force; A's mathematics is correct too,
    but A wrote no synthesis because the platform's 10-minute background ceiling killed its
    wave-2 explorer (S-w02-research-pi-2).
  - Not deciding at n = 1: B cost USD 6.47 against 4.88 and took 4540 s against 1269 s; 65% of B's
    wall time is one explorer (2956 s at 0.28 B).
  What does not add up: the spend budget never bound, while elapsed time did twice (A's explorer cut
  at the ceiling; B's explorer ran 49 min on a quarter of its budget). The user named "token or time
  budget". Next: add a time budget on the same note/stop path (w02-c6), then a second candidate run
  (arm B2) to see the mechanism fire in a real study.
- **PI decision on the ESCALATE of w02-c10** (reproducer-w02-10): the narrowed statement is
  accepted (the one self-reported spend in B3 was the platform's session-wide counter read as the
  worker's own; the PI quoted it). The 47-word text lands: it can only make reported spend more
  accurate; its effect is untested.
- **PI decision on the ESCALATE of w02-c8/w02-c2-style restatements** applies only where the
  verifier's own independent result gives the restated figures.
- **PI decision on w02-c7 and w02-c8** (both OVERSTATED, PI-authored): each head is restated to
  the statement its verifier's own independent result supports (ad73b5b). They are not re-verified;
  the synthesis states them as "below MEASURED: restate; restated by PI decision".
- **Budget hook switched off (b14130f).** reproducer-w02-8 found that, by the rule as written, the
  budget hook does not land: it fired only in B4 (USD 0.05), where both noticed workers delivered but
  ended at 3.0 and 2.4 B by the hook's estimate (about 3.8 B exact), past the 1.2 B limit; at real
  budgets it never fired. Earlier the PI had kept it on as "insurance"; that was a judgement outside
  the pre-registered rule and is reverted. `scripts/budget.py` stays, unregistered; reverting one
  commit switches it back on. The hand-back saver and the deny-once report request stay on.
- **Spend.** Wave 2 cost about USD 78 against the PI's own cap of about 60 (`/lab-status` at 16:41:
  study sessions USD 114 at least; plus about 32 for headless runs outside the repository). The
  overrun is disclosed in the synthesis.
- Plugin changes are now applied on the study branch `claude/murmuration-system-optimization-8cff9e`
  after a claim and a verdict, per the user's 12:26 answer. Nothing goes to `main`; the user merges.

closed: 2026-10-19
