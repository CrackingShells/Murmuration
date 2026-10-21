## S-w07-explorer-w07-f-1
The user's `-p` run and the platform's own startup code disagree about which managed file binds, and nobody has read `/status`. The server-managed cache `~/.claude/remote-settings.json` holds one key (`channelsEnabled`), and per the binary's first-wins rule that alone drops `managed-settings.json`. If true, the user's sudo-created file protects nothing on this account, and so does any future managed key put there. The wave-6 check read "this machine has managed settings" as success. The debug log's raw output is not on disk, so the line that names the source was never read.
refs: __reports__/wave-07/explorer-w07-f/binary_excerpts.md (patterns `managedSourcesBehavior:`, `function wr(`, `Ze=[`); ~/.claude/remote-settings.json (keys only); __reports__/wave-06/research-pi/managed_setting_check.md

## S-w07-explorer-w07-f-2
The transcript says bypass was active (field plus the platform's own reminder to the model) but the run made no tool call, so "did it skip permission checks" has still never been observed. Every statement in the lab on this (the guard stopped 21 of 21 runs; the setting did not stop one) rests on a label or a reminder, not on a refused or an executed tool call under the setting.
refs: ~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-blissful-villani-34edd8/3c5c3eec-45b8-4ffb-a8c7-1a9c17ac12e5.jsonl records 6, 13, 29; test 2 in __reports__/wave-07/explorer-w07-f/00-findings_v0.md

## S-w07-explorer-w07-f-3
Whether the user record is on disk when UserPromptSubmit fires decides if the proposed origin rule works on the first prompt of a session, which is exactly the spawned-session case. Creation time precedes the hook's start (n = 2, 0.2 s and 0.9 s), flush time is unknown, and `user_words.py`'s own docstring says the first prompt may come before any record is on disk (that was about the `cwd` record). A one-event probe hook logging "record with prompt_id found?" would settle it, and it needs a registered hook, which no worker may add to settings.
refs: __reports__/reflective_run/w04/author-w04-4/derived/recorded_payloads_rec1.jsonl (rows 1-2); scripts/user_words.py `session_cwd` docstring; __reports__/wave-07/explorer-w07-f/00-findings_v0.md (rule section)

## S-w07-explorer-w07-f-4
`user_words.md` also holds the user's `!`-commands (`<bash-input>sudo ...`, with the password prompt and stdout) as "words", and the user's own `-p` prompt ("say ok", `sdk-cli`). The first is origin human, the second sdk. Neither is a prompt to the lab, yet the file says "Prompts as the user typed them". The sudo entries sit in a committed file; no credential is in them (the password prompt text only), but the rule for what belongs there is not written down.
refs: __statera__/user_words.md lines 269-285; __reports__/wave-07/explorer-w07-f/words_vs_origin.txt
