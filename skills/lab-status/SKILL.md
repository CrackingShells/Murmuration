---
name: lab-status
description: Show the state of the Murmuration research lab in the current project: open puzzles, the current label of every claim (disputed ones flagged), and token spend per agent and model. Run it as `/lab-status`.
user-invocable: true
---

# /lab-status

Prints what is open in the lab, what each claim currently stands at, and what the work has cost
so far. It only reads files; it changes nothing.

Run it from the project folder (the one that holds `__statera__/`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lab_status.py"
```

Show the output to the user as it is. Then add at most a few lines of your own:

- **Open puzzles** are puzzles raised in `__scrupuli__/` that no closed wave note has given a
  disposition (`followed` or `parked`). Say how many and name them.
- **Claims** are listed with their current label: the author's label unless a verifier's latest
  verdict lowers it. `unverified` means no verdict yet; `disputed` means verifiers disagree and
  the PI must resolve it; `restate lower` means the author must restate the claim at a lower
  label; `WITHDRAWN` means the claim no longer stands. No note or report states a claim above
  its current label.
- **Spend** is read from Claude Code's transcripts for this project: tokens per agent and model,
  with no prices applied. If no transcripts are found the output says so; do not estimate.

If the project has no `__statera__/` folder the script says there is no lab; tell the user to
start one with `/lab <question>`.
