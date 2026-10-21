# P1 v0: the PI without the skills listing (registered before any run)

registered: 2026-10-22, by research-pi, before author-w07-1 starts. Claim: w07-c1.

## The change (B against A)

- A = `agents/research-pi.md` at bb7a713.
- B = A with `Skill` appended to `disallowedTools:`, the `skills:` frontmatter removed (it does
  nothing for a main-thread agent, explorer-w07-e v1 against v2), and a short body paragraph that
  tells the PI to Read `${CLAUDE_PLUGIN_ROOT}/skills/research-loop/SKILL.md` at session start, that
  the `${CLAUDE_PLUGIN_ROOT}` paths inside that file are under the same root as the path it was just
  given (the body is substituted, a Read file is not: S-w07-explorer-w07-e-1), and how to find
  another installed skill when a task needs one (Glob for `SKILL.md` under the plugin folders, then
  Read).
- Nothing else in the plugin changes.

## Measured ceiling and noise, before the rule (open item 27)

- Ceiling: denying `Skill` removed 11,655–11,953 tokens of request 0 in two headless cells; B's body
  paragraph adds a few hundred back (v6: −10,983 with a longer prompt). [source:
  `__reports__/wave-07/explorer-w07-e/pi_table.md`]
- Noise: three identical baselines spread over 329 tokens.
- So a threshold of 9,000 tokens sits 2,000–3,000 below the ceiling and about 25 noise ranges above
  zero. It can pass and can fail.

## Metrics and rule

All cells headless, Claude Code 2.1.304, `--agent murmuration:research-pi` from exports whose agent
files are set to haiku, `CLAUDE_CODE_SHELL=/bin/bash`, auto permission mode, a fresh lab folder per
cell, fixed prompts, A and B alternated in pairs.

- **p1 (context):** request 0 of B ≤ request 0 of A − 9,000 tokens in each of 3 pairs.
- **p2 (the procedure still reaches the PI):** with a fixed prompt that can only be answered from a
  reference file of `research-loop` (for example: the brief's default explorer budget, from
  `references/briefs.md`, and the first heading of `templates/wave.md`), B answers correctly in 3 of
  3 cells, and reads the reference at its real path with at most one failed Read per cell.
- **p3 (downstream steps):** in each pair, the number of model requests B needs to answer p2's
  prompt is at most A's + 1.
- **p4 (commands):** `/lab-status` runs in B (1 cell); `/lab` is shown to start in B (1 cell, a
  fresh folder).
- **p5 (other skills stay reachable):** asked to use an installed non-Murmuration skill by name
  (`dataviz`, then `writing-history`), B finds and reads its SKILL.md in 2 of 2 cells.

**Landing:** B lands on the local `main` if p1–p5 all pass and the verifier (reproducer-w07-1)
supports them. If p1 passes and p2 or p5 fails, the body paragraph is revised once (v1, registered
before its run) and only p2–p5 are re-run.

**Not covered, said now:** the Desktop. Every cell is headless haiku; the Desktop PI's request 0 was
46,738 tokens with Opus (w06-c1). The first Desktop PI session after the merge is the check, as
w06-c1 was for the denylist, and the synthesis states it as untested until then.
