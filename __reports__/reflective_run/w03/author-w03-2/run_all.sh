#!/bin/sh
# w03-c2: selftests, plugin validation, the colgrep scope probe, the baseline count over this study's workers, and (full only) the headless lab run and the author probe.
# Full:  sh run_all.sh <scratch dir outside the worktree> <session dir of the study>   about 10 minutes, about USD 2.0 by `total_cost_usd` (run1 1.57, author probe 0.39)
# Quick: sh run_all.sh <scratch dir outside the worktree> <session dir of the study> quick   selftests, validation, scope probe, baseline: about 1 minute, no model cost
# The scratch dir must be outside the worktree: headless runs below it register the plugin in ~/.claude/plugins/installed_plugins.json (w01-c14).
# Raw runs (run1.jsonl, the transcripts in ~/.claude/projects) hold the user's email and organization id: they stay out of git. Derived tables are written here.
set -e
H="$(cd "$(dirname "$0")" && pwd)"; W="$H/../../../.."; S="$1"; SESSION="$2"; Q="$3"
for f in budget handback lab_init lab_status resume_brief user_words; do python3 -I "$W/scripts/$f.py" --selftest; done
python3 -I "$H/bash_practice_measure.py" --selftest
(cd "$W" && claude plugin validate . | tail -1)
python3 -I "$H/colgrep_scope_probe.py" --json "$H/colgrep_scope_probe.json" | tail -5
python3 -I "$H/bash_practice_measure.py" --label baseline --exclude-name 'w03' --out "$H/baseline.json" "$SESSION" | tail -9
[ "$Q" = quick ] && exit 0
# the headless lab: export of the plugin as it is in the working tree, a fresh lab with its index inside the lab folder
mkdir -p "$S/export" && for d in agents skills scripts hooks .claude-plugin; do rm -rf "$S/export/$d"; cp -R "$W/$d" "$S/export/"; done
rm -f "$S/export/.claude-plugin/marketplace.json"; find "$S/export" -name __pycache__ -prune -exec rm -rf {} \;
rm -rf "$S/lab1" && mkdir "$S/lab1" && cd "$S/lab1" && git init -q . && export COLGREP_DATA_DIR="$S/lab1/.colgrep"
python3 "$S/export/scripts/lab_init.py" <<'MURMURATION_QUESTION'
How many distinct non-empty substrings can a binary string of length n have at most, and which strings reach that maximum? I would like an answer for general n, with the evidence for it.
MURMURATION_QUESTION
printf '.claude/settings.local.json\n.colgrep/\n' > .gitignore && git add -A && git -c user.name=lab -c user.email=lab@example.invalid commit -qm "lab: start"
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 claude -p --plugin-dir "$S/export" --agent murmuration:research-pi --permission-mode auto --max-budget-usd 4 --output-format stream-json --verbose "How many distinct non-empty substrings can a binary string of length n have at most, and which strings reach that maximum? I would like an answer for general n, with the evidence for it. You will not hear from me during this run. Keep the team small: one explorer, and one author with a verifier for the main claim. Run the study within the budget, and end with the synthesis in __statera__/synthesis.md." > "$S/run1.jsonl"
# the session of that run: the newest folder under its project's transcripts
SD=$(ls -dt "$HOME"/.claude/projects/-private-tmp-*lab1/*/ | head -1)
python3 -I "$H/bash_practice_measure.py" --label run1 --main --out "$H/run1_measure.json" "$SD"
cp -R "$S/lab1" "$S/lab1-after-run1"
python3 -I "$H/author_probe_runs.py" "$S" 3 --variant-file "$H/variant_b.txt"
