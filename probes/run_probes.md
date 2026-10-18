# Probe runs: the exact commands and prompts

Claude Code 2.1.296 (`claude --version`), macOS, 2026-10-18. Probe plugin: `probes/plugin`, loaded with
`--plugin-dir` for one session only; nothing is installed and no global setting is touched. Every run uses
`--setting-sources project` so the user's own hooks and plugins do not mix with the probe's (the debug log
shows 4 enabled plugins: the probe plus 3 built-in ones).

## Blocker found on the way

Every run that needs a model fails at the first API request:

```
claude auth status        -> {"loggedIn": false, "authMethod": "none"}   (Bash tool and the user's Terminal tab)
smoke1.debug.log:~310     -> API auth_error: OAuth refresh token is no longer valid; run /login to re-authenticate
```

A person has to run `claude auth login`; an agent must not. So the runs below split into:

- **Ran without a model** (hooks that fire before the first request, plus session plumbing): section A.
- **Ran through the host session** (two subagents messaging each other, a cross-session message into a probe
  session): section B.
- **Prepared, not run** (they need a model): section C. `probes/run_model_probes.sh` runs all of them;
  `probes/analyze.sh <tag>` prints the verdict view.

## Helpers

| File | What it does |
|:--|:--|
| `probes/run.sh <run> [flags] -- "<prompt>"` | One headless `claude -p` session, cwd `probes/out/work`, `--permission-mode bypassPermissions`, Bash/WebFetch/WebSearch disallowed, `--output-format stream-json --verbose --include-hook-events`, `--debug-file probes/out/<run>.debug.log` |
| `probes/run_stream.sh <run> [flags] -- '<feeder>'` | Same, but stdin is `stream-json`; the feeder is a bash snippet using `msg "<text>"`, `sleep`, `touch`, so several turns and file edits happen in one live session |
| `probes/logger.sh <label>` | Hook handler: appends `{ts, run, label, event, env, input}` to `probes/out/events.jsonl`; optional behaviours by env var (`PROBE_INJECT`, `PROBE_WATCH`, `PROBE_TITLE`, `PROBE_BLOCK`) |
| `probes/rewake.sh` | `asyncRewake` handler (exit 2 with a stderr message) when `PROBE_REWAKE=1` |
| `probes/stub_mcp/server.py` | MCP server `plugin:probe:stub`, tool `record`; appends its arguments to `probes/out/mcp_calls.jsonl`; `extra: "sleep:N"` makes it block N seconds |
| `probes/show.sh <run>` | Compact table of the hook inputs of one run |

## A. Runs without a model

| Run | Command (after `cd probes`) | Observes |
|:--|:--|:--|
| `smoke1` | `./run.sh smoke1 --model haiku -- "Reply with the single word: pong"` | Which events fire before the API call; `mcp_tool` at SessionStart(startup) skipped; `mcp_tool` at UserPromptSubmit works; `mcp_tool` at SessionEnd(exit) fails; StopFailure |
| `r1_default` | `PROBE_INJECT=1 PROBE_WATCH=$PWD/out/work/watched.txt ./run.sh r1_default --model sonnet -- "Reply with the single word: pong"` | Default system prompt (transcript `prompt_snapshot`); `additionalContext` of SessionStart and UserPromptSubmit reaches the model |
| `r2_agent` | `./run.sh r2_agent --model sonnet --agent probe:probe-author -- "Reply with the single word: pong"` | System prompt with the main-thread agent; `agent_type` on every hook input |
| `r3_agent_setting` | `./run.sh r3_agent_setting --model sonnet --settings '{"agent":"probe:probe-author"}' -- "Reply with the single word: pong"` | `agent` setting gives the same system prompt as `--agent` (byte-identical to `r2_agent`) |
| `s1_watch` | `PROBE_WATCH=$PWD/out/work/watched.txt PROBE_INJECT=1 ./run_stream.sh s1_watch --model haiku -- 'msg "first prompt"; sleep 3; echo $(date +%s) >> watched.txt; sleep 3; msg "second prompt"; sleep 3; echo $(date +%s) >> watched.txt; sleep 2; msg "/clear"; sleep 3; msg "third prompt"; sleep 2'` | `watchPaths` + FileChanged; `/clear` = SessionEnd(clear) + SessionStart(clear) with a new `session_id`; `mcp_tool` on both |
| `s2_misc` | `PROBE_TITLE=wave-1-probe PROBE_INJECT=1 PROBE_WATCH=$PWD/out/work/watched.txt ./run_stream.sh s2_misc --model haiku -- 'msg "/probe:probe-skill alpha beta"; sleep 3; msg "hello one"; sleep 2; echo x >> watched.txt; sleep 2; msg "/model sonnet"; sleep 3; msg "/compact"; sleep 4; msg "/clear"; sleep 3; msg "hello two"; sleep 2'` | UserPromptExpansion fields and matcher spelling; `sessionTitle`; FileChanged `systemMessage`/`additionalContext`; Pre/PostModelSwitch; PreCompact |
| `s3_rewake` | `PROBE_REWAKE=1 PROBE_WATCH=$PWD/out/work/watched.txt ./run_stream.sh s3_rewake --model haiku -- 'msg "first prompt"; sleep 3; echo x >> watched.txt; sleep 8'` | `asyncRewake` from FileChanged wakes an idle session; what UserPromptSubmit receives for that turn |
| `s4_watchdir` | `PROBE_WATCH="$PWD/out/work/store:$PWD/out/work/store/w1:$PWD/out/work/solo.txt" ./run_stream.sh s4_watchdir --model haiku -- 'msg "go"; sleep 3; echo n > store/w1/newseg.jsonl; sleep 1; echo x >> store/w1/old.jsonl; sleep 1; mkdir store/w2; echo z > store/w2/seg2.jsonl; sleep 1; echo y >> solo.txt; sleep 2'` | `watchPaths` with directories; new files (`add`); no-matcher and `*` FileChanged hooks |
| `a1_mcpasync`, `a2_mcpasync_timing` | `./run.sh a2_mcpasync_timing --model haiku -- "hi"` with two extra `mcp_tool` entries on UserPromptSubmit (`async: true` and plain, both `extra: "sleep:4"`; the entries were removed afterwards, so `plugin/hooks/hooks.json` stays fast) | `async: true` on an `mcp_tool` hook is accepted and ignored: the turn starts only after both 4 s calls |

