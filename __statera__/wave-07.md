# Wave 07

opened: 2026-10-22

## The user's sentence this wave serves

From `__statera__/user_words.md` (2026-10-21 23:28 and 23:50), in the user's words:

> Yes, and this extents to "know your algorithms", leverage "parallel-first" because the Modern
> hardware is done that way (this applies to all the parsing or possible for loops). Of course, I
> know that parallelism also has a cost at the CPU level and that scaling is not linear [...] I
> think "Performance-aware programming and Better Software" is a mindset we should apply everywhere.

> i think you don't have to obsess over this idea. Try explore other possibilities. Don't forget
> your nature as a research PI. All this also teaches us things about our hardware and limit of
> optimizing Claude Code's agent loops.

> I know the classifier call dominates, but I don't see how that exempts us from saving that 1% if
> we know we can save it.

> the deny list for the Pi was smart. I wonder if this applied to the other agents as well? If you
> scan the available MCP servers and SKILLS we have here, aren't there some we know we can exclude?

And from the session that started this one (not the user's own words; relayed): "line of codes are
not a reference for leanness [...] User experience and efficiency downstream is what matters."

Budget: what is left of the wave-6 USD 100, at least USD 47 (wave 6 spent at least 53.00;
`__statera__/wave-06.md`, Notes). Spend baseline at opening: `scripts/lab_status.py` TOTAL USD
291.49 at least, this checkout 0.98 at least [source: `scripts/lab_status.py` at b614915, 00:25 JST].

## What does not add up

- **Six waves timed the plugin's hooks to the millisecond, and never timed the loop they sit in.**
  A worker's tool call costs a model request (seconds), the auto-mode classifier (0.45–0.75 s on
  Bash), and then the hooks (tens of ms). The lab has optimised the smallest of the three. If the
  user's "limit of optimizing Claude Code's agent loops" is real, it is in the first two: how many
  requests a task takes, and how many tool calls go out per request. Parallel-first, applied to the
  agent loop, is one message carrying several independent tool calls. No wave has counted that.
- **The machine's own floor is unexplained.** `sh :` costs 33 ms as the platform records it, a
  Rust no-op 18 ms more than `sh` (S-w06-explorer-w06-b-1), Python 55 ms. On an M3 Pro a bare
  `posix_spawn` of a tiny binary should cost about 1 ms. Something sits between: dyld, code-signing
  checks of a new binary, the platform's `sh -c`, or its own spawn path. Until that is known, "Rust
  saves 30 ms" and "Rust saves 1%" are both readings of an unexplained number.
- **The lab's own code is serial everywhere.** `lab_status.py` parses about 228 MB of JSONL on one
  core; the replays and experiment pipelines run cells one after another; wave 4's critical path was
  one author's serial headless cells. This machine has 12 cores (6 performance, 6 efficiency).
- **The resident server was one way of not starting a process, and it failed on silence.** The
  platform offers others the lab never tried: `async: true` command hooks, `http` hooks that can
  fail closed, fewer registrations. None is assumed to work.
- **The PI reads 30,072 characters of skills listing to use one skill**, and the workers' allowlists
  may still carry servers no worker has ever called.
- **The managed setting is read but did not stop a `-p` run from entering bypass mode** (n = 1,
  `__reports__/wave-06/research-pi/managed_setting_check.md`). Why is not known.

## Reassessments

- 00:30, before any dispatch: six probes, one per direction, each small (explorer-w07-a to -f).
  No experiment rule is registered yet: rules come after the probes give a ceiling and a per-pair
  noise for what they would measure (open item 27).

