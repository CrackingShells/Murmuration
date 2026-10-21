# w05-c2: colgrep `paths` form, one search per case (CHECKED, 4 searches, 2 sessions)

Query for case 1 and 2 (session: the Desktop worktree session of author-w05-1, cwd `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/lab-system-optimization-1aa673`, plugin source and "additional working directory" `/Users/hacker/Documents/src/CrackingShells/Murmuration`): "E5 runner that builds plugin exports A and B and samples the process tree of headless workers", `pattern` `w05c1|PARAGRAPH`, `limit` 5. The script `__instrumenta__/w05c1_wait_arms.py` is committed in the worktree only (fc4d118); the main checkout does not have it.

| Case | `paths` | Echoed `paths` | Hits |
|:--|:--|:--|:--|
| 1 Desktop worktree, old form | `["__instrumenta__"]` | `/Users/hacker/Documents/src/CrackingShells/Murmuration/__instrumenta__` (the plugin source, not the lab) | `budget_arms_export.sh`, `e3_table.py`; `w05c1_wait_arms.py` absent |
| 2 Desktop worktree, new form | `["/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/lab-system-optimization-1aa673/__instrumenta__"]` | the same absolute path | `w05c1_wait_arms.py` first (score 1.68), then `budget_arms_export.sh`, `e3_table.py` |
| 3 headless lab in /private/tmp, old form | `["__instrumenta__"]` | `/private/tmp/murmuration-w05/author-w05-1/c2b/lab/__instrumenta__` (the lab) | `zz_lab_only_probe.py` (exists only in that lab) |
| 4 headless lab in /private/tmp, new form | the absolute path of that folder | the same | `zz_lab_only_probe.py` |

Cases 3 and 4: `__instrumenta__/w05c2_colgrep_path_probe.sh /private/tmp/murmuration-w05/author-w05-1/c2b` (haiku, USD 0.0085; a first run by hand gave the same, USD 0.0088). In that run the server's folder is the lab, so the relative form works; in the Desktop session the server's folder is the plugin source (the main checkout), so it does not. The absolute form found the lab-only script in both. Wave 4's `PATH_NOT_FOUND (relative paths ...)` in 2 of 5 searches is a third behaviour of the relative form that was not reproduced here.
