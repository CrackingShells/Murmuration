# P5 v0: SA1's pilot, the permission guard as one Rust binary in exec form (registered before any run)

registered: 2026-10-22, by research-pi, before author-w07-5 starts. Claim: w07-c6.

## Why now, and why the guard

- explorer-w07-a: on this machine one exec costs about 14–16 ms before the child's first
  instruction, whatever the language. C and every Rust build come within 1.2 ms of each other;
  `python3 -S -I -c pass` is +7.8 ms. Today's hook string costs three execs (`/bin/sh`, a trampoline
  into bash, then the program); exec form costs one. [source:
  `__reports__/wave-07/explorer-w07-a/00-findings_v0.md`]
- So in wave 6, a Rust start next to a Python one was a few ms inside 47+ ms of shell execs. Under
  exec form (P3), what is left of a Python hook is its one exec plus its interpreter and its own
  work, and Rust can remove the last two. The user: "I don't see how that exempts us from saving
  that 1% if we know we can save it."
- The guard is the pilot because it runs on every Bash call and on 30 Write/Edit rows, fails closed,
  and has the lab's best test corpus (121 registered cases, 4 malformed events, 5,136 recorded
  calls; w06-c13, w06-c14). `budget.py` and `handback.py` would follow in the same binary only if
  the pilot holds.

## The change (B against A)

- A = the guard rows of `hooks/hooks.json` in exec form, starting `python3 -S -I
  scripts/permission_guard.py` (P3's form, applied to A by the author in the test export only if P3
  has not landed yet).
- B = a Rust crate (`rust/` in the repo, std plus crates already in the local cargo cache, built
  `--offline`) with one binary, `murmuration`, whose `guard` subcommand gives the same decision as
  `permission_guard.py` on every input. Binaries for `aarch64-apple-darwin` and
  `x86_64-apple-darwin`, built locally and committed under `bin/<target>/`. No other target is
  built (no download; the user decides on CI).
- How a git-installed plugin picks its binary without a shell: a SessionStart hook (Python, once per
  session) copies the binary for this platform to `${CLAUDE_PLUGIN_DATA}/bin/murmuration` when it
  is absent or differs. When no binary fits this platform, it writes a launcher there that runs
  `permission_guard.py` instead. The guard rows exec `${CLAUDE_PLUGIN_DATA}/bin/murmuration guard`
  with `onFailure: block` and the same 20 s timeout. `permission_guard.py` stays, as the fallback and
  as the reference the binary is tested against.
- A `scripts/check_guard_equal.py` that replays the corpus through both and fails on any
  difference, for a dev git hook. The dev git hook and a CI workflow that builds the other targets
  are written as files for the user and not installed or pushed.

## Measured ceiling and noise, before the rule (open item 27)

- Ceiling per guard start, B against A, both in exec form: Python's start over a native no-op
  (+7.8 ms, explorer-w07-a) plus the guard's own work (w06-c14: 65 ms a Bash call in shell form,
  about 47 ms of which is three execs, so roughly 15–20 ms of Python start and work). So about
  15–25 ms a start, an ESTIMATE.
- Noise: explorer-w07-a's paired spawn bench resolves differences of about 0.4–1.2 ms (n = 150–200);
  platform-recorded hook times scatter about 20 ms a pair (w06-c9). So the outside bench can decide
  the sign with many pairs, while the in-platform sign test needs more pairs than P3's, and may
  still fail on noise alone. That is stated now, so a failure of g4 alone is read as "not shown",
  not as "no saving".

## Metrics and rule

- **g1 (same decisions, exact):** over the 121 registered cases, the 4 malformed events, the lab's
  recorded Bash/Write/Edit/NotebookEdit calls (5,136 at w06-c14; the current set, counted) and a
  fuzz set of at least 10,000 generated commands, B's exit code, stdout and decision equal
  `permission_guard.py`'s in every case. Any difference fails.
- **g2 (failure):** B blocks the Bash call (fail closed, visible to the model) when the binary
  crashes, when it is missing from `${CLAUDE_PLUGIN_DATA}`, and when it hangs (the 20 s timeout).
  With no binary for the platform, the launcher's decisions equal A's (g1's registered cases), live.
  The SessionStart copy fails visibly, never silently, when the data folder cannot be written.
- **g3 (time, outside the platform):** a paired bench, the hook's payload on stdin, B against A
  both started directly by `posix_spawn` (explorer-w07-a's driver), at least 200 interleaved pairs on
  a sample of recorded Bash payloads: B faster in at least 190. Report the median saving, its
  spread and the load.
- **g4 (time, in the platform):** 20 alternating pairs of headless sessions, the guard's recorded
  PreToolUse duration lower in B in at least 15 of 20. Report the median per-pair saving.
- **g5 (what it costs to ship):** the binary's size per target, the first-exec cost of a fresh copy
  (explorer-w07-a measured about 330 ms once per new binary), build time, and the crate's
  dependencies. Reported, not gated.

**Landing:** g1, g2 and g3 pass, g4 passes or fails only on noise as defined above (B's median
saving positive), and reproducer-w07-5 supports them. Otherwise the crate stays on its branch, with
its numbers in the synthesis.

**Not covered, said now:** Linux and Windows (no target built here), the Desktop app, and
`budget.py` and `handback.py`.
