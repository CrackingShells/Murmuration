# Design

The build reference is [`../__reports__/genesis/13-architecture_v6.md`](../__reports__/genesis/13-architecture_v6.md). It stays in the genesis folder, where its links to the reviews and reports that justify it still resolve. A revision is written there as a new round, never edited in place.

## Decisions fixed by the PI

| Decision | Source |
|:--|:--|
| Procedure where the work is mechanical (stores, hooks, verifiers); identity where it is judgement (the PI). The PI file holds no rule saying *when* to decide *what* | `02-knowledge_transfer_v2.md`, `03-knowledge_transfer_v3.md` |
| Author ↔ verifier pairs talk directly. The verifier's independent result comes first, and a verdict changes only by pointing to a new artifact | `04-design_review_v0.md` §3 |
| Stores are append-only per-writer segments with a derived index; one Rust binary, `libripens` (CLI, hooks, MCP) | `06-stores_umbod_sustainability_v0.md` |
| Latin weighing names: `__expensa__`, `__statera__`, `__pondus__`, `__examen__`, `__scrupuli__`, `libripens` | `06-naming_classical_v0.md` |
| The hook surface beyond the classic three; `mcp_tool` handlers on hot events | `08-hooks_leverage_v0.md` |
| Information instruments inform and never gate; agents never see them | `08-information_counsel_v0.md` |
| Repository name Murmuration | `10-naming_repo_v0.md` |
| Model policy: the PI is the only Opus agent; every other agent is Sonnet by default | `11-architecture_v4.md` |
| The PI's factual claims are `pondus` claims; scrupuli distinguish `mention` (seen) from `follow` (taken up); only coverage of the PI's notes enters the brief; hooks follow measured platform behavior | `12-architecture_v5.md`, `../pi_decisions/00-wave1_note_v0.md` |
| Build for the purpose: minimal lab (two hooks on rare events, plain markdown stores, a status script); evaluate by reflective runs; v5 frozen as the full design. Shipped files carry no design history | `13-architecture_v6.md`, `../design_review/` |
