# P5 v1: the Rust guard falls back to its reference on any doubt (registered after v0's results, before v1's runs)

registered: 2026-10-22, by research-pi, after w07-c6 (SUPPORTED, reproducer-w07-5) and saying so.
Claim: w07-c8 (builds on w07-c6).

## Why v1

v0 passes its rule, but its verifier found four gaps that matter for a guardrail
[source: `__pondus__/w07-c6.md` on `w07-p5-rustguard`, reproducer-w07-5's section]:

1. Nothing ties `bin/` to `rust/` or to `scripts/permission_guard.py`. A rebuild differs in 16–47
   bytes (LC_UUID and one signature page), so bytes cannot be compared, and an edit to the Python
   guard would silently stop applying wherever the binary runs.
2. The x86_64 binary has only quick Rosetta evidence and no artifact; an unrunnable binary blocks
   every Bash call.
3. The installed-plugin path has not been run.
4. A flipped byte inside the binary still ran with rc 0.

The rule for a guardrail is that doubt resolves to the reference, visibly, not to a block of every
call and not to a silent stale rule.

## The change (on top of v0, 029bdea)

- `bin/manifest.json`, written by the build step: per target, the sha256 of the committed binary;
  and the sha256 of `scripts/permission_guard.py` and of the `rust/` sources the binaries were built
  from.
- `scripts/install_binary.py` installs the binary only if (a) the binary's sha256 equals the
  manifest's, (b) the current `permission_guard.py` and `rust/` sources hash to the manifest's
  values, and (c) the installed copy, run on a fixed set of payloads (at least an allow, a G1, G2
  and G3 deny, and a malformed event), gives the Python guard's decisions. On any failure it
  installs the Python launcher instead and tells the session why: a SessionStart
  `additionalContext` line the model sees, and stderr.
- The pre-commit hook file and the CI file update the manifest; still files only, not installed
  or pushed.

## Ceiling and noise, before the rule (open item 27)

All metrics below are exact outcomes (installed binary or launcher, the notice present or not,
decisions equal or not), except h3's time, which is reported, not gated. The installer runs once per
session start; v0 measured a first exec of a fresh copy at about 152 ms, and each self-test payload
costs one exec of about 16 ms.

## Metrics and rule

- **h1 (each doubt falls back, visibly):** four faults, each in its own scratch install: a
  `permission_guard.py` edited after the build, a `rust/` source edited after the build, one byte
  flipped in the binary, and a binary that fails the self-test (for example the other target's
  binary under a name that does not run, or a stub that answers wrongly). In 4 of 4 the launcher is
  installed, the notice names the cause, and the registered cases are then decided as
  `permission_guard.py` decides.
- **h2 (the clean case):** an unmodified tree installs the binary; the x86_64 binary passes the
  self-test and a g1 quick run under Rosetta, with its artifact committed.
- **h3 (cost and races):** the installer's wall time per session start (median of 10), and 12
  concurrent installers against one data folder with 0 failed or wrong guard runs.
- **h4 (live):** in one headless session with a fault (h1's first), the model's context holds the
  notice and a Bash call is decided by the launcher; in one clean session, the binary decides.

**Landing:** h1–h4 pass and reproducer-w07-5 supports them. Then the merge to main is followed by a
headless smoke run from main's own tree, the installed plugin's path (open gap 3), and is reverted
if any Bash call is blocked that main's guard would allow.
