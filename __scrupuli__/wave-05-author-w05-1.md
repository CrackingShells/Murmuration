## symbols
cold mid-run request (E5 m1): a request, other than the first, after a gap over 300 s since the previous request, with cache read under 50% of its context; computed from the subagent transcript by `__instrumenta__/w05c1_wait_arms.py`.

## S-w05-author-w05-1-1
The cache lifetime depends on the thread type, not only on the plugin. In headless runs every cache write of the main thread is a 1-hour entry (`ephemeral_1h_input_tokens`), every write of a subagent a 5-minute entry. A 528 s wait in a main-thread author left cache read at 223k of 223k tokens; the same wait in a subagent rewrote 227k tokens. Wave 4's interactive workers (subagents) had 0 one-hour writes. So the claim "waiting over 5 minutes loses the cache" is true of subagents only, and the lab's PI (a main thread) may have 1-hour entries in the Desktop too; nobody has looked at the PI's `cache_creation` split. If the PI thread is 1-hour, its idle waits (75% of wave 4) are not cache losses, and the 1-hour write price (4.0 vs 2.5 USD per million, sonnet) is something the PI pays on every write.
refs: `__reports__/wave-05/author-w05-1/pilot1_mainthread/requests_pilot-A1.csv` (row 6: gap 528.7 s, cache_read 223,258); `__reports__/wave-05/author-w05-1/requests_A1.csv` (row 8, cold); `/private/tmp/murmuration-w05/author-w05-1/pilot-tools/run_default.jsonl` (`cache_creation` by `parent_tool_use_id`); explorer-w05-c table row "Cold cache events".

## S-w05-author-w05-1-2
Monitor can be given to a subagent and does not let it wait. A worker told to wait for Monitor events had none delivered, ended its turn, and handed back "incomplete". In an interactive session the same events would arrive as notifications after hand-back and resume it with a cold cache, which is the "reopened author-w04-4" of S-w05-explorer-w05-c-1. I did not test whether the event reaches a subagent that keeps working (a poll loop plus a Monitor), or what happens to a Monitor started by a worker that has handed back. The harness's "use Monitor" hint on a blocked `sleep` is therefore wrong advice for any worker, with or without Monitor in `tools:`.
refs: `__reports__/wave-05/author-w05-1/pilot_tools/README.md` probe 3; `/private/tmp/murmuration-w05/author-w05-1/pilot-tools/run3.jsonl`.

## S-w05-author-w05-1-3
The stop-your-jobs clause is untested and the hazard may not arise in headless. In all 12 E5 and pilot runs the worker waited until the job finished, so no stray process existed in either arm (m6 = 0 everywhere); wave 4's stray `until ... sleep` loops came from backgrounded 600 s waits, which an arm-B worker no longer starts. A test needs a job that outlives the worker: for example a brief that asks for a first result at 3 minutes and lets the job run on, or a worker that hits its time box. Also open: whether a worker can see its own background tasks' ids (the platform lists them as `task_id`) and whether `TaskStop` is reachable from a worker, which would be cleaner than `kill <pid>`.
refs: `__reports__/wave-05/author-w05-1/metrics.json` (m6 fields); `__scrupuli__/wave-05-explorer-w05-c.md` puzzle 1.

## S-w05-author-w05-1-4
The platform moves a Bash call past 120 s into the background unless the call carries `timeout:`. A worker that forgets it (arm A's pilot-A2 had `timeout: 130000`, A1 `timeout 580` with a long tool timeout) gets "moved to the background ... you will be notified"; the notice reaches it only between tool rounds. This is a second mechanism for waits that read no messages, and a third for the cold resume after the job ends. I did not test the notification path (a worker that backgrounds its job and ends the turn). Wave 4's waits of 313 to 602 s imply their calls carried `timeout:` up to 600000.
refs: `__reports__/wave-05/author-w05-1/pilot_tools/README.md` probe 2 side finding; `/private/tmp/murmuration-w05/author-w05-1/pilot-tools/run2_nohooks.jsonl` (task bpfhzz8vx).

## S-w05-author-w05-1-5
B3 copied `270` into both the Bash `timeout:` (270000, correct) and the shell `timeout` (should be 240), giving a 271 s call. My paragraph names both numbers in one sentence and a worker merged them. The rule's threshold (300 s) is met, the paragraph's own "4 minutes" is not. Rewording ("`timeout 240 ...` and, for the Bash call itself, `timeout: 270000`") would be an untested change, so I left it. A verifier may prefer a re-run of B with that wording.
refs: `__reports__/wave-05/author-w05-1/requests_B3.csv` (rows 7 and 8); `__pondus__/w05-c1.md`.

## S-w05-author-w05-1-6
The colgrep relative path behaves three ways: lab (headless, server folder = lab), plugin source (Desktop worktree; this session), and `PATH_NOT_FOUND` (wave 4, 2 of 5). I reproduced the first two and not the third, so I do not know what a worker's search would do in a third configuration (a lab in a subfolder, a worker started in `__reports__/...`). Also, the `research-loop` skill and `briefs.md` may repeat the relative path; I changed only the four agent files, which I was allowed to touch.
refs: `__reports__/wave-05/author-w05-1/c2_colgrep_path.md`; `__scrupuli__/wave-05-explorer-w05-c.md` puzzle 2.

## S-w05-author-w05-1-7
Measured cost per run is not only the worker's. `total_cost_usd` of a run includes the haiku dispatcher (about USD 0.01) and, for all 12 runs, the start of the subagent through the plugin's SubagentStart hook. The A/B difference (USD 0.565 median) matches the estimate for one cold request at 227k tokens (0.545), which suggests nothing else differs, but I did not decompose `modelUsage` per model for each run.
refs: `__reports__/wave-05/author-w05-1/metrics.json` (m3); `/private/tmp/murmuration-w05/author-w05-1/e5/runs/*/run.jsonl` final result record, field `modelUsage`.
