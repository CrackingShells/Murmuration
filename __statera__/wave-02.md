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
| author-w02-3 | author | w02-c3: ship the budget hook (USD, 80% note, 100% stop) and the hand-back saver with a deny-once report check | |
| author-w02-4 | author | w02-c4: report templates in research-loop; workers without `Skill`; maxTurns as fallback 150 | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

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
- Plugin changes are now applied on the study branch `claude/murmuration-system-optimization-8cff9e`
  after a claim and a verdict, per the user's 12:50 answer. Nothing goes to `main`; the user merges.

closed: YYYY-MM-DD
