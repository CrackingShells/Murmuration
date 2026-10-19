## S-w02-reproducer-w02-4-1
The 29,919-char `skill_listing` that makes up the whole 11,100-token saving is the user's own installed-skill roster (about 70 skills across several plugins), not something the plugin ships. The claim's headline gives absolute tokens, but the saving depends on the machine. Would a fresh install with few skills show any saving worth the loss of `Skill`? A control with a stripped `~/.claude` skill set, or a count of listing chars per installed skill, would settle it.
refs: __reports__/reflective_run/w02/author-w02-4/result.jsonl (skill_listing_chars 29919), scratchpad/w02/reproducer-w02-4/e_ctl_a.json and the ctl subagent transcript (attachment skill_listing)

## S-w02-reproducer-w02-4-2
The old plugin run wrote no report because the brief never names the path and the old plugin has no template, so the 0 of 2 against 6 of 6 is true but cannot fail: it shows the template steers, not that the steer survives a brief that omits or contradicts it. What does a worker do when the brief says "no report files" (explorer-w02-a saw an agent refuse and deliver nothing)?
refs: __reports__/reflective_run/w02/author-w02-4/brief.txt; __reports__/reflective_run/w02/explorer-w02-a/00-findings_v0.md line 39

## S-w02-reproducer-w02-4-3
The explorer's `maxTurns` went 60 to 150 inside a claim about the tool list and a template. Nothing in this claim ran past 10 turns, so 150 is untested everywhere. Meanwhile `waves.md` dropped "reaches its turn limit returns partial work" for a budget statement that depends on hooks which were not loaded in these runs. Which of the two limits does stop a runaway explorer, and has anyone seen either fire?
refs: git diff -- agents/explorer.md skills/research-loop/references/waves.md; hooks/hooks.json (uncommitted)

## S-w02-reproducer-w02-4-4
The author did not answer the four questions within about 5 minutes, though its puzzle file was written before they arrived. A resumed author on the same session may not have a delivery path back to a verifier running as a subagent. Is "no answer" here a property of the harness (reply goes to the parent session) rather than of the author? The send tool's description says replies to a cross-session message go to the parent's conversation.
refs: __pondus__/w02-c4.md (exchange); SendMessage tool description

## S-w02-reproducer-w02-4-5
My "no answer" in the first close was wrong about the author: it answered after I had handed back. Replies reach a verifier only while it is still in a tool round; a verifier that finishes first loses them. The exchange step has no wait. Should the verifier's procedure say to wait for the answer before closing, or to reopen the verdict on a late answer, as happened here?
refs: __pondus__/w02-c4.md (exchange, late answers)

## S-w02-reproducer-w02-4-6
With the branch's hooks, 2 of 5 explorers skipped the template and invented headings, though the preload and the brief were the same and first-turn context was unchanged. The author found no mechanism in the injected contexts. What differs: the transcripts of new_a and new_d under hooks versus new_a without, in the order of the first three tool calls and any hook_additional_context records.
refs: __reports__/reflective_run/w02/author-w02-4/result_with_hooks.jsonl (new_a, new_d)
