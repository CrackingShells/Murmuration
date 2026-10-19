## S-w02-reproducer-w02-9-1
The new rule trades one failure for another: a stray `verdict:` line quoted after the real verdict now wins, and only a warning shows it, while the old first-line rule survived that and failed on a revision. Which ordering is likelier in practice: a verifier revising in place (one case in 21 sections, w02-c4) or one quoting a line after closing (none)? Would a rule keyed on `changed_by:` itself (the revised verdict is the one followed by `changed_by:`) avoid both?
refs: scripts/lab_status.py `current_label`; __pondus__/w02-c4.md lines 80, 92, 94

## S-w02-reproducer-w02-9-2
My own brief and the PI's task wording say "the first line starting `verdict:` is the verdict", which the patched skill now reverses, so briefs given before and after this lands contradict each other. Also, the `changed_by:` check accepts any line starting `changed_by:` below the earlier verdict, including an empty value or a path that does not exist. Nobody checks that "a new artifact" is new.
refs: skills/research-loop/SKILL.md lines 75-80; agents/reproducer.md line 26

## S-w02-reproducer-w02-9-3
The template in SKILL.md puts `changed_by:` as the third line of one verdict block, which suggests a revision rewrites that block rather than adding a second verdict line. The patch accepts both: one verdict line plus `changed_by:` stands as is, and two lines need `changed_by:` between them. Does the skill say which form a verifier should use, and does a single block with `changed_by:` after an unrevised verdict look different from a revision to anyone reading the state?
refs: skills/research-loop/SKILL.md lines 66-73
