# Build

## Context
Second level of the Murmuration roadmap: runs after wave 1 (platform probes, instrument validation), whose findings may amend these nodes. Produces the plugin: agents, skills, commands, two hooks and the status script (architecture v6).

## Goal
Build the mechanical layer and the team, then pilot them.

## Pre-conditions
- [ ] `platform_probes` done: every mechanism v4 relies on is VERIFIED or has a recorded fallback
- [ ] `instrument_validation` done: the list of instruments allowed in the brief is decided

## Success Gates
- ✅ The plugin installs locally; its hooks and status script pass their self-tests
- ✅ The pilot node is done

## Status
```mermaid
graph TD
    libripens_core[libripens core]:::blocked
    agents_and_skills[Agents, skills and commands]:::done
    pilot[Pilot]:::planned
    minimal_lab[Minimal lab: scripts, hooks, lab commands, packaging]:::done
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `libripens_core.md` | 📄 Leaf Task | 🚫 Blocked |
| `agents_and_skills.md` | 📄 Leaf Task | ✅ Done |
| `pilot/` | 📁 Directory | ⬜ Planned |
| `minimal_lab.md` | 📄 Leaf Task | ✅ Done |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|
| A2 | 2026-10-19 | __reports__/genesis/13-architecture_v6.md | ["minimal_lab.md"] | Both reviews judged v5 overbuilt; the PI chose the minimal lab and reflective runs; libripens_core is blocked (superseded), revivable by a reflective-run proposal |

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
