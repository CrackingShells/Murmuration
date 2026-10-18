# Agents, skills and commands

**Goal**: Write the team: the PI identity, the Sonnet workers, the research-loop skill and the user commands, packaged as the `murmuration` plugin.
**Pre-conditions**:
- [ ] `platform_probes` and `instrument_validation` done
**Success Gates**:
- ✅ Every sentence of `research-pi.md` passes the test "does it tell the PI when to decide what?" (no) [static]
- ✅ Worker agent files set `model: sonnet`; only `research-pi` is Opus [static]
- ✅ The plugin installs locally and `/lab` starts a session with research-pi as the main agent [run]
**References**: [R01 §Agents, §Human-side UX](../../__reports__/genesis/11-architecture_v4.md); [R02](../../__reports__/genesis/04-design_review_v0.md) §4 — positive failure-mode instructions

## Step 1: Shared invariants and the PI
**Goal**: The identity in prose
**Implementation Logic**:
`AGENTS.md` (one screen of invariants and channel writers); `research-pi.md` from the v4 draft voice.
**Deliverables**: `AGENTS.md`; `agents/research-pi.md`
**Consistency Checks**: `test -f agents/research-pi.md` (expected: PASS)
**Commit**: `feat(agents): write the shared invariants and the PI identity`

## Step 2: Workers
**Goal**: Explorer, author, reproducer, proof-adversary, depth reviewer
**Implementation Logic**:
Each carries its positive habits in its own voice; independence-first and termination for the verifiers.
**Deliverables**: `agents/explorer.md`, `agents/author.md`, `agents/reproducer.md`, `agents/proof-adversary.md`, `agents/depth-reviewer.md`
**Consistency Checks**: `test -f agents/proof-adversary.md` (expected: PASS)
**Commit**: `feat(agents): write the Sonnet workers with their habits`

## Step 3: research-loop skill and commands
**Goal**: Procedures in a skill, not in the PI
**Implementation Logic**:
Brief templates (worker mandate, honesty tags, scrupuli), labels, lab-init; `/lab` and `/lab-status`.
**Deliverables**: `skills/research-loop/SKILL.md`; `skills/lab/SKILL.md`; `skills/lab-status/SKILL.md`
**Consistency Checks**: `test -f skills/research-loop/SKILL.md` (expected: PASS)
**Commit**: `feat(skills): add the research loop and the lab commands`

## Step 4: Package
**Goal**: Installable plugin
**Implementation Logic**:
Manifests and hooks.json via spawning-agent-plugins; local install test; a Nest entry prepared but not published.
**Deliverables**: `.claude-plugin/plugin.json` (id `murmuration`); `hooks/hooks.json`; `.mcp.json`
**Consistency Checks**: `test -f .claude-plugin/plugin.json` (expected: PASS)
**Commit**: `feat(plugin): package Murmuration for local install`
