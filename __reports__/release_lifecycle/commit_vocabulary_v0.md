# Murmuration commit vocabulary — Findings (v0)

Date: 2026-10-30

---
type: findings
topic: release_lifecycle
date: 2026-10-30
version: v0
prior-version: none
key-metric: subjects accepted by the proposed schema_pattern: 302 of 850 (prior: N/A, delta: N/A)
decision-required: confirm
---

Scope: `origin/main` at 3afb2da (local ref, not fetched), 850 commits, 2026-10-18 to 2026-10-30. All counts are mine, from `git log --name-only` parsed in Python.

## Headline Result

metric: subjects accepted by the proposed `schema_pattern` (every origin/main subject)
value: 302 of 850 (35.5%); 103 of 105 since 2026-10-27
unit: commits
prior: N/A (first run)
direction: new

The 548 rejects are 546 old trace-form subjects and 2 conventional ones. They are never rewritten, so only new ranges matter.

## Results Tables

### 1. Subject forms in use (850)

| Form | n | Examples |
|---|---|---|
| `type(scope): ` with a real type | 229 | docs 118, fix 45, feat 16, chore 14, test 13, build 5, merge 5, perf 5, ci 3, revert 3, refactor 2 |
| git `Merge …` | 53 | `Merge task/windows-paths: …` |
| id in the type slot | 362 | `w08-c1: …`, `wave-06: …`, `w09-j: …` |
| kind word in the type slot | 38 | `verdict(w06-c4)` 9, `user_words:` 6, `synthesis:` 6, `report(…)` 4, `lab_status:` 3 |
| no `x: ` form at all | 168 | `wave-09 author-w09-4: puzzles`, `w09 reproducer-w09-4: …` |

Matching no lexical `word(scope)?: ` form: 221 (168 + 53 Merge). Matching no known type: 621. 37 distinct scopes in the conventional commits. The only variants: `lab_status`/`lab-status`, `user_words`/`user-words`, and one comma scope.

### 2. Stores: do commits follow the folder?

| Store | commits touching | only this store | with another store | also touching plugin |
|---|---|---|---|---|
| `__pondus__` | 200 | 94 (47%) | 106 | 13 |
| `__scrupuli__` | 184 | 33 (18%) | 151 | 12 |
| `__statera__` | 172 | 122 (71%) | 50 | 8 |
| `__instrumenta__` | 191 | 28 (15%) | 163 | 33 |
| `__reports__` | 231 | 61 (26%) | 170 | 21 |
| `__roadmap__` | 51 | 43 (84%) | 8 | 3 |
| `__design__` | 9 | 1 | 8 | 0 |
| plugin tree | 157 | 98 | 59 | n/a |

620 commits touch a trace store; 247 (40%) touch two or more. `__statera__` holds three files: `wave-NN.md` (146 commits), `synthesis.md` (24), `user_words.md` (18). `handbacks/` has no commit yet. Verdicts are sections inside `__pondus__/<claim>.md`, so a verdict is an act, not a folder. Of the 200 pondus commits, 62 file a claim, 61 add a verdict, 58 edit a head, 3 record a PI decision alone, and 16 mix acts (12 filing plus verdict, 4 filing plus decision).

### 3. Research commits that touched shipped code

| Measure | n |
|---|---|
| old-form subjects touching plugin source | 61 (waves 4 to 8, all before 2026-10-27) |
| same, after the move into `plugins/murmuration/` | 0 |
| feat/fix/perf commits also carrying trace files | 14 |
| non-release types on the plugin tree since the move (43 commits) | test 8, build 5, chore 4, docs 4, refactor 2 |
| revert on the plugin tree | 3 |

### 4. Era comparison (the 60-day window is the whole history)

| Period | commits | conventional | git Merge | old trace forms | accepted |
|---|---|---|---|---|---|
| A 10-18 to 10-19 | 95 | 88 | 7 | 0 | 94 |
| B 10-20 to 10-26 (waves 4 to 9) | 650 | 47 | 40 | 563 | 105 |
| C 10-27 to 10-30 (plugin work) | 105 | 94 | 6 | 5 | 103 |

### 5. Proposed vocabulary

Evidence is the number of the 562 trace-only commits that the path rule below assigns to each type, except where marked.

