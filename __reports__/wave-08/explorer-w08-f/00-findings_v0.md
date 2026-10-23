---
type: findings
wave: wave-08
author: explorer-w08-f
date: 2026-10-24
version: v0
decision-required: none
---

# Thinking tokens billed again, and effort as a lever for Sonnet 5.5 workers: findings (v0)

Stayed inside the brief, with two departures. (1) The brief asks for a count nobody has seen; the stream-json output of a headless run carries one (`output_tokens_details.thinking_tokens` in each request's `message_delta`, and `modelUsage.thinkingTokens` in the result), so I used it instead of the token-counting endpoint (not called: it needs a credential). (2) My first verifier arms ran the test agents as the main-thread agent (`--agent`); the effort field did nothing there (see Result 3), so the verifier arms were rerun with the agent as a subagent of a Haiku parent. The main-thread runs are kept as a control.

## Result

1. **Thinking blocks of earlier requests are billed again as input in every later request of a tool loop: MEASURED.** In 168 consecutive request pairs (28 runs, six-step tool loop, cheap `echo` tool, no text), the context grew from one request to the next by exactly the previous request's `output_tokens` plus 30 to 60 tokens (84 pairs +30, 28 +31, 11 +32, 3 +37, 14 +39, 28 +60), thinking included; in the 37 pairs with at least 200 thinking tokens the excess is still 30 to 60. Had thinking been dropped, growth minus output would be minus the thinking tokens (minus 200 to minus 2,400). Fit over the 72 pairs of the `--effort` arms: growth = 41.5 + 0.997 x thinking tokens + 0.909 x other output tokens (R2 0.9987; bootstrap 95% interval of the thinking coefficient 0.976 to 1.010). After a new user turn (`--resume`) the context did not shrink either (43,522 against 43,293, with about 890 thinking tokens earlier in the session). The carried thinking is a cache write at the next request and a cache read at each one after (the next request's `cache_creation` equals the growth). [source: `think_cli_effort.txt`, `think_main_frontmatter.txt`, `think_fit_all.txt`, `requests_think_high_1_and_resume.tsv`]
2. **Size: MEASURED for these runs, ESTIMATE for the lab.** The platform's own count is 470 to 700 thinking tokens of 860 to 1,025 output tokens (61 to 67%) in the six-step loop at low, medium, high and default; 2,457 of 2,913 at max (84%). A transcript on disk stores no thinking text, only the signature; the platform's thinking token count against signature length (162 requests with thinking, signature 856 to 6,560 characters) is thinking_tokens = 0.3278 x (signature chars - 806), R2 0.962, residual sd 40 tokens. Applied to the 2,905 signed turns of explorer-w08-a's 68 workers (waves 4 to 7) it gives 1.82 M thinking tokens, 0.84 times the 2.16 M that explorer-w08-a inferred from context growth; at the same USD per carried token that is USD 15.8 or 18.9% of worker context USD, against its 22.5% (ESTIMATE; the lab's signatures reach 102,684 characters, far outside the fit range, and the median is 1,684). So the "about a fifth" holds in order of magnitude; the inference ran about 16% high on tokens. [source: `sig_fit.txt`, `apply_sigfit_to_w08a.txt`]
3. **Effort: the frontmatter field exists, is validated, and works for subagents, not for the main-thread `--agent` in a `-p` run: MEASURED (n=3 per arm).** CITED: `effort` is a documented subagent field (`low`, `medium`, `high`, `xhigh`, `max`; overridden by the `CLAUDE_CODE_EFFORT_LEVEL` variable, not by the session level) [source: https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/model-config, read through context7 `/websites/code_claude`]. MEASURED: `claude` 2.1.304 logs for a plugin agent file with `effort: bogus` "has invalid effort 'bogus'. Valid options: low, medium, high, xhigh, max or an integer" in its debug log and loads the agent anyway. A test agent with `effort` in a plugin folder dispatched by a Haiku parent changes the Sonnet 5.5 subagent's thinking: mean platform-reported thinking tokens 467 (low), 501 (default), 613 (high), 2,711 (max) on the six-step task; as the main-thread agent of a `-p` run, frontmatter low, medium, high and max gave 550, 548, 538 and 559 (default 566): no effect, while the `--effort` flag moves it (526, 527, 683, 2,457). The default for a Sonnet 5.5 agent behaves like low or medium here (566 against 526 and 527), whatever `effortLevel: high` the user's settings file holds (the documentation says models released after Opus 5.5 ignore the user-settings key).
4. **On the verifier task effort changed money only at `max`, and not the answer: MEASURED (two tasks, n=3 per arm, 30 subagent runs).** Both planted-error tasks were solved correctly in every run of every arm (30 of 30: recomputed total exact to 4 decimals, verdict UNSUPPORTED or OVERSTATED; none SUPPORTED). Sonnet subagent USD per run, mean (range), task A / task B: default 0.0194 (0.0174-0.0216) / 0.0190 (0.0156-0.0238); low 0.0185 / 0.0157; medium 0.0240 / 0.0204; high 0.0223 / 0.0215; max 0.1325 (0.1031-0.1538) / 0.1499 (0.1325-0.1640), 7 to 8 times default, with 8,204 to 8,959 thinking tokens against 104 to 137. Requests per run 3 to 5 in every arm. Low saved USD 0.001 to 0.003 a run on B and nothing on A: inside the run-to-run range of the default arm (USD 0.004 wide on A, 0.008 on B). [source: `verifier_A_subagent.txt`, `verifier_B_subagent.txt`]

