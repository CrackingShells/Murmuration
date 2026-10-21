## S-w05-research-pi-1
My task lists for the user, and the plans in four wave notes, never include a step that revises the
plan. The research-loop skill says "plan only the current wave", but neither `waves.md` nor
`templates/wave.md` has a place for a mid-wave reassessment, and the agents' files never mention
one. Is the checklist shape coming from me, from the procedure, or from the task-list tool? And does
a lab without re-plan points measurably pay for runs whose reason has expired? Wave 4's E3, E3b and
E3c each ran after the previous one showed the test did not test finding.
refs: __statera__/wave-04.md (Notes, "PI decision" entries), skills/research-loop/references/waves.md, skills/research-loop/templates/wave.md

## S-w05-research-pi-2
The plugin is read in place from the main checkout's working tree (CLI "Read from:"), yet
`installed_plugins.json` records a cache install at 9eb759b for every worktree, re-recorded at this
session's start. "Updating the installation" therefore changes nothing that runs. And
`--scope local` from a worktree writes to the main checkout's settings. So which settings file does
a Desktop worktree session actually read?
refs: ~/.claude/plugins/installed_plugins.json, /Users/hacker/Documents/src/CrackingShells/Murmuration/.claude/settings.local.json, .claude/settings.local.json
