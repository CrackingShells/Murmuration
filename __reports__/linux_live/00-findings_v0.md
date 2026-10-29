# Murmuration 0.1.2 on Linux: the first live Claude Code session

**Date:** 2026-10-29
**Reminder:** `murmuration-linux-live` (36777AC9)
**Run by:** the ssh session "Linux live check on banyan" (local_e044ddb6) and a desktop session Eliott opened in the lab, where he typed the prompts
**Checked by:** the coordinating session, which re-read the install and the lab files over ssh after the run

## Answer

murmuration 0.1.2 installs from Nest on Linux and runs in a live Claude Code session. The compiled
x86-64 guard binary is used, not the Python fallback. Every check in the reminder passed.

One defect turned up: `user_words.py` stores a `<system-reminder>` block that the app appends
*after* the typed text. [source: banyan `~/explore/murmuration-linux-live/__statera__/user_words.md`, read 2026-10-29]

## Environment

| Item | Value | Source |
|:--|:--|:--|
| Host | banyan, a cluster login node. Ubuntu, Linux 6.8.0-147-generic, x86_64 | `uname`, probe 2026-10-29 |
| glibc | 2.39 (`Ubuntu GLIBC 2.39-0ubuntu8.9`) | `ldd --version`, re-read |
| Python | 3.12.3 | `.verified`, re-read |
| Claude Code | 2.1.309, from `~/.claude/remote/ccd-cli/2.1.309-537ebbf12df5` (the copy the desktop app runs on banyan). Desktop app 4.29.0 | session report |
| `claude` on PATH | no; there are no stored CLI credentials, so `claude -p` stops at `Not logged in` | session report |
| Lab | `~/explore/murmuration-linux-live`: `git init` was run, nothing is committed, and the lab is left in place | `ls`, re-read |

## Checks

| # | Check | Observed | Result | Seen by |
|:--|:--|:--|:--|:--|
| 1 | Install from Nest | `claude plugin marketplace add https://github.com/CrackingShells/Nest.git` (registers `cracking-shells`), then `claude plugin install murmuration@cracking-shells --scope project`. `plugin list` shows `Version: 0.1.2`, `✔ enabled`. The cache holds `murmuration/0.1.2` only | pass | session; cache listing re-read |
| 2 | Install path | `bin/murmuration` is an `ELF 64-bit LSB pie executable, x86-64`. Its sha256 `f027cb35…f64d4a2` equals `manifest.json` `x86_64-unknown-linux-gnu`. `bin/.verified` records the same hash and `python 3.12.3`. **The compiled binary is in use.** The binary needs at most `GLIBC_2.34` | pass | re-read (file, sha256, manifest, `.verified`) |
| 3a | `/lab` | Eliott typed `/murmuration:lab Does the Murmuration plugin run cleanly on a Linux cluster login node?`. It created `__statera__/` (`user_words.md`, `wave-01.md`), `__pondus__/`, `__scrupuli__/`, `__design__/`, `__instrumenta__/` and `.ignore`, and wrote the deny rules `Bash(pkill:*)` and `Bash(killall:*)` to `.claude/settings.local.json` | pass | re-read (`ls`, settings file) |
| 3b | Guard | Case a01 from `e3_attacks.json`, as PreToolUse JSON piped to the installed binary's `guard`, gave `deny`, `permission_guard (G1): the command carries --dangerously…`. `ls` returned 0 with empty output (allowed). Live in the lab, Bash calls (`lab_init.py`, `ls -la`) went through the `onFailure: block` hook without a denial | pass | session |
| 3c | Budget hook | Live: the lab session dispatched a general-purpose subagent, which replied `hi`, and `hookErrors: []`. The handback hook wrote `__statera__/handbacks/general-purpose-a872c02d.md` | pass | session; handback file re-read |
| 4 | Prompt recording | The typed prompt landed under `## 2026-10-29 15:59`. The `/lab` question landed under `## 15:58`, written by `lab_init.py`. A peer session's message was not recorded. The typed prompt's record had `promptSource: sdk` with `origin.kind: human` and was kept, so `origin.kind` decided | pass, with a defect | re-read (`user_words.md`) |

## Defect: trailing platform block stored as the user's words

The prompt `Report to @[Linux live check on banyan — reminder 36777AC9]` was stored together with the
`<system-reminder>\n<session-mentions>…</session-mentions>\n…</system-reminder>` block that the app
appends after an @-mention.

The cause: `LEADING_BLOCKS` in `plugins/murmuration/scripts/user_words.py:45-51` cuts platform blocks
only when they are anchored at `\A`, the start of the prompt. A block placed after the typed text is
kept. [source: plugins/murmuration/scripts/user_words.py@60d6efb]

Cutting trailing blocks too has a cost. A user who types or pastes text containing
`<system-reminder>` would lose it. A narrow fix would cut only a final block whose first inner line
is `<session-mentions>`.

## What this settles and what it doesn't

- **Settles:** the `claude_code_release` goal that "`claude plugin install murmuration@cracking-shells`
  works on … Linux" is now observed live on glibc 2.39 x86-64.
- **Settles, for this host:** typed prompts reach `user_words.md` on Linux. That fits the explanation
  for the macOS youzuoqi puzzle, where prompts sent from another session are dropped by design.
  [assumption: youzuoqi's test prompts came from another session; not checked]
- **Not covered:**
  - aarch64 Linux;
  - glibc below 2.35, where the Python fallback is expected;
  - musl;
  - a terminal `claude` login, as opposed to the desktop app's remote CLI.
- **Friction worth knowing:** the auto-mode classifier on banyan refused the marketplace add and the
  install ("Untrusted Code Integration") until Eliott approved them. The banyan-docs and banyan-hpc
  MCP servers fail to connect there because `uv` is not on PATH, which is unrelated to the plugin.

## Left in place

- `~/explore/murmuration-linux-live`, including `.run1.json` and `.run1.err` from the failed `-p` attempt
- `~/.claude/plugins/cache/cracking-shells/murmuration/0.1.2`
- `~/.claude/plugins/data/murmuration-cracking-shells/`
- Eliott's clone at `/home/eliott/src/CrackingShells/Murmuration`, untouched at 60d6efb