## Table

### Thinking carried in a six-step tool loop (Sonnet 5.5, `--effort` flag, same prompt) [MEASURED]

| Arm | Runs | Mean USD | Requests | Mean output tokens | Mean thinking tokens | Thinking share of output | Thinking USD share (generation / carried) | Source |
|:--|--:|--:|--:|--:|--:|--:|:--|:--|
| low | 3 | 0.0220 | 7 | 860 | 526 | 61% | 23.9% / 10.0% | `think_cli_effort.txt` |
| medium | 3 | 0.0221 | 7 | 866 | 527 | 61% | 23.8% / 10.0% | same |
| high | 3 | 0.0244 | 7 | 1,025 | 683 | 67% | 28.0% / 11.7% | same |
| max | 3 | 0.0514 | 7 | 2,913 | 2,457 | 84% | 47.8% / 20.5% | same |

Thinking USD share = thinking tokens x 10 per MTok, plus the carry (next request at the 1-hour write rate 4, later ones at read rate 0.10), over the run's USD at list price [ESTIMATE; the cache prefix was warm, so the total is small and the carry share here is mostly the one write: in a worker with 100+ requests the reads of the carry dominate]. Run USD is the input side plus output at list price from the stream, equal to the result record's `total_cost_usd` in every run checked.

### Effort field by route, six-step task, mean thinking tokens (n=3 each) [MEASURED]

| Route | low | medium | default (no field) | high | max |
|:--|--:|--:|--:|--:|--:|
| `effort:` in agent file, agent as main thread (`--agent`) | 550 | 548 | 566 | 538 | 559 |
| `effort:` in agent file, agent as subagent of a Haiku parent | 467 | not run | 501 | 613 | 2,711 |
| `--effort` flag, agent file without field | 526 | 527 | (566) | 683 | 2,457 |

Source: `think_main_frontmatter.txt`, `subagent_effort_thinking_task.txt`, `think_cli_effort.txt`. Answers of the six problems: 27 of 27 runs gave the right answer to each of problems 1, 2, 3, 5, 6 and a right answer to problem 4 (48 divisors, 36 even) in a different format each time; the `answers_ok` column in the think tables undercounts only because of that format.

