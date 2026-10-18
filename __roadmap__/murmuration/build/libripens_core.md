# libripens core

**Goal**: Build the Rust binary that is the only writer path to the stores, the hook entry point and the MCP server.
**Pre-conditions**:
- [ ] `platform_probes` and `instrument_validation` done (this node is amended from their findings first)
**Success Gates**:
- ✅ `cargo test` passes on darwin and linux, arm64 and x64 [run]
- ✅ A replay of the genesis study's reports into the stores reproduces the reproducer's and reviewer's catches as gate or brief entries [run]
**References**: [R01 §Stores, §libripens, §Hooks](../../__reports__/genesis/11-architecture_v4.md); [R02](../../__reports__/genesis/06-stores_umbod_sustainability_v0.md) §2–5

## Step 1: Stores
**Goal**: Append-only per-writer segments with schema validation
**Implementation Logic**:
Event schemas for the five stores; `append` writes one validated line to the caller's own segment and fsyncs; derived state (current label, disputed, puzzle status, budget left) is a fold over events.
**Deliverables**: `libripens/src/stores.rs` (types `ExpensaRun`, `StateraEvent`, `PondusEvent`, `ExamenMsg`, `ScrupulusEvent`; fn `append`); `libripens/src/derive.rs` (fn `current_label`)
**Consistency Checks**: `cargo test --manifest-path libripens/Cargo.toml stores` (expected: PASS)
**Commit**: `feat(libripens): add the five append-only stores with derived state`

## Step 2: Index and queries
**Goal**: Millisecond queries without a source-of-truth database
**Implementation Logic**:
Gitignored SQLite index with per-segment byte watermarks; `query`, `rebuild`, `brief` (ordered as in v4).
**Deliverables**: `libripens/src/index.rs` (fn `ingest`, fn `rebuild`); `libripens/src/brief.rs` (fn `render_brief`)
**Consistency Checks**: `cargo test --manifest-path libripens/Cargo.toml index` (expected: PASS)
**Commit**: `feat(libripens): index the stores and render the session brief`

## Step 3: Hooks and measures
**Goal**: One binary behind every hook
**Implementation Logic**:
`hook` subcommands for the events in v4; the guard; the presence gate; `measure` (zstd bits with a project dictionary, conditional bits, coverage).
**Deliverables**: `libripens/src/hooks.rs` (fn `subagent_stop`, fn `pre_tool_use`); `libripens/src/measure.rs` (fn `bits`, fn `new_bits`, fn `coverage`)
**Consistency Checks**: `cargo test --manifest-path libripens/Cargo.toml hooks` (expected: PASS)
**Commit**: `feat(libripens): serve the hook events and the information measures`

## Step 4: MCP server and CI
**Goal**: Resident server for mcp_tool handlers; cross-platform builds
**Implementation Logic**:
`libripens mcp` exposing append, query and measure as typed tools; CI matrix building release binaries.
**Deliverables**: `libripens/src/mcp.rs` (tools `append`, `query`, `measure`); `.github/workflows/libripens.yml`
**Consistency Checks**: `cargo test --manifest-path libripens/Cargo.toml mcp` (expected: PASS)
**Commit**: `feat(libripens): expose the stores over MCP and build every platform`