Also read offline: the transcript of each run under `~/.claude/projects/...-probes-out-work/<session_id>.jsonl`
(attachments `prompt_snapshot`, `hook_additional_context`, `hook_non_blocking_error`; user entries carry
`promptSource` and `turnOrigin`).

## B. Runs through the host session

| Probe | How | Observes |
|:--|:--|:--|
| Cross-session message | `./run_stream.sh x1_xsession --name probe-recv --model haiku --settings '{"crossSessionInbound":"accept"}' -- 'msg "genuine typed prompt before the cross-session message"; sleep 75'` in the background, then the `SendMessage` tool of the host session with `to: "probe-recv"` | UserPromptSubmit input for a typed prompt and for a cross-session message in the same session |
| Two subagents messaging each other | Host `Agent` tool: agent B, prompt "reply B-READY and finish"; agent A, prompt "SendMessage to B's agent id: PING-FROM-A nonce=7731, ask for PONG-FROM-B nonce=7731" | Direct sibling-to-sibling `SendMessage` by agent id; resume of a finished agent; reply back; transcripts in `__reports__/platform_probes/evidence/subagent_pair_transcripts.txt` |

The host session's own hooks are not the probe's, so no `SubagentStart`/`SubagentStop` fields were captured there.

## C. Prepared, not run (need a model)

Run `claude auth login` once, then `probes/run_model_probes.sh` and `probes/analyze.sh <tag>`. The prompts are in
the script; in short:

| Run | Flags | Prompt (abridged) | Answers |
|:--|:--|:--|:--|
| `m1_pair_<tag>` | `PROBE_INJECT=1`, sonnet | Spawn `probe:probe-verifier` (name `verifier`) and `probe:probe-author` (name `author`) in parallel in the background; author SendMessages `verifier`, verifier answers author; main thread then asks `author` what it received | Priority 1: named plugin agents messaging each other; SubagentStart/Stop fields and matcher spellings; `mcp_tool` on SubagentStart/Stop/PostToolUse/PostToolBatch; PostToolUse on `Agent` and `SendMessage`; UserPromptSubmit for a subagent hand-back |
| `m2_inject_block_<tag>` | `PROBE_INJECT=1 PROBE_BLOCK=1` | One foreground `probe:probe-author` | SubagentStart `additionalContext` reaches the subagent; SubagentStop `decision: block` once, `stop_hook_active` true on the second stop |
| `m3_default_<tag>`, `m3_agent_<tag>` | without / with `--agent probe:probe-author` | Write `hello.txt`, list the tools used, say what is known about git state | Behaviour diff of the main-thread agent |
| `m4_compact_<tag>` | `run_stream.sh`, `PROBE_INJECT=1` | Two remember-a-word turns, `/compact`, a recall question | PostCompact `compact_summary`; SessionStart(compact); `mcp_tool` on both |
| `m5_resume_<tag>` | sonnet | Spawn `v2`, then main-thread `SendMessage` to `v2` | Resume by name; hand-back as UserPromptSubmit |
| `m6_auto_resume_<tag>` | `--permission-mode auto` | as M5 | `SubagentHandback` shape in auto mode (`last_assistant_message` is not the report) |
