# Store names for the research lab, transmission traditions — Naming Report (v0)

Date: 2026-10-18 · Input to architecture v2. Sibling of `06-naming_classical_v0.md` (Latin weighing).

**Concept:** a team that keeps an open account of what it spends, records why each stage of work was
run and seals that record, asserts results at a stated strength, has each result examined by an
independent second party, and holds on to the small difficulties that did not fit.
**Target community / register:** an international research team and its agents; technical
register. The source register (scholastic, archival) is close to the phenomenon's own, so the name
matches rather than reframes it. Cultural visibility: acknowledged, never foregrounded.
**Hard constraints:** lowercase ASCII, usable as `__<name>__/` and as a binary name; short;
pronounceable internationally; no collision with `umbod`, `managing-roadmaps`, `writing-reports`,
`__design__` or known commands; no religious or political baggage that distorts the meaning.

## 1. Concept Mapping

Read as *transmission*, the six objects fall into two groups of three, and the groups mirror each
other across the traditions surveyed.

| Object | Relational structure | What the name must encode |
|---|---|---|
| puzzles | a difficulty noticed in something that otherwise passes | an *objection raised against a received thing*, with a life: open, answered, or left standing |
| claims | a statement put forward at a graded strength | a *commitment*: the author stakes credit on it; strength is that of the weakest support |
| threads | author and verifier, independent result first | a *discussion between peers that aims at the truth*, not at winning |
| ledger | open account of outlay, one row per run | an account that *lies open and is only added to* |
| lab | current note plus sealed history | a record whose *writer is protected from later revision*, including by the PI |
| CLI | writes, queries, summarizes, backs hooks | a *keeper who is not an actor*: agents do not keep their own books |

What the placeholders cannot say: "claims" does not say commitment; "threads" is already taken by
`umbod`; "puzzles" does not say that the thing has a lifecycle (open, answered, parked); "lab" names a
place, not a sealed record; "ledger" is taken as a command name (per the sibling report).

## 2. Root Sources

Eleven families were examined. Three are carried forward as sources of the recommended names (A, B, C);
two give a single name each (D, E). The rest are listed with the reason they were set aside.

### A. Rabbinic scholarship (Talmudic study and communal record-keeping) — carried forward

- **Root:** *kushya* (difficulty, objection; Aramaic *kashya*, Yiddish *kashe*); *sugya* (a unit of
  discussion; Aramaic *segi*, "to go"); *sofer* (scribe, from the root *s-p-r*: count, write, tell);
  *pinkas* (communal register, Greek *pinax* "tablet" borrowed into Mishnaic Hebrew).
- **Family / cognates:** a *kushya* is answered by a *terutz* (resolution) or left as *teiku*
  ("let it stand"); a decisive objection is a *tiyuvta* (refutation); study is done in a *havruta* (a
  pair of companions, from *haver*, "friend"). The Talmud explains *soferim* as "those who counted"
  (Kiddushin 30a): the scribes counted the letters of the text they copied.
- **Internal logic:** the sugya is a give-and-take of challenge and answer (*shakla ve-tarya*) built on a
  received text. Raising a difficulty is the scholar's contribution, not a complaint, and the tradition
  has a native word for each possible end of a difficulty. That is the asset: three statuses, already
  named, that match open / followed / parked.
- **Connotation & history:** a religious-scholarly register, used here as technical vocabulary.
  *Teiku* carries a popular acronym (Elijah will resolve difficulties and questions, hence a messianic
  overtone); the scholarly etymology is a shortening of *teikum*, "it stands". The Mishnah (Avot 3:16)
  says the ledger lies open and the hand writes, which is about accountability for every entry.
- **Anchoring exemplar:** the printed Talmud page: a received text with layers of questions and
  answers around it, never overwritten, only added to.

### B. Sanskrit debate and inquiry (Nyaya) — carried forward

- **Root:** *pratijna* (the thesis put forward, first member of the five-part argument), *hetu*
  (reason, evidence), *siddhanta* (established tenet), *vada* (discussion aimed at truth), *samshaya*
  (doubt that starts inquiry), *nirnaya* (ascertainment).
