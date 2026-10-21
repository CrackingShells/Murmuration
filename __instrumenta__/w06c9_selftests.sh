# w06-c9: runs the six selftests of a plugin tree; input: the plugin root as $1; output: the last line of each selftest (PASS <name> or the failure) on stdout
cd "$1" || exit 1
python3 scripts/budget.py --selftest 2>&1 | tail -1
python3 scripts/handback.py --selftest 2>&1 | tail -1
python3 scripts/lab_status.py --selftest 2>&1 | tail -1
python3 scripts/resume_brief.py --selftest 2>&1 | tail -1
python3 scripts/user_words.py --selftest 2>&1 | tail -1
python3 scripts/lab_init.py --selftest 2>&1 | tail -1
