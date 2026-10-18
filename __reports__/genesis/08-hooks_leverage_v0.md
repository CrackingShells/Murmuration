# Research-lab: leveraging the full hook surface — Architecture Analysis (v0)

Date: 2026-10-18 · Input to architecture v3. The source is the Claude Code hooks reference
(code.claude.com/docs/en/hooks, read in full on 2026-10-18: 33 events, 5 handler types). v2 used
only SessionStart, SubagentStop and PreToolUse.

## Executive Summary

Six hooks change the design itself, not just its plumbing:
1. **`UserPromptSubmit` captures the user's words automatically.** Every genuine user prompt in a
   lab session is appended verbatim to `framing.md §0` / the `statera` inbox. `/lab-steer` stops
   being something the user must remember.
2. **`SubagentStart` injects the per-run context** (wave, claim id, partner agent, store paths,
   honesty contract) into every subagent. umbod's "worker mandate travels with delegation" then
   holds without the PI pasting it, which also saves communication.
3. **`PostToolUse` on `SendMessage` mirrors pair conversations into `__examen__`.** Mirroring
   becomes a guarantee, not something agents must remember. The same event is where the
   information measures of every message are taken.
4. **`SessionStart.watchPaths` + `FileChanged` make the back-flow live.** When a verifier raises a
   scrupulus or a claim turns disputed, a one-line `systemMessage` reaches the PI and the human at
   once, without waiting for the next brief.
5. **`PreCompact` / `PostCompact`** record what the PI's own context kept and dropped
   (`compact_summary`). This is an information measure of the PI's attention, and SessionStart
   (`compact`) re-injects the scrupuli afterwards.
6. **`mcp_tool` handler type.** Hooks call `libripens` through its MCP server instead of starting a
   process per event, which removes the per-call start-up cost entirely on the hot events.

## Event → lab function map

| Event (matcher) | Handler | Lab function | Mode served |
|:--|:--|:--|:--|
| `SessionStart` (startup / resume / compact / fork / clear) | command (`mcp_tool` is skipped at launch) | Brief (scrupuli first); `watchPaths` on the store directories; `sessionTitle` = the current wave; uses `seconds_since_last_response` and `prompt_cache_likely_expired` to say "resuming after N h, cache cold" | attention |
| `UserPromptSubmit` | mcp_tool | Append genuine user prompts verbatim to the user-words channel (skip subagent hand-backs and cross-session messages, which also fire this event); `additionalContext` lists steer notes not yet acknowledged | attention |
| `UserPromptExpansion` (`lab`, `lab-*`) | mcp_tool | `/lab` runs lab-init if the channels are missing (also covers a typed `/lab`, which bypasses PreToolUse on Skill) | UX |
| `SubagentStart` (worker agent types) | mcp_tool | Open an `expensa` run event (so in-flight runs are known); inject wave, claim id, partner, the framing pointer and the honesty contract as `additionalContext` | hardening, communication |
| `PreToolUse` (`Agent`) | mcp_tool | Measure the brief: bits, and redundancy against what SubagentStart will inject; tell the PI as `additionalContext` (never `deny`) | communication |
| `PreToolUse` (`Bash`, `Edit\|Write`) | command | Guard: no kills by pattern; stores and the user-words file are append-only through `libripens`. Exit 2 = deny with a reason | hardening |
| `PostToolUse` (`SendMessage`) | mcp_tool, async | Mirror the message into `__examen__` when sender and receiver form a pair; record a `comm` event (bits, new bits given the receiver, redundancy) | hardening, communication |
| `PostToolUse` (`Agent`) | mcp_tool, async | Use the run telemetry in `tool_response` for the ledger (foreground runs) | sustainability |
| `PostToolUse` (`Write\|Edit` under `data/`, figures) | mcp_tool, async | Register raw artifacts (path, producer, wave), so the brief can point the PI at *new raw material*, not only at reports | attention |
| `PostToolUse` (`Read`, main thread) | mcp_tool, async | Count the PI's raw-artifact reads per wave (a signal for the human) | attention (measured) |
| `PostToolBatch` | mcp_tool | After the PI dispatches a portfolio in parallel, record the batch as one probe set (exploration diversity is measured per set) | exploration |
| `PostToolUseFailure` | mcp_tool, async | `expensa` failure events: retries and waste, with `duration_ms` | sustainability |
| `PermissionDenied` | mcp_tool, async | Friction log (what the team tried that the environment refused) | process |
| `SubagentStop` (workers) | command | Close the run (tokens from `agent_transcript_path`); presence gate with `decision: block` once (`stop_hook_active`) | hardening |
| `Stop` (main thread) | command, async | Turn snapshot: comm totals, spend by mode; nothing blocks | sustainability |
| `StopFailure` (rate_limit, overloaded, …) | command | Log API failures and their cost; no output possible | sustainability |
| `PreCompact` (auto / manual) | mcp_tool | Snapshot: open scrupuli, the current wave note and unacknowledged steer notes are already in stores; record the PI context size | attention |
| `PostCompact` | mcp_tool | Store the `compact_summary` as a `statera` event; later compare it with the stores to see which open scrupuli the PI's summary dropped | attention (measured) |
| `InstructionsLoaded` | command, async | Hash the loaded instruction files: a prompt-cache stability check (AGENTS.md, rules) | sustainability |
| `PreModelSwitch` | command | Log the switch with `estimated_cache_write_usd` and `pricing`; tell the human the cache cost (`systemMessage`); never deny | sustainability |
| `PostModelSwitch` | command | Ledger: the model changes the energy coefficient from here on | sustainability |
| `FileChanged` (store segments via `watchPaths`) | command | Live `systemMessage`: "new scrupulus from reproducer on w3-author-2", "claim disputed" | attention |
| `ConfigChange` (project settings) | command | Log changes to `agent: research-pi` or to the lab hooks mid-study (no block) | process |
| `WorktreeCreate` / `WorktreeRemove` | command | If pairs run in worktrees: register them in `statera`; at wave seal, list the worktrees to prune (materials) | sustainability |
| `Notification` (`agent_needs_input`, `idle_prompt`) | command | `terminalSequence` desktop notification for hard questions (budget gone) | UX |
| `MessageDisplay` | command | Display-only: render claim ids in the PI's messages with their *current* label, e.g. `w3-author-2 [CHECKED]`. The transcript is unchanged | UX |
| `SessionEnd` | command | Flush the index, write the closing ledger summary (Wh, tokens, CPU per accepted claim). The 1.5 s shared budget is another reason for a Rust binary | sustainability |
| `TaskCreated` / `TaskCompleted` / `TeammateIdle` | command | Agent Teams fallback only: ledger and gate move here; `TeammateIdle` exit 2 keeps a verifier working until its thread has a verdict | hardening (fallback) |

