## S-w01-author-w01-4-1
The Desktop session of this run has process cwd = the worktree, `--add-dir=<main checkout>`, no CLAUDE_PROJECT_DIR in the process environment (ps -E on CLAUDE_PID), and a transcript whose every record says cwd = the worktree. Headless runs that copy those facts (cases 1, 2, 4, with the Desktop's own 2.1.299 binary) give CLAUDE_PROJECT_DIR = the worktree, not the main checkout. Yet both prompts landed in the main checkout. Only the "start in the repository, then enter the worktree" route (cases 5/6) reproduces the signature, and I could not show the Desktop does that. What the Desktop payload's `cwd` holds is therefore unknown, and the claim's root fix depends on it.
refs: __reports__/reflective_run/w01/author-w01-4/probe/cases.sh (cases 1-6); /Users/hacker/Documents/src/CrackingShells/Murmuration/__statera__/user_words.md entries 10:56, 11:04; `ps -ww -E -p $CLAUDE_PID`

## S-w01-author-w01-4-2
`claude -p` in a scratch directory leaves a trace in the user's `~/.claude/plugins/installed_plugins.json`: one `local`-scope install entry per project path, for murmuration@murmuration-local (the file lists the explorers' `scratch/run*/work` folders and author-w01-1/-2 run folders, all stamped within minutes of those runs). My runs in the scratchpad (`wt/main`, `wt/wtA`, `demo_repo`, worktrees under `wt/main/.claude/worktrees/`) very likely added more; I did not re-check. Headless probes by the team write into the user's global plugin registry, and the entries point at paths that are then deleted.
refs: ~/.claude/plugins/installed_plugins.json (key murmuration@murmuration-local); explorer-w01-f scratch/run*/work; this author's probe/cases.sh

## S-w01-author-w01-4-3
`origin` in the transcript means different things on different surfaces. Desktop: typed prompts have `origin.kind: human` and `turnOrigin: human`. Headless stream-json input: `origin` null, `promptSource: sdk`, `turnOrigin: sdk`, the same null as the platform's own "finished a turn" notices. So no transcript rule that keys on `origin` can serve both the Desktop and the headless runs a lab also has (reproducer and verifier runs). Does the research loop want "the user's words" to include what a headless caller sends?
refs: __reports__/reflective_run/w01/author-w01-4/probe/demo_output.txt (Stop prototype wrote nothing); explorer-w01-f scratch/run4/ups.jsonl (`turnOrigin: sdk`)

## S-w01-author-w01-4-4
A prompt sent while a turn runs (a steering message) is a first-class UserPromptSubmit event with the turn's own `prompt_id`, but the transcript keeps it as an `attachment` of type `queued_command`, not as a `user` record. Anyone counting the user's prompts from `user` records misses 13 of 87 (15%) in these transcripts. This probably also touches S-w01-research-pi-7 (69 vs 28 human prompts in 82e8a947) and explorer-w01-d/-e counts: whose count includes `queued_command`?
refs: __reports__/reflective_run/w01/author-w01-4/replay_rows.tsv (class human_midturn); probe case7 (see probe/cases.sh); explorer-w01-e prompts_82e8a947.json

## S-w01-author-w01-4-5
Prompts that are not the human's still fire the hook and are stored by the shipped rule: 5 scheduled prompts ("Check-in on the v8 banyan ca…", `turnOrigin: scheduled`, no wrapper, reproduced with a one-minute cron in a headless run) and a session-start brief from a parent session ("Task (from the session that started this one)…", origin null). A text rule cannot see either. Are these "the user's words"? A scheduled prompt is usually written by an agent from a user's request; the brief is another session's text.
refs: __reports__/reflective_run/w01/author-w01-4/replay_rows.tsv (class scheduled, platform_notice); probe/demo_output.txt (CRON-TICK stored)

## S-w01-author-w01-4-6
The platform keeps adding wrapper tags in front of typed text: I found `<system-reminder>`, `<artifact-view-context artifact=…>` (with a viewer-state JSON and a disclaimer saying it was "not typed by the user"), `<side-sessions-event>`, `<pasted_content id=…>` and an `<!-- attach: Artifacts -->` page-quote block (kept by my rule; one turn is a page-sent request, 81d948, whose text the user did not type but did trigger). Four tags in five transcripts suggests the list is not closed. The disclaimer inside the artifact block is the only place where the platform says what is not the user's; there is no field.
refs: ~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/2947f9dc-1c3a-452b-97a5-39d4510a1271.jsonl (promptId prefixes 81d948, e6255f); replay_rows.tsv column reason

## S-w01-author-w01-4-7
The reminder blocks were counted by explorer-w01-f as 49 of 80 "human-origin turns"; my count is 49 of 74 human user records (the numerator agrees) plus 3 of 13 mid-turn prompts. I could not reproduce his denominator of 80 from `origin.kind == human` (74) or from adding the 9 null-origin notices (83). Small, but the two scripts disagree on what a turn is.
refs: __reports__/reflective_run/w01/author-w01-4/replay_rows.tsv; __reports__/reflective_run/w01/explorer-w01-f/report.md §5 item 4

## S-w01-author-w01-4-8
The skills listing (about 12k tokens) was appended to the result of many Bash calls in this run, not only at session start. My run used roughly 280k of the 300k budget mostly on that repeated text: about 20 reminder copies. Is the listing re-injected whenever a tool result follows a changed skill set, and can a hook or setting stop it? If it is the platform's per-turn reminder, then every agent pays it on every call, and the cost belongs in the SA3 ledger as its own line.
refs: this agent's transcript (subagent of ab96c5ed), the tool results after the Bash calls that wrote files under __reports__/reflective_run/w01/author-w01-4/
