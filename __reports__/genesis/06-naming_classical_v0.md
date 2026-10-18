# Store names for the research lab, classical register — Naming Report (v0)

**Concept:** a team that spends a finite resource, asserts results at graded strength, checks them
through an independent second party, and follows the small discrepancies that did not balance.
**Target community / register:** an international research team and its agents; paper-grade
vocabulary. Register is deliberately Latin and concrete, like *imbrex* (a Roman building object):
names taken from Roman material life (weighing, paying), not abstract Greek.
**Hard constraints:** ASCII identifier usable as `__<name>__/`; the binary name must not shadow a
known command; short; pronounceable internationally.
**Scope:** classical and scientific-technical mining only. A sibling agent covers non-classical
transmission traditions.

## 1. Concept Mapping

The six objects are not six unrelated records. Read together they describe **one act performed
in different roles: weighing.**

| Object | Relational structure | What the name must encode |
|---|---|---|
| ledger | account of outlay, one row per run | what was *paid out*, by amount |
| lab | current state plus sealed history of waves | the standing *balance* (exploration vs hardening, budget left) and its resting points |
| claims | registry of assertions with strength | what each assertion *can bear*; strength = weakest verdict |
| threads | author and verifier, independent result first | an *independent second weighing* of the same thing |
| puzzles | what did not add up, reopening exploration | a *small residual that tips the balance* and is not rounded away |
| CLI | writes, queries, summarizes, backs hooks | a *neutral officer* who holds the instrument; the agents do not keep their own books |

Distinctions the placeholder names cannot make: "ledger" is taken by an existing CLI and says
nothing of strength; "lab" names a place, not a state; "threads" is already used by `umbod`;
"puzzles" does not say that the thing is *small but not dismissible*, which is its whole job.

## 2. Root Sources

Three families were mined and understood; one is carried forward.

### A. Latin weighing and metrology (carried forward)

