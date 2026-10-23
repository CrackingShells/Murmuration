## S-w08-reproducer-w08-5-1
A start line can be confirmed and wrong with 3 same-type same-second dispatches: when an answer for an agent that has already started finds its record still pending, `bind` moves it to names/<id>.json (an orphan) instead of leaving it, so the pool loses a record and a later start takes the wrong one as the only one in play. The author's scenarios (c5_three and the fuzz) did not hit it; 4 of 58 sampled 3-dispatch orders showed a problem (2 of this kind). Python and Rust agree byte for byte, so equality testing cannot see it. The author accepted it and narrowed the scope to 1 or 2 dispatches.
refs: /private/tmp/murmuration-w08/reproducer-w08-5/mrg/scripts/budget.py (bind, claim_pending); `python3 -I __instrumenta__/w08_v5_pairs.py ... --only n3ss`; case n3ss_P0P1S1P2A1S0A2S2A0_111

## S-w08-reproducer-w08-5-2
The pool of a claimed record is copied onto the records that remain, including a record created after it, so a later start's candidate list can omit its true name (n3ss_P0P1S0P2S1A0S2A2_101: x2 says candidates e,f; its name is g).
refs: same script, scripts/budget.py claim_pending

## S-w08-reproducer-w08-5-3
agentId is used unsanitised as a file name in names/ (agentId "../x0" overwrites the state file of agent x0 with a dispatch record, Python and Rust). The same platform field is already used unsanitised for state and lock files, so the trust boundary is old; still, tool_use_id is sanitised in the same function and agentId is not.
refs: `w08_v5_pairs.py --only EXTRA`, scenario agentId_dotdot_hits_state_file

## S-w08-reproducer-w08-5-4
My first full enumeration run (all 3-dispatch orders, stride 7) left an empty log and its process vanished without output at about 12 minutes; I could not tell why. I replaced it with smaller runs. Separately, the shipped binary does not byte-reproduce from a plain `cargo build --release --offline` in my tree (sha 704e07... against the manifest's e67bd8...), so I verified the shipped binary by behaviour only (it equals Python over all my scenarios), not by rebuilding.
refs: /private/tmp/murmuration-w08/reproducer-w08-5/pairs_all.log (empty), /private/tmp/murmuration-w08/reproducer-w08-5/tgt2

## S-w08-reproducer-w08-5-5
A double quote in the lab path gives a start note whose `paths: ["..."]` literal contains an unescaped quote. Paths with spaces, a symlink, a worktree, a plain checkout, a cwd in a subfolder and a cwd 7 levels down with CLAUDE_PROJECT_DIR were all right. Edge only; the author already lists `[` and `*` as not covered.
refs: /private/tmp/murmuration-w08/reproducer-w08-5/ (w08_v5_paths.py, "double quote" rows)
