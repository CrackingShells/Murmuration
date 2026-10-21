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

- 01:50, after author-w07-1 returned (w07-c1, P1):
  - **P1 does not land, by its rule, and I do not override it.** p2–p4 pass: the PI without the
    Skill tool read `research-loop` and its references at the real path (6 of 6, 0 failed Reads),
    took the same 3 requests, and ran `/lab-status` and `/lab`. But p5 fails on a real loss: the
    built-in `dataviz` skill has no `SKILL.md` on disk, so a PI without the Skill tool cannot reach
    it (0 of 2), and wave 6's PI used it. p1 fails in one pair (8,236 against 9,000) on a noise
    source my registration missed: the deferred tool-name list changes with which MCP servers have
    connected at launch (110 to 229 names, `mcp__arangodb__*` alone 119), about 2.4k tokens. Where
    the names match, the drop is 10.6–11.9k tokens.
  - Why no override, when wave 6 overrode e2: there the rule failed at the physical ceiling of an
    identical-behaviour change. Here a capability is lost. By the user's "User experience and
    efficiency downstream is what matters", a PI that cannot draw a figure with the user's own skill
    is a worse PI for about 11k cached tokens a request (an ESTIMATE of USD 1 a wave at cache-read
    price, to be priced in the synthesis from `lab_status.py`'s prices).
  - What the lab learned: the listing is all or nothing, and the PI's request 0 is not a constant of
    the plugin. It moves by thousands of tokens with the user's MCP servers' connection timing
    (S-w07-author-w07-1-1). reproducer-w07-1 checks the numbers the synthesis will quote.

- 02:00, after explorer-w07-d returned:
  - **Parallel-first does not pay in `lab_status.py`, and the reason is the algorithm.** Cold, the
    script takes 0.90 s, 0.65 s of it Python parsing 274 MB. A forked pool of 12 or a Rust helper
    on 6 threads brings that to about 0.32–0.33 s. The warm cache it already has takes 0.39–0.42 s,
    and 0.155 s of that is a `git worktree list` child, not parsing. So the user's "know your
    algorithms" comes first here: an incremental cache beats a parallel re-parse, and the remaining
    waste is a process start. I do not ship a pool or Rust for it.
  - **What the machine taught:** parse scaling flattens at the 6 performance cores (Python pool
    6.0x at 12 workers; Rust 87 ms on one thread, 16–17 ms on 10–12, efficiency 0.42–0.53); each
    efficiency core adds about 0.3–0.5 of a performance core. On macOS, `spawn` (the default start
    method) costs 63–172 ms a pool against 2–10 ms for `fork`, which would cancel the gain. Rust's
    parser is 7x Python's on one core, yet the whole script would gain little, because the fixed
    costs are elsewhere. A rayon split by file size plateaued; one task per file was 2x faster.
  - **A silent under-count:** `merge_usage` drops `speed` and `server_tool_use`, so fast mode and
    web searches are never priced (S-w07-explorer-w07-d-2). No record has them yet.
  - Registered P4 v0 (`__reports__/wave-07/03-protocol_p4_labstatus_v0.md`): drop the git child
    with a fallback, and carry the two usage fields, sign-test rule. author-w07-4 runs it as w07-c4.
  - The other serial CPU loop, `w06c13_v7_diff_two_guards.py`, goes from 8.7 s to 1.7 s at 6
    workers; it is a one-off instrument, so nothing to land. Headless cells are API-bound.

- 02:10, after reproducer-w07-1's verdict on w07-c1 (OVERSTATED):
  - Every number recomputes from the raw transcripts. The statement's "10.6k–11.9k where the names
    matched" is too wide: the matched pairs give 10,620–10,952; 11.9k is an unmatched pair. And
    "unreachable" holds for `dataviz`'s `SKILL.md` body only; its `references/` are readable by
    path. Not restated, since no decision depends on it (B does not land either way); the synthesis
    quotes the verifier's figures. The verifier adds that over a 3-request session B's input was
    25–35k tokens lower, because the 10k-character SKILL.md then enters later requests.

- 02:25, after author-w07-2 returned (w07-c2, P2 v0):
  - **Right offline, blind live.** The origin rule classified 2,965 recorded prompts with 0
    errors, and the outputs equal main's except where it drops a session's or the harness's
    message. But q2 fails: a prompt's record is written after the UserPromptSubmit hooks exit, so
    the synchronous hook never sees it (found in 1 of 10 within 0.3 s), and its poll adds 0.3 s to
    every prompt. A replay could not have caught that; only the live run did.
  - **Platform fact:** the only field that tells a Desktop spawned session from a terminal `-p` is
    `entrypoint`, and a `claude -p` started from Desktop's Bash inherits `claude-desktop`. So the
    lab's own headless probes look like spawned sessions; they are throwaway labs, so dropping
    their prompts is harmless.
  - **P2 v1 registered** (`__reports__/wave-07/01-protocol_p2_origin_v1.md`): the same rule from an
    `async: true` hook, which explorer-w07-c measured as not holding up the loop. A new mechanism,
    so a new claim, w07-c5, by the same author (warm).

- 02:40, after explorer-w07-a returned:
  - **The machine's floor is one exec, about 14–16 ms, whatever the language.** `posix_spawn`
    returns in 0.17 ms and `main()` starts 14–16 ms later; a binary the kernel kills before any user
    code still costs 13.6 ms; `fork()` without exec costs 0.48 ms. dyld and libSystem are at most
    about 2 ms. C, assembly and every Rust build are within 1.2 ms of each other; `python3 -S -I` is
    +7.8 ms. The cause of the 14 ms is a CONJECTURE: the kernel's exec security path, with the
    Falcon endpoint-security extension installed and `opendirectoryd` burning about 11 ms of CPU per
    exec but none per fork. A new binary's first exec costs about 330 ms, once.
  - **Wave 6's two unexplained numbers are exec counts.** `/bin/sh` is a trampoline into bash (two
    execs), so `sh :` is 33 ms; a binary behind `sh -c` is a third exec, which is the Rust no-op's
    "+18 ms" (S-w06-explorer-w06-b-1). The platform runs every hook as `/bin/sh -c`, whatever
    `CLAUDE_CODE_SHELL` or `"shell"` says, and its recorded `durationMs` ends 0–1 ms after the
    hook's `main()` starts: the recorded time is all spawn path. explorer-w07-c's exec form removes
    two of the three execs. The two probes, run independently, agree.
  - **So Rust comes back, on top of exec form.** Registered P5 v0
    (`__reports__/wave-07/04-protocol_p5_rustguard_v0.md`): the permission guard as one Rust
    binary, picked per platform at session start through `${CLAUDE_PLUGIN_DATA}`, with the Python
    guard as fallback and reference; exact decisions over the whole corpus; a paired bench and an
    in-platform sign test. author-w07-5 runs it as w07-c6.
  - **Spend so far:** this checkout USD 15.11 at least (0.98 at opening), headless under
    `/private/tmp/murmuration-w07/` 1.22, so at least USD 15.35 of the 47
    [source: `scripts/lab_status.py --spend` and `--project /private/tmp/murmuration-w07 --spend`, 02:35].