| Type | Scope rule | Paths | Releases | Evidence |
|---|---|---|---|---|
| `feat` | component, kebab or snake | `plugins/murmuration/**` | minor | 16 |
| `fix` | same | same | patch | 45 |
| `perf` | same | same | patch | 5 |
| `docs` `test` `build` `ci` `chore` `refactor` `revert` | same | anywhere; never trace stores | no | 118, 13, 5, 3, 14, 2, 3 |
| `claim` | `wNN-cN` | `__pondus__` head, plus its scripts and puzzles | no | 209 (2 literal) |
| `verdict` | `wNN-cN` | verdict or PI-decision section | no | 82 (9 literal) |
| `wave` | `wNN` | `__statera__/wave-NN.md` | no | 134 |
| `synthesis`, `user_words` | optional `wNN` | those two files | no | 13 (6), 11 (6) |
| `reports` | topic dir or agent id (`w09-i`) | `__reports__/**`, explorer hand-offs | no | 113 |
| `rdm` | campaign dir | `__roadmap__/**` | no | 45 literal |
| `merge` | scope | PR merge subjects | no | 5 literal |
| `Merge …` | none | git's own | no | 53 literal |

Priority when a commit spans stores: `__pondus__` over `__statera__` over the rest. Only 18 of 562 (3%) need it: 5 pondus with statera, 13 with several statera files. 218 of the 562 need the agent role (author gives claim, reproducer gives verdict, explorer gives reports) read from the subject or file name rather than the path alone.

## Observations

| Signal | Baseline / Expected | Observed [source] | Interpretation |
|---|---|---|---|
| Lead form converging | one form by the last wave | `wNN-cN:` leads 78% of wave 4 (43 of 55) and 22% of wave 9 (20 of 89); `wave-NN:` 0% to 34%; wave+agent forms 0% to 29% [source: git log] | Diverging within waves; the period C "convergence" is the trace stores going quiet (6 trace commits: 3 `docs(…)`, 3 `user_words:`). |
| Claim id equals the claim file touched | scope derivable from paths | 138 of 258 subjects led by a claim id touch that file (53%) [source: name-only] | The id names the claim served, not the file; the scope must be written. |
| Wave id available to write | scope writable by agents | 489 of 502 old trace subjects carry a wave id; 44 name two or more claims | One id per commit; a multi-claim commit takes the wave id. |
| Types fitting the existing forms | existing forms reusable | `verdict(wNN-cN)`, `synthesis:`, `user_words:`, `claim(…)` already pass: 22 old subjects | The proposal ratifies what agents already wrote. |
| Hidden shipped change | none | 61 trace-form commits changed plugin source | A trace type must never cover plugin paths. |

## Charts & Visualizations

Share of old-form subjects led by `wNN-cN:`, by wave (n in brackets):

```
w4 [ 55] ################################ 78%
w5 [ 51] ############################## 73%
w6 [137] ####################           50%
w7 [ 81] ###############                37%
w8 [127] ###################            46%
w9 [ 89] #########                     22%
```

## Contradictions & Surprises

- The brief's "last 60 days against all history" is the same set: the first commit is 2026-10-18, 12 active days. I compared three periods instead.
- `plugins/murmuration/**` exists only since d0c605d (2026-10-27, 46 renames). Before it the plugin lived in 7 root folders, so the research-versus-plugin check returns 0 by construction on the new path. I counted the old root paths (61).
- The repo has no `AGENTS.md`, `CLAUDE.md`, commitizen config, `CONTRIBUTING` or tag (the local clone lists none, although 0.1.1, 0.1.2 and 0.2.0 were released). The three releases are hand-written `chore(release): murmuration X.Y.Z`.
- 846 of 850 commits are by one author; the 4 others are the CI bot's `build(bin)`.

## Steering Questions

- [now] D1 to D5 below.
- [now] Approve the regex, or say which types to drop.
- [next run] Add the path check to CI and the rules to the briefs.
- [later] Re-derive after the next research wave, since waves 4 to 9 supplied all the trace evidence.

## Decisions for Eliott

