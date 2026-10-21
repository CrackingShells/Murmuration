## S-w06-reproducer-w06-2-1
Explorer-w06-c's "about 1.5-3 min" of dispositions in a "1.8-min close" does not match the transcript: the disposition write took about 69 s (01:50:07-01:51:16 UTC), turns 23-24 together last 319 s, and no 1.8-min interval is visible; the disposition work also overlapped the last verifier's 216 s run, so it was not on the user's critical path.
refs: __reports__/wave-06/explorer-w06-c/00-findings_v0.md line 75; __reports__/wave-06/explorer-w06-c/w4_req.tsv rows 98-100; __instrumenta__/w06c2_pi_close_window.py

## S-w06-reproducer-w06-2-2
Wave 4's disposition rows are unusually pointer-heavy (56 of 104 cite a numbered open item in synthesis.md, 11 distinct items; wave 5: 7 of 92). Why did wave-4's PI cluster at the disposition step and wave 5's not? Any estimate priced on wave 4 may not transfer.
refs: __statera__/wave-04.md "Puzzle dispositions"; __instrumenta__/w06c2_dispo_vs_handback.py (column synth_item)

## S-w06-reproducer-w06-2-3
`/lab-status` counts a puzzle as disposed only from a closed note, so under the new bullet a PI reading `/lab-status` at the close (step 1) sees every puzzle of the wave open even if rows exist. Is that the intended step-1 reading, or should step 1 read the open note too?
refs: scripts/lab_status.py `disposed_puzzles` (line 139); skills/research-loop/references/waves.md "Closing a wave" steps 1-2

## S-w06-reproducer-w06-2-4
Commit order is a weak clock for "when a puzzle was raised": 105 of 297 claim-citing rows have the claim head committed after the puzzle file, mostly same-minute commits of one batch. A real hand-back-time test needs the worker's own message time (not recorded outside the PI transcript for waves 1-3).
refs: __instrumenta__/w06c2_dispo_vs_handback.py (columns puzzle_first_commit, claim_first_commits)