- 02:50, after explorer-w07-g returned:
  - **The Bash call's 1.5 s is the classifier and the program, not the hooks.** In paired
    headless arms, a trivial Bash call's tool phase is 55 ms in default mode and 709 ms in auto
    mode, 628 ms of it the classifier's wait; the worker-like arm (auto, colgrep hook, lab plugin)
    is 1,054 ms. The workers' 1.49 s median is not a trivial call: 1,623 of 1,869 run a program
    (median 1.72 s); bare `ls`/`cat` take 1.02 s. The missing 0.6–0.9 s of b is accounted for.
    The classifier's wait doubles between identical sessions (528 against 1,015 ms) and does not
    grow with context from 42k to 102k tokens.
  - **A PreToolUse hook hides behind the classifier in auto mode** (CHECKED): the wait to dispatch
    is 642 ms with the colgrep hook, 631 ms without. The PostToolUse hook is not hidden (70–80 ms a
    call). The lab's hooks are about 0.5% of summed worker wall, the classifier about 1.9%
    (ESTIMATE). So P5's guard saves CPU and energy in auto mode and wall only elsewhere; a note says
    so in its protocol before its run. The budget's PostToolUse is the hook a worker actually waits
    on; it follows the guard if the pilot holds.
  - **Four reads, four ways (n = 1 each):** four Reads in one message 2.83 s; one chained `cat`
    3.39 s; four Bash calls in one message 3.79 s; four Reads in four messages 5.11 s. Reads never
    reach the classifier. The lesson for the workers' text, if any: independent reads go out as
    Reads in one message, not as Bash. Not yet a claim: b found 0.8–1.6% of requests batchable.
  - **The subagent cache lifetime has a plugin-side lever** (CHECKED by reading the binary):
    `experimental: {cacheTtl: "1h"}` in an agent file. The break-even nets authors +USD 4.49 of
    43.90 over three waves and loses on the others. Registered P6 v0
    (`__reports__/wave-07/05-protocol_p6_cachettl_v0.md`), authors only, exact counts from the usage
    records. author-w07-6 runs it as w07-c7.

