# Platform probes

**Goal**: Verify, in a throwaway probe plugin, every Claude Code mechanism architecture v4 relies on, and record a fallback for each one that fails.
**Pre-conditions**:
- [ ] Claude Code version recorded (`claude --version`)
**Success Gates**:
- ✅ Each mechanism in the table of v4 §Platform facts and §Hooks is marked VERIFIED, FAILED (with fallback) or NOT TESTABLE, with the probe run that shows it [run]
- ✅ The minimum Claude Code version for the v4 hook set is stated
**References**: [R01 §Hooks, §Platform facts](../../__reports__/genesis/11-architecture_v4.md); [R02](../../__reports__/genesis/08-hooks_leverage_v0.md) — event map; [R03](../../__reports__/genesis/04-design_review_v0.md) §3 — mechanisms table

## Step 1: Probe plugin
**Goal**: A minimal plugin that logs what the platform actually delivers
**Implementation Logic**:
Two named agents (`probe-author`, `probe-verifier`, both Sonnet); a hooks.json that registers every event v4 uses with a logger appending the raw hook input to a JSONL file; a stub MCP server exposing one tool, for `mcp_tool` handler probes. Probe code is disposable and never shipped.
**Deliverables**: `probes/plugin/.claude-plugin/plugin.json`; `probes/plugin/agents/probe-author.md`, `probes/plugin/agents/probe-verifier.md`; `probes/plugin/hooks/hooks.json`; `probes/logger.sh` (function `log_event`); `probes/stub_mcp/` (tool `record`)
**Consistency Checks**: `test -f probes/plugin/hooks/hooks.json` (expected: PASS)
**Commit**: `test(probes): add a throwaway plugin that logs every hook input`

## Step 2: Run the probes
**Goal**: Observe each mechanism once
**Implementation Logic**:
Run scripted sessions that exercise: (a) direct SendMessage between the two named subagents; (b) SubagentStart and SubagentStop fields for plugin agents; (c) an `mcp_tool` handler calling the stub server; (d) UserPromptSubmit inputs for a genuine prompt, a subagent hand-back and a cross-session message; (e) the main-thread `agent` setting, with a diff of behaviors the default prompt provided; (f) FileChanged via SessionStart `watchPaths`; (g) PreCompact and PostCompact fields.
**Deliverables**: `probes/out/events.jsonl` (gitignored); `probes/run_probes.md` (the exact prompts and commands used)
**Consistency Checks**: `test -f probes/run_probes.md` (expected: PASS)
**Commit**: `test(probes): record the probe runs for each v4 mechanism`

## Step 3: Findings
**Goal**: Decide what v4 can rely on
**Implementation Logic**:
Mechanism table with verdicts, version requirements, and the fallback chosen for each failure; amendments to the build nodes if a fallback changes them.
**Deliverables**: `__reports__/platform_probes/00-findings_v0.md` (table Mechanism verdicts)
**Consistency Checks**: `test -f __reports__/platform_probes/00-findings_v0.md` (expected: PASS)
**Commit**: `docs(probes): report which platform mechanisms v4 can rely on`