### Verifier task, effort as a subagent field [MEASURED]

| Task | Arm | Runs | Subagent requests | Mean Sonnet USD | Range | Mean thinking tokens | Correct |
|:--|:--|--:|--:|--:|:--|--:|--:|
| A (18 requests, 4 duplicate rows, 1-hour price bug) | default | 3 | 4.3 | 0.0194 | 0.0174-0.0216 | 104 | 3/3 |
| A | low | 3 | 3.3 | 0.0185 | 0.0151-0.0213 | 196 | 3/3 |
| A | medium | 3 | 5.0 | 0.0240 | 0.0212-0.0257 | 65 | 3/3 |
| A | high | 3 | 3.7 | 0.0223 | 0.0207-0.0249 | 261 | 3/3 |
| A | max | 3 | 4.7 | 0.1325 | 0.1031-0.1538 | 8,204 | 3/3 |
| B (40 requests, 9 streamed rows, two planted errors) | default | 3 | 4.0 | 0.0190 | 0.0156-0.0238 | 137 | 3/3 |
| B | low | 3 | 3.7 | 0.0157 | 0.0138-0.0175 | 0 | 3/3 |
| B | medium | 3 | 4.3 | 0.0204 | 0.0177-0.0225 | 118 | 3/3 |
| B | high | 3 | 4.0 | 0.0215 | 0.0183-0.0233 | 138 | 3/3 |
| B | max | 3 | 5.0 | 0.1499 | 0.1325-0.1640 | 8,959 | 3/3 |

Tasks: `task_A/`, `task_B/` (what the agent saw); the right numbers in `truth_A.json`, `truth_B.json` (A: true 0.3277, claimed 0.3051, no-dedup trap 0.3869; B: true 0.8771, claimed 0.7915). Correct = verdict not SUPPORTED and recomputed total within 0.0005 of the truth. Noise: 12 main-thread runs with no effect of the field (a replicate set at default) range USD 0.0184-0.0301 on B and 0.0187-0.0213 on A; the same prompt cost USD 0.0329 in the very first (cold-cache) smoke run and 0.019 later: cache state moves a run's cost by as much as any arm difference below `max`. Source: `verifier_A_subagent.txt`, `verifier_B_subagent.txt`, `verifier_main_thread_frontmatter.txt`.

## Worst-fitting case

The story is "thinking is carried and billed, so a lower effort should pay". Three cases fit it worst. (i) **Task B at low**: 0 thinking tokens in all three runs and USD 0.0157, the lowest arm, yet task A at low had more thinking (196) than default (104): at levels from low to high the thinking count on a task this easy is 0 to 260 tokens and does not order with the label. (ii) **Main thread**: frontmatter `max` as the main-thread agent of a `-p` run cost USD 0.0224, equal to low (0.0224); an agent file's `effort` can look accepted (no warning, valid value) and do nothing, so a probe that sets it on the main thread and sees no change would wrongly conclude "no lever". (iii) **One pair in 168** does not match the typical +30: the fifth request (k = 4 counting from 0) was followed by a context that grew by out + 60 in all 28 runs (every other k gives 30 to 39); the extra 30 tokens are not explained (puzzle 3). The case that fits the carried-thinking story best: every pair with at least 200 thinking tokens (37 of 37) has growth minus output between +30 and +60, never near minus the thinking count.

## Not covered