- 03:00, after author-w07-2 returned (w07-c5, P2 v1):
  - **The async hook sees the record.** 10 of 10 first prompts were found and decided by origin
    (5 dropped as another session's, 5 kept as a terminal's), within 0.2–0.7 s, and the platform
    ran the hook in the background (1–4 ms) in 11 of 11. r1 again 0 errors on 3,001 records.
    Missing: main's synchronous arm for r3 (n = 1) and a synchronous crash control.
  - **Platform fact found by accident:** two hook rows with the same command string are merged
    into one, with nothing in the debug log (S-w07-author-w07-2-7). P3 and P5 should know it.
  - The time from a prompt to its first API request is set by a user-level synchronous hook
    (`inject_plan_directive.py`, 177–206 ms), not by the lab's.
  - reproducer-w07-2 verifies w07-c2 and w07-c5 together, and runs the two missing controls.

- 03:10, after author-w07-4 returned (w07-c4, P4):
  - o1–o4 pass by the rule (28 of 30 pairs faster; repeats 24 and 29 of 30). But the saving is
    0.051 s a call, about a third of the 0.155 s I took as the ceiling: that figure was a
    difference of two medians under load 3–15, not a paired measure. My registration repeated a
    small form of item 27: a ceiling read from unpaired medians.
  - **PI decision: change 1 does not land, change 2 does (pending the verifier).** Change 1 saves
    a few seconds a wave (about 50 calls) and re-implements git's worktree list; its first version
    gave the enclosing repository's list for a missing folder and for a bare repository, silently,
    and got the order wrong where git ignores case. The git child cannot fail that way. That is a
    failure-mode cost the rule did not price, and by the user's own measure ("efficiency
    downstream is what matters") a few seconds a wave do not buy it. Change 2 is a correctness fix:
    fast mode and web searches were never priced. The author splits it onto its own branch.
  - A cache bump makes an old and a new script sharing one cache rewrite each other's file; the
    author measures it before the landing.

