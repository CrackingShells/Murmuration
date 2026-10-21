## S-w06-explorer-w06-a-1
Three side-by-side hooks on UserPromptSubmit (isolated): the Rust binary is slower than the python script (median 296 against 214 ms, n = 4 runs; stamped variant: python finished first in 4 of 4). Every other cell has Rust ahead or level. Is there an ordering effect in which hook the platform starts first, or is it noise? A paired run with the hook order permuted (n of 20) would say.
refs: `__reports__/wave-06/explorer-w06-a/hook_lang_probe_table.md` (rows `ups-all3-iso`, `ups-stamped3-iso`, `ptu-all3-iso`); `/private/tmp/murmuration-w06/explorer-w06-a/out/main_rows.jsonl`

## S-w06-explorer-w06-a-2
The first 100 ms. Every language pays 98-129 ms recorded for a script that runs in 0.1 ms, against 52-82 ms for the same commands outside the platform; `sh -c true` alone costs 33 ms bare, and a 500 KB Rust no-op 52 ms. That floor looks like the kernel's exec path (scanning), not the platform. The debug log shows the platform running its own `sh` (telemetry module, 101 ms) at the same moment as the hooks start. Whether that contends with hook spawns is untested, and so is the floor on an idle machine.
refs: `__reports__/wave-06/explorer-w06-a/hook_bare_cost_n40.md`; `/private/tmp/murmuration-w06/explorer-w06-a/out/dbg2.log` (lines "$.process.run (cc-plugin-telemetry): sh ... 101ms")

## S-w06-explorer-w06-a-3
The user's sibling hooks cost my hook 96-137 ms on UserPromptSubmit although only one silent python hook sits beside it (`inject_plan_directive.py`, 82 ms bare). One python start should add less than one python start's cost if the platform ran any in parallel; it added more than all of it. In the Murmuration hooks.json SubagentStart has three hooks side by side (budget.py, tool routing policy, colgrep via `uv run`): the probe says the last of them waits for the two before it. Would one dispatcher per event beat a Rust rewrite? Untested on the shipped hooks.
refs: `__reports__/wave-06/explorer-w06-a/hook_lang_probe_table.md` (`ups-*-alone` against `ups-*-alone-iso`); `__reports__/wave-06/explorer-w06-a/hook_x8_order_stats.md`; `hooks/hooks.json`
