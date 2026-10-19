## S-w02-reproducer-w02-2-1
My independent extraction differs from the author's by exactly one typed record: the slash-command record of 566fa912 (`<command-message>scheduling-work</command-message>\n<command-name>/scheduling-work</command-name>\n<command-args>…`, 271 characters in the transcript) against the author's rebuilt `/scheduling-work <args>` (162 characters). The 109-character gap in both columns of the character total comes from this one record. What the hook's `prompt` holds for a slash command is the assumption the claim names ("assumed") and nobody has dumped it. If the real payload is the expanded XML form, the rule stores `<command-message>…` as the user's words; the rule does not handle it (it is not cut, and `is_bare_command`/`LAB_COMMAND` do not match it). The 72 / 51 / 0 does not depend on it, but what is stored for a skill invocation does.
refs: __reports__/reflective_run/w02/reproducer-w02-2/headline.py, __reports__/reflective_run/w02/author-w02-2/replay_rows.tsv

## S-w02-reproducer-w02-2-2
The block regexes end in `\s*`, so the first typed line loses its indentation when a platform block precedes it, and keeps it when none does. `unwrap_pasted` also strips leading blank lines from prompts that carry no wrapper. Both are invisible in the 72 real prompts (0 affected) and appear in no selftest case; the claim lists "the indentation of the first line" as kept untouched.
refs: __reports__/reflective_run/w02/reproducer-w02-2/cases.py, scripts/user_words.py lines 33-37 and 77-79

## S-w02-reproducer-w02-2-3
The new rule drops 8 platform notices that the old rule stored (reminder chain ending in `<side-sessions-event>`), but the claim cannot say whether those notices ever reach the `UserPromptSubmit` hook. If they do, the old rule had been storing about 30k characters of non-user text per study and the new one removes it; if they do not, the third regex has no use. The author calls the benefit unproven and the cost nil; the one-line cost is a regex that nobody can test against a real firing.
refs: __reports__/reflective_run/w02/author-w02-2/replay_output.txt, __pondus__/w02-c2.md

## S-w02-reproducer-w02-2-4
The head says MEASURED, the body adds a CONJECTURE (Task 2) whose facts are MEASURED headless. A reader of `/lab-status` sees one label per claim. Whether a claim that joins a measured fix and a conjectured prototype should be filed as two claims is a question the format does not answer.
refs: __pondus__/w02-c2.md

## S-w02-reproducer-w02-2-5
The author edited the shipped file (sha256 63603d78 -> bac8b5cf) and the claim head after my independent result, and reported that the PI agreed to the head sentence. I re-ran the checks on the new file, but I cannot see that agreement anywhere in a file; the process has no artifact for "PI agreed to a head edit" (the author's own message is the only trace). Because a head edit rewrites what a verdict was about, a one-line record in the claim file would help.
refs: __pondus__/w02-c2.md
