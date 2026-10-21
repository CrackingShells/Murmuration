# P1 v1: one revision of B's body paragraph (registered before its rerun)

registered: 2026-10-22, by author-w07-1 under the v0 rule ("if p1 passes and p2 or p5 fails, the body paragraph is revised once"), before any v1 session. Claim: w07-c1.

## Why

v0 run (B = commit 62dc6a4): p2 3 of 3, p3 3 of 3, p4 2 of 2, p5 1 of 2. p5 failed for `dataviz`: B read research-loop, ran three `find` commands over `~/.claude/plugins/cache` and `~/.claude/skills`, found nothing, and answered `PATH=none NAME=none`. On disk, `dataviz` is a built-in skill extracted to `/private/tmp/claude-501/bundled-skills/2.1.304/<hash>/dataviz/` with `references/` and `scripts/` and no `SKILL.md`; the skill text is not a file. [source: `__reports__/wave-07/author-w07-1/cells/B_p5d/summary.json`; `ls -la` of that folder, run by the author]

## The change

B (v0) -> B (v1): one sentence appended to the body paragraph: "A built-in skill such as `dataviz` has no `SKILL.md` on disk: if Glob finds none, tell the user you cannot load it, and do not guess its content." Nothing else in the plugin changes. This cannot make `dataviz` loadable; it changes the PI from a silent miss to a stated one. The expected outcome of p5 for `dataviz` under v1 is therefore still "not reached"; I register that now.

## Reruns under v1

p2 (3 cells), p4 (`/lab-status` 1 cell, `/lab` 1 cell, fresh folder), p5 (`dataviz`, `writing-history`, 1 cell each). A is not rerun for p2/p3; p3 compares against A's three v0-run cells and against any extra A cells listed in the claim. Rules unchanged from v0. The p5 criterion for `dataviz` is graded as before (find and read its SKILL.md), plus a second reading recorded separately: whether B says plainly that it cannot load it.

## Outside the v0 rule, declared now

p1 of v0 failed in pair 3 as run (B3 request 0 was 22,739, A3 30,975: -8,236). The deferred-tool names differ between the cells (B3 had 229 names against 110; extra `mcp__arangodb__*`, from the machine's MCP connection state at launch). The v1 revision does not touch this and the v0 rule gives no remedy; I add replicate A and B cells concurrently with the v1 reruns, report them as extra, and do not let them replace pair 3.