- **Root:** PIE *\*(s)pend-* ("draw, stretch") → Latin *pendere* ("weigh out, pay"), *pondus*
  ("weight"), *libra* ("scales, pound"), *statera* ("steelyard, balance"), *examen* ("tongue of a
  balance, weighing, examination"). Roman payment was made by weighing bronze, so one verb covers
  both paying and judging.
- **Family / cognates:** *expendere* (weigh out, spend), *impendere*, *dispensare*,
  *dispensator* (steward who weighs out and keeps accounts), *stipendium*, *pensum*,
  *perpendere* ("weigh thoroughly, examine"), *ponderare*, *deliberare*, *aestimare*;
  Romance *pensare* ("think", literally "weigh"); Danish and Norwegian *pondus* ("gravity,
  authority"), English *spend*, *expense*, *ponder*, *examine*, *scruple*.
- **Internal logic:** the same act yields *cost* (what is weighed out) and *judgement* (what is
  weighed). A ledger entry and a verdict are two readings of one balance. This is the asset
  mined: the stores can be named as parts of one instrument rather than as unrelated nouns.
- **Connotation & history:** neutral, technical, no religious or political charge. Two named roles
  fit the design closely: the **libripens**, the citizen who held the scales in the Roman sale
  per aes et libram (separate from the five witnesses), and the **scrupulus**, which is both a
  small sharp stone (hence a nagging doubt) and the smallest weight in the Roman and apothecary
  series (1/24 ounce, 20 grains).
- **Anchoring exemplar:** a discrepancy of one scruple on the balance that was followed instead of
  rounded off. Rayleigh's nitrogen from air against nitrogen from chemical sources differed by
  about half a percent, and following it gave argon (1894). Kepler's eight minutes of arc is the
  same pattern in astronomy. Both are quoted from memory and not re-checked in this session.

### B. Greek *poros* ("way, passage, means") (runner-up)

- **Root:** *poros*, PIE *\*per-* ("pass over"). **Family:** *a-poria* (no way through, also lack of
  means), *eu-poria*, *dia-porein* ("go through the difficulties, with another"), *porisma*
  ("thing procured", also the geometric by-product), *poroi* (state revenues, Xenophon).
- **Internal logic:** ways and means in one root: impasse, passage found, gain procured.
- **Connotation:** *aporia* is ready-made for the puzzle store and is already English philosophical
  vocabulary. The Socratic pattern *elenchus then aporia* matches "peer review that produces
  puzzles". Weak spots: *porisma* is a defined term in geometry (Poncelet's porism), so a claims
  store with that name would mislead mathematicians; *poros* reads as "pore".
- **Exemplar:** Aristotle, *Metaphysics* B, "first go through the difficulties well".

### C. Alexandrian philological apparatus (rejected as a family)

*lemma* (quoted text), *scholion* (marginal note on a lemma), *obelos* (sign of doubt),
*zetema* (problem raised), *diorthosis* (correction). Good for claims-plus-threads, but it names
a text-editing practice, not spending, so it leaves the ledger, lab and CLI uncovered.
*Obelos* and *obolos* are variants of one word (spit, then coin), a nice fact but not enough.
*Lemma* already means a helper theorem in this project.

## 3. Candidates

Template adaptation within family A: Latin loan, keeping Latin sounds (opaque to partial
transparency, since most terms have English cognates), full family seeded.

| Object | Candidate | Gloss | Gains / Loses |
|---|---|---|---|
| ledger | **expensa** | "things weighed out", the Roman *expensum* entry | Gains: exact accounting sense, readable to English and Romance speakers. Loses: close to "expensive" |
| ledger | impensa | outlay on a purpose | Gains: "outlay on a claim" is the actual join. Loses: less immediate |
| ledger | obol (Greek) | smallest unit of account | Gains: very short. Loses: Obol is a crypto network; outside family A |
| lab | **statera** | steelyard; the balance | Gains: the lab *is* the balance between exploration and hardening; echoes "state". Loses: also a React library on npm |
| lab | annales / fasti | year-by-year record | Gains: sealed yearly notes. Loses: say nothing of the live balance |
| claims | **pondus** | weight, what a thing can bear | Gains: strength is the point; Danish "pondus" means gravity. Loses: `pondus` is the name of two existing tools (see flags) |
| claims | tessera | token, tile; the split tally half | Gains: tile, so kin to imbrex; "halves must fit" suits verification. Loses: ConsenSys product, die/gambling echo |
| claims | porisma (Greek) | thing procured | Loses: geometric term of art |
| threads | **examen** | tongue of the balance; weighing; examination | Gains: the verifier's independent weighing; fits the family. Loses: reads as "exam" in Spanish, French, German |
| threads | collatio | bringing together, comparing, conferring | Gains: best fit to "independent result first, then compare" (textual collation). Loses: SQL collation; not from *pend-* |
| threads | elenchus (Greek) | cross-examination | Gains: couples to aporia. Loses: only refutation |
| puzzles | **scrupulus** | sharp pebble; doubt; smallest weight | Gains: small, nagging, not dismissible; in the family by metrology. Loses: four syllables |
| puzzles | aporia | impasse | Gains: known word. Loses: names a block, not a small residual |
| puzzles | residuum | what remains (Herschel's residual phenomena) | Gains: exact history. Loses: "residual" is ML jargon |
| CLI | **libripens** | scale-holder in the Roman sale | Gains: neutral officer, free on every registry checked. Loses: nine letters; "libri-pens" may be read as "book pens" |
| CLI | trutina | balance | Loses: PyPI name taken |
| CLI | dispensator | steward who weighs out | Gains: accounts. Loses: ten letters |

## 4. Morphological Family

Recommended set, with directory, forms and the verbs the CLI can use. Forms marked *constructed*
are by analogy and need a Latinist's review.

| Object | Recommended | Dir / identifier | Entry (one) | Verb (CLI) | Agent / adjective | Derived forms |
|---|---|---|---|---|---|---|
| ledger | **expensa** | `__expensa__/` | *expensum* | `expend` (*expendere*) | *dispensator*: the hook that writes the rows | "outlay", budget left = what has not yet been weighed out |
| lab | **statera** | `__statera__/` | the current *note*; each sealed wave | `seal` | adjective: none needed | wave number = position of the beam |
| claims | **pondus** | `__pondus__/` | a claim, with its weight | `weigh` (*ponderare*) | *ponderous* is rejected (negative sense) | "carries weight"; weakest open verdict = the weight it is rated at |
| threads | **examen** | `__examen__/<claim-id>.md` | one thread | `examine` | *examinator* for the verifier (constructed use) | the verifier's first entry is its own *examen* |
| puzzles | **scrupulus** | `__scrupuli__/` | a *scrupulus*, pl. *scrupuli* | `raise`, `follow`, `park` | *scrupulosus* ("scrupulous"): an agent that follows them | "to follow a scruple" |
| CLI | **libripens** | `libripens` | none | `libripens <store> <verb>` | none | short alias `lbp` if wanted (check) |

Example commands: `libripens scrupulus raise`, `libripens pondus weigh 3-author-1`,
`libripens expensa summary --wave 3`.

## 5. Recommendation

The set is **expensa, statera, pondus, examen, scrupuli, libripens**, one family.

1. **Mapping fidelity.** Each name is a role in one act of weighing, and each role is the one the
   object plays: cost (expensa), standing balance (statera), what a result bears (pondus),
   independent second weighing (examen), small residual (scrupulus), neutral holder of the scales
   (libripens). No candidate from families B or C covers all six without misfit.
2. **The puzzles store gets the best fit.** A scrupulus is small, sharp and nagging, and it is
   also the smallest unit on the weighing scale. "It did not balance by a scruple" is the
   phrase that the store exists to catch and not round away.
3. **The pairs carry meaning.** *Expensa* and *pondus* are the two sides of the same ledger
   (what it cost, what it weighs). *Libripens* matches the design rule that agents do not write
   their own books.
4. **Configuration.** Latin sounds kept; ASCII-clean without change; full paradigm for the
   family, with verbs only where well formed; register is technical Latin, as for *imbrex*.
5. **How it pairs with imbrex.** Not by root, but by register: Latin, concrete, Roman material
   culture, one object per word. *Imbrex* is a tile and *libripens* a person with scales; both can
   be explained in one sentence. If a root-sharing pair is wanted, the tile family offers
   *tegula* (flat tile) for any store, but none of the six objects maps to it.

Fall-backs, in the order to try them: threads **collatio**; claims **pondera** (plural, if the
`pondus` tools cause confusion); lab **annales**; ledger **impensa**.

## 6. Pronunciation & Orthography

- **Pronunciation:** ex-PEN-sa; sta-TEH-ra; PON-dus; ex-AH-men (English "ig-ZAY-men"); skroo-POO-loos,
  plural skroo-POO-lee; LEE-bree-pens (classical LIB-ri-pens).
- **Spelling notes:** no diacritics in use; Latin macrons are dropped. Common misspelling risks:
  "scrupulus" (one *l* in the middle), "libripens" (one *p*).
- **Identifier-safe form:** `__expensa__`, `__statera__`, `__pondus__`, `__examen__`,
  `__scrupuli__`, binary `libripens`. All are lowercase ASCII and recognizable from the headwords.
- **Informal shortening:** "scruples" for the puzzles; avoid it in prose where "scruples" reads as
  ethics.

## 7. Provenance

- **Sources consulted:** Wiktionary Latin entries for *scrupulus*, *statera*, *examen* and *pondus*
  (the fetched pages), Wikipedia on *mancipatio* (the libripens as a separate scale-holder, with at
  least five witnesses) and on the scruple (1/24 troy ounce, 20 grains, from Roman *scrupulum*);
  the earlier naming report `__reports__/naming/01-findings_v1.md` for register; the design in
  `__reports__/meta_process/05-architecture_v1.md`.
- **Collision checks run (2026-10-18):**
  - On this machine, none of libripens, statera, pondus, expensa, examen, scrupulus, scrupuli,
    aporia, trutina, impensa, collatio, elenchus, dispensator, obol is on PATH, nor in
    /usr/bin, /usr/local/bin or /opt/homebrew/bin.
  - Registries (npm, PyPI, crates.io): **libripens, expensa, scrupulus, scrupuli are unclaimed on
    all three**, which matters for the binary. `statera` is a React state library on npm.
    `examen` exists on npm and PyPI. `trutina` exists on PyPI. `aporia` exists on all three.
    **`pondus` exists on all three**: a GitHub-organization CLI on npm and an AI-model benchmark
    aggregator on PyPI and crates.io (`cargo install pondus`). As a directory name it does not
    collide; as a binary it would, so it is not used as one.
  - Project collisions: none of the six names appears in the existing `umbod` file set
    (`__threads__`, INTENT.md, INBOX.md, QUESTIONS.md, STATUS.md, HANDOFF.md, WORKLOG.md,
    ARTIFACTS.md), `__roadmap__`, `__reports__`, `__design__` or `__canons__`. Replacing
    `__threads__` removes the clash with `umbod`.
- **Baggage flags:**
  - *examen*: "exam" in Spanish and French (confirmed on the Wiktionary page), probably German;
    Jesuit "examen" in Spanish-language usage (from memory).
  - *pondus*: Danish and Norwegian "gravity, authority" (confirmed, favourable); a Norwegian comic
    strip bears the name (from memory).
  - *scrupulus*: "scruple" means a moral qualm in English and cognate languages; this is
    deliberate for the puzzles, not for the ledger.
  - *libripens*: "libri" reads as "books" in Romance languages; harmless, memorable.
  - *expensa*: Argentine and Uruguayan *expensas* = building maintenance fees (from memory); still
    money.
  - *statera*: a React library, not a tool shadowing a command.
- **Unverified, open for review:**
  - Latin forms *expensum* as a ledger entry (Roman bookkeeping, "expensum ferre"), *examinator*,
    *dispensator*, and the verbs used as CLI words: constructed or taken from memory, not checked
    against Lewis & Short. Wiktionary for *libripens* returned 404; the word rests on the
    *mancipatio* page and my knowledge of Gaius, Institutes 1.119, which I did not re-read.
  - The scruple as a unit of arc (Kepler's "eight scrupula") was not confirmed: the scruple page
    mentions only mass. Treat that link as unconfirmed.
  - The Rayleigh and Kepler anecdotes are from memory.
  - The "state" pun on *statera* is an association (both come from PIE *\*steh₂-*), not a
    derivation.
  - No native Latin or international-team pronunciation test was done.
