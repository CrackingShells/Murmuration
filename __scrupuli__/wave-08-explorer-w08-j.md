## S-w08-explorer-w08-j-1
The guard lets the natural launch form through: `claude -p "$(cat prompt.txt)" <flag>` and `env -u CLAUDE_PROJECT_DIR claude ... <settings-sources flag>` are ALLOWED by both guards (probe cases p1, p2, p5, p7, p9), while the plain forms are denied. Eight real calls of the lab's own explorers in waves 1-6 had this shape and were allowed (they started claude with project-only settings). The splitter closes the quote after `$(`, so the flags land in a segment led by the inert `cat`; and `program()` takes the value of `env -u` as the program. Does every worker that builds a prompt with `$(cat ...)` pass by accident?
refs: __instrumenta__/w08j_probe_cases.json, __instrumenta__/w08j_probe_run.py (output ALLOW for p1,p2,p3,p5,p7,p9), __reports__/wave-08/explorer-w08-j/guard_replay_v0.json (source lab-allowed-claude-flag, label true, indirect false)

## S-w08-explorer-w08-j-2
17 of 19 live denials in the lab's own sessions (waves 6-8) are false, and the 2 true ones are both Writes of a scratch settings file by an author running an experiment. In the whole record I found no live denial of a worker that tried to loosen the permission layer on its own. Is the guard measuring anything but the lab's own writing about the guard? The 269 arena denials are by construction (test lists).
refs: guard_replay_v0.json field live_deny (stratum lab), score_v0.md; wave notes of waves 7 and 8

## S-w08-explorer-w08-j-3
G4 cannot be replayed from a frozen set: a Write over an existing file is compared with the file's current words, so 4 calls that the full replay allowed were denied in the frozen set (lab-allowed-trigger, rule G4). The set therefore does not freeze G4 behaviour; a stable measure for item 26 needs the old file content in the case, which is more transcript text than the brief allows.
refs: __reports__/wave-08/explorer-w08-j/score_v0.md (false denials G4, lab-allowed-trigger 4); scripts/permission_guard.py g4_script

## S-w08-explorer-w08-j-4
The labels are one reader's. The G1 labels for heredocs that write a script and run it in the same call (13 true-indirect) and for the 31 python/bash heredoc prose cases that no narrower test separates are the ones I trust least. A second labeller on the 175 lab-denied cases would show how far "false" depends on reading intent.
refs: guard_replay_v0.json (lab-denied, indirect true), __instrumenta__/w08j_build_frozen_set.py label tables G1_T, G1_TI, G1_FS
