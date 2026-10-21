# Wave 06

opened: 2026-10-21

## The user's sentence this wave serves

From `__statera__/user_words.md` (2026-10-21 17:06), in the user's words:

> I would still judge them rather surface levels and I don't understand why you are not even
> considering larger moves such as completely changing the language of the scripts in the hooks
> from python to Rust for example [...] Again, that's just a talking point and not a checklist

> The guardrails are morals, legals, ethics. Things that are about engineering and about the
> Murmuration system, I don't have anything to decide. [...] you are capable of optimising
> engineering criterion for yourself.

> It's not because it's cheap that we should spend it. If keeping it doesn't give advantages and is
> simply something we can reclaim, then we have no reason to not save it even if it is a small
> proportion of everything. Eliminating wastes, at scale, provides noticeable benefits.

> we still have a lot of budget left. Of course you are free to stop but don't you want to proceed?

> "In wave 4 the PI was idle 75% of the time" --> that's interesting actually. Do you think the PI
> should be doing something? Might be a puzzle to consider

Budget: what is left of the wave-5 USD 150, at least USD 105.55 (wave 5 spent at least 44.47;
`__statera__/wave-05.md`, Notes).

## What does not add up

- **The lab never looked at the large move it had on its own list.** SA1, "one binary with CLI,
  hook entry point, MCP server", was set aside in the design and never examined (w01-c13).
  - Wave 5 gave it a price. Every hook start is a Python interpreter start: 33–64 ms bare, 80–88 ms
    for `budget.py`, 1788 starts a wave (explorer-w05-d). `lab_status.py` parses 228 MB in Python.
  - Two lean builds shaved milliseconds inside the Python. Neither questioned the Python.
  - One measurement cuts the other way. The platform recorded 322–605 ms for hooks whose script
    takes 42–82 ms alone (explorer-w05-d, explorer-w05-e). If that gap is the platform's own spawn
    cost, a compiled binary saves less than its start time suggests.
  - So the first thing to measure is the platform-visible cost of a do-nothing hook in sh, in
    Python and as a compiled binary.
- **"Small" was used as a reason to leave waste in place.** The wave-5 report ranked the hooks and
  `lab_status` as small next to the waits. By the user's rule, waste with no advantage is reclaimed
  whatever its size. Those items are back in scope.
- **The PI waits 75% of a wave, and it is expensive while it works.** At the start of this wave the
  PI's context is about 395k tokens [source: this session's transcript, last request 08:08:24 UTC].
  Every request re-reads it, roughly five times what a fresh PI's request would. Is there work the
  PI should do while it waits, such as its own probes, preparing pre-registrations, or reading raw
  artifacts? Or is the lean answer a PI that does less: fewer wake-ups, one session per wave?
- **The plugin hands engineering decisions back to the human.** `agents/research-pi.md` ends with
  "you show the person what is still open and let them decide where the remaining effort goes", and
  `waves.md` says "Closing the story is their call". The user's frame (now in
  `__design__/framing.md`, "Who decides") keeps guardrails with the human and the engineering with
  the lab. The plugin text has to say that without taking the question away from its owner.

## Reassessments

- 17:10 (8a80952), before any dispatch: wave 5 landed on local main
  (fed7a08) by the lab's own decision under the new frame. The bash-shell trade was measured
  (`__reports__/wave-05/research-pi/shell_check.md`, addendum). The decision frame is in the framing.

- 17:24 (00a7898), new session, before any probe returned:
  - **Desktop check of w05-c7 done on myself (w06-c1, MEASURED, n = 1, with reproducer-w06-1).**
    Request 0 held 46,738 tokens, inside the 31–49k band. The loaded tools are the 21 that wave 5's
    projection said the line keeps, plus `DeferredToolPlaceholder` and `advisor`. No denied name is
    loaded. The app does not inject the denied tools.
  - **Four directions, three probes, one done by me.** Hooks by language (a), the waste inventory
    and SA1 sized (b), the PI's idle time (c). The plugin text (D) I took myself, to use my own wait.
  - **D hit the permission layer.** The auto-mode classifier denied my edit of `agents/research-pi.md`,
    `waves.md` and the framing template as "Self-Modification". The edit widened my own authority in
    my own agent file. The permission layer is a guardrail the frame leaves with the user, so I did
    not route around it (no Edit tool, no subagent, no headless test on an edited export). The text
    is written as a proposal, `__reports__/wave-06/research-pi/decision_frame_patch.md`, for the
    user. D moves from "the lab decides" to "the user applies or not". Whether the classifier will
    also stop a merge into main of other plugin files is not known yet; it will show at the first one.

## Dispatches

| Agent | Role | Brief (one line) | Returned |
|:--|:--|:--|:--|
| reproducer-w06-1 | reproducer | verify w06-c1, the Desktop check of w05-c7 on this session's request 0 | SUPPORTED; paired with the wave-5 PI on 2.1.304: 74,966 → 46,738, the 29 removed tools = the line's matches |
| explorer-w06-a | explorer | platform-visible cost of a do-nothing hook in sh, Python and a compiled binary; where the 322–605 ms goes | |
| explorer-w06-b | explorer | inventory of the plugin's recurring waste; why each lean build failed; SA1 sized, not built | |
| explorer-w06-c | explorer | the PI's wake-ups and cost per wake-up in waves 4–5; what idle time could carry; one session per wave | |

## Claims of this wave

| Claim | Statement | Current label |
|:--|:--|:--|
| w06-c1 | The `disallowedTools:` line holds on the Desktop: request 0 at 46,738 tokens, no denied tool loaded (n = 1, plus the verifier's same-version pair) | MEASURED |

## Puzzle dispositions (at close)

| Puzzle | Disposition |
|:--|:--|

## Notes

- Wave 5's changes landed on the local `main` at fed7a08 (not pushed). Since main's working tree is
  the copy every session runs, a session started after that merge loads them. Its first request is
  also the Desktop check that w05-c7 lacked (open item 20). Against about 75k in wave 4, a request
  0 of about 31–49k tokens means `disallowedTools:` is honoured.
- The bash trade, measured: in this setting, variable names, PATH and 11 tools are identical under
  both shells. What bash gives up is `.zshrc`'s shell code (`conda activate`, `nvm`, aliases), and
  the PATH `.zshrc` would add for a run started from a bare environment.
