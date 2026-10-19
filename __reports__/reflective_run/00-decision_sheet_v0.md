# Reflective run, wave 1: proposals for your decision

Date: 2026-10-19. Lab: `__statera__/wave-01.md` (closed). Each proposal is a claim in `__pondus__/`.
Its label is the one `python3 scripts/lab_status.py` shows; "by PI decision" means the verifier
escalated and the PI decided, as recorded in the wave note. Nothing has been applied to the plugin.

## Your question, answered in one paragraph

Of the elements set aside as over-engineering, the evidence brings back only one, in a smaller
shape: a hook that saves each subagent's final report to the lab (SA6, as w01-c14). One more
changes shape: the cost ledger (SA3) becomes a fixed `/lab-status` reader with no new store
(w01-c3). Nothing argued for the other set-aside elements. Six were examined and stay out:
the examen mirror, SubagentStart injection, the friction hooks, FileChanged notices, the
question machinery and the bundled MCP servers. Nine were not examined; they include the Rust
binary and the JSONL stores (w01-c13). The faults that mattered were in what shipped, not in what
was cut. The prompt hook saved platform text as your words and wrote to the wrong checkout. Cost
tracking missed worktree sessions and double-counted forks. Three of six explorers ran out of turns.

## Proposals

| # | Change to the plugin | Axis | Claim · label | Evidence (one line) | Cost |
|:--|:--|:--|:--|:--|:--|
| P1 | A hook on `SubagentStop` and `PostToolUse(SubagentHandback)` saves each hand-back verbatim to `__statera__/handbacks/`. Briefs stop asking for report files | 1, 2 | w01-c14 · MEASURED | The Write tool refuses `REPORT*`, `SUMMARY*`, `FINDINGS*` and `ANALYSIS*.md` from subagents, and 4 of 6 explorers lost their report to it. The hook saved 7 of 7 hand-backs byte for byte, headless, on both binaries | 101 statement lines of Python plus 2 hook entries; about 43 ms per hand-back. Relies on undocumented fields. A read-only folder loses a report silently. **Condition:** the file is a recovery aid for the PI and you; nothing may feed it back to agents |
| P1′ | Zero-code alternative to P1: briefs ask for the report as the final message, plus `<name>-notes.md` if a file is wanted | 1 | (a puzzle in w01-c1; not a claim) | The refusal applies only to the four basename prefixes | No code. Fidelity rests on the platform's rendering, which is lossy (S-w01-research-pi-13) |
| P2 | Fix `/lab-status` spend: count each message once by `sessionId`, find worktree sessions through `git worktree list`, show USD (exact from `cost-state`, else list price), mark subagent output as a lower bound | 2, 3 | w01-c3 · MEASURED | Matches Claude Code's own USD within 0.05% in 52 of 54 cells. Today's reader inflates totals ×1.32–1.44 on forks and finds 0 sessions from the main checkout | About 56 lines against 33 today; relies on the undocumented transcript layout |
| P3 | In P2, flag subagent output as exact or a lower bound with the "every request's last record has a stop reason" test. Document OpenTelemetry as the opt-in exact source | 2 | w01-c2 · MEASURED by PI decision | In headless haiku runs, `auto` and `plan` modes leave subagent output truncated in 39 of 39 cells; the test agrees with exactness in 199 of 199. None of this run's 23 subagent files is final | A few lines in P2. OpenTelemetry needs your own environment variables; a plugin cannot set them |
| P4 | Prompt hook, text part: cut leading `<system-reminder>` and `<artifact-view-context>` blocks, then apply the command tests, then unwrap pasted text | 1, 3 | w01-c9 · below MEASURED: restate | The numbers were reproduced independently: 72 typed prompts, 51 cleaned, 0 dropped. Only the title said more than was run | +132/−12 lines including the selftest. Relies on undocumented tags. A message that genuinely begins with a reminder block would be cut |
| P5 | Prompt hook, root part: pick the lab from the payload `cwd` | 1 | w01-c10 · below CONJECTURE: restate | It fixes the case this run hit and breaks the opposite one. What the Desktop passes to hooks was never observed | **Do not land** until the one-minute Desktop probe (O1) is run |
| P6 | `maxTurns`: explorer 60 → 75, author 120, reproducer and proof-adversary 80. Workers append findings to their puzzle file as they go | 1 | w01-c8 · MEASURED by PI decision (the values are CONJECTURE) | 3 of 6 explorers stopped at 60 turns with no report. Resuming within about 5 min cost no cache rewrite; 0 of 38 notices waited over 300 s | 4 frontmatter lines and a sentence in each agent file. The values rest on 6–7 earlier runs per role |
| P7 | At each wave close, a chat message to you: your question first, then each verdict in one quotable sentence with its scope, cost, and what needs you | 3 | w01-c6 · below CONJECTURE: restate | The verifier's figure: it would plausibly have pre-empted 3 of your 55 prompts at wave close, and none clearly | +168 words in shipped files |
| P8 | An asking habit for the PI: read your recent words before asking, ask only what only you can decide, and state a default | 1, 3 | w01-c7 · below CONJECTURE: restate | The verifier's figure: it removes 1–2 of 19 asks and does not recover the 479-minute wait, which was your night | +127 words in `working_defaults.md` |

Stays out: see w01-c13 (CONJECTURE, verifier SUPPORTED). Keep the explicit `tools:` allowlists.

## What the checking itself showed

Of the 14 claims filed, 3 stand as filed or as supported restatements (w01-c3, w01-c13, w01-c14).
Every first statement except w01-c3's was judged overstated or escalated by its verifier. Verifiers
caught two double counts through forked sessions, a 420-character truncation in an evidence table,
a regression in a proposed fix, and two hook bugs. The independent check earned its cost in this
study.

## Still open

| # | Open item | Who | Cost |
|:--|:--|:--|:--|
| O1 | Desktop probe: what `cwd` and `CLAUDE_PROJECT_DIR` does a plugin hook get in a Desktop worktree session? This decides P5 | you (needs a new Desktop session) | 1 minute |
| O2 | Your `~/.claude/plugins/installed_plugins.json` has about 212 local entries for `murmuration@murmuration-local`. The study's headless runs added them, because they ran under this worktree's `.claude/settings.local.json`. Clean them up? Future probes should run outside the worktree | you | minutes |
| O3 | `__reports__/reflective_run/w01/author-w01-2/runs/` (228 MB, untracked) holds raw runs; four OTel files still carry your email and organization id. Delete it? | you | — |
| O4 | Leanness: the skill listing, about 30k characters, is repeated 7–17 times in each worker's context, the largest avoidable cost seen. Can a plugin shorten it for workers? | a probe | about USD 1–3 |
| O5 | Subagent prompt cache lives 5 min, the main thread's 1 h (tuning target `cacheTtl`). Is it settable? | a probe | about USD 1 |
| O6 | Research-loop protocol: authors edited claim heads mid-verification; PI-authored claims get late answers; derived tables can truncate silently; a restatement round cost about USD 3–5 each time | a protocol claim | — |
| O7 | Nine set-aside elements not examined (SA1, SA2, SA7, SA10, SA11 mostly, SA12, SA14, SA16, SA17) | further waves | — |
| O8 | Tuning targets not covered: `omitClaudeMd`, `autoCompactWindow`, brief vs skill redundancy, whether parked puzzles came back. `effort` is `high` on every message, so there is nothing to tune from data | further waves | — |

Spend so far: USD 60.56 at least, about 75.65 by ESTIMATE. The budget proposed in USD is
USD 70–90; you confirmed the earlier token figure but not this one.
