## S-w04-reproducer-w04-1-1
Resuming a session from another directory (`claude -p --resume <id>` from main, session begun in wtA) keeps the original transcript file, so the transcript-first rule keeps writing to wtA while the user's shell and payload cwd are in main. Is that what the user wants? Under payload-first it would be main. The author's first draft said the opposite and had not run it; I do not know what the Desktop does on resume (it may copy the transcript).
refs: /private/tmp/murmuration-w04/reproducer-w04-1/run2/resume-main.payload.jsonl (second row: payload_cwd main, head cwd wtA); __instrumenta__/hook_enter_worktree_resume_run.py

## S-w04-reproducer-w04-1-2
EnterWorktree mid-session, headless: the payload cwd moves to the new worktree but the transcript head and CLAUDE_PROJECT_DIR stay main, so the user's words go to main, not to the worktree the user is now working in. The claim lists this as uncovered; nothing says how often each case (shell `cd` vs EnterWorktree/resume) occurs. A data point for the PI: this wave's own Desktop session started in a worktree.
refs: /private/tmp/murmuration-w04/reproducer-w04-1/run2/enter-main.payload.jsonl

## S-w04-reproducer-w04-1-3
Four scripts resolve the lab four different ways: user_words/resume_brief (transcript head, payload cwd, CLAUDE_PROJECT_DIR), budget/handback (payload cwd, five parents, CLAUDE_PROJECT_DIR), lab_init/lab_status (CLAUDE_PROJECT_DIR, cwd). In a shell-moved or Desktop-worktree session they can name three different labs for the same session. lab_status in wtA with CLAUDE_PROJECT_DIR=main printed main's wave-01 while wtA held wave-02. A single shared resolver was not tried.
refs: scripts/handback.py lab_root; scripts/lab_status.py project_root; scripts/lab_init.py project_root; /private/tmp/murmuration-w04/reproducer-w04-1/run/wtA/__statera__/wave-02.md

## S-w04-reproducer-w04-1-4
The author's wall-time numbers (+1.4 ms, +4.6 ms) were taken on a quiet machine; mine on a loaded one swung from -6 ms to +4 ms for the same code, so they only bound the cost from above at a few ms. Also the claim head's `evidence:` and `scope:` cite 7c8d630 although user_words.py changed at 37de695; the landing table was not rerun on the bounded-read code.
refs: /private/tmp/murmuration-w04/reproducer-w04-1/timing/ (ev_real.json, ev_giant.json)

## S-w04-reproducer-w04-1-5
Reading the transcript head is an undocumented-format dependency (`cwd` key of the first record that has one). In every headless transcript the first two records are queue-operation without cwd and the first prompt of a session has no transcript on disk, so step 2 (payload cwd) decides for prompt 1. In the Desktop whether a transcript exists at hook time for prompt 1 is unknown.
refs: /private/tmp/murmuration-w04/reproducer-w04-1/run/changed.payload.jsonl