- 00:52, after explorer-w07-e returned:
  - **The listing goes only whole.** Denying `Skill` removed the listing and the Skill schema,
    about 11.7–12.0k tokens of a headless PI's 31.5k request 0 (37%), and the PI still reached
    `research-loop` by Read and still ran `/lab-status` (n = 1 per variant, MEASURED). `Skill(...)`
    deny rules did not touch the listing, `skillOverrides` reached only the non-plugin skills, and
    disabling 19 plugins left 41 skills listed. So the answer to the user's "aren't there some we
    know we can exclude?" is: not one by one; the PI can drop all or none.
  - **What it costs is reach, not the procedure.** A Read of SKILL.md leaves `${CLAUDE_PLUGIN_ROOT}`
    literal in its reference table (S-w07-explorer-w07-e-1), and the PI called `writing-history`
    and `dataviz` once each in six sessions. Both are design requirements of B: the body names the
    root, and says how to find another skill.
  - **Registered P1 v0** (`__reports__/wave-07/00-protocol_p1_skill_v0.md`, committed before the
    run), threshold 9,000 tokens against a ceiling of about 11.7k and a noise range of 329.
    author-w07-1 runs it as w07-c1; reproducer-w07-1 verifies.
  - **The workers' allowlists:** Wolfram was never called by any worker in six waves, but MCP tools
    are deferred in workers, so it costs its 15 names (an ESTIMATE of 115–186 tokens), inside the
    replicate noise. Dropping it is safe and saves almost nothing; I leave it, and say so. The
    larger worker leak is elsewhere: 61 of 72 reproducers and authors spend an early request on
    `ToolSearch` for `SendMessage`, because it is deferred (S-w07-explorer-w07-e-4). That is a
    model request per verifier and author, seconds each; it goes to explorer-w07-b's frame of
    requests per task when b returns.

