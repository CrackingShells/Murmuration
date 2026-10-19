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
| explorer-w01-d | explorer | Every human intervention: what it was, what triggered it, what the team would have needed to act alone (SA13, SA9) | |
| explorer-w01-e | explorer | Human review UX: what humans read, what confused them, established UX for reviewing agent runs (axis 3) || yes, 219k tok, 8 min; wrote `w01/explorer-w01-e/report.md` itself via Bash |
| explorer-w01-f | explorer | Platform capabilities for logging and cost now (hooks on 2.1.302, OpenTelemetry, status line, transcripts) || yes, 319k tok, 12 min; report saved by PI (`w01/explorer-w01-f/report.md`) |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- The worktree branch `claude/murmuration-system-optimization-8cff9e` was fast-forwarded to
  `roadmap/reflective_run` (79fb6cf) so the lab is visible here (S-w01-research-pi-2). The hook keeps writing the user's prompts to the
  main checkout; the PI copies them over verbatim with `cp` until that is fixed (S-w01-research-pi-5).

- Token figures in the Returned column are the platform's `subagent_tokens`, which is the size of
  the last request, not spend (explorer-w01-f §3, explorer-w01-a §3); kept only as a size marker.
- My puzzle S-w01-research-pi-6 read the notification's usage block as a free ledger line. That
  reading is wrong: the block is the last request's context size (explorer-w01-f §3).
- The Write tool refused `report.md` from subagents five times (agents a, b, c, f: "Subagents should
  return findings as text, not write report files"); e and d wrote theirs through Bash heredocs
  instead. Checked in the subagent transcripts by the PI. Reports a, b, c, f were saved from the
  hand-backs with `__reports__/reflective_run/tools/save_handback.py`.

closed: YYYY-MM-DD