- The lab's own agents (`agents/*.md`) were not run; only test agents with the same frontmatter shape in a plugin folder under `/private/tmp/murmuration-w08/explorer-w08-f/plug`. Whether a lab worker (150 turns, long contexts, 40,000-token prompts) thinks differently by effort is not measured; the two verifier tasks are easy (3 to 5 requests, 0 to 260 thinking tokens at every level but `max`), so they show that effort did not change the answer, not that it never would on a hard claim.
- `xhigh`, a numeric `effort`, `CLAUDE_CODE_EFFORT_LEVEL` and `maxEffortLevel` were not tried; the medium arm was not run on the six-step task as a subagent.
- Whether the carried thinking is exactly the platform's thinking count (rather than count plus a constant per block) is not separated from the +30 per request: a ~30-token offset per request cannot be split into tool-call wrapper, result and block overhead with these runs.
- The token-counting endpoint was not called (needs a credential, not read). The result of (1) does not need it: the next request's own `usage` is the count of what was sent.
- The default effort for Sonnet 5.5 in a subagent is inferred from behaviour (thinking like low or medium), not read from a log: the debug log lines name no effective level.
- Thinking across a new user turn: one `--resume` run only. Cache lifetime effects (1 hour against 5 minutes) on the carried thinking are not measured.
- Runs share the machine's user-level hooks and plugins (the init record lists 26 plugins and 89 skills), so the base context is about 5,000 tokens, larger than a lab worker's first request only in the tools list; USD per run is therefore small.

## Steering questions

- [now] Effort as a lever: the evidence on a verifier-like task is "no change of answer from low to high, a 7 to 8 times cost at max, savings from low inside the noise"; do you want a probe on a hard claim (one where the default verifier is sometimes wrong) before deciding whether to set `effort: low` or `medium` in the lab's agent files?
- [now] Subagent frontmatter works, main-thread `--agent` frontmatter did not in `-p`: does the lab ever run an agent file as a main thread (the PI file does, `agents/research-pi.md`)? If so the PI's effort has to come from the session (`--effort`, settings), not from its frontmatter.
- [later] Thinking tokens can now be read from a transcript by signature length (R2 0.96); do you want `lab_status.py` or the harness hook to report thinking tokens per agent from it?

## Pointers

Everything in `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-8-928ebd/__reports__/wave-08/explorer-w08-f/` (tables and tasks, no transcript text); raw stream-json runs stay in `/private/tmp/murmuration-w08/explorer-w08-f/runs/` (98 runs, USD 3.44 by their result records; not committed). Prices: Sonnet 5.5 list price per MTok: input 2, read 0.10, write 5-minute 2.5, write 1-hour 4, output 10 (`scripts/lab_status.py` PRICES). `claude` 2.1.304, `CLAUDE_CODE_SHELL=/bin/bash`, permission mode auto, no budget flag, no seeds (model sampling; n=3 per arm).

- `python3 -I __instrumenta__/w08f_make_task.py <S>/src` and `w08f_make_task_hard.py <S>/srcB` build the two tasks (seeds 8 and 88 inside).
- `python3 -I __instrumenta__/w08f_run.py <S> <label> [--agent plugin:name] [--effort L] [--model haiku] [--task --src src|srcB] --prompt <text>` runs one headless session (driver shells `arms.sh`, `arms_th.sh`, `arms_cli.sh`, `arms_sub.sh`, `arms_vsub.sh` copied here; `prompt_think.txt` is the six-problem prompt).
- `python3 -I __instrumenta__/w08f_think.py <S> T- C-` gives `think_*.txt` (per-run table, growth fit, bootstrap); `w08f_requests.py <run.jsonl>` the per-request table (`requests_think_high_1_and_resume.tsv`); `w08f_sub_table.py <S> <PREFIX> [truth.json]` the subagent tables; `w08f_arms_table.py <S> A:src B:srcB` the main-thread verifier arms; `w08f_sig_fit.py <S> out.tsv` and `w08f_apply_sigfit.py <items dir> <items.tsv> 0.3278 806.4` the signature fit and its application to explorer-w08-a's items. Each runs in seconds. Scripts cited as `__instrumenta__/<file>@<commit>` at the commit of this report.
- Test plugin: `test_plugin/` (agents `vf-*`, `th-*`, with and without `effort`).
- Void runs: the first task-B main-thread batch used task A's files (my runner copied the wrong folder); its 12 runs are discarded and rerun, not in any table.
