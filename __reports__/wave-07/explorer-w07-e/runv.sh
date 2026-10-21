#!/bin/bash
S=/private/tmp/murmuration-w07/explorer-w07-e; P=/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/xenodochial-franklin-bc67fb/__instrumenta__/w07e_pi_cell.py
python3 $P $S v1_deny_skill $S/export --deny Skill > $S/v1.out 2>&1 &
python3 $P $S v2_deny_skill_nofm $S/export --deny Skill --noskillsfm > $S/v2.out 2>&1 &
python3 $P $S v3_overrides_off $S/export --settings $S/cfg_overrides.json > $S/v3.out 2>&1 &
python3 $P $S v4_skill_rules $S/export --settings $S/cfg_skillrules.json > $S/v4.out 2>&1 &
python3 $P $S v5_plugins_off $S/export --settings $S/cfg_plugins_off_keep_colgrep.json > $S/v5.out 2>&1 &
wait
