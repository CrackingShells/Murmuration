## S-w05-reproducer-w05-8-1
The pathspec-commit sentence installed by w05-c8 fails for the commonest agent output, a new untracked file: `git commit -m m -- newfile` errors with "pathspec ... did not match any file(s) known to git" unless `git add newfile` came first. The check script never tries a new file, and its two-file case uses tracked files only.
refs: __instrumenta__/pathspec_commit_breaks.sh (cases 6 and 7, run with a scratch dir); skills/research-loop/references/briefs.md rule 5 at 73a7565

## S-w05-reproducer-w05-8-2
A named path that another agent also staged and edited is committed whole, with their edit and without leaving their staging behind. "Commits only the named paths" is true, but the guarantee does not protect two agents who touch one file.
refs: __instrumenta__/pathspec_commit_breaks.sh (cases 3 and 3c)

## S-w05-reproducer-w05-8-3
Clock labels in `__statera__/wave-05.md` Reassessments (14:5x ... 17:4x) run ahead of the git commit times of the notes that carry them (the "17:4x" entry was committed at 16:00, the machine clock read 16:01 JST). The claims w05-c8 ("after 16:5x") and w05-c9 ("14:5x to 16:5x") repeat the labels. Nothing in the files says where the labels come from.
refs: `git log --format='%h %ad %s' --date=format:%H:%M -- __statera__/wave-05.md`; __statera__/wave-05.md lines 50-132

## S-w05-reproducer-w05-8-4
w05-c9's entry 5 ("a rule gap caught before its claim could pass on it") does not match the record: w05-c3's head disclosed the connector loss in its own text at 15:24, one minute before E6b was added, and w05-c3 then passed SUPPORTED. Who saw the gap first cannot be told from the files.
refs: __pondus__/w05-c3.md ("Not kept ... real cost"); `git log` times of b3910ff, c599890, 0bd9570, 56f21e3

## S-w05-reproducer-w05-8-5
Evidence that earlier PIs "did not re-plan" cannot come from wave notes 1-4: those record closing state. Wave 2's dispositions already say a finding "switched the budget hook off", which is a plan change recorded elsewhere under another name. The user's remark ("you never consider replan") is about the plans, and the plans are not in the notes.
refs: __statera__/wave-02.md lines 48-59, 79, 119; __statera__/wave-0{1,3,4}.md

## S-w05-reproducer-w05-8-6
The incident attribution in w05-c8 (author-w05-2's commit carrying author-w05-3's staged revert) is not recoverable from git: all commits share one author identity. Only the stat (10 files, +1922/-1454, equal to the inverse of 4c46fe4's 1454/-1921 plus one line) is checkable.
refs: `git show --stat baba44f`; `git show --stat 4c46fe4`
