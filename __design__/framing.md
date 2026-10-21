# Framing

## The question

In the user's words (`__statera__/user_words.md`, 2026-10-19 10:56):

> Search how the system should optimize itself, starting mostly from the elements we considered
> adding but set aside as over-engineering for now. Each of them may come back, change shape, or
> stay out, depending on what the evidence shows.

> 1. **The system itself.** Communication schemes, commands, easy sorting and parsing of outputs,
>    standardization of MCP servers, leanness and sustainability. All of it serves one purpose: the
>    system tackling rather open research questions efficiently on its own, not a human researcher
>    sitting in an interactive session and micro-managing it.
> 2. **Logging.** [...] probably where hooks can help, by automating the logging that tracks the
>    system's behavior during a research task, and also basic performance and cost tracking.
> 3. **UX for humans.** [...] the system must not become so alien to humans that we can no longer
>    review it.

> Every change you propose to the plugin is a claim with evidence from the transcripts and files,
> a cost, and an independent verdict. I decide which ones land.

Earlier (09:25): "once we have v1, I plan to run the agent system on itself; a reflective
operation for the agent system to tune itself."

**The PI's reading.** The shipped plugin (v6, "minimal lab") is a deliberate cut of the v5 design.
The question is which cut elements the evidence calls back, in what shape, and which stay out,
judged against one purpose: a team that works an open research question **on its own** while
staying legible to a human who looks in rarely. Priority order: the system's own mechanics, then
logging (hooks are the suspected lever), then human UX. A proposal is a plugin change with
(a) evidence from transcripts or files, (b) a cost (tokens, maintenance, platform dependence,
alienness to humans), (c) an independent verdict. Staying out is a legitimate outcome and is
reported as such.

## Notation

| Symbol | Meaning |
|:--|:--|
| v5 | `__reports__/genesis/12-architecture_v5.md`, the full, frozen design |
| v6 | `__reports__/genesis/13-architecture_v6.md`, the shipped minimal lab |
| SA*n* | a set-aside element: in v5, absent from v6 (list below) |
| genesis study | session `566fa912…` and its subagents: the combinatorics study, run before Murmuration existed |
| design session | session `82e8a947…`: retrospective, design and build of Murmuration (includes the probes) |
| this run | the present session: the first run of the shipped plugin on a real question |
| proposal | a change to `agents/`, `skills/`, `scripts/`, `hooks/` or `.claude-plugin/`, filed as a claim |

Set-aside elements:

| SA | Element |
|:--|:--|
| SA1 | `libripens`: one binary with CLI, hook entry point, MCP server; single writer path with schema validation |
| SA2 | JSONL per-writer event stores (instead of markdown) and the derived SQLite index |
| SA3 | `__expensa__` ledger: per-run tokens, wall time, tool calls, model, exit; Wh estimate |
| SA4 | `__examen__`: pair messages mirrored by `PostToolUse(SendMessage)` |
| SA5 | `SubagentStart` context injection (wave, claim id, partner, contract) |
| SA6 | `SubagentStop` close-run + presence gate (`decision: block` once) |
| SA7 | `PreToolUse` guard on stores; brief measurement on `Agent` |
| SA8 | friction hooks: `PostToolUseFailure`, `PermissionDenied`, `StopFailure` |
| SA9 | `FileChanged` + `asyncRewake` live notices to the PI |
| SA10 | `PreCompact`/`PostCompact` context accounting |
| SA11 | other events: `PostToolBatch`, `Stop` snapshot, `InstructionsLoaded`, model switch, worktree, `Notification`, `MessageDisplay`, `SessionEnd` |
| SA12 | information instruments: coverage, uptake, read ratio, bits, label reliability |
| SA13 | soft/hard questions to the human (`ask`/`answer`) |
| SA14 | depth reviewer agent |
| SA15 | bundled `.mcp.json` (Wolfram, colgrep, arxiv, web search) and a shared `AGENTS.md` |
| SA16 | `mention` vs `follow` scrupulus events |
| SA17 | composition with umbod for multi-session campaigns |

## Scope

