# READMEs and the Nest entry

**Goal**: A reader of the repository or of the installed plugin knows it is Claude Code only, macOS and Linux, installed from Nest; Nest's entry is ready on a local branch.
**Pre-conditions**:
- [ ] `relocate_plugin` merged into `release/claude-code`
- [ ] `../Nest` on `main`, clean (checked 2026-10-27 at 6318249)
**Success Gates**:
- ⬜ [static] Root `README.md` opens with a warning banner: Claude Code only (2.1.295 or later), installs on macOS and Linux, Windows installs and other harnesses are planned and not supported
- ⬜ [static] Root `README.md` install section gives `claude plugin marketplace add CrackingShells/Nest` then `claude plugin install murmuration@cracking-shells`, and a maintainer section (CI owns `bin/`; bump `plugin.json` only after the `build(bin)` commit for the same sources is on `main`; the pre-commit hook; `--plugin-dir plugins/murmuration` for local work)
- ⬜ [static] Root `README.md` has a "Research record" section saying what `__reports__/ __pondus__/ __statera__/ __scrupuli__/ __instrumenta__/ __roadmap__/ probes/ validation/` hold, that they are the design experiment's evidence, and that `__design__/settings_record/` keeps the settings the lab ran with
- ⬜ [static] `plugins/murmuration/README.md` exists: the banner, what the plugin is, `/lab`, requirements, link to the repository
- ⬜ [run] In `../Nest` on branch `feat/list-murmuration`: `.claude-plugin/marketplace.json` parses and lists `murmuration` with `source: {source: git-subdir, url: https://github.com/CrackingShells/Murmuration.git, path: plugins/murmuration}`, no version, ref or sha; `README.md` has its row; `claude plugin validate ../Nest` passes; nothing pushed
- ⬜ [run] `check_plugin.py --root plugins/murmuration` output is recorded in the campaign Gotchas as advisory (it rejects exec-form `args`, `if`, `onFailure`, `PostToolBatch` by design for cross-harness portability)
**References**: `README.md` (current: "not yet published", `--plugin-dir /path/to/Murmuration`); `../Nest/.claude-plugin/marketplace.json` entry shape (git-subdir entries such as `colgrep-mcp-dev`); `../Nest/README.md` plugin table

## Step 1: Root README for a public repository
**Goal**: The root README reflects the published layout and scope.
**Implementation Logic**:
1. Banner (GitHub `> [!WARNING]` block) at the top.
2. Install via Nest; local development via `claude --plugin-dir plugins/murmuration`.
3. Layout table (plugin subdir vs research record) and the maintainer notes listed in the gates.
4. Contributing: the issue tracker is live.
**Deliverables**: `README.md` (sections Install, Use, Requirements, Layout, Research record, Maintainers)
**Consistency Checks**: `grep -q 'murmuration@cracking-shells' README.md && grep -q 'WARNING' README.md && ! grep -q 'not yet published' README.md` (expected: PASS)
**Commit**: `docs(readme): Claude Code only, Nest install, layout and research record`

## Step 2: Plugin README and manifest description
**Goal**: The cached plugin carries its own short README.
**Implementation Logic**:
1. `plugins/murmuration/README.md`: banner, the team table, `/lab` and `/lab-status`, requirements, repository link.
2. `plugin.json` `description` names the scope in one sentence; version stays `0.1.0`.
**Deliverables**: `plugins/murmuration/README.md`; `plugins/murmuration/.claude-plugin/plugin.json` (`description`)
**Consistency Checks**: `claude plugin validate plugins/murmuration/.claude-plugin/plugin.json` (expected: PASS)
**Commit**: `docs(plugin): a README inside the plugin tree`

## Step 3: Nest entry on a local branch
**Goal**: Nest can list Murmuration with one push once `build(bin)` has landed.
**Implementation Logic**:
1. In `../Nest`, branch `feat/list-murmuration` from `main`.
2. Append the entry: `name murmuration`, the git-subdir source, `displayName Murmuration`, a one-line description, `category Productivity`. Claude catalogue only (no Codex entry: the hooks are Claude Code only).
3. README row: `| \`murmuration\` | Murmuration | <description> (Claude Code only) |`.
4. Commit on that branch; do not push (the user's go-ahead #3 comes after CI's `build(bin)`).
**Deliverables**: `../Nest/.claude-plugin/marketplace.json` (entry `murmuration`); `../Nest/README.md` (row)
**Consistency Checks**: `claude plugin validate ../Nest` (expected: PASS)
**Commit**: `feat(marketplace): list the Murmuration plugin`
