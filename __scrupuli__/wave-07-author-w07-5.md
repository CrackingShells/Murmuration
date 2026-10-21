## S-w07-author-w07-5-1
The Python guard hangs on one long word. `python3 -c write aaaa...` with a 300,000-character word makes `permission_guard.py` run longer than 40 s (killed by the checker), while the Rust binary answers in 0.05 s. Cause, read from the code and not profiled: `re.findall(r"[^\s'\"=,()]*(?:managed-settings...|settings(?:\.local)?\.json)", cmd)` is quadratic on a long run of non-space characters when an interpreter name and a write word are present. In the live platform the 20 s timeout would turn such a call into a block (onFailure block). Real calls rarely carry a 300 kB word, so this is a finding about the reference, not a reason to doubt the port; it is also the one place where B is not "the same decision" in practice (B allows, A times out and blocks).
refs: `__reports__/wave-07/author-w07-5/g1_full_run.txt` (STRESS rows), `scripts/check_guard_equal.py` (`tc:long_word`)

## S-w07-author-w07-5-2
The first exec of a freshly copied binary costs 152 ms here (median of 12 copies, later execs of the same file 24 ms) and of a freshly built one about 480 ms (3 builds), against explorer-w07-a's 330 ms for fresh C and Rust binaries. In the first headless B session the first guard call was recorded at 393 ms against 36-49 ms for the next ones. So the cost is per file, not per cdhash alone (the copy has the committed binary's cdhash, which this machine had already run from another path). Not explained: what is checked on a new file (syspolicyd, the endpoint-security extension) and whether the installer's copy could be made cheaper (a hard link, or running the binary once from the installer).
refs: `__reports__/wave-07/author-w07-5/g5.txt`

## S-w07-author-w07-5-3
I ran out of sessions for one run of my own mistake. The first Bstub session used a stub file that I had truncated (`open(p, "w").write(open(p).read())`), so it showed ENOEXEC instead of the crash and the hang, and I had to spend a session on a rerun; the cap of 44 sessions then left 19 pairs for g4, not the registered 20. The result: g2's crash and hang were run live (a Mach-O stub), g4 has 19 pairs. A reader who wants the 20th pair needs one more session.
refs: `__instrumenta__/w07c6_make_exports.py`, `__reports__/wave-07/author-w07-5/g2_live.md`

## S-w07-author-w07-5-4
The port agrees on every string-valued event but not on every JSON type. Where a tool input holds a float, a list or an object where Python would take `str(...)` of it (`content`, `new_string`, `new_source`) the Rust guard denies with `UnsupportedType`; Python allows (a list or dict is turned into its repr, which can carry the words). A non-empty list as `command` gives `TypeError` in Python for some shapes and a quirky joined string for others; Rust denies. These 10 of 189 odd-type events are reported apart, not gated. Does the platform ever send such types? Not seen in 8,722 recorded calls. Whether the registered rule's "every input" was meant to include them is the PI's call.
refs: `__reports__/wave-07/author-w07-5/g1_full_run.txt` (typeconf rows), `g1_differences_typeconf_stress.json`

## S-w07-author-w07-5-5
No mutation test of the checker. 0 differences in 20,847 gated events is only worth what the events can tell apart. The fuzz set denies 44% of its commands (4,414 of 10,000) and covers the attack words with case folds (`ſ`, `İ`, `ı`, Kelvin sign), Unicode spaces, unbalanced quotes, `sh -c` nesting, `cd` before a write, redirections, wrappers and heredocs, but I did not seed deliberate bugs into the port to see how many the checker catches. The first full run found nothing to fix, which is either a good port or a weak test; the port was written from the Python source, line by line, and the tables from Python's own `unicodedata`.
refs: `rust/tests/fuzz_vocab.json`, `scripts/check_guard_equal.py`

## S-w07-author-w07-5-6
The two arms of g4 are not the plugin as it is today. A is the guard rows in exec form (P3's form, not yet landed), so the saving measured is the Python interpreter's start and the guard's own work, not the shell chain that today's string form adds. Against today's shell form the saving would be larger by about two execs (explorer-w07-c: 36 ms against 116 ms for a Python hook). I measured the smaller number on purpose, and said so; but nobody has measured B against the string form that actually runs today.
refs: `__instrumenta__/w07c6_make_exports.py` (A rows), `__reports__/wave-07/explorer-w07-c/00-findings_v0.md`

## S-w07-author-w07-5-7
g4 shows a recorded hook duration, which is the spawn path plus the guard's own work, not a wall saving for the user in auto mode. explorer-w07-g found the PreToolUse hook hidden behind the classifier there (642 against 631 ms to dispatch). I ran g4 in default mode with an allow list, so the classifier is absent; the saving I show for the call's wall is therefore the default-mode one, and for auto mode only CPU (g3) is shown. The first number the PI will want, the energy at 1,788 starts a wave, is a multiplication I did not do (about 16 ms of CPU a start).
refs: `__reports__/wave-07/author-w07-5/g3_table.md`, `__reports__/wave-07/explorer-w07-g/00-findings_v0.md`

## S-w07-author-w07-5-8
The installer's cold path costs 853 ms (median of 10, min 807, max 887; one cold run took 1,042 ms; 3,340 ms once under Rosetta with the system Python 3.9) against 38 ms warm and 22 ms for an empty `python3 -S -I`. The cold path is the copy, one first exec of a new file (150 to 480 ms, S-w07-author-w07-5-2) and 12 payloads run twice (the binary and the Python guard). It is paid once per data folder and plugin version, and the SessionStart row's timeout is 10 s, so it fits; but it is 25 times the v0 installer's copy, and h3 ran at load 6.6 (other agents). Not tried: storing the expected outputs in the manifest, which would drop the 12 Python runs (about 0.5 s) at the price of a second thing that can go stale.
refs: `__reports__/wave-07/author-w07-5/v1/h3.md`

## S-w07-author-w07-5-9
What the manifest ties, and what it does not. It records that these binaries, this `permission_guard.py` and these Rust sources were together when `build_manifest.py` ran; it does not show that the binary was built from those sources (the builder writes the hashes of whatever is in the tree). The only behavioural tie is the self-test, 12 payloads. A binary that is right on those and wrong elsewhere installs. A reproducible build would close it, and bytes are not reproducible here (LC_UUID follows the output path). Also h1's last column ("decisions equal") is nearly tautological after a fallback, since the launcher is the Python guard; the evidence that carries h1 is the launcher, the notice and the named cause, and h4's live `permission_guard-EDITED` text.
refs: `__reports__/wave-07/author-w07-5/v1/h1_h2.md`, `__reports__/wave-07/author-w07-5/v1/h4_live.md`

## S-w07-author-w07-5-10
Hashing `rust/` at every session start needs `rust/` in the installed copy of the plugin. In the `--plugin-dir` exports it is there (I archived it). If a marketplace install left it out, the installer would say "the Rust sources cannot be hashed" and install the launcher: safe and visible, but the saving is lost. Open gap 3 (the installed-plugin path) is therefore still open and is the landing step's smoke run; I did not run an installed copy.
refs: `scripts/install_binary.py` (`doubt`)