- **Family / cognates:** *vada* is set against *jalpa* (arguing to win) and *vitanda* (attacking
  without holding any thesis of one's own). Among the "points of defeat" (*nigrahasthana*) the
  tradition lists *pratijnahani* (abandoning one's thesis), *pratijnantara* (shifting the thesis) and
  *pratijnavirodha* (contradicting it).
- **Internal logic:** the debater who changes the claim under attack, or attacks without a position,
  has lost by the tradition's own rules. The lab's rules are the same rules: the verifier records its own
  result first (so it cannot be a *vitanda*), and a changed claim statement escalates (so the author
  cannot shift the thesis quietly).
- **Connotation & history:** secular philosophical vocabulary, centuries of commentary. *Pratijna* in
  Hindi (*pratigya*) also means a vow, which adds the sense of staking one's credit. Low baggage.
- **Anchoring exemplar:** the debate between two parties who each take up a position and a
  counter-position, with the aim of finding out, not of winning.

### C. Islamic hadith criticism — carried forward as logic, set aside as names

- **Root:** *isnad* (chain of transmitters, "supporting"), *matn* (the text), *'ilal* (hidden defects in
  an apparently sound report), *muqabala* (collation of a copy against its exemplar).
- **Internal logic:** a report is as strong as its weakest link; independent routes strengthen it; a
  critic with trained judgement spots a defect that every formal check misses, by gathering all variants
  of the report and comparing them. This is the closest match to the claims rule and to the puzzles
  mission.
- **Why set aside:** `isnad` and `sanad` are taken in this exact domain (see section 7), so using them
  would confuse the lab's claims with an existing multi-agent provenance framework.

### D. Imperial and royal records (Chinese *shilu*, Korean *sillok*) — one name

- **Root:** *shilu* (實錄, "veritable record"; Korean *sillok*).
- **Internal logic:** a state record compiled by a committee from the historians' daily notes after a
  reign; in Joseon the historians were legally protected from interference by the king, and the drafts
  were pulped after compilation. The norm: the record's writer cannot be edited by the person the
  record is about.
- **Connotation:** dynastic chronicle; the hierarchy is incidental to the norm used here.

### E. Andean *khipu* — alternative for the ledger

- **Root:** *khipu* (knot), *khipukamayuq* (keeper of the knots). Cord colour, position and knots
  recorded storehouse contents, tribute and census; sources report that colonial courts called keepers
  to read them out. Gary Urton has argued for a binary coding in their features (contested), a
  resonance with this project that is not load-bearing.

### Set aside

| Family | Reason |
|---|---|
| Japanese *koan* (from Chinese *gong'an*, "public case file") | puzzles; overloaded Zen reading and a tech cliché |
| Japanese *mondo* | master-to-disciple, not peers; also an English intensifier |
| Chinese *jiaochou* (collation as a pair of "opponents") and *cunyi* ("keep the doubt") | strong ideas for the pair and for parking; pinyin hard for non-Chinese speakers |
| Arabic *daftar*, Persian-Turkish *defter* (register) | `daftar` is a PyPI tool that records what produced each computational result |
| Persian-Arabic *tarikh* (chronicle, date) | `tarikh` is an agentic "chief of staff" repository and a date package |
| Indigenous genealogical and oral records (*whakapapa*, songlines, wampum) | sacred or restricted in many communities; a naming exercise should not borrow them |

## 3. Candidates

Recommended name first; alternatives with gain and loss. Strategy for all recommendations is **loan**:
source phonology kept, spelling reduced to ASCII, opaque to English speakers, glossed in `AGENTS.md`.

| Object | Recommended | Alternatives | Gains / Loses |
|---|---|---|---|
| puzzles | **kushya** | *'ilal* (hidden defects); *mushkil* (everyday word for "difficulty" across Arabic, Persian, Urdu, Turkish); *samshaya* (doubt that starts inquiry) | `kushya` carries the three statuses natively (kushya, terutz, teiku). `ilal` fits "passes every check but looks off" best but has no lifecycle. `samshaya` is one typo from *samsara*. |
| claims | **pratigya** | *paksha* (position held; short, but means "side/party" in Hindi news); *dalil* (evidence; "theorem" in Indonesian; npm name taken); *siddhanta* (settled tenet, overclaims for a CONJECTURE); *isnad* (**rejected**, prior art) | `pratigya` is a thesis one is committed to, with a native list of ways to lose it. Longer than the rest; the *g/j* is a pronunciation risk. |
| threads | **sugya** | *vada* (truth-seeking discussion; crowded name, also a snack); *munazara* (Arabic disputation); *havruta* names the pair, not the record | `sugya` is exactly a challenge-and-answer unit per issue. Gap: a sugya opens on a cited text, not on the verifier's own result. |
| ledger | **pinkas** | **khipu** (knotted-cord account; strong image, but PyPI, npm and crates.io names are taken); *heshbon* (reckoning; guttural) | `pinkas` is literally a community's register, and its Mishnaic line is about an open ledger. Loses: Greek origin (a mediated loan) and a "pink" echo. |
| lab | **shilu** | *sillok* (Korean spelling, same record); *tarikh* (**rejected**) | `shilu` carries sealing and the writer's independence. Gap: a shilu is compiled after the reign; the lab note is written during and sealed per wave (the Korean *sacho* is the draft stage; the family covers both). |
| CLI | **sofer** | *kamayuq* (Quechua, "keeper"; clean, long); *katib* (Arabic "scribe", **rejected**: Kubeflow Katib, 1.7k stars, AutoML) | `sofer` is scribe, counter and teller in one root, which is what the binary does (append, count, tell). Loses: an npm package of that name exists (no command), and a Hebrew-transcription company uses the name. |

## 4. Morphological Family

Only well-formed members are listed. *Constructed* means built by analogy and needing review by a
speaker. The traditions are not all productive: `kushya` and `pratigya` give families, `shilu` gives
almost none, and the table says so.

| Object | Identifier | One entry | Agent / role | Verb (CLI) | Status or adjective | Notes |
|---|---|---|---|---|---|---|
| puzzles | `__kushya__/` | a *kushya* (pl. *kushyot*; the directory stays singular) | the one who raises it: *mekashe* (constructed use) | `raise` | open = *kushya*; followed = *terutz*; parked = *teiku*; one that overturns a claim = *tiyuvta* (optional, unverified) | the `terutz` field points to the brief or claim that followed; "followed" is looser than "resolved" |
| claims | `__pratigya__/` | a *pratigya* (English plural *pratigyas*) | author = the one who *makes* it; evidence field = *hetu* | `assert` | asserted = *pratijnata* (Sanskrit participle, "avowed"); settled = *siddhanta* (optional) | *pratijnantara* (shifting the thesis) names the escalation trigger "claim statement changed" |
| threads | `__sugya__/<claim-id>.md` | a *sugya* (pl. *sugyot*) | the pair = a *havruta* | `open`, `reply` | none needed | the pair carries the failure vocabulary *jalpa* and *vitanda* (section 5) |
| ledger | `__pinkas__/` | a row = *reshuma* (modern Hebrew "record", unverified) | keeper = *sofer* | `enter` | none needed | pl. *pinkasim*; "budget left" is a field, not a word |
| lab | `__shilu__/` | the current note; each sealed wave | none | `seal` | sealed = English | noun only; Chinese gives no clean verb or agent here |
| CLI | `sofer` | none | `soferet` (a woman scribe; real Hebrew form), `soferim` (pl.) | `sofer <store> <verb>` | none | example: `sofer kushya raise`, `sofer pratigya show 3-author-1`, `sofer pinkas enter` |

## 5. Recommendation

The set is **pinkas, shilu, pratigya, sugya, kushya, sofer**.

1. **Mapping fidelity, puzzles.** `kushya` is the one candidate whose own tradition has the three
   statuses the store needs (`kushya`, `terutz`, `teiku`) and that treats raising the difficulty as the
   valued act. `ilal` models the detection better but not the afterlife, so it is the alternative.
2. **Mapping fidelity, claims and threads.** Nyaya states the lab's two core rules as rules of debate.
   A discussion where one side holds no thesis of its own is a *vitanda*, which the verifier's
   "independent result first" entry prevents. A thesis shifted under attack is a *pratijnantara*, which
   the "claim statement changed" escalation catches. Arguing to win rather than to find out is *jalpa*.
   These three words are usable as pilot signal names whatever the stores are called.
3. **Mapping fidelity, records.** `pinkas`, `shilu` and `sofer` share one rule: the keeper is not the
   actor and the record is added to, never rewritten. That is the invariant "channel files are
   append-only" in `05-architecture_v1.md`, stated as a cultural norm rather than a hook.
4. **Configuration.** Loan, opaque, ASCII, technical register, acknowledged source. Every name is two
   or three open syllables, so the set sounds like one family even though it is not (next section).
5. **Collisions.** `kushya`, `pratigya`, `shilu`, `sugya`, `pinkas` are unclaimed on npm, PyPI,
   crates.io and Homebrew; none is on PATH. `sofer` is only an npm library without a command.
   `sugya` removes the `umbod` collision on `__threads__/`.
6. **Rejected on evidence, not taste:** `isnad` and `sanad` (in-domain prior art), `tarikh`, `daftar`
   (research-tool collisions), `katib` (Kubeflow).

**How the set hangs together.** No single tradition names all six, so this is stated plainly: four
names are Hebrew or Aramaic (`pinkas`, `sugya`, `kushya`, `sofer`), one Sanskrit (`pratigya`), one
East Asian (`shilu`). The links are structural.
- *The loop.* kushya (a difficulty noticed) leads to a pratigya (a claim put on the line), which a
  sugya (a paired discussion) can overturn, and a sugya leaves new kushyot. Rabbinic and Nyaya
  traditions reached this loop independently, which is why they fit together.
- *The custody rule.* pinkas, shilu and sofer are the open account, the sealed reasons and the
  keeper. The two groups meet at `sofer`, who writes into all five stores.
- *With the classical set.* The sibling report names the same system as weighing; this one names it as
  handing on and disputing. The two are not exclusive, and no name in either set collides with the
  other.
- *Single-tradition fallback (Hebrew and Aramaic only):* claims would be *hiddush* (a novelty offered for
  testing; too narrow, it excludes CITED) and lab *perek* (chapter; too small, it loses the state).
  Both are worse than the recommendation.

## 6. Pronunciation & Orthography

| Name | Approximate | Native | Notes |
|---|---|---|---|
| kushya | KOOSH-yah | Modern Hebrew *ku-SHYA*; Ashkenazi *KASH-ya* (hence "kasha"-like variants) | do not spell *kashya* in code |
| pratigya | pruh-TIG-yah | Hindi *pratigya*; Sanskrit *pratijna* (pruh-tij-NYAH) | the ASCII form follows Hindi; an alias `pratijna` is possible but not needed |
| sugya | SOOG-yah | *su-GYA* | |
| pinkas | PIN-kahs | Yiddish *pinkes* | |
| shilu | SHEE-loo | pinyin *shi* is a syllabic consonant, English approximates it | Korean *sillok* is the alternative spelling |
| sofer | SOH-fer | Modern Hebrew *so-FER*; Ashkenazi *SOH-fer* | |

Diacritics: none needed; no spelling here loses a distinction a reader would care about. Informal
shortening: none recommended (`sofer` is already short; shortening `pratigya` to "pratig" has no
precedent). Identifier-safe forms: `__pinkas__/`, `__shilu__/`, `__pratigya__/`, `__sugya__/`,
`__kushya__/`, binary `sofer`; each is the headword unchanged.

## 7. Provenance

**Sources consulted this session**
- Sugya definition, etymology, structure: [Wikipedia, Sugya](https://en.wikipedia.org/wiki/Sugya).
- Teiku, its acronym and its scholarly etymology: [OU Torah, "Teiku: Let It Stand"](https://outorah.org/p/261881);
  [Sefaria sheet, "From Teiku to Tikkun"](https://voices.sefaria.org/sheets/396413.1).
- Soferim and counting, Kiddushin 30a: [Etzion, 30a odd letters Torah](https://etzion.org.il/en/talmud/seder-nashim/massekhet-kiddushin/30a-odd-letters-torah).
- Pinkas as community register, Greek origin, Avot 3:16: [Wikipedia, Pinkes](https://en.wikipedia.org/wiki/Pinkes);
  [Jewish Encyclopedia, Pinkes](https://www.jewishencyclopedia.com/articles/12168-pinkes.html).
- Vada, jalpa, vitanda: [Wikipedia, Debates in ancient India](https://en.wikipedia.org/wiki/Debates_in_ancient_India);
  points of defeat (*pratijnahani*, *pratijnantara*, *pratijnavirodha*): search excerpts only, see
  [Vadanyaya of Dharmakirti](https://vedamsbooks.com/books/vadanyaya_of_dharmakirti_the_logic_of_debate).
- Isnad and matn, Schacht, isnad-cum-matn analysis: [Wikipedia, Isnad](https://en.wikipedia.org/wiki/Isnad).
- *'Ilal*, route collection: [Wikipedia, Ali ibn al-Madini](https://en.wikipedia.org/wiki/Ali_ibn_al-Madini),
  [ISAM, hidden defect in hadiths](https://www.isam.org.tr/en/publication/hidden-defect-in-hadiths-illa-and-shadh-2).
- Joseon sillok: [Wikipedia, Veritable Records of the Joseon Dynasty](https://en.wikipedia.org/wiki/Veritable_Records_of_the_Joseon_Dynasty).
- Khipu, keepers, colonial courts: [Quipu](https://wiki.riteme.site/wiki/Quipu) and the secondary
  sources behind a search on *khipukamayuq*.
- Collision checks run on 2026-10-18: `command -v` on this machine; npm, PyPI, crates.io and Homebrew
  lookups for about 25 headwords; GitHub repository search by name.

**Validation flags**
- **Prior art found (changes the result).** PyPI `isnad` (3.1.7) describes an "Isnad-Rijal framework for
  claim-level provenance in multi-agent knowledge systems", with a 52-star GitHub repository, a
  documentation site and a paper listed in its metadata; there is also an npm `isnad` verifier.
  PyPI `sanad` is a "hallucination gate that rejects any claim without a chain of proof". Both sit in
  this lab's own domain, so `isnad` was dropped although it matched best on logic. The framework's
  existence supports the weakest-link idea but is not evidence for our use of it.
- Other collisions, all tolerable for directory names: `khipu` (PyPI payments client, npm job queue,
  reserved crate for a note system, 300-star blockchain repository), `sofer` (npm library, no
  command), `vada` (npm architecture library, a snack), `daftar` (PyPI provenance recorder),
  `tarikh` (agentic "chief of staff" repository; Jalali date package), `katib` (Kubeflow, 1,706 stars).
  No name collides with `umbod`'s files, `__roadmap__`, `__reports__` or `__design__`. A grep of the
  repository for the six names found none in use.
- **Not verified in this session, from memory:** the term *terutz* as the standard answer to a
  *kushya*; *tiyuvta* as "decisive refutation"; *reshuma* as the modern Hebrew database "record";
  the *havruta* and *soferet* forms; *mutawatir* and *mudtarib* (mentioned nowhere in the
  recommendations); Urton's binary-coding claim; the order of Nyaya's categories (not used).
- **Flagged for a speaker:** all Hebrew and Aramaic forms (*mekashe* is a constructed use), the
  Sanskrit participle *pratijnata* used as an English adjective, and the Mandarin pronunciation note.
- **Known mapping gaps:** *teiku* formally closes a *be'aya* (an open question) rather than a *kushya*,
  so "parked" is a loose use; a *sugya* opens on a cited text, where our thread opens on the
  verifier's own result; a *shilu* is compiled after the reign; the claim that Joseon kings could not
  read the record rests on secondary sources, while the article confirms only the historians'
  protection and editorial independence.
- **Baggage.** `kushya`, `teiku` and `pinkas` come from religious scholarship, but as technical
  vocabulary; the messianic acronym of *teiku* is a popular etymology and not needed. `pratigya`
  (a vow) and `shilu` (dynastic records) carry no charge that distorts the lab meaning. No term is
  taken from a sacred or restricted indigenous practice. Residual uncertainty: whether any team member
  will find Hebrew or Sanskrit terms for a lab's stores distracting; the alternatives column offers
  neutral words (`mushkil`, `dalil`).