Not used: `Setup`, `DirectoryAdded`, `CwdChanged`, `Elicitation`, `ElicitationResult`, and
`PermissionRequest` (permissions stay with the user).

## Handler-type choices

| Type | Where | Why |
|:--|:--|:--|
| `mcp_tool` → `libripens` MCP server | most observational and hot events | No process start per event; typed input via `${tool_input.…}` substitution; the server keeps the index warm |
| `command` → `libripens hook …` | SessionStart, SubagentStop gate, guard, SessionEnd, FileChanged | Events where `mcp_tool` is skipped (launch) or where exit-2 semantics and speed at start-up matter |
| `async` / `asyncRewake` | measurement hooks; the offline `libripens map` at wave seal | Never on the critical path. `asyncRewake` lets the map wake the PI only when it has something to show; the PI judges what it means |
| `prompt` / `agent` (LLM-evaluated) | **not used by default** | They would put judgement into hooks and cost tokens on every event. Optional, on demand: sampled semantic entropy on disputed claims (see the information counsel, 08) |

## Invariants this adds

- Hooks never decide research direction. The `deny` and `block` outputs are used only for the
  guard (pattern kills; append-only stores) and for the presence gate. Everything else is
  `additionalContext`, `systemMessage` or a stored event.
- The user's words are captured by `UserPromptSubmit`, never written by an agent.
- Pair messages reach `__examen__` via `PostToolUse(SendMessage)`, so the PI's view of a pair is
  complete even if an agent forgets to mirror.
- Per-event overhead: `mcp_tool` calls to a resident server, plus async for anything heavier than
  appending a line.

## Risks

| Risk | Mitigation |
|:--|:--|
| `UserPromptSubmit` also fires for subagent hand-backs and cross-session messages | Capture only prompts without the hand-back/cross-session wrappers; log the rest as `comm` events |
| `FileChanged` notifications become noise | Notify only for scrupuli, disputes and ESCALATEs; batch the rest into the brief |
| Version drift (several fields need v2.1.25x–2.1.29x) | `lab-init` checks the Claude Code version and degrades to the v2 hook set |
| `MessageDisplay` rendering misleads (display ≠ transcript) | Display-only by design; labels are fetched live from the index |
