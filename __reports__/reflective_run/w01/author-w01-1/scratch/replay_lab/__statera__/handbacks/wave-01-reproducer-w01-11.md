# Hand-backs of wave-01-reproducer-w01-11

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T11:57:45+09:00 | agent_id=a14c1a51f2af8092b type=murmuration:reproducer event=PostToolUse status=delivered bytes=3330 sha256=0cf7321a1b96
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

verdict: OVERSTATED (reproducer-w01-11, claim w01-c11). The count in the title matches the rows, but several rows misstate their fact's scope or label, and several verdicts need evidence the row does not give. The PI ("main") did not answer; the question was queued and logged as "no answer". No experiments re-run.

**Title count.** It matches the rows: one back (SA6), one changed (SA3), fifteen stays out, five not examined (SA10, SA12, SA14, SA16, SA17). SA16 is worded "not examined as such".

**Rows that match their source.** SA4, SA5 (numbers), SA6 (facts), SA9 (numbers) and SA13 (the channel claim) are quoted as their sources state. The labels of c1, c2, c3, c6 and c7 in the table are right.

**Where fact or label is misquoted:**
- **SA9 and SA2, c8 label.** The rows say "MEASURED by PI decision", but lab_status prints `escalated: PI decides`. The PI decision is only in wave-01.md.
- **SA2, fact column.**
  - "136 puzzles, 11 claims, two real format slips" has no cited source. Explorer-b §5 says 14 listed puzzles for one file (7 today).
  - The 0.36 s is w01-c3's Spend-section scan of transcripts, not a scan of markdown stores.
  - §5 also records four silent parser failure modes (N1, N2, N3, N8) that the row omits.
  - The "420-character cap" source is a puzzle with no label.
- **SA3, scope.** The 0.05% holds in 52 of 54 cells that hold no subagent output. On the combinatorics project the reader is 7.5% under. The verdict "no Wh" has no fact in the row.
- **SA8.** The "about 12%" is explorer-c's untested CONJECTURE, stated as fact. The source itself proposes a PostToolUse classifier, a changed shape the row does not weigh.
- **SA15.**
  - The 58k to 23.5k drop is attributed to the `tools:` lists. The source attributes only about 7k and calls the rest CONJECTURE. It also compares genesis general-purpose agents with shipped explorers.
  - "0 MCP calls in 299" comes from a report that calls this run the "worst fit" for that count.
- **SA13.** "1 to 2 of 19 asks" is the re-rating inside w01-c7's verdict section, and c7 is below CONJECTURE. Explorer-d §5 says 1 of 19 materially.
- **SA12.** "Only measure the human asked for" is stronger than a table of prompts that asked to see, rewrite or complained.
- **Title.** "Brings one back" rests on w01-c1, which is unverified. reproducer-w01-1 found corrections there: 3 sections instead of 2 in auto mode with a resume, 84 to 93 lines instead of 69, and two edge cases.

**Where the verdict needs evidence the row does not give:**
- **SA1.** The facts (hook frequency, 43 ms, 0 MCP calls) do not touch the single-writer path.
- **SA5.** pi-9 is a question about whether the skill listing can be suppressed. It does not establish a lever.
- **SA7.** "No agent wrote into another's store" has no cited check, and the brief-measurement half is unaddressed.
- **SA11.** The facts bear on 2 of 8 events.
- **SA16.** The number of puzzles says nothing about mention vs follow. Its source, a lab_status run at close, does not exist yet.

**Files**
- Verdict section, appended: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__pondus__/w01-c11.md`
- Puzzles (5): `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-reproducer-w01-11.md`

## hand-back 2 | 2026-10-19T11:57:45+09:00 | agent_id=a14c1a51f2af8092b type=murmuration:reproducer event=PostToolUse status=delivered bytes=3056 sha256=df997a132424
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

reproducer-w01-11 on w01-c11: verdict OVERSTATED.

Summary: The title count matches the rows: one back (SA6), one changed (SA3), fifteen stays-out, five not examined (SA10, 12, 14, 16, 17). Many numbers are as their sources state, but 13 items in my independent result are defective. The main ones:
- SA2: "136 puzzles, 11 claims, two real format slips" is not in the cited explorer-w01-b §5. That section says 14 listed puzzles and cites four silent parser failure modes (N1, N2, N3, N8). The 0.36 s is w01-c3's whole Spend section, a transcript scan, not a scan of markdown stores. The "420-character cap" is an unlabelled puzzle (S-w01-research-pi-12).
- SA2 and SA9: w01-c8 is shown as "MEASURED by PI decision", but lab_status prints "escalated: PI decides".
- SA3: the "0.05%" holds only in 52 of 54 cells without subagent output. The reader is 7.5% under on the combinatorics project. Nothing in the row supports dropping Wh.
- SA8: the "12%" is explorer-w01-c's untested CONJECTURE. The source also proposes a PostToolUse result classifier, which the row does not weigh.
- SA15: the 58k to 23.5k drop is attributed to the `tools:` lists, but the source attributes only about 7k tokens to them and calls the rest CONJECTURE. The "0 of 299" MCP calls come from a run the source calls the "worst fit".
- SA13: the "1 to 2 of 19" figure is a re-rating from the verdict section of w01-c7 (a claim below CONJECTURE). Explorer-d §5 says 1 of 19.
- SA5: S-w01-research-pi-9 is a question, not a measured lever.
- SA7, SA11, SA1, SA16: the verdict rests on facts about other elements, or on an absence nobody checked.
- Title: "brings one back" rests on w01-c1, which is unverified. The reproducer-w01-1 section in w01-c1 reports corrections (auto-mode resume gives 3 sections not 2, line counts 84 to 93 not 69, and one header-line edge case).

Exchange: I sent seven questions to "main" and logged "no answer" when closing, because no reply had arrived. The PI's answers then arrived and conceded nearly all of them, as logged in a "late answers" subsection:
- SA7 becomes "not examined".
- SA5 becomes CONJECTURE.
- SA8 is reworded to "stays out as specified; an untested alternative is a PostToolUse classifier".
- SA11 and SA16 are narrowed.
- The c8 and c7 labels are corrected.
- The title becomes conditional on w01-c1.
The PI will file the restatement as w01-c12 (supersedes w01-c11); I have not verified it, and it does not exist yet. The late answers confirm the verdict and give no new artifact, so there is no `changed_by:`.

Not edited: other claim files, agents/, skills/, scripts/, hooks/, and I did not commit. The "no answer" line in the exchange stays in the append-only file and is marked superseded.

Files:
- /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__pondus__/w01-c11.md (my section starts at `## verdict: reproducer-w01-11`)
- /Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-reproducer-w01-11.md (6 puzzles)
