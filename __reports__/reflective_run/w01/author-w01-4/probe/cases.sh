#!/bin/bash
# Transcription of the headless probes behind claim w01-c4 (they were run inline, in this order, from a shell;
# this file only writes the same commands down. Not meant to be run blindly: it launches ~8 claude sessions).
# Cost: about USD 0.02 each with --model haiku; the cron case keeps a session open ~100 s.
# Run from anywhere. $W = this author's folder, $S = a scratch directory OUTSIDE the repository.
set -u
W=/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/author-w01-4
S=${1:?scratch dir}/wt
mkdir -p "$S" && cd "$S"
git init -q main && cd main && mkdir -p __statera__ sub && echo x > sub/f && echo a > a.txt
git add a.txt sub && git -c user.email=a@b -c user.name=a commit -qm files
git worktree add -q ../wtA -b wtA            # a linked worktree outside the repository folder

mk() { python3 -I "$W/probe/make_settings.py" "$S/$1.jsonl" "$S/$1.settings.json" "$W"; }   # hook dumper: UPS, Stop, SessionStart
run() { n=$1; d=$2; shift 2; mk "$n"; (cd "$d" && claude -p "say OK" --model haiku --setting-sources project \
        --settings "$S/$n.settings.json" --permission-mode bypassPermissions --max-budget-usd 0.20 --output-format json "$@" > "$S/$n.out.json"); }

run case1 "$S/wtA"                                   # started in the worktree
run case2 "$S/wtA" --add-dir "$S/main"               # same, plus the main checkout as extra dir (what the Desktop passes)
run case3 "$S/main" -w wt3                           # claude creates and enters a worktree
run case4 "$S/wtA" --add-dir "$S/main"               # like case2 with the Desktop's binary: replace `claude` by "$CLAUDE_CODE_EXECPATH" (2.1.299)
# case5/6: started in main, then the EnterWorktree tool, then `cd sub`, one turn per message (drive.py waits for each result)
mk case6; python3 -I "$W/probe/drive.py" "$S/main" "$S/case6.settings.json" "$S/case6.out.jsonl" \
  "Load the EnterWorktree tool with ToolSearch (select:EnterWorktree) and call it with name ew2. Then reply DONE." \
  "Run the shell command: cd sub && pwd . Reply with its output only." "Reply OK."
# case7: a second prompt sent while the first turn runs (stream-json, both lines at once): same prompt_id, one Stop,
#        and the second prompt is stored in the transcript as attachment type queued_command, not as a user record
# case8: CronCreate every minute, session kept open (DRIVE_LINGER=100): UPS fires with the raw cron prompt;
#        the transcript record has turnOrigin "scheduled", isMeta true, origin null
mk case8; DRIVE_LINGER=100 python3 "$W/probe/drive.py" "$S/main" "$S/case8.settings.json" "$S/case8.out.jsonl" \
  "Load the CronCreate tool with ToolSearch (select:CronCreate) and call it to create a recurring cron job running every minute (* * * * *) with the prompt: CRON-TICK say hi. Then reply DONE."
# UPS (patched rule) against the Stop prototype in one session:
python3 -I "$W/probe/demo_ups_vs_stop.py" "$S"
# Replay over five real transcripts (2 s, no network):
python3 -I "$W/replay.py"