- 03:20, after author-w07-3 returned (w07-c3, P3):
  - **Exec form holds.** x1 (42 of 42 handlers equal after the shell's own splitting, and the
    check can fail), the scripted x2 (215 of 215 starts equal) and x4 pass: B was lower in 10 of 10
    pairs for both hooks. Medians per pair: guard 76.8 ms saved (pooled 123 → 42 ms), budget
    PostToolUse 71.0 ms (104.5 → 41 ms); about 3.0 s of hook time a session. B fails closed when
    the guard crashes and when `python3` is missing, with different wording and fewer transcript
    records of the repeated failure (the debug log has all). The live graded budget note in A was
    not shown (the platform refused the worker's bare `sleep`), so the verifier runs it.
  - **What it does not show:** a shorter session. Tool-call intervals differed by a median 54 ms
    with a spread of ±600 ms, and session wall was not lower. That fits explorer-w07-g: the
    classifier and the model dominate, and a PreToolUse hook hides behind the classifier. So exec
    form is CPU, energy and hook time, with downstream wall unresolved; the synthesis says so.
  - **x5:** `args` exists since 2.1.139; `onFailure` since 2.1.295, above the README's stated 2.1.271
    (a wave-6 slip). A version without `args` would feed the payload to `python3` as a script: a
    silent no-op guard. So the README's minimum must say 2.1.295 in the same landing.
  - reproducer-w07-3 verifies, with the missing live note, the failure cases and its own pairs.

- 03:40, after author-w07-4's split and author-w07-6 returned:
  - **w07-c4's landing build** (`w07-p4b-usage`, 1bc47d0): change 2 only, byte-identical output on
    a frozen clone, fast mode and web search priced. An old and a new script sharing one cache made
    every call cold (0.955 s against 0.25 s); a cache file named by its version removes that.
    reproducer-w07-4 verifies.
  - **w07-c7 (P6):** the agent-file key is honoured for a plugin author (all writes 1-hour in B,
    all 5-minute in A), and after a 422 s gap B read 99.98% of its context against A's 40.8%. c1–c3
    pass, so it lands by its rule if reproducer-w07-6 supports it. The money is nearly even: the
    author's recomputation over 19 authors with a gap rule nets +USD 0.87 of 47.80 (ESTIMATE),
    explorer-w07-g's +4.49 counted every re-write as saved, and the sign turns if re-writes fall
    below 0.385 of write tokens (observed 0.414). What the rule did not price is time: a resumed
    author reading 100k+ tokens instead of re-writing them starts its answer sooner. I keep the
    rule as registered; the synthesis states the estimate with its fragility.

- 03:55, after reproducer-w07-2's verdicts (w07-c2 SUPPORTED, w07-c5 SUPPORTED):
  - **PI decision: P2 v1 lands.** Reproduced: 0 errors offline on 3,027 records; live, 3 of 3
    inherited first prompts dropped, 4 of 4 terminal-like kept within 0.13–0.39 s; the hook in the
    background in 8 of 8; no visible added wait against main's synchronous row (median 0.158 s
    against 0.250 s, interleaved but not randomised); 21 failure cases equal to main's. Of the
    `user_words.md` entries it could match, it drops exactly the three known wrong ones and no typed
    entry.
  - **Its two costs, accepted and stated:** a crash of the recorder under `async` leaves only a
    debug-log line, where main's synchronous row leaves a transcript record; and a prompt followed by
    a quit within about 0.4 s may go unrecorded. Against them: the lab stops writing another
    session's words as the user's, which is the record the user's question is read from. The script
    catches its own exceptions, so the silent case is an interpreter that does not start, which every
    other hook would show.
  - Not run by anyone: a live typed prompt in the Desktop. The first one after the merge is the
    check (the next `user_words.md` entry).
  - Protocol note: author-w07-2 added a note to the claim head during verification (open item 5,
    again); it states costs and changes no number.

- 04:15, after reproducer-w07-3 (w07-c3 SUPPORTED) and reproducer-w07-4 (w07-c4 SUPPORTED at
  c473203):
  - **Merged into this branch:** `w07-p2-origin` (2500241), `w07-p4b-usage` at c473203 (ad2440a),
    `w07-p3-exec` (5e16a53). The one conflict, the `user_words` row, takes both: exec form and
    `async`. The README's minimum goes from 2.1.271 to 2.1.295, which `onFailure: "block"` needs and
    the guard has relied on since wave 6. The records of w07-c1 and w07-c4's dropped change come
    from their branches without their plugin edits (a656a69).
  - **The merge broke one selftest, and a hook did not:** `budget.py`'s selftest matched the hook
    row's command string, which exec form no longer has. No author or verifier ran it on the
    combined tree, because each branch was tested alone. Fixed (3c00fc6); all six scripts'
    selftests pass on the merged tree. The combined smoke run comes after P5 and P6.
  - reproducer-w07-3 reproduced exec form: the live graded note reached the worker in both arms,
    the guard 6 of 6 pairs lower (median 81.5 ms), budget 6 of 6 (57.2 ms), session wall unchanged.
    A missing `python3` blocks in both arms, but B names the cause on the first call only.
  - reproducer-w07-4: 21 usage shapes priced as intended at c473203; 1bc47d0 crashed `--spend` on
    an infinite search count. Dropped change 1 saves 0.04–0.05 s a call (9 of 10 pairs). The
    fast-mode factor and search price are the script's own, UNVERIFIED against a fetched page.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w07-a | explorer | what an exec costs on this machine and through the platform's hook path: sh, C, Rust, Python; dyld, signing, `sh -c` | ee7c125: one exec ≈ 14–16 ms any language; `/bin/sh` is two execs; hooks always `/bin/sh -c` |
