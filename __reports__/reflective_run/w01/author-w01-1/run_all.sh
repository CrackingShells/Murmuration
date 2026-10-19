#!/bin/bash
# Full experiment of w01-c1: 12 headless haiku runs, about USD 0.08, about 4 minutes. Usage: run_all.sh [quick]
# quick = the selftest and the first two runs (default and auto mode, two hand-backs each), then collect.py: about 1 minute, USD 0.012.
# Runs on the installed claude (2.1.302) and, where D299 is used, on the Desktop 2.1.299 binary. Needs no Anthropic key beyond the logged-in CLI.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
SCR=/private/tmp/claude-501/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087/scratchpad/hb_nolab
D299="/Users/hacker/Library/Application Support/Claude/claude-code/2.1.299/4fa9694b7975/claude.app/Contents/MacOS/claude"
run() { ./run_probe.sh "$@" < /dev/null; }
python3 -I plugin/scripts/handback.py --selftest
run p4_default_two default claude 1 1 prompt_two.txt
run p4_auto_two    auto    claude 1 1 prompt_two.txt
[ "${1:-}" = quick ] && { python3 -I collect.py; exit 0; }
run p5_auto_bg_nasty    auto    claude 1 1 prompt_nasty_bg.txt
run p5_default_bg_nasty default claude 1 1 prompt_nasty_bg.txt
run p6_auto_stoponly    auto    claude 1 2 prompt_one.txt          # capture route of auto mode removed
run p7_nolab_auto       auto    claude 1 1 prompt_one.txt 0 "$SCR" # not a lab: must write nothing
run p8_d299_default_two default "$D299" 1 1 prompt_two.txt
run p8_d299_auto_two    auto    "$D299" 1 1 prompt_two.txt
run p9_auto_big       auto    claude 1 1 prompt_big.txt           # a hand-back of about 9 KB
run w1_sub_302 bypassPermissions claude 0 0 prompt_write_sub.txt   # which Write calls does the platform refuse in a subagent?
run w2_main_302 bypassPermissions claude 0 0 prompt_write_main.txt  # control: the same names from the main thread
run w3_sub_299 bypassPermissions "$D299" 0 0 prompt_write_sub.txt
python3 -I collect.py
