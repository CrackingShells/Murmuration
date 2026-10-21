## S-w07-reproducer-w07-7-1
The guard's Bash deny of a bypass-flag command could not be exercised from a reproducer's session. The plugin's own guard and the auto-mode classifier deny writing the test prompt (G1 on the heredoc, G4 on a script that builds the flag from two strings, the classifier on reading wave 6's existing instrument's string). So the guard stops its own tests from being authored under it. Is that wanted? A tester needs a prompt file the user places, or a session without the plugin.
refs: __reports__/wave-07/reproducer-w07-7/00-smoke_v0.md ("Not run"); /private/tmp/murmuration-w07/reproducer-w07-7/stubbin/claude (no stub.log was ever written)

## S-w07-reproducer-w07-7-2
A plain `sleep 30` in a worker's Bash is blocked by the platform ("Blocked: standalone sleep 30 ... Do not chain shorter sleeps"), before the PreToolUse guard runs (pi_terminal: 2 Bash calls, 1 guard.log line). The `until`-loop form the message suggests went through. Does a brief or skill anywhere tell a worker to wait with `sleep`? Explorer w99-1 in pi_terminal also reported the block as a departure from its brief.
refs: __reports__/wave-07/reproducer-w07-7/raw/check_pi_terminal.txt, raw/pi_terminal_guard.log

## S-w07-reproducer-w07-7-3
The brief says six scripts' selftests; seven scripts in `scripts/` carry `--selftest` (budget, handback, lab_init, lab_status, permission_guard, resume_brief, user_words). All seven pass. `run_hook.py` has none. Which six did the PI mean, and should lab_init's selftest, whose output talks about colgrep indexes of the machine's temp folder, count?
refs: __reports__/wave-07/reproducer-w07-7/raw/selftest_rc.txt, raw/selftest_lab_init.txt

## S-w07-reproducer-w07-7-4
In a short session (r1_guard_inherited, 15.8 s) the inherited-environment prompt left no `user_words.md` entry, and the debug log only says the async hook "moved to the background"; no line says it finished or what it decided. So the absence of an entry cannot tell "dropped by the origin rule" from "killed at session exit". What separates them is the paired sessions (terminal-like kept in 35 s and 150 s sessions, inherited dropped), not a hook record. A log line from the hook for each drop would make this checkable.
refs: __reports__/wave-07/reproducer-w07-7/raw/r1_guard_inherited_user_words.md, raw/check_r1_guard_inherited.txt