Covers: the five agent files, the three skills, the four scripts, `hooks/hooks.json`, the project
settings written by `/lab`, and the SA list above. The tuning targets in
`__roadmap__/murmuration/build/pilot/reflective_run.md` are in scope.

Leaves out: the research protocol's core contracts (labels, independence first, `changed_by`),
which both reviews judged sound; naming; the external benchmark plan. A claim may still touch them
if the transcripts show they fail.

Evidence caveat, stated up front: the genesis study ran **before** Murmuration existed, so it shows
what a plain Opus-PI-plus-Sonnet-workers session did, not what the shipped plugin does. The only
run of the shipped plugin on a real question is this run. Every claim says which of the two its
evidence comes from.

## Rules for the team

- Compute: no hard limit per call; keep each explorer under about 400k tokens. Extract from the
  JSONL transcripts with scripts (`python3 -I`, `jq`), never by reading whole transcript files into
  context. Write scripts and derived tables under `__reports__/reflective_run/w01/<your name>/`.
- Data (read only; no downloads):
  - Session transcripts of the genesis study and of the work that followed it, in
    `~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/`:
    - `566fa912-7009-421a-9d79-11145e2b8db9.jsonl`: the research study (principal investigator and
      team), with its subagent transcripts in the folder of the same name;
    - `82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl`: the retrospective of that study, the design of
      Murmuration and its build;
    - `3ccc590f-0187-4f79-b7af-4955944f1374.jsonl` and `2947f9dc-1c3a-452b-97a5-39d4510a1271.jsonl`:
      two further sessions in the same project.
    These files are still appended by other sessions; read them, never write them.
  - Probe transcripts: `~/.claude/projects/-Users-hacker-Documents-src-CrackingShells-Murmuration-probes-out-work/`.
  - This run's transcript and subagents:
    `~/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl`
    (and the folder of the same name).
  - The genesis study's files: `/Users/hacker/Documents/explore/combinatorics_on_binary` (reports,
    roadmap, decision notes, notebook, git history). Never write there; other sessions use it.
  - This repository: the shipped plugin (`agents/`, `skills/`, `scripts/`, `hooks/`), its design
    records (`__reports__/`, especially `platform_probes/01-findings_v1.md`), roadmap (`__roadmap__/`).
- Changes to the plugin: every change to `agents/`, `skills/`, `scripts/`, `hooks/` or
  `.claude-plugin/` is a claim with a verdict. Since wave 2 (the user's 12:50 answer: "decide
  that based on experiment on the new architecture") a change may be applied on the study branch
  once its claim stands. Prototypes live under `__reports__/reflective_run/`.
- **Who decides (the user, 2026-10-21 17:06).** "The guardrails are morals, legals, ethics. Things
  that are about engineering and about the Murmuration system, I don't have anything to decide."
  - The lab decides what lands, on the evidence and the verdicts, and merges it into the local
    `main`, which is the copy every session runs (explorer-w05-e).
  - The user keeps moral, legal, ethical and safety questions: credentials, the permission layer,
    other people's data.
  - The user also keeps anything visible outside this machine: pushing, publishing, messages.
  - A report to the user states what was decided and why. It does not hand engineering choices back
    as questions.
- Headless `claude -p` probes run in folders OUTSIDE this worktree (e.g. the PI's scratchpad):
  runs below it register the plugin in the user's `~/.claude/plugins/installed_plugins.json`
  (w01-c14). Never commit raw run output: hook payloads and OTel bodies carry account identifiers.
- Platform: the Desktop app that runs this lab is Claude Code 2.1.299 (its `CLAUDE_CODE_EXECPATH`;
  every transcript record of this run); the `claude` on PATH is 2.1.302; the probes ran on 2.1.296
  (corrected after S-w01-explorer-w01-f-1). Platform behaviour taken from the
  probes is CITED to the probe report unless a claim depends on it, in which case re-run it.
- Tools: colgrep `search` for meaning-level search in this repository (shell `grep -r` is blocked);
  plain `grep` on one file and `cmd | grep` are allowed; `python3 -I` and `jq` for transcripts;
  `context7` for Claude Code documentation.
- Every cost carries its unit: tokens, USD at a cited list price, minutes, or lines of code to
  maintain.
- Commit only your own files.
