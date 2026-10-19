## S-w01-explorer-w01-f-1
The Desktop app that runs the PI's sessions is Claude Code 2.1.299 (`CLAUDE_CODE_EXECPATH=.../claude-code/2.1.299/...`; every record of this run's transcript says `version 2.1.299`), while `claude` on PATH is 2.1.302 and the framing says "now 2.1.302". All my headless probes ran 2.1.302. Every platform claim of this wave, mine and the probe report's (2.1.296), is therefore about a binary other than the one the team actually runs on. Nothing tested whether payload fields or the OpenTelemetry route differ between .299 and .302, or whether the Desktop app honours OTEL variables in `~/.claude/settings.json`.
refs: `env | grep CLAUDE_CODE_EXECPATH` in the explorer's shell; `__reports__/reflective_run/w01/explorer-w01-f/scratch/run1/stdout.jsonl` (init event, `claude_code_version`); transcript `ab96c5ed-....jsonl` field `version`

## S-w01-explorer-w01-f-2
`PostToolUse(Agent).totalTokens`, stream `task_notification.usage.total_tokens` and OTel `subagent_completed.total_tokens` are all the footprint of the subagent's last request, not its spend (foreground run7: 33,350 reported against 94,499 input-side tokens actually used; 0.35). The probe report (row 18) and the v5 design ("PostToolUse(Agent) gives tokens for the ledger") read it as run telemetry. If any ledger or `/lab-status` figure were built on it, per-agent spend would be understated by a factor of 2 to 3, silently.
refs: `scratch/run7/hooks.jsonl` (PostToolUse Agent record), `scratch/run7` subagent transcript summed by `ledger_from_transcript.py`; `scratch/run3/otlp_parsed.json` (subagent_completed vs api_request rows); `__reports__/platform_probes/01-findings_v1.md` row 18

## S-w01-explorer-w01-f-3
The `<system-reminder>` text that the hook stored as the user's words is not only the worktree notice: in 49 of 80 human-origin turns across five transcripts of this user's sessions (linked-session notices, fork notices, worktree notice) the same kind of block sits as a separate first text block, always exactly two blocks. The hook payload gives no origin field and concatenates the blocks, and at `UserPromptSubmit` time the current prompt's record is not yet in the transcript. So `user_words.py` as shipped will record "Linked sessions now (status, not an instruction)..." on most turns of any linked session, not just once.
refs: `scratch/run4/ups.jsonl` (hook-time and Stop-time views); `__statera__/user_words.md` entry 2026-10-19 10:56; the scan output is in the report section 5 (reminder kinds 32/13/2/1/1)

## S-w01-explorer-w01-f-4
The only whole-session cost number with a per-model split (`cost-state` in the transcript; genesis study: USD 95.62, Opus 58.77, Sonnet 30.59, Fable 6.24, Haiku 0.02, wall 22.1 h of which API 3.4 h and tools 1.7 h) is written at session close, undocumented, and a live session has none. A Fable model line (6.24 USD, 36.8k output tokens) appears in a study the framing describes as Opus PI plus Sonnet workers; I did not find which agent used it.
refs: `~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/566fa912-7009-421a-9d79-11145e2b8db9.jsonl` lines 2146 and 2148 (`type: cost-state`)

## S-w01-explorer-w01-f-5
A default-enabled built-in plugin `cc-plugin-telemetry@builtin` (with hooks) is loaded in every session next to `cc-plugin-sec-default`, `cc-plugin-agents-md`, `cc-plugin-plugin-authoring`. I could not find what it logs or where. If it already writes session or agent telemetry locally, a lab ledger might be duplicating it; if it sends it elsewhere, a lab ledger is the only local copy.
refs: `scratch/run1/stdout.jsonl` line 4 (`plugins`); `scratch/run3/otlp_parsed.json` (`plugin_loaded`, `has_hooks: true`)

## S-w01-explorer-w01-f-6
Asynchronous command hooks behave differently at the end of `claude -p`: an async `Stop` hook that took 3 s never wrote its file, while an async `SessionEnd` hook wrote 2.5 s after the process had exited. Reproducer or verifier runs launched headless (and the probes' own `-p` runs) end inside this window, so "async: true so logging stays off the critical path" loses records in exactly the runs a logger most needs to see, and the loss is silent.
refs: `scratch/run5/` (`async_stop.txt` absent; `slow_sessionend.txt` 1792375684.12 vs `end.txt` 1792375681.63)

## S-w01-explorer-w01-f-7
`PostToolUseFailure` for `ls /nonexistent_dir_xyz` reports `duration_ms: 6239` for a command that fails instantly, while the sibling background subagent was running; and the main transcript's `totalToolDuration` for the whole run was 10.3 s. I could not tell whether `duration_ms` includes waiting on a lock, a sandbox start, or the concurrent subagent. If per-tool `duration_ms` is going to be the friction signal (SA8), its meaning under concurrency is unknown.
refs: `scratch/run1/hooks.jsonl` (PostToolUseFailure record); `scratch/run1/stdout.jsonl` result `duration_ms`
