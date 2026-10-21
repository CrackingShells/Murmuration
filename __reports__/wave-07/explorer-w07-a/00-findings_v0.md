---
type: findings
wave: wave-07
author: explorer-w07-a
date: 2026-10-22
version: v0
decision-required: confirm
---

# What an exec costs on this machine and in the platform's hook path: findings (v0)

I stayed in the brief; where I deviated: no `--plugin-dir` export (hooks went in through `--settings`, as wave 6 did), and only 3 headless sessions were run (budget and time, 28 of 30 min). All tables below use the load average recorded per batch; other agents ran throughout (load 4 to 14).

## Result

- **A process start here costs a fixed ~14 ms (min 12.6 to 14.9) before the child's first instruction, whatever the binary, language, build or signature, and it is not dyld.** `posix_spawn` returns after 172 us, `main()` is reached 14.2 to 16.4 ms later (median 16.4, p90 39.5 at load 4.4), a `fork()`+`_exit` with no exec costs 0.48 ms, and an exec that the kernel kills before any user code (a copied system binary, rc 137, cpu 0.03 ms) still costs 13.6 ms. Unsigned or malformed images are refused in 0.1 ms. So the 14 ms is in the kernel exec security path, not in the loader, libc init or the program. MEASURED [source: `stamp1_table.md`, `spawn3_table.md`; `__instrumenta__/w07a_spawn_stamp.c`, `w07a_spawn_bench.c`].
- **Every language lands on the same number.** At load 5.0 (n = 150 per case, round-robin, paired per round), median wall ms: C no-op 16.7, `/usr/bin/true` 15.9 to 21.6, Rust default, release, lto, panic=abort, strip, `opt-level=z`, `#![no_main]`, and `#![no_std]` + `no_main` (16 KB) all within +0.4 to +1.2 ms of the C no-op in their paired differences, whose p10 to p90 spread is -27 to +29 ms (noise at load 7). Hand-written arm64 assembly the same. `python3 -S -I -c pass` +7.8 ms, `python3 -c pass` +19.3 ms. The exec floor is ~14 ms; a language only adds what its runtime does after exec (CPU column: 1.4 ms C, 1.8 Rust std, 7.7 python -S -I, 20 python). MEASURED [source: `spawn1_table.md`].
- **S-w06-explorer-w06-b-1 is explained: counting execs.** `/bin/sh` on this macOS is a trampoline: `/private/var/select/sh -> /bin/bash`, so `sh -c X` is **two execs before X**; `/bin/dash -c :` and `/bin/bash -c :` are one (16.7 and 16.9 ms against `/bin/sh -c :` 32.5 ms; paired difference +15.4 ms [+13.5, +30.9], n = 150). A command that is not a shell builtin adds a **third** exec: `sh -c <C no-op>` is +44 ms over the direct C no-op, the same for a Rust binary (+44.5) and a `no_std` one (+45.4). The "Rust 18 ms slower than `sh :`" is the third exec (~16 ms), in any language. MEASURED [source: `spawn2_table.md`, `spawn1_table.md`, `ls -l /private/var/select/sh`].
- **The platform runs every command hook as `/bin/sh -c <command>`, with `claude` as the parent, and neither `CLAUDE_CODE_SHELL=/bin/bash` nor the hook field `"shell": "bash"` changes it.** A hook that wrote `ps -o command= -p $$ -p $PPID` showed `/bin/sh -c ...` with parent pid = the `claude -p` process, `$0 = /bin/sh`, `BASH_VERSION = 3.2.57` (bash in sh mode, after the trampoline); n = 4 in session 1, 24 `shellprobe_bash` rows in session 2 (the `"shell":"bash"` registration, the same). The environment's `SHELL` was `/bin/zsh`. MEASURED (n = 28 probes) [source: `shellprobe.txt`, `rows1.jsonl`, `table2b.md`; `__instrumenta__/w07a_hook_probe.py`].
- **The platform's recorded hook time is, to the millisecond, the time until the hook's `main()` starts; nothing after.** A C hook that stamps `CLOCK_REALTIME` at the first line of `main()`: platform `finished` line minus that stamp = 0 to 1 ms (13 hooks in session 1: 0, 0, 0, 0, 0, 1, 0 for `stamp`; 0, 0, 0, 0, 0, 1 for `execstamp`); the spawn-issue to `main()` interval was 52 to 103 ms (load 6 to 7) and equals the recorded duration within 1 to 9 ms. So 100% of a hook's recorded time is the spawn path (the 2 or 3 execs, plus the platform's issue time); the hook's own work is not in it for a no-op. MEASURED, n = 13 [source: `rows1.jsonl`, 13 rows with `main_ms`]. The session-2 re-join of stamps to rows (`rows2b.jsonl`) gave issue-to-main minimums (35 ms) below the recorded durations (47 ms), so its order-based join is unreliable and I do not use it.
- **First run of a freshly built binary costs ~330 ms, not 14 ms.** 24 binaries (12 C by clang, 12 Rust by `rustc -O`, each with a unique constant, so each a new cdhash, linker ad-hoc signed): first spawn median 329.7 ms (p90 369.8, max 389.9; C 332, Rust 330), spawns 2 to 4 of the same binary 26.9, 26.5, 26.5 ms, a control binary 26.4 ms (load 3.9 to 4.0; the 26 ms here is the same exec floor under load). First run slower than the binary's own later median by 294.8 ms (p10 278, p90 342), in 24 of 24. MEASURED [source: `fresh_table.md`, `fresh2_rows.jsonl`; `__instrumenta__/w07a_fresh_make.sh`, `w07a_fresh_table.py`]. Consequence for the plugin: a committed binary that is built on one machine and first run on another, or rebuilt per version/session, pays about 0.3 s once per new cdhash per machine; with 1788 starts per wave that is nothing, but a build-on-SessionStart design pays it every time.
- **Platform-recorded hook times, same session, interleaved** (session 2, two sessions, load 4.2; the model made more than the requested calls, n 27 to 93): `: ` 52 ms median (min 30, p90 149), `: #b` with `"shell":"bash"` 66 (min 31), C no-op 96 (min 47), C no-op with `exec` 86 (min 48), `python3 -S -I -c pass` 96 (min 54), `/bin/sh -c :` 102 (min 61). The minima follow the exec count: 30 ms (builtin: 2 execs), 47 to 48 ms (a binary: 3 execs), 61 (a builtin through a nested `sh`: 4 execs), and the medians are 1.5 to 2.2 times the minima because the machine was loaded. MEASURED [source: `table2b.md`, `rows2b.jsonl`; the per-variant `if` registration makes variants share a session's load but they are not paired, so I give no paired spread for these].
- **The ceiling (ESTIMATE).** Lowest platform-recorded hook start here: 30 ms (a shell builtin as the whole command; 2 execs; n = 43, min 30). The lowest for a binary: 47 ms (3 execs). What no language choice removes: the `/bin/sh` trampoline plus bash (about 2 x 14 ms = 28 ms) is 93% of the 30 ms floor, 60% of the 47 ms floor of a binary hook; the third exec (the binary itself) is the language-dependent part and it is ~16 ms in every build tried, so a Rust, C or assembly hook buys nothing against another except the CPU after exec. The platform's own bookkeeping outside exec is ~2 ms at the minima (30 minus 28 for `sh -c :` bare at its own minimum) but ~14 to 19 ms at medians under load (52 to 70 ms recorded against 56 bare at load 6.8) [formula: recorded minus bare minimum from `spawn1_table.md` and `table2b.md`; the loads differ between the two, so this is an ESTIMATE].
- **What the exec does on the machine (CONJECTURE).** An endpoint-security client is installed on this machine (`systemextensionsctl list`: `com.crowdstrike.falcon.Agent`, Falcon Sensor, an Endpoint Security extension). Over 4 alternating pairs of 600 spawn windows against equal idle windows (ps cputime, 10 ms resolution), `opendirectoryd` used **+10.8 ms CPU per spawn** [min 9.2, max 18.9] and the Falcon agent +4.2 [0.9, 12.1]; the same measurement over 1000 `fork()`+`_exit` (no exec) windows gave opendirectoryd +0.04 and Falcon -0.17 ms per fork; a second exec series gave opendirectoryd +12.3 [4.5, 25.0] per spawn and Falcon -2.8 [-34.6, 24.6]. So the exec-specific work is a lookup chain through `opendirectoryd`, in step with the 14 ms. That the ES extension is the cause is not shown: I cannot unload it (SIP on, no root), and `eslogger` needs root.

## Table

Bare spawn (C harness, `posix_spawn`+`wait4`, stdout/stderr/stdin to /dev/null, warm), batch 1 (n = 200 per case, load 6.8 at median; the paired column is per round against the C no-op; rows in `spawn1_table.md`):

| Case | wall median ms | p90 | min | CPU median ms | paired diff vs C no-op median [p10, p90] |
|:--|--:|--:|--:|--:|:--|
| `/usr/bin/true` | 21.6 | 64.7 | 14.5 | 1.31 | -0.9 [-30.8, +15.9] |
| `/bin/sh -c :` | 56.1 | 156.8 | 28.3 | 3.24 | +27.5 [+12.8, +94.5] |
| `/bin/bash -c :` | 27.9 | 80.1 | 14.6 | 1.65 | -0.2 [-14.7, +18.3] |
| C no-op | 26.9 | 68.8 | 14.9 | 1.45 | 0 |
| Rust default / release / lto / strip / abort / z+lto+abort / `no_main` / `no_std` | 26.7 to 29.0 | 71 to 80 | 14.6 to 15.4 | 1.5 to 1.8 | +0.4 to +1.2 |
| `sh -c <C no-op>` / `<Rust release>` / `<Rust no_std>` | 72.6 / 80.1 / 75.8 | 202 to 220 | 43.7 to 44.2 | 5.1 to 5.4 | +43.7 / +44.5 / +45.4 |
| `python3 -S -I -c pass` (miniforge) | 34.1 | 77.7 | 20.8 | 7.65 | +7.8 [-12.7, +25.0] |
| `python3 -c pass` | 45.3 | 97.4 | 32.3 | 20.2 | +19.3 [-5.1, +45.3] |

Batch 2 (n = 150, load 5.0) and batch 3 (n = 200, load 11.4 to 14.0) isolate the shells and the failure paths (`spawn2_table.md`, `spawn3_table.md`):

| Case | wall median ms | min | paired diff vs C no-op |
|:--|--:|--:|:--|
| C no-op (batch 2) | 16.7 | 14.4 | 0 |
| `/bin/sh -c :`, `-c ''`, `-c 'exit 0'`, `--version` | 32.5 / 32.6 / 33.4 / 31.9 | 27.3 to 29.3 | +15.1 to +15.8 |
| `/bin/dash -c :`, `/bin/bash -c :`, `bash --posix -c :`, `bash --version` | 16.7 / 16.9 / 16.8 / 15.9 | 14.0 to 14.2 | -0.7 to -0.2 |
| copied `sh`/`dash` (killed at exec, rc 137, cpu 0.03 ms) | 14.6 / 15.3 | 13.0 / 13.8 | -2.0 / -1.2 |
| (batch 3, load 11.4) C no-op | 16.0 | 14.9 | 0 |
| (batch 3) killed copy of sh | 14.0 | 12.9 | -2.2 [-4.5, -1.1] |
| (batch 3) `ENOEXEC` file, nonexistent path, unsigned static binary (refused with errno 85) | 0.16 / 0.09 / 0.13 | 0.07 to 0.11 | -15.9 |

Phases of one start (batch `stamp1`, n = 300, load 4.4):

| Phase | median us | p90 us | min us |
|:--|--:|--:|--:|
| `posix_spawn` returns | 172 | 211 | 140 |
| return to child's first line of `main` | 16 394 | 39 495 | 14 203 |
| last line of `main` to `wait4` returns | 211 | 252 | 166 |
| `fork()` + `_exit(0)`, no exec | 481 total | 556 | 354 |

Platform hook path:

| Item | Observed | Label | Source |
|:--|:--|:--|:--|
| Hook shell | `/bin/sh -c <cmd>`, parent `claude`, regardless of `CLAUDE_CODE_SHELL=/bin/bash` and `"shell":"bash"` | MEASURED n=28 | `shellprobe.txt` |
| `/bin/sh` | `/private/var/select/sh -> /bin/bash`: sh = trampoline = 2 execs | MEASURED | `ls -l`, `spawn2_table.md` |
| recorded time after hook `main()` | 0 to 1 ms | MEASURED n=13 | `rows1.jsonl` |
| per-exec cost | 14 ms min, 16 ms median (load 4 to 5) | MEASURED | `stamp1_table.md` |
| hook min by exec count | 30 ms (builtin), 47 (binary), 61 (builtin via nested sh) | MEASURED (min of n 31 to 43) | `table2b.md` |
| first exec of a new cdhash | +295 ms [278, 342], 24 of 24 | MEASURED | `fresh_table.md` |
| dyld + libSystem init + exit for a no-op | at most ~1.5 to 2 ms (exec of a binary killed before dyld costs 1.2 to 2.2 ms less than a running one), ESTIMATE; `DYLD_PRINT_STATISTICS` printed nothing on this macOS; `DYLD_PRINT_LIBRARIES` works for non-system binaries (35 images for `libSystem`, all from the shared cache) | ESTIMATE | `spawn2_table.md`, `spawn3_table.md` |
| static binary without dyld (`LC_UNIXTHREAD`) | refused on arm64: unsigned killed, ad-hoc signed killed (rc 137) | MEASURED n=1 | `static_exit.s` |

## Worst-fitting case

The story "an exec costs 14 ms everywhere, so the shell chain is what matters" fits worst in two places. (1) The platform's recorded medians are 1.5 to 2.2 times its minima, and the unpaired variant medians are in the wrong order for the exec count (`: #b` 66 ms vs `:` 52; `cnoop` 96 vs `execcnoop` 86; `execcnoop` 86 is not better than `cnoop` 84 to 96): at load 4 to 14 with other claude sessions running, per-variant medians in this design (variants interleaved but not paired) cannot rank variants within ~20 ms; only the minima and the bare paired benchmark can. The one-line reading "a builtin-only hook is 30 ms, a binary 47 ms" rests on minima. (2) The 14 ms floor sits on this machine's endpoint-security stack (CONJECTURE, correlation of daemon CPU with execs only); on a machine without it a bare exec is likely 1 to 3 ms and the whole picture (language not mattering) would shift: dyld and the runtime's CPU would be most of what remains. All numbers here are for this M3 Pro, macOS 26.6.2, Falcon 8.10 installed. The case that fits best: `fork`+`_exit` 0.48 ms against exec of the identical no-op 16.4 ms, 34 times.

## Not covered

- Which part of the 14 ms is Falcon, AMFI, syspolicyd or the kernel: not separable without root (`eslogger`, `fs_usage`, dtrace). A machine without the endpoint extension would give the control.
- A signed vs ad-hoc vs Developer ID comparison (no identity here; every binary is linker ad-hoc signed; `codesign -f -s -` re-signing was not timed). The quarantine xattr and XProtect effect on a downloaded binary: not tested; the 330 ms first-run figure is for locally linked binaries, and I did not separate what the 330 ms is made of (syspolicyd assessment, Falcon file analysis of a new file, or both).
- A paired design inside one session for platform hooks (same variant pairs per turn); `async: true`, `http` hooks (explorer-w07-c's); how `claude` spawns (the process uses `posix_spawn` or fork+exec: not looked at); the platform's own ~2 to 19 ms outside exec.
- Python from `/usr/bin/python3` and `/opt/homebrew/bin/python3`: only miniforge's `python3` (first on PATH) was timed; what the platform's PATH resolves to for `python3` was not checked.
- Only 3 headless sessions (1 + 2); the model made 238 and 145 hook rows against 90 requested per session in session 2, so call counts per variant are uneven.
- The stamp join in session 2 (see Result); `rows2b.jsonl`'s `main_ms` fields should not be used.

## Steering questions

- [now] Should the plugin's hooks be written so that the common case is a shell builtin (`case`/`read` in the hook string itself, 2 execs, 30 ms recorded) and the process-start of a script happens only when the gate says so? This is B1 of wave 6's list, and it is now explained, not just measured: a binary in any language costs a third exec (~16 ms) that only avoiding the exec removes.
- [now] Is a one-off first-run cost of ~330 ms per new binary cdhash acceptable for a committed Rust binary (no: if the binary is rebuilt per session), and should a build-on-first-use design be dropped?
- [later] Re-run the bare benchmark on a machine without the endpoint extension (or the same machine with the sensor absent) to know how much of the 14 ms is this machine's.

## Pointers

Scratch: `/private/tmp/murmuration-w07/explorer-w07-a/` (debug logs there carry account identifiers: not copied). Raw artifacts, copied to `__reports__/wave-07/explorer-w07-a/`:
- `spawn1.jsonl`, `spawn1_table.md` (cases `cases1.tsv`): `w07a_spawn_bench cases1.tsv 200 3 > spawn1.jsonl; python3 -I __instrumenta__/w07a_spawn_table.py spawn1.jsonl --ref c_noop`. Same for `spawn2` (cases2) and `spawn3` (cases3, 200 rounds). Build: `clang -O2 -o spawn_bench __instrumenta__/w07a_spawn_bench.c`; binaries from `noop.c`, `noop_std.rs`, `noop_nomain.rs`, `noop_nostd.rs` (`-C link-arg=-lSystem`), `noop_asm.s` with the flags named in each row (`opt-level=z`, `lto=fat`, `panic=abort`, `strip=symbols`).
- `stamp1.jsonl`, `stamp1_table.md`: `w07a_spawn_stamp 300` (`clang -O2 -o spawn_stamp __instrumenta__/w07a_spawn_stamp.c`).
- `fresh2_rows.jsonl`, `fresh_table.md`: `sh __instrumenta__/w07a_fresh_make.sh $PWD/fresh2 24 4 $PWD/bin/c_noop; w07a_spawn_bench fresh2/cases.tsv 1 0 > fresh2_rows.jsonl; python3 -I __instrumenta__/w07a_fresh_table.py fresh2_rows.jsonl 4`.
- `daemon_cpu.md`, `daemon_cpu_fork_vs_exec.md`: `python3 -I __instrumenta__/w07a_daemon_cpu_pairs.py 600 4 -- w07a_spawn_bench cases4.tsv 600 0` (the fork-versus-exec file: `... 1000 4 -- w07a_spawn_stamp 1000 0 {1|0}`; its head cut the exec arm's table to 4 rows).
- `rows1.jsonl` (session 1), `rows2b.jsonl`, `table2b.md` (sessions of job 2), `shellprobe.txt`: `CLAUDE_CODE_SHELL=/bin/bash python3 -I __instrumenta__/w07a_hook_probe.py plat/w1 bin --sessions 1 --calls 8 --seed 11`; job 2: `plat/w2 bin --sessions 2 --calls 9 --seed 22 --variants colon,colon_bash,cnoop,cnoop_bash,execcnoop,stamp,stamp_bash,shellprobe_bash,shc,pysi`, re-read with `--reparse` after fixing the command-text match.
- Scripts at this report's commit: `__instrumenta__/w07a_spawn_bench.c`, `w07a_spawn_stamp.c`, `w07a_spawn_table.py`, `w07a_daemon_cpu_pairs.py`, `w07a_fresh_make.sh`, `w07a_fresh_table.py`, `w07a_hook_probe.py`, `w07a_stamp_hook.c`.
