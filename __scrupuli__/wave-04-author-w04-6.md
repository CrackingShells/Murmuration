## S-w04-author-w04-6-1
`colgrep init -y` writes its whole report (`Indexed ...`, `Index is up to date for ...`) on stderr and nothing on stdout. A first version of the fix that read stdout (as the old code's `capture_output` suggests) printed "ran `colgrep init`; it said: nothing" and the selftest caught it. Anyone who parses colgrep output for a script needs stderr; the colgrep guide does not say so.
refs: /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-wave-4-3417be/scripts/lab_init.py (build_index); /private/tmp/murmuration-w04/author-w04-6/data

## S-w04-author-w04-6-2
For a lab inside an indexed parent, colgrep updated the parent's index at `init` time ("Indexed <parent> (subdir: lab2) (added: 1 ...)") and a later `init` on the same subfolder said "up to date (4 files)" for the parent, with no mention of the subfolder. Whether a parent index that has changed elsewhere in the tree is re-indexed whole by a lab's `init` (a cost on a big parent such as `/private/tmp`) was not measured; the 90 s timeout in `build_index` then applies to the parent's work.
refs: transcript commands on /private/tmp/murmuration-w04/author-w04-6/parent and parent/lab2

## S-w04-author-w04-6-3
The wave-02 puzzle heading `## What used my 60 turns` is a cost account, not a puzzle, so the `/lab-status` warning about it is not a missed puzzle but a prose section the explorer wrote in a puzzle file. That the file mixes the two suggests the explorer agent file or the closing request should say what else may go in a puzzle file; not tested.
refs: __scrupuli__/wave-02-explorer-w02-b.md lines 13-; scripts/lab_status.py (scan_puzzles)

