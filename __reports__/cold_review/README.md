# Cold reviews

Reviews of the files that ship with the plugin, read by an agent that had never seen the project.
Each round reads only `agents/`, `skills/`, `scripts/`, `hooks/hooks.json`, `.claude-plugin/plugin.json`
and `README.md`, and checks them on five axes: meta-discourse, cold usability, consistency between
the skill's formats and the scripts, agent tool lists against role instructions, and silent
failures.

| Round | File | What it holds |
|:--|:--|:--|
| 0 | [`00-findings_v0.md`](00-findings_v0.md) | First pass: 37 findings (4 blockers, 17 should-fix, 16 nits) |
| 1 | [`01-findings_v1.md`](01-findings_v1.md) | A verdict on each round-0 row (20 fixed, 8 partly, 9 not fixed), then a fresh pass: 16 new findings (1 blocker, 4 should-fix, 11 nits) |