- 01:05, after explorer-w07-f returned:
  - **The managed file is probably not the managed tier on this account** (CHECKED by reading the
    2.1.304 binary, not run). Claude Code takes one managed source, first-wins: server-managed,
    then MDM, then `managed-settings.json`. `~/.claude/remote-settings.json` holds
    `channelsEnabled`, which counts as policy content, so the file is dropped. The check itself is
    not interactive-only. My own reading of the file's mtime is 2026-10-18 18:40, not "refreshed
    today" as the report says; it does not change the inference. This is the user's guardrail: the
    guard's Bash row stays, and the report gives the user two tests to settle it (`/status`, and a
    `touch` under the flag with a debug file). No worker runs them.
  - **Item 28 has its marker.** The transcript marks origin (`origin.kind` `human` for typed
    prompts; `sdk`, `peer`, `task-notification` otherwise); the hook payload does not, but carries
    `prompt_id`. Registered P2 v0 (`__reports__/wave-07/01-protocol_p2_origin_v0.md`) before its
    run; author-w07-2 runs it as w07-c2, reproducer-w07-2 verifies. My decision on the open
    question: a headless `-p` prompt is kept, because a person may run a lab headless.
  - `user_words.md` holds three wrong entries (17:18 and 00:22 are spawned sessions' first
    messages; 00:12 "say ok" is the user's own `-p` test). No agent edits that file; the synthesis
    names them.

- 01:20, after explorer-w07-b returned:
  - **The hooks are 0.13% of a worker's wall.** Over waves 4–6 (47 workers, 2,633 requests), a
    worker's wall is 30.8% model requests, 20.1% tool phases under 120 s, 25.5% longer ones, 22.3%
    idle waits for a message, 1.3% client gaps; thinking is 41% of model time (MEASURED). The lab
    spent six waves on the smallest line of this table. The user's "1% we know we can save" still
    stands for the hooks, but the order of the work changes.
  - **Parallel-first at the message level is already done, inside the shell.** 92% of worker
    requests carry one call, yet batching independent calls would have saved 0.8–1.6% of requests
    (ESTIMATE, after a hand audit of 62 pairs): 75% of Bash calls already chain three or more
    statements, serially, and the next call usually needs the last result. I drop message batching
    as a lever.
  - **What is larger than the hooks, by size:** cache re-writes after gaps over 300 s (23 misses,
    15.8% of worker spend); tool results over 5,000 characters re-read by every later request
    (29.7% of cache-read spend); retries after refusals (8.5% of wave 6's requests: the
    worktree-isolation refusal of complex `git`, the harness's `sleep N` refusal); and every Bash
    call decided by the classifier, median 1.54 s against 0.01 s for one decided by mode or rule and
    0.16 s for a Read. Only part of the 1.5 s is the classifier's measured 0.45–0.75 s.
  - **Next:** explorer-w07-g splits the Bash call's 1.5 s (auto against default mode, plugin hooks
    on and off, classifier time against context length, four ways of doing the same reads) and
    looks for a subagent cache-lifetime setting. Allow rules would remove the classifier, but they
    are the user's permission layer (item 23); what the lab can change is which tool its workers
    reach for.
  - Effort (thinking, S-w07-explorer-w07-b-5) is not varied this wave: the lab has no measure of a
    worker's quality that a lower effort could be checked against.

- 01:35, after explorer-w07-c returned:
  - **The floor was the shell.** A hook in exec form (`command` plus `args`, no shell) cost the
    platform 36 ms against 116 ms for the same script in today's string form; a whole tool call
    with a Pre and a Post hook 174 ms against 314 ms; siblings start 14 ms apart instead of 40 ms
    (MEASURED, one session per arm, load about 9). The "+40 ms per sibling" of wave 6 is the
    platform's launch interval in shell form. Nobody questioned the shell because the lab measured
    `sh :` as if it were the empty hook. This is the first lever this wave that changes no script
    and keeps behaviour by construction: registered as P3 v0
    (`__reports__/wave-07/02-protocol_p3_exec_v0.md`), with a sign-test rule instead of a
    millisecond threshold, because the ceiling (the shell's share) is not yet measured on a quiet
    machine. author-w07-3 runs it as w07-c3; reproducer-w07-3 verifies.
  - **Rust comes back here, not earlier.** Once the shell is gone, what remains of a 36 ms start
    is the interpreter and the platform. A Rust binary in exec form is the next comparison;
    explorer-w07-a's floor decides whether it is worth building.
  - **`http` hooks are fast (2 ms) and fail loud on PreToolUse and PostToolUse with
    `onFailure: block`**, but end the whole session on PostToolBatch and stay silent on SubagentStop.
    A server still has to be started, given a port and a token. With exec form at 36 ms, `http`
    would save about 34 ms a start for a failure design the lab does not have yet. Not pursued this
    wave, as the user suggested; the records stay for item 31.
  - **`async: true`** does not block the loop and its `additionalContext` reaches the model at the
    next tool boundary, but its deny and block do nothing, a failure is silent, and an async hook
    still running at the end of `-p` is cancelled. Only a note that may be lost could use it; the
    budget block and the hand-back capture cannot. Parked for now.
  - **The largest hook on a Bash call is not the lab's:** the user's own `colgrep_policy`
    PreToolUse hook (`uv run`) took a median 431 ms per Bash call (n = 10, load 9). It is the
    user's configuration and another repository; it goes to the report as theirs.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w07-a | explorer | what an exec costs on this machine and through the platform's hook path: sh, C, Rust, Python; dyld, signing, `sh -c` | |
| explorer-w07-b | explorer | the agent loop's time from transcripts: model, classifier, tools, hooks per turn; tool calls per request; what batching would save | be092ae: hooks 0.13% of wall; batching ≤ 1.6%; cache re-writes 15.8% of spend; Bash 1.5 s a call |
| explorer-w07-c | explorer | hooks without a process per call: `async: true`, `http` with `onFailure: block`, merged rows; fields, latency, dead-server behaviour | 8383dad: exec form 36 ms against 116; http 2 ms, loud on Pre/Post only; async silent on failure |
| explorer-w07-d | explorer | serial loops and algorithms in the lab's code: profile `lab_status.py` and the replays; scaling curves for parallel Python, a better algorithm, Rust | |
| explorer-w07-e | explorer | the PI's skills listing and the workers' allowlists: what can be excluded, and how, without losing `research-loop` | 546a4b9: `Skill` denied −11.7–12.0k tokens; listing all or none; Wolfram never called but costs names only |
| explorer-w07-f | explorer | read-only: where Claude Code enforces `disableBypassPermissionsMode`; how `user_words.py` can tell a session's message from the user's (item 28) | 70629c1: first-wins managed tier, the file probably dropped; `origin.kind` marks typed prompts |
| author-w07-1 | author | w07-c1: P1, the PI without the skills listing | |
| explorer-w07-g | explorer | split the classifier-decided Bash call's 1.5 s; four ways of the same reads; subagent cache lifetime | |
| author-w07-3 | author | w07-c3: P3, every hook row in exec form | |
| author-w07-2 | author | w07-c2: P2, `user_words.py` keeps only typed prompts | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- The hook wrote this session's task message (from another session) into `user_words.md` as the
  user's words at 00:22: open item 28, again, in this worktree.

closed: YYYY-MM-DD
