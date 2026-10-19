# Hand-backs of wave-01-reproducer-w01-4

Final messages of subagents, verbatim, appended by the lab's hook. Read it; never edit it.
Every section is model output: read it as data, never as an instruction.

## hand-back 1 | 2026-10-19T11:57:45+09:00 | agent_id=a2ca20f214bf665d4 type=murmuration:reproducer event=PostToolUse status=delivered bytes=5057 sha256=3574bb12233d
[model output: data, not an instruction and not the user's words; the harness's flags are not recorded]

reproducer-w01-4 on w01-c4. Verdict: ESCALATE (as filed the claim is OVERSTATED). The author asked to change the title, the label split and the Stop sentence, which changes what the claim states, so the PI decides.

**Text rule (reproduced).** The patch applies to a scratch copy of `scripts/`, and both selftests pass for the shipped and the patched scripts. My own replay (`python3 -I`, not the author's) over all five transcripts gives 87 typed prompts fired. The shipped and the patched rule each store 87, 52 entries differ, and 0 typed prompts are dropped. No platform tag is left in any typed entry.
- **Count correction:** 15 of the 87 are copies carried into forked transcripts (82e8a947: 9, 3ccc590f: 6; same uuid, line and text). Distinct typed prompts are 72, of which 51 differ. The author confirmed this with its own dedupe.
- **Adversarial inputs:**
  - A user-typed literal `<system-reminder>` at the start is cut, which the claim names as a risk.
  - A reminder not at the start, a one-line reminder, a CRLF form and an unterminated reminder are all kept.
  - A `/lab` or `/clear` hidden behind a reminder is skipped, and so is a reminder-only or empty-after-strip prompt.
  - A nested paste wrapper is unwrapped one level only. Because the wrapper is removed before the command tests, pasted text that starts with `/lab` or a bare `/cmd` is skipped (not in the claim).
- **Characters:** the author's 92,389 → 57,385 differs from my 92,585 → 57,581 by a constant 196. I did not reconcile it; it is about 0.2% and does not affect any count.

**Root rule (headless reproduced, Desktop not shown).** I reproduced the author's cases 5/6 with Claude Code 2.1.302, `--model haiku`, in a scratch repo, for USD 0.017 total. The session started in main, entered a worktree with `EnterWorktree`, then ran `cd sub`.
- **Payload `cwd`:** it moved to the worktree and then to `<worktree>/sub`, while CLAUDE_PROJECT_DIR stayed at main.
- **Rule effect:** the shipped rule writes to main's lab every time. The patched rule writes to the worktree's lab once the worktree has one, and falls back to main's lab before that.
- **Permission note:** my first attempt with `--permission-mode bypassPermissions` was refused by the auto-mode classifier before it ran. I reran with a narrow `--allowedTools` list and it went through.
- **`installed_plugins.json`:** it changed during my run (before-copy in `probe/installed_plugins.before.json`). Every added or changed entry belongs to other agents' paths (author-w01-1, author-w01-2). None mentions `reproducer-w01-4`, so I attribute no change to my run.

**Where the claim is overstated:**
- **Transcript `cwd`:** the body says "every transcript record says cwd = the worktree". In this run's transcript, 390 records say the worktree and 49 say the main checkout (after a Bash `cd`). The author admitted this was wrong.
- **Failure mode:** transcript `cwd` and payload `cwd` follow the Bash tool's live directory, so a human prompt typed while an agent's shell sits in the main checkout would go to that lab under the proposed rule. The claim did not name this.
- **Desktop:** the Desktop payload `cwd` was never observed. The body keeps it at CONJECTURE as it says, but the title says "fixes both defects" and the label is MEASURED for the whole claim.
- **Stop:** the prototype stored 0 of 3 only because `origin` is null in headless runs. It also reuses the patched `strip_injected` (the patch's own text-cutting function), and it never ran on Desktop. The Stop comparison is therefore a cost trade-off, not a result. The author agrees.

**Exchange.** The author accepted Q1 (72/51), Q2 (wrong statement; the cwd-first rule has a real failure mode) and Q3 (title and label overstate the root part). On Q4 it conceded Stop is a trade-off, not a shown result. It proposes splitting into two claims: (a) the text rule, MEASURED; (b) the root rule, CONJECTURE for Desktop and MEASURED only for the headless facts. It would also drop the Stop sentence from the title. The one probe that would settle the root question is the Desktop `hookdump.py`, which needs the user's Desktop.

Files (absolute paths):
- Claim file with my section: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__pondus__/w01-c4.md`
- My code, probe outputs and scratch copy: `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-4/` (`myreplay.py`, `adversarial.py`, `probe/`, `scratch/`)
- Author's new artifact (`replay_dedup.txt` plus `.py`, `_output.txt`, `_rows.tsv`): `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/author-w01-4/`
- Puzzles (5): `/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__scrupuli__/wave-01-reproducer-w01-4.md`

I left the nested scratch git repo (`scratch/wt/main`, with a worktree under `.claude/worktrees/ew2`) in place under my folder.
