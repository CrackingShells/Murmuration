# P5 v0: read a combined short-option cluster containing `c` as `-c` in `bash`, `sh`, `zsh`, `dash`, `ksh` (registered before the change is written)

registered: 2026-10-24, by author-w08-14. Claim: w08-c14. Branch `w08-c14-shellc` (worktree `/private/tmp/murmuration-w08/author-w08-14/wt`, from `ab68424`). Prior: S-w08-reproducer-w08-10-5 (`bash -lc 'claude ... --bare'` is allowed on main), w08-c13 "not covered".

## The hole and what would differ if the claim were false

`expand()` descends into `bash -c '<script>'` only when the word `-c` is a token of its own, and takes the word after the first `-c` as the script. Hence on main: `bash -lc '<claude start with a bypass flag>'` allowed (hole 1); `bash -c -x '<script>'` reads `-x` as the script (hole 2, sibling: options after `-c`); `bash -ec`, `-xc`, `-ic`, `-euc`, `zsh -fc`, `bash -O extglob -c`, `bash --norc -lc`, `sh -c -- '<script>'` likewise.

The claim is false if, after the change, (i) any such form whose plain form (`bash -c '<script>'`, denied on main) is denied stays allowed in Python or Rust, or (ii) any case allowed before becomes denied that is not a form of the hole (a loosened case is a failure of "tightening only"), or (iii) Python and Rust differ.

## The change (guard only: `scripts/permission_guard.py`, `rust/src/guard.rs`, `rust/src/shlex.rs` if needed, `scripts/guard_selftest_holes.json`, case lists)

For a segment whose program (after wrappers) is one of SHELLS, `expand` reads the words after the program as the shell does: options come first; a word of one `-` and letters containing `c` is `-c`; `-o`, `+o`, `-O`, `+O` (a letter `o` or `O` in a cluster too) take the next word as value; `--rcfile`, `--init-file` take the next word; `--` ends the options; other `-x`/`--long` words are options; the first other word is the script when `-c` was seen, and is expanded as the string of `-c`. The old reading (the word after the first literal `-c` anywhere after the program) is kept as well, so every command expanded today is still expanded (monotone: the new reading only adds strings to read).

## Metrics

- **(a)** `w08_c10_registered_diff.py` before/after on the registered lists (wave-6 e3 lists): attacks denied stay denied, ordinary allowed stay allowed, per case.
- **(b)** The frozen set `__reports__/wave-08/explorer-w08-j/guard_replay_v0.json` (739 cases), before/after, Python and Rust: newly denied cases by label (a false-labelled one must be shown to be a combined-`c` form, named), true cases allowed not more than before, newly allowed 0. Also the recorded calls (`w08_c10_recorded_diff.py`).
- **(c)** Python and Rust equal on the frozen set, `scripts/check_guard_equal.py` (seed 0, default fuzz) and the new cases of `__instrumenta__/w08_c14_cases.py`.
- **(d)** `--selftest` of every script of `scripts/` and `__instrumenta__/` that has one.
- **(e)** clean clone of the branch: `scripts/install_binary.py` installs the binary, manifest matches the sources.
- **Hole closure (can fail).** `__instrumenta__/w08_c14_cases.py`: for about 30 base commands whose plain `bash -c '<script>'` form is denied on main (registered attacks, G1/G2/G3 forms), build the variants: shells x clusters (`-lc`, `-ec`, `-xc`, `-ic`, `-euc`, `-cl`, `-lec`, `-cx`), options before (`-l`, `-e`, `-x`, `-i`, `-o pipefail`, `-O extglob`, `--login`, `--norc`, `--noprofile`, `--posix`, `--rcfile F`), options after `-c` (`-c -x`, `-c -e`, `-c --`, `-c -o pipefail`), under wrappers (`env`, `sudo`, `timeout 5`) and nested (`bash -lc "bash -lc '...'"`). Law: plain form denied => variant denied. Run on main (the count allowed is the hole count) and on the branch (must be 0 except named residuals). Controls: the same variants of ordinary scripts (no bypass flag) must stay allowed; and clusters without `c` (`bash -lx script.sh --bare`, `bash -l`) must be decided as on main.

## Not claimed

`bash` reading its script from stdin (`bash -s`, pipe, heredoc into `bash`: heredoc is read as commands since w08-c13), a script held in a variable or file, `busybox sh -c`, `su -c`, `ssh`, `find -exec`, `$'..'` words, a shell named other than the five (`fish`, `csh`, `tcsh`, `rbash`, `bash5`, `pdksh`, `mksh`), `-c` under `+c`.