| # | Decision | Options | Recommendation and evidence |
|---|---|---|---|
| D1 | What the type follows | folder; act on the primary artifact; one `trace` type | The act. Folders fail: only 15 to 26% of scrupuli, instrumenta and reports commits stand alone. Pondus commits are single-act in 184 of 200. |
| D2 | Own types for `puzzle` and `probe` | add both; add neither | Neither. 82% of scrupuli commits and 85% of instrumenta commits touch another store; the 33 puzzle-only commits are 25 author, 5 PI, 2 reproducer, 1 explorer, so puzzles take the owning act's type. `probe` collides with the top-level `probes/` folder (3 `test(probes)`). The 28 instrumenta-only commits are claim scripts and become `claim(wNN-cN)`. |
| D3 | Id grammar | `wave(09)` against `wave(w09)` | `w09` everywhere (`wave(w09)`, `claim(w09-c8)`, `reports(w09-i)`); the brief's examples mix both. |
| D4 | Plugin guard | rule only; CI path check next to `cz check` | CI check: trace types, `rdm` and `reports` may not touch `plugins/murmuration/**`. cz sees no paths. Also require `fix` to revert a released change (3 reverts today), and note that `build(bin)` ships binaries yet never releases (5). |
| D5 | Release and bot subjects | keep hand-written; configure `bump_message` | Set `bump_message` to `chore(release): murmuration $new_version`; cz's default `bump: …` fails the regex. `build(bin): …` already passes. |
| D6 | Scope required on code types | required; optional | Required. One reject (`chore:` on 10-18) and 227 accepted. |
| D7 | Subject length | none; 120 | None for now: 458 of 850 exceed 72 chars; a 120 cap rejects 42 of 302 accepted. |

## Writers

| Writer | Today | What changes |
|---|---|---|
| author, reproducer, explorer, proof-adversary | `briefs.md` rule 5 and `working_defaults.md:30`: "a message that says why", no format | Add the role-to-type table and the id grammar to both lines. |
| research PI | commits wave notes by hand | `wave(wNN)`, `synthesis`, `user_words`; the hook `user_words.py` only writes the file and calls no git. |
| `managing-roadmaps` | generic `<type>(<scope>)` (`dirtree-execution.md:138`) | name `rdm(<campaign>)`. |
| CI bot | `build(bin): … for <sha>` (workflow line 284) | none. |
| umbod | none: 0 of 850 commits show `close cycle`, `pi-ack` or `__threads__` | None today. Its `commits.rs` emits `style` and `pi-ack(<slug>)`, which this regex rejects. `SKILL.md` names a `committing-changes` skill I did not find in this session. |

## schema_pattern (draft)

```
(?s)(?:(?:feat|fix|perf|docs|test|build|ci|chore|refactor|revert)\([a-z0-9][a-z0-9_-]*\)!?|(?:claim|verdict)\(w\d{2}-c\d+\)|wave\(w\d{2}\)|(?:synthesis|user_words)(?:\(w\d{2}\))?|(?:reports|rdm|merge)\([a-z0-9][a-z0-9_-]*\)):( [^\n\r]+)((\n\n.*)|(\s*))?$|Merge .*
```

Tested with Python `re.match` (cz is not installed here, so `cz check` itself did not run). Run on the 850 subjects: 302 accepted, 548 rejected. Rejected: 546 old trace forms and 2 conventional.

| Reject sample | Why |
|---|---|
| `w08-c11: fenced blocks are text; …` | id in type slot |
| `wave-07 reproducer-w07-2: live runs, …` | no type, no colon after it |
| `w04-c10 verdict (reproducer-w04-10), …` | no type |
| `wave-08 report v0 (two placeholders …)` | no type |
| `fix(wave-05, research-loop): reassessment times …` | comma scope |
| `chore: add the AGPL-3.0 license and gitignore` | scope missing |

Unit checks pass: `feat(guard)!: x`, a body with a trailer, `verdict(w08-c1): SUPPORTED`, `merge(guard): x`, `Merge pull request #1 from a/b`. They fail as intended: `wave(09): x`, `claim(w08): x`, `bump: version …`, an empty subject. The regex needs `allowed_prefixes` only if a `Revert "…"` subject is wanted.

## Pointers

- Method: `writing-history` 1.2.0 `references/convention-setup.md`.
- Brief rules: `plugins/murmuration/skills/research-loop/references/briefs.md` (lines 26 to 28), `working_defaults.md` (line 30).
- CI: `.github/workflows/guard-binaries.yml`.
- Move commit: d0c605d. Release commits: b511983, 72a61d0, 1f164ae.
