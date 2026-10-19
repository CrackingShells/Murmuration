# Wave 02

opened: 2026-10-19

## The user's sentence this wave serves

The user answered the PI's decision questions through the Desktop question dialog (`AskUserQuestion`,
about 12:50 JST). These answers are not in `__statera__/user_words.md`, because they arrive as a
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

Budget: about 6 hours of wall time from about 12:50 JST, set by the user. In USD the PI caps this
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
| author-w02-1 | author | w02-c1: apply the measured `/lab-status` spend fix (w01-c3 + w01-c2 detector) to the shipped script | |
| author-w02-2 | author | w02-c2: apply the prompt-text rule (w01-c9) to the shipped hook; prototype AskUserQuestion capture | |
| explorer-w02-a | explorer | How a token/time budget can reach a running worker through hooks; presence gate; first look at "anxiety" | |
| explorer-w02-b | explorer | Report names vs the Write refusal; loading writing-reports; skill-listing size; subagent cache lifetime | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- Plugin changes are now applied on the study branch `claude/murmuration-system-optimization-8cff9e`
  after a claim and a verdict, per the user's 12:50 answer. Nothing goes to `main`; the user merges.

closed: YYYY-MM-DD
