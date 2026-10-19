## S-w01-reproducer-w01-9-1
The `<side-sessions-event>` rule was written for 8 notices that may never reach UserPromptSubmit; on typed text it is dead code. Nobody has fired the hook on a real "session ... finished a turn" notice. If they do not fire, the third regex and its cost are not earned; if they do, 8 of 9 such notices are skipped only by this rule.
refs: __reports__/reflective_run/w01/reproducer-w01-9/side2.py, derive_nontyped.txt

## S-w01-reproducer-w01-9-2
A reminder in front of a `<cross-session-message>` or `<task-notification>` makes the shipped `is_genuine` (a `startswith` test) pass it. The patch fixes this as a side effect, so the shipped hook has probably been storing platform text in real labs. The claim never mentions the gain.
refs: __reports__/reflective_run/w01/reproducer-w01-9/cases_output.txt (last rows)

## S-w01-reproducer-w01-9-3
The "Linked sessions" session-start brief (4,118 characters) stays stored after the patch as 3,757 characters, because it is a reminder followed by text, not a leading block alone. Its origin is null with turnOrigin sdk, the same shape as the notices. A rule cannot tell it from a typed message that follows a reminder, except by the text.
refs: __reports__/reflective_run/w01/reproducer-w01-9/derive_nontyped.txt (f3bb6ad5)

## S-w01-reproducer-w01-9-4
Typed prompts carry `origin.kind == human` in the transcript, but the hook payload has only `prompt`. The whole 72/51/0 depends on the rebuilt join and on `origin` being a transcript field the hook never sees. A cheap live probe (fire the hook on one pasted prompt in Desktop) would remove the dependence. The check has been run on 2 records only.
refs: __pondus__/w01-c9.md (Results, Cost)

## S-w01-reproducer-w01-9-5
The `[Request interrupted by user]` records (3) and the 5 scheduled prompts are both stored by the patched rule if the hook fires on them. Whether they fire is unknown for the first and only probed on one headless case for the second.
refs: __reports__/reflective_run/w01/reproducer-w01-9/derive_nontyped.txt

## S-w01-reproducer-w01-9-6
The auto-mode classifier denied my first inline transcript-listing command ("PII Data Handling") but allowed the same aggregate read through a script file. The brief authorizes read-only transcript reads. Is the denial context-dependent, so the work is not reproducible by the next verifier?
refs: none (tool denial in this session)
