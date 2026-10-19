## S-w01-reproducer-w01-4-1
The claim's "87 typed prompts" counts records copied into forked sessions: 82e8a947 and 3ccc590f repeat the first records of 566fa912 (same uuid, same line number, same text). Distinct typed prompts are 72 (51 differ, not 52). Any per-prompt count over the four combinatorics transcripts, by any author, may have the same inflation; does every wave-01 number that sums over the transcripts dedupe forks?
refs: __reports__/reflective_run/w01/reproducer-w01-4/myreplay.py (run with and without --nodedupe)

## S-w01-reproducer-w01-4-2
The `cwd` the hook payload carries seems to be the Bash tool's live working directory, not the session's start directory: in this run's transcript 49 of 439 records carry the main checkout's path after one Bash call that did `cd`; in my headless probe the payload cwd moved with `cd sub`. A lab-resolving rule built on `cwd` then depends on where an agent's shell happens to sit when the human types. Is there a documented field that holds the session's own root, and what does the Desktop send?
refs: __reports__/reflective_run/w01/reproducer-w01-4/probe/dump.jsonl; ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl lines 66-144

## S-w01-reproducer-w01-4-3
A headless `claude -p --permission-mode bypassPermissions` launch was refused by the auto-mode classifier here, while the same probe with a narrow `--allowedTools` list ran and cost USD 0.017. The author's cases.sh and drive.py use bypassPermissions. A reproducer in another permission setup may be unable to re-run them as written. Should probe scripts for this lab prefer a narrow allowlist?
refs: __reports__/reflective_run/w01/reproducer-w01-4/probe/drive6.py vs __reports__/reflective_run/w01/author-w01-4/probe/drive.py

## S-w01-reproducer-w01-4-4
`~/.claude/plugins/installed_plugins.json` changed during my run, but only with entries for other agents' project paths (author-w01-1, author-w01-2). With several agents running `claude -p` at once the file cannot show what one run changed. Is it worth a per-agent canary (hash before, list of added projectPaths after) or is this file's drift a known cost of every headless run?
refs: __reports__/reflective_run/w01/reproducer-w01-4/probe/installed_plugins.before.json

## S-w01-reproducer-w01-4-5
Pasted text is unwrapped before the lab-command and bare-command tests, so a paste that begins with `/lab ...` or `/something` is skipped, and a user who pastes a single slash command word loses it from the words file. Not in any of the five transcripts; is it worth an order change (test the command on the typed text before the unwrap)?
refs: __reports__/reflective_run/w01/reproducer-w01-4/adversarial.py (case "paste wrapper, content = lab cmd")
