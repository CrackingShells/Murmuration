# Naming the research-lab repository — Findings (v0)

---
type: findings
topic: meta_process
date: 2026-10-18
version: v0
prior-version: none
key-metric: recommended repository name: Murmuration (prior: "research-lab" placeholder)
decision-required: confirm
---

## 1. Concept Mapping

The repository ships a multi-agent research team as a Claude Code plugin: a judgement-led PI,
explorers, and author ↔ verifier pairs that talk directly; shared stores (the *libripens* balance);
and hooks that make anomalies propagate back so they reopen exploration. Its relational core,
learned the hard way in the imbrication study, is **collective behavior that emerges from local
exchanges, in which one member's weak signal can redirect the whole group**. It is not a chain of
command.

Constraints set by the PI:
- English;
- uncomplicated;
- at the intersection of the science register and the bird register of Cracking Shells, whose
  repositories are Hatch, Hatchling, Nest, Plumage, Pinion and Wobble: one capitalized English
  word drawn from the life of birds.

## 2. Root Sources

Mined: the English collective nouns for birds, and the vocabulary of field ornithology and
collective-behavior science.

| Source | Internal logic | Fit |
|:--|:--|:--|
| *murmuration* (starlings; Middle English, from Latin *murmuratio*, "a murmuring") | A flock that coordinates through each bird tracking a handful of neighbors, not a leader. A turn or alarm noticed by a few birds at the edge travels as a wave through the whole flock. This is studied in collective-behavior physics (topological interaction, scale-free correlations, "agitation waves") | **Direct.** Local exchanges between peers produce coherent group behavior, and one member's signal propagates to all: the scrupuli back-flow |
| *rookery* (a breeding colony of rooks, a corvid) | A dense colony of birds that live, nest and call together. Rooks solve puzzles and use tools in classic cognition experiments (raising the water level with stones, Aesop's fable reproduced) | Good for "a colony of puzzle-solvers"; weak on emergence |
| *skein* (geese in V formation; also a length of thread) | A led formation: the front bird breaks the air, the others fly in its upwash and spend less energy, and the lead rotates | Good for leadership and energy saving (sustainability), and *thread* echoes the examen threads; but it is leader-centric |
| *kettle* (hawks circling together in a thermal) | One bird finds rising air and circles; others see it and join. Following a signal | Excellent mapping for exploration, but the name is unusable (below) |

## 3. Candidates

| Candidate | Gains | Loses |
|:--|:--|:--|
| **Murmuration** | Names the behavior the package exists to make emerge: coherence from peer exchanges, and a local anomaly reaching everyone. Real science stands behind it. Plain English, one word, bird register | Four syllables. The lab does have a PI, which a murmuration lacks; but the PI here is attention, not command, so the image holds |
| Rookery | Short; corvids are the emblematic puzzle-solving birds; a colony is a lab | The verb *to rook* means to swindle: wrong baggage for a system built on honest labels. It also has a historical sense of slum |
| Skein | Short; it carries leadership, energy saving and threads | Collides with the Skein hash function (a well-known cryptography name); it centers the leader, which is the PI-as-hub habit the design moved away from |

Rejected without forging: *kettle* (Pentaho Kettle dominates the name in software),
*parliament* (owls; political), *colony* and *flock* (too generic).

## 4. Morphological Family (Murmuration)

| Form | Word | Use |
|:--|:--|:--|
| repository, plugin | **Murmuration** · `murmuration` | `CrackingShells/Murmuration`; plugin id `murmuration` |
| one run of the lab | a murmuration | "the imbrication murmuration ran five waves" |
| the act of exchanging | to murmur | peers murmur in the examen threads; deliberately understated, not a coined term to enforce |
| internal names | unchanged | *libripens*, `__expensa__`, `__statera__`, `__pondus__`, `__examen__`, `__scrupuli__` stay as they are. The repository name is the bird; the instruments inside are the Roman balance, as Cracking Shells pairs a bird name with technical parts (Pinion, Plumage) |

## 5. Recommendation

**Murmuration**, because:
1. **Mapping fidelity.** It names the property the whole design is built to obtain: group
   behavior that emerges from local peer exchanges, in which one member's weak signal propagates
   to all. That is exactly what the imbrication study lacked and what the scrupuli and
   `FileChanged` back-flow restore.
2. **Register.** It is an English bird word with a real body of collective-behavior science behind
   it: the intersection the PI asked for.
3. **Simplicity.** One common word, readable by anyone. It needs no coinage, only a choice.
4. **Fit with siblings.** Hatch, Nest, Plumage, Pinion and Murmuration read as one family; the
   Latin balance stays inside as the instruments.

## 6. Pronunciation & Orthography

mur-myuh-RAY-shun. Repository `Murmuration`; plugin and package id `murmuration`; ASCII-clean.

## 7. Provenance

- **Ecosystem register:** the CrackingShells profile README, and the repository list (Hatch,
  Hatchling, Nest, Plumage, Pinion, Wobble, colgrep-mcp), read 2026-10-18.
- **Collision checks (2026-10-18):**
  - `murmuration` on PyPI is AWS encryption primitives; on crates.io it is "starlings at dusk, in
    your terminal"; 310 GitHub repositories match the name, none of them a research multi-agent
    system.
  - `rookery`: a PyPI dev-tool package manager.
  - `skein`: Apache YARN deployment (PyPI) and Skein hash functions (crates).
  - `kettle`: 2,535 GitHub matches, led by pentaho-kettle.
  - The PyPI and crates.io name for `murmuration` is taken, so the plugin is distributed through
    Nest (the Cracking Shells marketplace), not as a registry package. The binary is `libripens`.
- **Science behind the image** (from memory, UNVERIFIED here): Ballerini et al. 2008 (topological
  interaction in starling flocks), Cavagna et al. 2010 (scale-free correlations), Hemelrijk et al.
  (agitation waves); Bird & Emery 2009 (rooks and the Aesop task); V-formation energy studies
  (Weimerskirch 2001; Portugal 2014).
