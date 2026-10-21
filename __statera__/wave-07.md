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

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| explorer-w07-a | explorer | what an exec costs on this machine and through the platform's hook path: sh, C, Rust, Python; dyld, signing, `sh -c` | |
| explorer-w07-b | explorer | the agent loop's time from transcripts: model, classifier, tools, hooks per turn; tool calls per request; what batching would save | |
| explorer-w07-c | explorer | hooks without a process per call: `async: true`, `http` with `onFailure: block`, merged rows; fields, latency, dead-server behaviour | |
| explorer-w07-d | explorer | serial loops and algorithms in the lab's code: profile `lab_status.py` and the replays; scaling curves for parallel Python, a better algorithm, Rust | |
| explorer-w07-e | explorer | the PI's skills listing and the workers' allowlists: what can be excluded, and how, without losing `research-loop` | |
| explorer-w07-f | explorer | read-only: where Claude Code enforces `disableBypassPermissionsMode`; how `user_words.py` can tell a session's message from the user's (item 28) | |

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