| explorer-w07-b | explorer | the agent loop's time from transcripts: model, classifier, tools, hooks per turn; tool calls per request; what batching would save | be092ae: hooks 0.13% of wall; batching ≤ 1.6%; cache re-writes 15.8% of spend; Bash 1.5 s a call |
| explorer-w07-c | explorer | hooks without a process per call: `async: true`, `http` with `onFailure: block`, merged rows; fields, latency, dead-server behaviour | 8383dad: exec form 36 ms against 116; http 2 ms, loud on Pre/Post only; async silent on failure |
| explorer-w07-d | explorer | serial loops and algorithms in the lab's code: profile `lab_status.py` and the replays; scaling curves for parallel Python, a better algorithm, Rust | 19d5dce: warm cache beats pool and Rust; the git child is 0.155 s; scaling flat past 6 P-cores |
| explorer-w07-e | explorer | the PI's skills listing and the workers' allowlists: what can be excluded, and how, without losing `research-loop` | 546a4b9: `Skill` denied −11.7–12.0k tokens; listing all or none; Wolfram never called but costs names only |
| explorer-w07-f | explorer | read-only: where Claude Code enforces `disableBypassPermissionsMode`; how `user_words.py` can tell a session's message from the user's (item 28) | 70629c1: first-wins managed tier, the file probably dropped; `origin.kind` marks typed prompts |
| author-w07-1 | author | w07-c1: P1, the PI without the skills listing | 9a942f3 (branch w07-p1-skill): p1 and p5 fail; does not land |
| reproducer-w07-1 | reproducer | verify w07-c1 offline, for the numbers the synthesis quotes | d72b8d3: OVERSTATED (matched range 10.6–11.0k) |
| explorer-w07-g | explorer | split the classifier-decided Bash call's 1.5 s; four ways of the same reads; subagent cache lifetime | 3292ed5: classifier 628 ms, hooks hidden behind it; `cacheTtl` frontmatter |
| author-w07-3 | author | w07-c3: P3, every hook row in exec form | 2e043b7: x1, x4 pass (10/10, ~71–77 ms a start); x2, x3 mostly; wall unresolved |
| reproducer-w07-3 | reproducer | verify w07-c3, with the missing live note and failure cases | 9658909: SUPPORTED |
| author-w07-4 | author | w07-c4: P4, `lab_status.py` without the git child, usage fields priced | 627fb4d: o1–o4 pass, 0.051 s a call; change 1 dropped by PI decision; change 2 split for landing |
| author-w07-5 | author | w07-c6: P5, the permission guard as a Rust binary in exec form | |
| author-w07-6 | author | w07-c7: P6, a 1-hour cache for authors | 6041f28: c1–c3 pass; c4 +USD 0.87 of 47.80, fragile |
| reproducer-w07-4 | reproducer | verify w07-c4's landing build (change 2) | ffd1f6b: SUPPORTED at c473203 |
| reproducer-w07-6 | reproducer | verify w07-c7, c2 rerun apart | |
| reproducer-w07-2 | reproducer | verify w07-c2 and w07-c5, with the missing controls | SUPPORTED both; async crash silent; v1 lands |
| author-w07-2 | author | w07-c2: P2, `user_words.py` keeps only typed prompts | e84afec (branch w07-p2-origin): q1 passes, q2 fails (record written after the hook); resumed for v1 as w07-c5; 7fbee58: v1 r1, r2, r4 pass; r3 and crash controls missing |

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
