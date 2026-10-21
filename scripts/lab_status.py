#!/usr/bin/env python3
"""Report the state of a lab project: open puzzles, the current label of each claim, and spend.

Read-only. Python standard library only.

    lab_status.py [--project DIR]   print the report for DIR (default: the project directory)
    lab_status.py --spend [--project DIR]   print only the spend section (DIR needs no `__statera__/`)
    lab_status.py --selftest        check the reports on a temporary project

The project directory is CLAUDE_PROJECT_DIR, else the current directory.

What it reads
    Markdown files are read without their HTML comments (`<!-- ... -->`).

    __scrupuli__/wave-NN-<name>.md   puzzles: `## S-wNN-<name>-<n>` headings (characters a-z 0-9 -).
                           Puzzles are kept per (file, id); duplicate ids and headings that are
                           not puzzle ids produce a warning line, never silence.
    __statera__/wave-NN.md wave notes; a note is closed when it has a `closed: YYYY-MM-DD` line.
                           A puzzle is disposed when a closed note has its id followed by a cell or
                           text starting `followed:` or `parked:`. (If the note has a heading
                           containing "disposition", only the lines under it count.)
    __pondus__/<id>.md     claims: a head (`# <id>: <statement>`, `label:`, optional `supersedes:`),
                           then one section per verifier, from `## verdict: <name>` to the next such
                           heading, whose last `verdict:` line counts when it is exactly a verdict
                           (case, bold and a trailing period tolerated; extra text warns). A verifier that
                           revises in place adds a new `verdict:` line and a `changed_by:` line below
                           the earlier one; with no `changed_by:` the script warns.
    ~/.claude/projects/    Claude Code's transcripts. The sessions of the lab are those whose first
                           `cwd` is the project directory or below it, or is in another git worktree of
                           the same repository (needs `git`; without it only the project directory).
                           Each API message is counted once, for the session named in its own record
                           (`sessionId`), so a forked session does not pay for its parent's messages.
                           USD: the session's `cost-state` record where the session has ended, else
                           list price (the table in this file). A subagent's output tokens are marked
                           `+` (at least) unless the last record of every one of its requests has a
                           `stop_reason`. Set CLAUDE_CONFIG_DIR to use another configuration directory.

Claim states shown: `unverified <LABEL>`, `cited (not verified)`, `<LABEL>`, `<LABEL> (gap)`, `below <LABEL>: restate`,
`<LABEL> (may restate higher)`, `withdrawn`, `escalated: PI decides`, `disputed: PI decides`,
`superseded by <id>`. Lines starting with `!` are warnings about files the script could not
read as specified.
"""
import collections
import contextlib
import glob
import io
import json
import os
import re
import subprocess
import sys
import tempfile

# A puzzle id is `S-wNN-<agent name>-<n>`; agent names use a-z, 0-9 and "-".
PUZZLE_ID = r"S-w\d+-[a-z0-9]+(?:-[a-z0-9]+)*-\d+"
PUZZLE_RE = re.compile(PUZZLE_ID)
PUZZLE_HEADING_RE = re.compile(r"^(%s)(?:\s|:|$)" % PUZZLE_ID)
PUZZLE_CLUSTER_RE = re.compile(r"%s(?:[\s,;|/&]*(?:and\s+)?%s)*" % (PUZZLE_ID, PUZZLE_ID))
CLOSED_RE = re.compile(r"^\s*closed:\s*\d{4}-\d{2}-\d{2}", re.M | re.I)
DISPOSITION_RE = re.compile(r"^[\s|:\-–—*)(\]]*(?:followed|parked)\s*:", re.I)
WAVE_RE = re.compile(r"wave-(\d+)\.md$")

# Verdict -> family. SUPPORTED/SOUND keep the label, SOUND WITH GAP keeps it marked gap,
# OVERSTATED/LABEL TOO STRONG need a lower label, LABEL TOO WEAK allows a higher one,
# UNSUPPORTED/WRONG withdraw the claim, ESCALATE leaves the claim with the PI.
VERDICTS = {
    "SUPPORTED": "accept",
    "SOUND": "accept",
    "SOUND WITH GAP": "gap",
    "OVERSTATED": "lower",
    "LABEL TOO STRONG": "lower",
    "LABEL TOO WEAK": "higher",
    "UNSUPPORTED": "withdraw",
    "WRONG": "withdraw",
    "ESCALATE": "escalate",
}
LABELS = ["THEOREM", "CHECKED", "MEASURED", "ESTIMATE", "CONJECTURE", "CITED"]
# What each kind of verifier may say; the kind is recognised by its name (`reproducer-w03-2`).
ROLE_VERDICTS = {
    "reproducer": ["SUPPORTED", "OVERSTATED", "UNSUPPORTED", "ESCALATE"],
    "proof-adversary": ["SOUND", "SOUND WITH GAP", "WRONG", "LABEL TOO STRONG", "LABEL TOO WEAK", "ESCALATE"],
}

# The state shown is decided by the weakest standing verdict; any escalation comes first because
# it needs a person whatever the other verifiers said.
WEAKNESS = ["escalate", "withdraw", "lower", "gap", "accept", "higher"]
# Two standing verdicts disagree when one stands behind the claim (accept, gap, higher) and
# another rejects it (lower, withdraw).
STANCE = {"accept": "stands", "gap": "stands", "higher": "stands", "lower": "rejects", "withdraw": "rejects"}


def project_root():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def natural(path):
    """Sort key putting w01-c2 before w01-c10."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path)]


COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def strip_comments(text):
    """Remove HTML comments (`<!-- ... -->`, also across lines), keeping the line count."""
    return COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def read(path):
    """The file's text; markdown files come back without their HTML comments, which are not content."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    return strip_comments(text) if path.endswith(".md") else text


# ---------------------------------------------------------------- waves and puzzles

def wave_notes(root):
    """[(number, path, text, closed)] for each `__statera__/wave-NN.md`, in order."""
    notes = []
    for path in glob.glob(os.path.join(root, "__statera__", "wave-*.md")):
        match = WAVE_RE.search(path)
        if match:
            text = read(path)
            notes.append((int(match.group(1)), path, text, bool(CLOSED_RE.search(text))))
    return sorted(notes)


def current_wave(root):
    """(number, path, text) of the highest wave note without a `closed:` date, else the latest; or None."""
    notes = wave_notes(root)
    if not notes:
        return None
    open_notes = [n for n in notes if not n[3]]
    number, path, text, _ = (open_notes or notes)[-1]
    return number, path, text


def disposed_puzzles(root):
    """Ids a closed wave note disposes of: the id's cell or line continues with `followed:` or `parked:`."""
    disposed = set()
    for _, _, text, closed in wave_notes(root):
        if not closed:
            continue
        lines = text.splitlines()
        start = next((i for i, l in enumerate(lines) if re.match(r"#{1,6}\s.*disposition", l, re.I)), None)
        if start is not None:
            section = []
            for line in lines[start + 1:]:
                if re.match(r"#{1,6}\s", line):
                    break
                section.append(line)
            lines = section
        for line in lines:
            for cluster in PUZZLE_CLUSTER_RE.finditer(line):
                if DISPOSITION_RE.match(line[cluster.end():]):
                    disposed.update(PUZZLE_RE.findall(cluster.group(0)))
    return disposed


def scan_puzzles(root):
    """Read `__scrupuli__/*.md`. Returns (puzzles, warnings).

    Each puzzle is {id, file, text}, one per `## S-wNN-<name>-<n>` heading; puzzles are identified
    by (file, id) and none is dropped. Warnings name duplicate ids and level-2 headings that are
    not puzzle ids.
    """
    puzzles, warnings = [], []
    seen = {}  # id -> first file
    pairs = set()
    for path in sorted(glob.glob(os.path.join(root, "__scrupuli__", "*.md")), key=natural):
        rel = os.path.relpath(path, root)
        current = None
        text = read(path)
        before = len(puzzles)
        for line in text.splitlines():
            other = re.match(r"^(#(?!#)|#{3,6})\s+(.*?)\s*$", line)
            if other and PUZZLE_RE.search(other.group(2)):
                warnings.append("%s: '%s' is a level-%d heading, so the puzzle under it is not tracked; "
                                "a puzzle starts with a level-2 heading `## S-wNN-<agent name>-<n>`"
                                % (rel, line.strip(), len(other.group(1))))
            level2 = re.match(r"^##(?!#)\s+(.*?)\s*$", line)
            if level2:
                heading = re.sub(r"[*`]", "", level2.group(1)).strip()
                match = PUZZLE_HEADING_RE.match(heading)
                if not match and heading.lower() == "symbols":
                    current = None  # new notation proposed to the PI; not a puzzle
                    continue
                if not match:
                    current = None
                    warnings.append("%s: heading '## %s' is not a puzzle id (form S-wNN-<agent name>-<n>, "
                                    "characters a-z 0-9 -); the puzzle under it is not tracked" % (rel, heading))
                    continue
                pid = match.group(1)
                if (rel, pid) in pairs:
                    warnings.append("%s: duplicate puzzle id %s in the same file" % (rel, pid))
                elif pid in seen:
                    warnings.append("%s: puzzle id %s is also raised in %s" % (rel, pid, seen[pid]))
                pairs.add((rel, pid))
                seen.setdefault(pid, rel)
                current = {"id": pid, "file": rel, "lines": []}
                puzzles.append(current)
            elif current is not None:
                current["lines"].append(line)
        if text.strip() and len(puzzles) == before and not any(w.startswith(rel + ":") for w in warnings):
            warnings.append("%s: has text but no `## S-wNN-<agent name>-<n>` heading, so no puzzle in it is "
                            "tracked" % rel)
    for p in puzzles:
        body = [l.strip() for l in p.pop("lines") if l.strip() and not l.strip().lower().startswith("refs:")]
        p["text"] = " ".join(body)
    return puzzles, warnings


def raised_puzzles(root):
    return scan_puzzles(root)[0]


def open_puzzles(root):
    """Puzzles raised in `__scrupuli__/` that no closed wave note has disposed of."""
    disposed = disposed_puzzles(root)
    return [p for p in raised_puzzles(root) if p["id"] not in disposed]


def puzzle_warnings(root):
    """Problems with puzzle ids, plus dispositions naming a puzzle no file raises."""
    puzzles, warnings = scan_puzzles(root)
    raised = {p["id"] for p in puzzles}
    for pid in sorted(disposed_puzzles(root) - raised):
        warnings.append("a closed wave note disposes of %s, which no file in __scrupuli__/ raises" % pid)
    return warnings


def report_puzzles(root):
    puzzles = open_puzzles(root)
    warnings = puzzle_warnings(root)
    out = ["## Open puzzles (%d)" % len(puzzles)]
    if not puzzles:
        if warnings:
            out.append("none among the puzzles that could be read: see the warnings below")
        elif raised_puzzles(root):
            out.append("none: every raised puzzle has a disposition in a closed wave note")
        else:
            out.append("none raised: `__scrupuli__/` holds no puzzles")
    for p in puzzles:
        text = p["text"] if len(p["text"]) <= 160 else p["text"][:157] + "..."
        out.append("- %s (%s) %s" % (p["id"], p["file"], text))
    out += ["! " + w for w in warnings]
    return out


# ---------------------------------------------------------------- claims

def field_re(name):
    """A `name: value` line, tolerating a list bullet, bold around the name or colon, and case."""
    return re.compile(r"^\s*(?:[-*>]\s+)?(?:\*\*|__)?%s\s*(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(.*)$" % name, re.I)


LABEL_RE, SUPERSEDES_RE, VERDICT_RE = field_re("label"), field_re("supersedes"), field_re("verdict")
CHANGED_BY_RE = field_re("changed_by")
VERDICT_HEADING_RE = re.compile(r"^##(?!#)\s+(?:\*\*|__)?verdict\s*(?:\*\*|__)?\s*:\s*(.*?)\s*$", re.I)
TITLE_RE = re.compile(r"^#(?!#)\s+(\S+?)\s*:\s*(.*?)\s*$")


def clean_value(value):
    return value.strip().strip("*_`").strip().rstrip(".;,").strip()


def parse_claim(text):
    """Split a claim file into {id, statement, label, supersedes, sections}.

    The head is everything before the first level-2 heading. A verifier section starts at a
    `## verdict: <name>` heading and runs to the next one: sections is [(name, [lines])].
    """
    out = {"id": "", "statement": "", "label": "", "supersedes": "", "sections": []}
    in_head, section = True, None
    for line in text.splitlines():
        heading = VERDICT_HEADING_RE.match(line)
        if heading:
            in_head = False
            section = (re.sub(r"[*_`]", "", heading.group(1)).strip() or "verifier", [])
            out["sections"].append(section)
        elif re.match(r"^##(?!#)\s", line):
            in_head = False
            if section is not None:
                section[1].append(line)
        elif section is not None:
            section[1].append(line)
        elif in_head:
            title = TITLE_RE.match(line)
            if title and not out["id"]:
                out["id"], out["statement"] = title.group(1), title.group(2)
                continue
            for key, rx in (("label", LABEL_RE), ("supersedes", SUPERSEDES_RE)):
                match = rx.match(line)
                if match and not out[key]:
                    out[key] = clean_value(match.group(1))
    return out


def normalise_verdict(raw):
    """Match `raw` exactly against the verdict vocabulary: (verdict, extra).

    Case, bold, backticks, a trailing period and runs of spaces are ignored. `verdict` is the
    vocabulary entry when the text is exactly that phrase, else None. `extra` is the text found
    after a vocabulary phrase (longest phrase first), or None: "SOUND with a gap" gives
    (None, "with a gap"), because it is not the verdict SOUND.
    """
    upper = re.sub(r"[\s_]+", " ", clean_value(raw).upper())
    if upper in VERDICTS:
        return upper, None
    for name in sorted(VERDICTS, key=len, reverse=True):
        if upper.startswith(name) and not upper[len(name):len(name) + 1].isalnum():
            return None, clean_value(raw)[len(name):].strip(" :-\u2013\u2014,;(") or clean_value(raw)
    return None, None


def claim_state(label, standing):
    """The state shown for a claim at `label` with these standing verdicts ({verifier: verdict})."""
    if not standing:
        if label.split()[0].upper() == "CITED":
            return "cited (not verified)"
        return "unverified %s" % label
    families = [VERDICTS[v] for v in standing.values()]
    if "escalate" in families:
        return "escalated: PI decides"  # whatever the other verifiers said
    if len({STANCE[f] for f in families if f in STANCE}) > 1:
        return "disputed: PI decides"
    weakest = next(f for f in WEAKNESS if f in families)
    return {
        "escalate": "escalated: PI decides",
        "withdraw": "withdrawn",
        "lower": "below %s: restate" % label,
        "gap": "%s (gap)" % label,
        "accept": label,
        "higher": "%s (may restate higher)" % label,
    }[weakest]


def current_label(text):
    """The state of one claim, from the text of its `__pondus__/<id>.md` file (not counting supersession).

    Returns a dict: id, label (the author's), supersedes, current (one of: `unverified <LABEL>`,
    `<LABEL>`, `<LABEL> (gap)`, `below <LABEL>: restate`, `<LABEL> (may restate higher)`,
    `withdrawn`, `escalated: PI decides`, `disputed: PI decides`), verdicts ({verifier: verdict},
    each verifier's latest recognised one) and warnings (a list of strings).
    """
    claim = parse_claim(text)
    label = claim["label"]
    warnings = []
    if not label:
        warnings.append("no `label:` line in the claim head")
        label = "(no label)"
    elif label.split()[0].upper().strip("*`") not in LABELS:
        warnings.append("label '%s' is not one of %s" % (label, ", ".join(LABELS)))
    standing = {}
    for name, lines in claim["sections"]:
        hits = [(i, m.group(1)) for i, m in enumerate(map(VERDICT_RE.match, lines)) if m]
        if not hits:
            warnings.append("verdict section '%s' has no `verdict:` line" % name)
            continue
        value = hits[-1][1]  # a verifier that revises in place has the last `verdict:` line stand
        if len(hits) > 1 and not any(CHANGED_BY_RE.match(l) for l in lines[hits[-2][0] + 1:]):
            warnings.append("verdict section '%s' has %d `verdict:` lines and no `changed_by:` line below the earlier one; "
                            "the last counts" % (name, len(hits)))
        verdict, extra = normalise_verdict(value)
        if verdict is None and extra is not None:
            warnings.append("verdict section '%s': '%s' has text after the verdict phrase, so it is not counted; "
                            "write only the verdict on the `verdict:` line and the explanation on `reason:`"
                            % (name, clean_value(value)))
            continue
        if verdict is None:
            warnings.append("verdict section '%s': '%s' is not a recognised verdict" % (name, clean_value(value)))
            continue
        for role, allowed in ROLE_VERDICTS.items():
            if role in name.lower() and verdict not in allowed:
                warnings.append("verdict section '%s': %s is not in the %s's vocabulary (%s); counted anyway"
                                % (name, verdict, role, ", ".join(allowed)))
        standing[name] = verdict  # a later section by the same verifier replaces an earlier one
    return {"id": claim["id"], "statement": claim["statement"], "label": label,
            "supersedes": claim["supersedes"], "verdicts": standing, "warnings": warnings,
            "current": claim_state(label, standing)}


def read_claims(root):
    claims = []
    for path in sorted(glob.glob(os.path.join(root, "__pondus__", "*.md")), key=natural):
        info = current_label(read(path))
        info["file"] = os.path.relpath(path, root)
        info["id"] = info["id"] or os.path.splitext(os.path.basename(path))[0]
        claims.append(info)
    by_id = {c["id"]: c for c in claims}
    for c in claims:
        c["superseded_by"] = sorted(o["id"] for o in claims if o["supersedes"] == c["id"])
        if c["superseded_by"]:
            c["current"] = "superseded by %s" % ", ".join(c["superseded_by"])
        if c["supersedes"] and c["supersedes"] not in by_id:
            c["warnings"].append("supersedes %s, which is not a claim file" % c["supersedes"])
    return claims


def report_claims(root):
    claims = read_claims(root)
    disputed = [c for c in claims if c["current"].startswith("disputed")]
    warned = sum(len(c["warnings"]) for c in claims)
    out = ["## Claims (%d, %d disputed, %d warnings)" % (len(claims), len(disputed), warned)]
    if not claims:
        out.append("none: `__pondus__/` holds no claim files")
    for c in claims:
        line = "- %s  %s" % (c["id"], c["current"])
        if c["verdicts"] and not c["superseded_by"]:
            line += "  <- " + "; ".join("%s: %s" % kv for kv in sorted(c["verdicts"].items()))
        out.append(line)
        out += ["    ! " + w for w in c["warnings"]]
    return out


# ---------------------------------------------------------------- spend

# USD per million tokens: input, output, cache read, cache write for 5 minutes, cache write for 1 hour.
# [source: https://platform.claude.com/docs/en/about-claude/pricing, "Model pricing" table, fetched 2026-10-19]
# These rows reproduce the costUSD that Claude Code writes in its own `cost-state` record.
PRICES = {
    "claude-opus-5-5": (4.0, 20.0, 0.20, 5.0, 8.0),
    "claude-sonnet-5-5": (2.0, 10.0, 0.10, 2.5, 4.0),
    "claude-fable-5-1": (10.0, 50.0, 0.25, 12.5, 20.0),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125, 0.20),  # up to 100,000 prompt tokens
}
LONG_HAIKU = (0.50, 2.50, 0.05, 0.625, 1.0)  # Haiku 5.5 above 100,000 prompt tokens
WEB_SEARCH_USD = 0.01  # $10 per 1,000 searches
FAST_FACTOR = 2.0  # fast mode (`usage.speed == "fast"`) is billed at twice the price
USAGE_FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def encode(path):
    """The name Claude Code gives a project's transcript folder: the path with every non-alphanumeric a dash."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def git_worktrees(root):
    """Paths of the git worktrees of root's repository, the main checkout first (needs git; else empty)."""
    try:
        out = subprocess.run(["git", "-C", root, "worktree", "list", "--porcelain"], capture_output=True,
                             text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return [line[9:] for line in out.splitlines() if line.startswith("worktree ")]


def lab_roots(root, trees=None):
    """The lab's directory, its real path, and every git worktree of its repository (and their real paths); `trees` is `git_worktrees(root)` when the caller has it."""
    roots = [os.path.abspath(root), os.path.realpath(root)]
    for path in git_worktrees(root) if trees is None else trees:
        roots += [path, os.path.realpath(path)]
    return list(dict.fromkeys(roots))


def first_cwd(path, limit=300):
    """The `cwd` of the first record of a transcript that has one."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for _, line in zip(range(limit), fh):
                if '"cwd"' in line:
                    try:
                        cwd = json.loads(line).get("cwd")
                    except ValueError:
                        continue
                    if cwd:
                        return cwd
    except OSError:
        pass
    return None


def under(cwd, roots):
    return bool(cwd) and any(cwd == r or cwd.startswith(r.rstrip("/") + "/") for r in roots)


def find_sessions(roots):
    """Main transcripts of every session whose `cwd` is a root or below it. A project folder is opened only
    when its name starts with a root's encoded name (a cwd below a root gives such a name; names over about
    200 characters are cut, hence the first 100)."""
    base = os.path.join(config_dir(), "projects")
    prefixes = tuple(encode(r)[:100] for r in roots)
    files = []
    try:
        entries = sorted(os.listdir(base))
    except OSError:
        return files
    for entry in entries:
        folder = os.path.join(base, entry)
        if entry.startswith(prefixes) and os.path.isdir(folder):
            files += [f for f in sorted(glob.glob(os.path.join(folder, "*.jsonl"))) if under(first_cwd(f), roots)]
    return files


def message_usd(model, use):
    """USD of one API message from its usage block, at list price; None for a model with no price here."""
    p = PRICES.get(re.sub(r"-\d{8}$", "", model or ""))
    if p is None:
        return None
    cc = use.get("cache_creation") if isinstance(use.get("cache_creation"), dict) else {}
    cw1, cw5 = int(cc.get("ephemeral_1h_input_tokens") or 0), int(cc.get("ephemeral_5m_input_tokens") or 0)
    cw = int(use.get("cache_creation_input_tokens") or 0)
    cw5 += max(0, cw - cw1 - cw5)  # a write with no recorded split is charged at the 5 minute rate
    i, o, cr = (int(use.get(f) or 0) for f in ("input_tokens", "output_tokens", "cache_read_input_tokens"))
    if model.startswith("claude-haiku-5-5") and i + cr + cw > 100000:
        p = LONG_HAIKU
    usd = (i * p[0] + o * p[1] + cr * p[2] + cw5 * p[3] + cw1 * p[4]) / 1e6
    if use.get("speed") == "fast":
        usd *= FAST_FACTOR
    searches = use.get("server_tool_use") if isinstance(use.get("server_tool_use"), dict) else {}
    return usd + WEB_SEARCH_USD * int(searches.get("web_search_requests") or 0)


def merge_usage(into, use):
    """A message id is one API call; its records (one per content block) repeat the usage while
    `output_tokens` grows during the stream, so each field keeps its maximum."""
    for f in USAGE_FIELDS:
        into[f] = max(int(into.get(f) or 0), int(use.get(f) or 0))
    if isinstance(use.get("cache_creation"), dict):
        into["cache_creation"] = use["cache_creation"]


def parse_transcript(path, warnings):
    """One transcript file: ({message id: message}, last `cost-state` record, `agent-setting` name).

    A message is {model, usage, ts, sid, final}. `sid` is the `sessionId` of its record: a forked session
    or a copied agent file holds copies that still name the session that made the call. `final` is whether
    the message's last record in this file has a `stop_reason`: when it has none, the file holds the
    output tokens as they were when the stream started, so the count is a lower bound."""
    msgs, cost_state, setting = {}, None, None
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"assistant"' not in line and '"cost-state"' not in line and '"agent-setting"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(rec, dict):
                    continue
                kind, m = rec.get("type"), rec.get("message")
                if kind == "cost-state" and rec.get("totalCostUSD") is not None:
                    cost_state = rec
                elif kind == "agent-setting" and rec.get("agentSetting") and not setting:
                    setting = rec["agentSetting"]
                elif kind == "assistant" and isinstance(m, dict) and isinstance(m.get("usage"), dict) \
                        and m.get("model") != "<synthetic>":
                    key = m.get("id") or rec.get("requestId") or rec.get("uuid") or len(msgs)
                    msg = msgs.setdefault(key, {"model": m.get("model") or "unknown", "usage": {}, "ts": rec.get("timestamp"),
                                                "sid": rec.get("sessionId")})
                    merge_usage(msg["usage"], m["usage"])
                    msg["final"] = bool(m.get("stop_reason"))
    except OSError as err:
        warnings.append("could not read %s: %s" % (path, err.strerror or err))
    return msgs, cost_state, setting


CACHE_VERSION = 1   # change it when parse_transcript returns something else: an older cache file is then ignored
_cache = []   # [Cache] while report_spend runs


class Cache:
    """What parse_transcript found in each transcript, kept in a JSON file and used while the file's size and modification time are the same (w05-c5). The file is replaced
    atomically; one that cannot be read, or is of another version, is ignored; only the transcripts of this run are kept. Message ids are stored as pairs so that an id that
    is a number stays one."""

    def __init__(self, path):
        self.path, self.files, self.seen, self.dirty = path, {}, {}, False
        try:
            with open(path) as fh:
                data = json.load(fh)
            if data.get("v") == CACHE_VERSION and isinstance(data.get("files"), dict):
                self.files = data["files"]
        except (OSError, ValueError, AttributeError):
            pass

    def read(self, path, warnings):
        try:
            st = os.stat(path)
        except OSError:
            return parse_transcript(path, warnings)
        stamp = [st.st_size, st.st_mtime_ns]
        hit = self.files.get(path)
        if isinstance(hit, list) and len(hit) == 5 and hit[:2] == stamp and os.access(path, os.R_OK):   # a file that has become unreadable is parsed, and warned about, as before
            self.seen[path] = hit
            return dict((k, m) for k, m in hit[2]), hit[3], hit[4]
        before = len(warnings)
        msgs, cost_state, setting = parse_transcript(path, warnings)
        if len(warnings) == before:
            self.seen[path] = self.files[path] = stamp + [list(msgs.items()), cost_state, setting]
            self.dirty = True
        return msgs, cost_state, setting

    def save(self):
        if not (self.dirty or len(self.seen) != len(self.files)):
            return
        tmp = "%s.%d.tmp" % (self.path, os.getpid())
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            gitignore = os.path.join(os.path.dirname(self.path), ".gitignore")
            if os.path.basename(os.path.dirname(self.path)) == ".harness" and not os.path.exists(gitignore):   # the lab's own state folder; a folder named by $LAB_STATUS_CACHE is left as it is
                with open(gitignore, "w") as fh:
                    fh.write("*\n")
            with open(tmp, "w") as fh:
                json.dump({"v": CACHE_VERSION, "files": self.seen}, fh)
            os.replace(tmp, self.path)
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def cache_path(root):
    """`$LAB_STATUS_CACHE`, else the lab's `__statera__/.harness/lab_status_cache.json` (git-ignored); None for a folder that is no lab (`--spend` needs none), `-` or `off` in the variable: no cache."""
    given = os.environ.get("LAB_STATUS_CACHE")
    if given:
        return None if given in ("-", "off") else given
    return os.path.join(root, "__statera__", ".harness", "lab_status_cache.json") if os.path.isdir(os.path.join(root, "__statera__")) else None


def read_transcript(path, warnings):
    """parse_transcript through the cache, while report_spend has one open."""
    return _cache[0].read(path, warnings) if _cache else parse_transcript(path, warnings)


def agent_label(path):
    """A subagent's name from its `.meta.json` (`name`, else `agentType`), else 'subagent <id>'."""
    fallback = "subagent " + os.path.basename(path)[len("agent-"):-len(".jsonl")][:6]
    try:
        with open(path[:-len(".jsonl")] + ".meta.json", encoding="utf-8") as fh:
            meta = json.load(fh)
        return str(meta.get("name") or meta.get("agentType") or fallback)
    except (OSError, ValueError, AttributeError):
        return fallback


def load_sessions(mains, warnings):
    """Read the sessions and count each API message once, under the session named in its own record.

    Returns (sessions, copies): a session is {path, cost_state, agent_files, start, rows}; rows maps
    (agent, model) to a Counter of msgs, output, usd, unpriced and lower (messages of a subagent whose
    last record has no `stop_reason`). A message copied into a session from another session that is
    not among `mains` is counted nowhere: that session did not pay for it."""
    owned, sessions, copies = {}, {}, 0
    for path in mains:
        sid = os.path.basename(path)[:-len(".jsonl")]
        msgs, cost_state, setting = read_transcript(path, warnings)
        sources = [(setting + " (main thread)" if setting else "main thread", False, msgs)]
        subs = sorted(glob.glob(os.path.join(path[:-len(".jsonl")], "subagents", "**", "agent-*.jsonl"), recursive=True))
        sources += [(agent_label(f), True, read_transcript(f, warnings)[0]) for f in subs]
        sessions[sid] = {"path": path, "cost_state": cost_state, "agent_files": len(subs), "start": None, "rows": {}}
        for label, is_sub, found in sources:
            for key, msg in found.items():
                have = owned.get(key)
                if have is None:
                    owned[key] = dict(msg, label=label, sub=is_sub, own=(msg["sid"] == sid))
                    continue
                copies += 1
                merge_usage(have["usage"], msg["usage"])
                have["final"] = have["final"] or msg["final"]
                if msg["sid"] == sid and not have["own"]:  # the copy in the owner's own file names the agent
                    have.update(label=label, sub=is_sub, own=True)
    for msg in owned.values():
        s = sessions.get(msg["sid"])
        if s is None:
            continue
        row = s["rows"].setdefault((msg["label"], msg["model"]), collections.Counter())
        row["msgs"] += 1
        row["output"] += int(msg["usage"].get("output_tokens") or 0)
        usd = message_usd(msg["model"], msg["usage"])
        row["unpriced"] += usd is None
        row["usd"] += usd or 0.0
        row["lower"] += msg["sub"] and not msg["final"]
        if msg["ts"] and (s["start"] is None or msg["ts"] < s["start"]):
            s["start"] = msg["ts"]
    return sorted(sessions.values(), key=lambda s: s["start"] or "9"), copies


def table(rows):
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    lines = []
    for n, r in enumerate(rows):
        lines.append("  ".join(c.ljust(widths[i]) if i < 2 or not c[:1].isdigit() else c.rjust(widths[i])
                               for i, c in enumerate(r)).rstrip())
        if n == 0:
            lines.append("  ".join("-" * w for w in widths))
    return lines


def report_spend(root):
    """The spend section: USD per session group and per agent, exact where Claude Code recorded it."""
    trees = git_worktrees(root)   # one call: git is a slow start here
    roots = lab_roots(root, trees)
    warnings = []
    path = cache_path(root)
    _cache[:] = [Cache(path)] if path else []
    try:
        sessions, copies = load_sessions(find_sessions(roots), warnings)
        if _cache:
            _cache[0].save()
    finally:
        _cache[:] = []
    out = ["## Spend (USD: Claude Code's cost-state where a session has ended, else list price of 2026-10-19)"]
    if not trees:
        out.append("! git is not available, or this folder is not in a git repository: only sessions started in this "
                   "folder or below it were counted")
    if not sessions:
        out.append("no transcripts found for %s (looked for sessions whose cwd is the lab or one of its git worktrees, "
                   "under %s)" % (os.path.abspath(root), os.path.join(config_dir(), "projects")))
        return out
    here = os.path.realpath(root)
    main_checkout = os.path.realpath(trees[0]) if trees else None
    groups, exact, listed, unpriced = collections.OrderedDict(), 0.0, 0.0, 0
    for s in sessions:
        cwd = first_cwd(s["path"]) or ""
        base = next((r for r in sorted(roots, key=len, reverse=True) if under(cwd, [r])), None)
        label = "(cwd unknown)" if base is None else "this checkout" if os.path.realpath(base) == here else \
            "main checkout" if os.path.realpath(base) == main_checkout else "worktree " + os.path.basename(base.rstrip("/"))
        if base is not None and cwd != base:
            label += ", sessions started below it"
        usd = sum(r["usd"] for r in s["rows"].values())
        unpriced += sum(r["unpriced"] for r in s["rows"].values())
        ended = s["cost_state"] is not None
        if ended:
            usd = s["cost_state"]["totalCostUSD"]
            exact += usd
        else:
            listed += usd
        g = groups.setdefault(label, {"n": 0, "agents": 0, "usd": 0.0, "ended": 0, "open": 0})
        g["n"] += 1
        g["agents"] += s["agent_files"]
        g["usd"] += usd
        g["ended" if ended else "open"] += 1
    n_open = sum(g["open"] for g in groups.values())
    if n_open:
        out.append("TOTAL  USD %.2f at least   (%.2f exact + %.2f at list price for %d session%s still open)"
                   % (exact + listed, exact, listed, n_open, "" if n_open == 1 else "s"))
        out.append("A session still open has no cost-state yet. Its figure leaves out helper-model calls (such as web-fetch "
                   "summaries) and counts a subagent's output tokens as they were when its stream started, so it is a lower bound.")
    else:
        out.append("TOTAL  USD %.2f   (exact, all sessions ended)" % exact)
    out.append("")
    tab = [("where", "sessions", "agent files", "USD", "basis")]
    for label, g in groups.items():
        basis = "exact" if not g["open"] else "at least" if not g["ended"] else "%d exact, %d at least" % (g["ended"], g["open"])
        tab.append((label, str(g["n"]), str(g["agents"]), "%.2f" % g["usd"], basis))
    out += table(tab)
    out.append("")
    agents = collections.OrderedDict()
    for s in sessions:
        for (label, model), r in s["rows"].items():
            agents.setdefault((label, model), collections.Counter()).update(r)
    ranked = sorted(agents.items(), key=lambda kv: -kv[1]["usd"])
    tab = [("agent", "model", "msgs", "list-price USD", "output tokens")]
    for (label, model), a in ranked[:12]:
        mark = "+" if a["lower"] else ""
        tab.append((label, re.sub(r"^claude-", "", model), str(a["msgs"]), "%.2f%s" % (a["usd"], mark),
                    "{:,}{}".format(a["output"], mark)))
    if len(ranked) > 12:
        rest = [a for _, a in ranked[12:]]
        tab.append(("(%d more)" % len(rest), "", str(sum(a["msgs"] for a in rest)), "%.2f" % sum(a["usd"] for a in rest), ""))
    out += table(tab)
    out.append("`+` = at least: some of that agent's output tokens are stored at their start-of-stream value. Agent rows are priced "
               "from transcripts at list price and add up to %.2f of the %.2f total above; the rest is what only cost-state records."
               % (sum(a["usd"] for a in agents.values()), exact + listed))
    if copies:
        out.append("%d message record%s copied a message already counted (forked sessions, copied agent files); each is charged "
                   "once, to the session named in its record." % (copies, "" if copies == 1 else "s"))
    if unpriced:
        out.append("%d message%s of a model with no price here, left out of the list-price figures."
                   % (unpriced, " is" if unpriced == 1 else "s are"))
    out += ["! " + w for w in warnings]
    return out


# ---------------------------------------------------------------- report and selftest

def report(root):
    if not os.path.isdir(os.path.join(root, "__statera__")):
        return "No lab in %s: `__statera__/` is missing. Run `/lab <question>` to start one." % os.path.abspath(root)
    parts = [report_puzzles(root), report_claims(root), report_spend(root)]
    wave = current_wave(root)
    head = "# Lab status\n\nCurrent wave note: %s" % (os.path.relpath(wave[1], root) if wave else "none")
    return head + "\n\n" + "\n\n".join("\n".join(p) for p in parts)


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "my.project_x")
        cfg = os.path.join(tmp, "config")
        os.environ["CLAUDE_CONFIG_DIR"] = cfg
        os.environ.pop("CLAUDE_PROJECT_DIR", None)

        # Without a lab: say so.
        os.makedirs(root)
        assert "No lab" in report(root)

        # ---- Puzzles
        scrupuli = os.path.join(root, "__scrupuli__")
        _write(os.path.join(scrupuli, "wave-01-explorer-w01-a.md"),
               "## S-w01-explorer-w01-a-1\nthe 3-bit rows vanish\nrefs: data/a.csv:12\n\n"
               "## S-w01-explorer-w01-a-2\nfigure 2 has a kink\nrefs: figs/2.png\n\n"
               "## S-w01-explorer-w01-a-3\nrunning time drops at n=9\n\n"
               "## S-w01-explorer-w01-a-4\nfour\n\n"
               "## S-w01-explorer-w01-a-5\nfive\n")
        # A second explorer of the same wave has its own file and ids: both are listed.
        _write(os.path.join(scrupuli, "wave-01-explorer-w01-b.md"),
               "## S-w01-explorer-w01-b-1\nthe other explorer's puzzle\n\n"
               "## S-w01-explorer-w01-b-1\nsame id again, same file\n\n"
               "## Puzzle 1\nnot an id\n\n## S-w01-Explorer-1\nbad case\n\n## S-w01-author.v2-1\nbad character\n\n"
               "## S-w01-explorer-w01-a-3\nan id another file already raised\n")
        _write(os.path.join(scrupuli, "wave-02-author-w02-1.md"),
               "## S-w02-author-w02-1-1\nfactor of two between the tables\nrefs: t.md\n\n"
               "### S-w02-author-w02-1-2\na level-3 heading is body text, not a puzzle\n")
        _write(os.path.join(root, "__statera__", "wave-01.md"),
               "# Wave 01\n\nopened: 2026-01-02\n\n## Notes\n\nWe looked at S-w01-explorer-w01-a-3 again, not followed up.\n\n"
               "## Puzzle dispositions (at close)\n\n| Puzzle | Disposition |\n|:--|:--|\n"
               "| S-w01-explorer-w01-a-1 | followed: w02-c1 |\n"
               "| S-w01-explorer-w01-a-2 | parked: cosmetic |\n"
               "| S-w01-explorer-w01-a-3 | not followed |\n"
               "| S-w01-explorer-w01-a-4, S-w01-explorer-w01-a-5 | parked: duplicates of S-w01-explorer-w01-b-1 |\n"
               "| S-w09-nobody-1 | parked: typo |\n"
               "| S-wNN-<agent>-<n> | followed: <brief or claim id> |\n\nclosed: 2026-01-09\n")
        _write(os.path.join(root, "__statera__", "wave-02.md"),
               "# Wave 02\n\nopened: 2026-01-10\n\n## Puzzle dispositions (at close)\n\n"
               "| S-w02-author-w02-1-1 | followed: w03-c1 |\n")  # open note: does not count
        found = [(p["file"].split("/")[-1], p["id"]) for p in open_puzzles(root)]
        assert found == [
            ("wave-01-explorer-w01-a.md", "S-w01-explorer-w01-a-3"),
            ("wave-01-explorer-w01-b.md", "S-w01-explorer-w01-b-1"),
            ("wave-01-explorer-w01-b.md", "S-w01-explorer-w01-b-1"),
            ("wave-01-explorer-w01-b.md", "S-w01-explorer-w01-a-3"),
            ("wave-02-author-w02-1.md", "S-w02-author-w02-1-1"),
        ], found
        warnings = puzzle_warnings(root)
        joined = "\n".join(warnings)
        assert "duplicate puzzle id S-w01-explorer-w01-b-1 in the same file" in joined, joined
        assert "S-w01-explorer-w01-a-3 is also raised in __scrupuli__/wave-01-explorer-w01-a.md" in joined, joined
        for bad in ("## Puzzle 1", "## S-w01-Explorer-1", "## S-w01-author.v2-1"):
            assert "heading '%s' is not a puzzle id" % bad in joined, (bad, joined)
        assert "disposes of S-w09-nobody-1, which no file" in joined, joined
        assert "wave-02-author-w02-1.md: '### S-w02-author-w02-1-2' is a level-3 heading" in joined, joined
        assert len(warnings) == 7, warnings
        assert current_wave(root)[0] == 2
        _write(os.path.join(root, "__statera__", "wave-02.md"),
               "# Wave 02\n\nopened: 2026-01-10\n\n## Puzzle dispositions (at close)\n\n"
               "| S-w02-author-w02-1-1 | followed: w03-c1 |\n\nclosed: 2026-01-20\n")
        assert ("wave-02-author-w02-1.md", "S-w02-author-w02-1-1") not in \
            [(p["file"].split("/")[-1], p["id"]) for p in open_puzzles(root)]
        assert current_wave(root)[0] == 2  # all closed: the latest
        text = report(root)
        assert "## Open puzzles (4)" in text and "! " in text and "other explorer's puzzle" in text, text

        # HTML comments are not content: example rows in a comment dispose of nothing, and ids,
        # headings and closing dates inside one do not count.
        _write(os.path.join(scrupuli, "wave-03-explorer-w03-b.md"),
               "<!-- ## S-w03-explorer-w03-z-1\nnot a puzzle -->\n## S-w03-explorer-w03-b-1\nreal one\n")
        _write(os.path.join(scrupuli, "wave-03-only-a-comment.md"), "<!-- nothing here yet -->\n")
        _write(os.path.join(root, "__statera__", "wave-03.md"),
               "# Wave 03\n\nopened: 2026-02-01\n\n## Puzzle dispositions (at close)\n\n"
               "<!-- One row per puzzle, for example:\n| S-w03-explorer-w03-b-1 | followed: w04-c1 |\n"
               "closed: 2026-02-02\n-->\n\n| Puzzle | Disposition |\n|:--|:--|\n\nclosed: YYYY-MM-DD\n")
        ids = [p["id"] for p in open_puzzles(root)]
        assert "S-w03-explorer-w03-b-1" in ids and "S-w03-explorer-w03-z-1" not in ids, ids
        assert current_wave(root)[0] == 3, "a closing date inside a comment must not close the note"
        assert not any("wave-03" in w for w in puzzle_warnings(root)), puzzle_warnings(root)
        os.remove(os.path.join(root, "__statera__", "wave-03.md"))
        os.remove(os.path.join(scrupuli, "wave-03-explorer-w03-b.md"))
        os.remove(os.path.join(scrupuli, "wave-03-only-a-comment.md"))
        assert current_wave(root)[0] == 2

        # A puzzle file with no puzzle heading warns, and the report never claims "none" then.
        lonely = os.path.join(tmp, "lonely")
        os.makedirs(os.path.join(lonely, "__statera__"))
        assert "none raised" in report_puzzles(lonely)[1]
        _write(os.path.join(lonely, "__scrupuli__", "wave-01-explorer-w01-a.md"),
               "1. the rows vanish\n2. figure two has a kink\n\n### S-w01-explorer-w01-a-1\nnot level two\n"
               "# S-w01-explorer-w01-a-2\nnor level one\n")
        lines = report_puzzles(lonely)
        joined = "\n".join(lines)
        assert "none:" not in joined and "none among the puzzles that could be read" in joined, joined
        assert "'### S-w01-explorer-w01-a-1' is a level-3 heading" in joined, joined
        assert "'# S-w01-explorer-w01-a-2' is a level-1 heading" in joined, joined
        _write(os.path.join(lonely, "__scrupuli__", "wave-02-explorer-w02-a.md"), "just prose, no headings\n")
        assert "wave-02-explorer-w02-a.md: has text but no `## S-wNN" in "\n".join(report_puzzles(lonely))
        # A fully disposed lab with no warnings says so.
        _write(os.path.join(lonely, "__scrupuli__", "wave-01-explorer-w01-a.md"), "## S-w01-explorer-w01-a-1\nx\n")
        os.remove(os.path.join(lonely, "__scrupuli__", "wave-02-explorer-w02-a.md"))
        _write(os.path.join(lonely, "__statera__", "wave-01.md"),
               "## Puzzle dispositions\n| S-w01-explorer-w01-a-1 | parked: r |\n\nclosed: 2026-01-01\n")
        assert "none: every raised puzzle has a disposition" in report_puzzles(lonely)[1]

        # ---- Claims
        def claim(cid, label, *verdicts, extra="", head=""):
            body = "# %s: some statement\n\nlabel: %s\nscope: s\nevidence: e\nmethod: m\nauthor: a\n%s\n" % (
                cid, label, head)
            for who, verdict in verdicts:
                body += ("\n## verdict: %s\n\n### independent result\nfound this first\n\n### exchange\n"
                         "- Q: why? - A: because\n\n%s: %s\nreason: because\n" % (
                             who, "verdict", verdict))
            return body + extra

        cases = [
            ("unverified", claim("w01-c1", "MEASURED"), "unverified MEASURED"),
            ("cited", claim("w01-c40", "CITED"), "cited (not verified)"),
            ("supported", claim("w01-c2", "MEASURED", ("reproducer-w01-1", "SUPPORTED")), "MEASURED"),
            ("sound", claim("w01-c3", "THEOREM", ("proof-adversary-w01-1", "SOUND")), "THEOREM"),
            ("gap", claim("w01-c4", "THEOREM", ("v", "SOUND WITH GAP")), "THEOREM (gap)"),
            ("overstated", claim("w01-c5", "MEASURED", ("v", "OVERSTATED")), "below MEASURED: restate"),
            ("too strong", claim("w01-c6", "THEOREM", ("v", "LABEL TOO STRONG")), "below THEOREM: restate"),
            ("too weak", claim("w01-c7", "CONJECTURE", ("v", "LABEL TOO WEAK")), "CONJECTURE (may restate higher)"),
            ("unsupported", claim("w01-c8", "MEASURED", ("v", "UNSUPPORTED")), "withdrawn"),
            ("wrong", claim("w01-c9", "THEOREM", ("v", "WRONG")), "withdrawn"),
            ("escalate", claim("w01-c10", "MEASURED", ("v", "ESCALATE")), "escalated: PI decides"),
            ("latest of one verifier", claim("w01-c11", "MEASURED", ("v", "UNSUPPORTED"), ("v", "SUPPORTED")),
             "MEASURED"),
            ("weakest of two", claim("w01-c12", "THEOREM", ("v1", "SOUND"), ("v2", "SOUND WITH GAP")),
             "THEOREM (gap)"),
            ("dispute 1", claim("w01-c13", "MEASURED", ("v1", "SUPPORTED"), ("v2", "UNSUPPORTED")),
             "disputed: PI decides"),
            ("dispute 2", claim("w01-c14", "MEASURED", ("v1", "SUPPORTED"), ("v2", "OVERSTATED")),
             "disputed: PI decides"),
            ("too weak is not a dispute", claim("w01-c15", "THEOREM", ("v1", "SOUND"), ("v2", "LABEL TOO WEAK")),
             "THEOREM"),
            ("escalate beats reject", claim("w01-c16", "MEASURED", ("v1", "ESCALATE"), ("v2", "OVERSTATED")),
             "escalated: PI decides"),
            ("escalate beats a dispute", claim("w01-c17", "MEASURED", ("v1", "ESCALATE"), ("v2", "SUPPORTED"),
                                               ("v3", "OVERSTATED")), "escalated: PI decides"),
        ]
        for name, text, state in cases:
            got = current_label(text)
            assert got["current"] == state and got["warnings"] == [], (name, got)
        # Tolerated spellings and layouts of the verdict line.
        for line in ("**verdict:** SUPPORTED", "**verdict**: **SUPPORTED**", "Verdict: supported.", "VERDICT:SUPPORTED",
                     "verdict:  `Supported`", "> verdict: SUPPORTED"):
            text = ("# w01-c20: s\n\nlabel: MEASURED\n\n## verdict: verifier-w01-1\n\n### independent result\nx\n\n"
                    "%s\nreason: r\n" % line)
            got = current_label(text)
            assert got["current"] == "MEASURED" and not got["warnings"], (line, got)
        # Extra text after a verdict phrase is a warning and the verdict is not read: "SOUND with a gap"
        # is not SOUND, and a longer phrase beats its shorter prefix.
        for value in ("SOUND with a gap in step 3", "SOUND - LABEL TOO WEAK", "SUPPORTED but OVERSTATED",
                      "OVERSTATED (true but stronger than the evidence)", "SOUND WITH GAP, see below"):
            got = current_label("# w01-c40: s\n\nlabel: THEOREM\n\n## verdict: v1\n\nverdict: %s\n" % value)
            assert got["current"] == "unverified THEOREM", (value, got)
            assert "has text after the verdict phrase" in got["warnings"][0], (value, got)
        assert normalise_verdict("sound with gap.") == ("SOUND WITH GAP", None)
        assert normalise_verdict("Label  too   weak") == ("LABEL TOO WEAK", None)
        assert normalise_verdict("SOUNDLY") == (None, None) and normalise_verdict("maybe") == (None, None)
        # A label outside the table, and a verdict outside its verifier's own vocabulary, warn (and still count).
        got = current_label("# w01-c41: s\n\nlabel: FOO\n")
        assert got["current"] == "unverified FOO" and "label 'FOO' is not one of THEOREM" in got["warnings"][0], got
        assert current_label("# w01-c42: s\n\nlabel: cited UNVERIFIED\n")["warnings"] == []
        got = current_label("# w01-c43: s\n\nlabel: MEASURED\n\n## verdict: reproducer-w01-1\n\nverdict: SOUND\n")
        assert got["current"] == "MEASURED" and "not in the reproducer's vocabulary" in got["warnings"][0], got
        got = current_label("# w01-c44: s\n\nlabel: THEOREM\n\n## verdict: proof-adversary-w01-1\n\nverdict: SUPPORTED\n")
        assert "not in the proof-adversary's vocabulary" in got["warnings"][0], got
        # The verdict may follow other level-2 headings inside the section. One `verdict:` line counts.
        # Two lines: the last stands; with a `changed_by:` below the earlier one that is a revision, else a warning.
        head = "# w01-c21: s\n\nlabel: CHECKED\n\n## verdict: v1\n\n"
        got = current_label(head + "verdict: OVERSTATED\nreason: r\n")
        assert got["current"] == "below CHECKED: restate" and got["warnings"] == [], got
        got = current_label(head + "verdict: SUPPORTED\n\n### after the exchange\nverdict: OVERSTATED\nreason: r\nchanged_by: new/file.md\n")
        assert got["current"] == "below CHECKED: restate" and got["warnings"] == [] and got["verdicts"] == {"v1": "OVERSTATED"}, got
        got = current_label(head + "verdict: SUPPORTED\nchanged_by: a.md\nverdict: OVERSTATED\nverdict: SUPPORTED\nchanged_by: b.md\n")
        assert got["current"] == "CHECKED" and got["warnings"] == [], got  # three lines: the last stands
        got = current_label(head + "verdict: SUPPORTED\n\nverdict: OVERSTATED\nreason: r\n")
        assert got["current"] == "below CHECKED: restate" and "2 `verdict:` lines and no `changed_by:`" in got["warnings"][0] \
            and len(got["warnings"]) == 1, got
        got = current_label(head + "verdict: OVERSTATED\n\nverdict: SUPPORTED\nchanged_by: x\n")
        assert got["current"] == "CHECKED" and got["warnings"] == [], got  # the last stands in either direction
        # An earlier changed_by does not excuse a later revision.
        got = current_label(head + "changed_by: z\nverdict: SUPPORTED\nverdict: OVERSTATED\n")
        assert got["current"] == "below CHECKED: restate" and len(got["warnings"]) == 1, got
        text = ("# w01-c21: s\n\nlabel: CHECKED\n\n## verdict: v1\n\nverdict: OVERSTATED\n\n## notes\n\nplain notes\n")
        assert current_label(text)["current"] == "below CHECKED: restate"
        text = "# w01-c22: s\n\nlabel: CHECKED\n\n## verdict: v1\n\n## notes\n\nverdict: SUPPORTED\n"
        assert current_label(text)["current"] == "CHECKED"  # level-2 headings do not end the section
        # Bad sections warn and do not count.
        got = current_label("# w01-c23: s\n\nlabel: CHECKED\n\n## verdict: v1\n\nreason: I forgot the verdict\n")
        assert got["current"] == "unverified CHECKED" and "no `verdict:` line" in got["warnings"][0], got
        got = current_label("# w01-c24: s\n\nlabel: CHECKED\n\n## verdict: v1\n\nverdict: MAYBE\n")
        assert got["current"] == "unverified CHECKED" and "'MAYBE' is not a recognised verdict" in got["warnings"][0], got
        got = current_label("# w01-c25: s\n\nscope: no label here\n")
        assert "no `label:` line" in got["warnings"][0], got
        # Verifier part is not read as the head: a `label:` line inside it does not replace the author's.
        text = claim("w01-c26", "MEASURED", ("v", "SUPPORTED"), extra="\nlabel: THEOREM\n")
        assert current_label(text)["label"] == "MEASURED"

        pondus = os.path.join(root, "__pondus__")
        for name, text, _ in cases:
            _write(os.path.join(pondus, "%s.md" % parse_claim(text)["id"]), text)
        # Supersession: c5 (OVERSTATED) is restated by c30; c31 points at nothing.
        _write(os.path.join(pondus, "w01-c30.md"), claim("w01-c30", "CHECKED", head="supersedes: w01-c5\n"))
        _write(os.path.join(pondus, "w01-c31.md"), claim("w01-c31", "CHECKED", head="supersedes: w09-c1\n"))
        _write(os.path.join(pondus, "w01-c32.md"), "# w01-c32: s\n\nlabel: MEASURED\n\n## verdict: v1\n\nverdict: ???\n")
        by_id = {c["id"]: c for c in read_claims(root)}
        assert by_id["w01-c5"]["current"] == "superseded by w01-c30", by_id["w01-c5"]
        assert by_id["w01-c30"]["current"] == "unverified CHECKED"
        assert any("w09-c1, which is not a claim file" in w for w in by_id["w01-c31"]["warnings"])
        text = report(root)
        assert "- w01-c5  superseded by w01-c30\n" in text, text
        assert "- w01-c13  disputed: PI decides  <- v1: SUPPORTED; v2: UNSUPPORTED" in text, text
        assert "- w01-c1  unverified MEASURED\n" in text
        assert "## Claims (%d, 2 disputed, 2 warnings)" % len(by_id) in text, text
        assert "    ! verdict section 'v1': '???' is not a recognised verdict" in text, text

        # ---- Spend. Records name their session and cwd; the folder is the cwd with every non-alphanumeric a dash.
        real = os.path.realpath(root)
        assert encode(real).endswith("my-project-x"), real
        folder = os.path.join(cfg, "projects", encode(real))

        def record(mid, model, i, o, cw=0, cr=0, stop="end_turn", sid="s1", cache_creation=None, **extra):
            use = {"input_tokens": i, "output_tokens": o, "cache_creation_input_tokens": cw, "cache_read_input_tokens": cr}
            if cache_creation:
                use["cache_creation"] = cache_creation
            rec = {"type": "assistant", "sessionId": sid, "message": {"id": mid, "model": model, "stop_reason": stop,
                                                                      "usage": use}}
            rec.update(extra)
            return json.dumps(rec) + "\n"

        def head(sid, cwd, setting=None):
            text = json.dumps({"type": "user", "sessionId": sid, "cwd": cwd}) + "\n"
            if setting:
                text += json.dumps({"type": "agent-setting", "agentSetting": setting}) + "\n"
            return text

        def cost_state(sid, usd):
            return json.dumps({"type": "cost-state", "sessionId": sid, "totalCostUSD": usd}) + "\n"

        opus, sonnet = "claude-opus-5-5", "claude-sonnet-5-5"
        # s1 has ended: its cost is cost-state's. A message streamed in two records is one message.
        _write(os.path.join(folder, "s1.jsonl"),
               head("s1", real, "murmuration:research-pi")
               + record("m1", opus, 1, 5, stop=None) + record("m1", opus, 1, 50)
               + record("m2", opus, 1000000, 0) + record("m3", "<synthetic>", 0, 0) + "not json\n"
               + json.dumps({"type": "user", "message": {"id": "u1"}}) + "\n" + cost_state("s1", 7.5))
        sub = os.path.join(folder, "s1", "subagents")
        _write(os.path.join(sub, "agent-aaa.jsonl"), record("a1", sonnet, 3, 30, 10, 10, stop=None))  # truncated stream
        _write(os.path.join(sub, "agent-aaa.meta.json"), json.dumps({"agentType": "murmuration:explorer", "name": "explorer-w02-a"}))
        _write(os.path.join(sub, "agent-bbb.jsonl"), record("b1", sonnet, 4, 40))  # final
        _write(os.path.join(sub, "agent-bbb.meta.json"), json.dumps({"agentType": "murmuration:explorer"}))
        # Only the LAST record of a request counts: a final record followed by an unfinished one is not final.
        _write(os.path.join(sub, "agent-ccc.jsonl"), record("c1", sonnet, 1, 2) + record("c1", sonnet, 1, 3, stop=None))
        # s2 is still open: list price, with the 1 hour cache write rate, and a model with no price.
        _write(os.path.join(folder, "s2.jsonl"),
               head("s2", real) + record("n1", opus, 1000000, 0, cw=1000000, sid="s2",
                                         cache_creation={"ephemeral_1h_input_tokens": 1000000, "ephemeral_5m_input_tokens": 0})
               + record("n2", "claude-mystery-1", 5, 5, sid="s2"))
        # s3 started below the lab and is a fork: it holds a copy of m2 (s1's) and of a message of a session outside the lab.
        below = os.path.join(real, "sub")
        _write(os.path.join(cfg, "projects", encode(below), "s3.jsonl"),
               head("s3", below) + record("m2", opus, 1000000, 0, sid="s1") + record("g1", opus, 1000000, 0, sid="gone")
               + record("f1", sonnet, 1000000, 0, sid="s3"))
        # A session elsewhere is not the lab's.
        _write(os.path.join(cfg, "projects", encode(os.path.join(tmp, "elsewhere")), "s5.jsonl"),
               head("s5", os.path.join(tmp, "elsewhere")) + record("e1", opus, 1000000, 0, sid="s5"))

        warns = []
        sessions, copies = load_sessions(find_sessions(lab_roots(root)), warns)
        by_sid = {os.path.basename(s["path"])[:-6]: s for s in sessions}
        assert sorted(by_sid) == ["s1", "s2", "s3"] and warns == [], (sorted(by_sid), warns)
        r1 = by_sid["s1"]["rows"]
        main_row = r1[("murmuration:research-pi (main thread)", opus)]
        assert (main_row["msgs"], main_row["output"]) == (2, 50) and abs(main_row["usd"] - (4.0 + (4 + 50 * 20) / 1e6)) < 1e-9, main_row
        assert r1[("explorer-w02-a", sonnet)]["lower"] == 1 and r1[("explorer-w02-a", sonnet)]["output"] == 30
        assert r1[("murmuration:explorer", sonnet)]["lower"] == 0, "a request whose last record has a stop_reason is exact"
        assert r1[("subagent ccc", sonnet)]["lower"] == 1, "the last record of the request has no stop_reason"
        assert list(by_sid["s3"]["rows"]) == [("main thread", sonnet)], by_sid["s3"]["rows"]  # m2 and g1 are not s3's
        assert copies == 1, copies
        n = by_sid["s2"]["rows"][("main thread", opus)]
        assert abs(n["usd"] - (4.0 + 8.0)) < 1e-9, n  # 1M input at $4 + 1M cache write for 1 hour at $8
        assert by_sid["s2"]["rows"][("main thread", "claude-mystery-1")]["unpriced"] == 1
        assert abs(message_usd("claude-haiku-5-5", {"input_tokens": 200000}) - 0.5 * 0.2) < 1e-9  # long-prompt Haiku
        assert abs(message_usd(opus, {"output_tokens": 1000000, "speed": "fast"}) - 40.0) < 1e-9
        text = "\n".join(report_spend(root))
        # exact 7.5 (s1) + list price 12.0 (s2) + 2.0 (s3: sonnet f1 only); s3 and s2 are open
        assert "TOTAL  USD 21.50 at least   (7.50 exact + 14.00 at list price for 2 sessions still open)" in text, text
        assert "this checkout, sessions started below it" in text and "1 exact, 1 at least" in text, text
        assert "explorer-w02-a" in text and "30+" in text and "murmuration:explorer" in text, text
        assert "1 message record copied a message already counted" in text and "1 message is of a model" in text, text
        # The same folder is found through a symlinked project path.
        link = os.path.join(tmp, "link")
        os.symlink(root, link)
        assert [os.path.basename(f) for f in find_sessions(lab_roots(link))] == ["s1.jsonl", "s2.jsonl", "s3.jsonl"] \
            and "TOTAL  USD 21.50 at least" in "\n".join(report_spend(link))
        # An unreadable transcript is reported, not silently counted as empty.
        locked = os.path.join(sub, "agent-bbb.jsonl")
        os.chmod(locked, 0)
        try:
            if not os.access(locked, os.R_OK):
                seen = []
                load_sessions(find_sessions(lab_roots(root)), seen)
                assert any("could not read" in w and "agent-bbb.jsonl" in w for w in seen), seen
                assert "! could not read" in report(root)
        finally:
            os.chmod(locked, 0o644)
        # A path too long to name in full: found by the start of its name plus the records' cwd.
        longroot = os.path.join(tmp, "x" * 210)
        os.makedirs(longroot)
        longname = encode(os.path.realpath(longroot))
        _write(os.path.join(cfg, "projects", longname[:200] + "-9f8e7d", "s9.jsonl"),
               head("s9", os.path.realpath(longroot)) + record("l1", opus, 1, 1, sid="s9"))
        _write(os.path.join(cfg, "projects", longname[:200] + "-000000", "s9.jsonl"),
               head("s9", "/somewhere/else") + record("l2", opus, 5, 5, sid="s9"))
        assert [os.path.basename(os.path.dirname(f)) for f in find_sessions(lab_roots(longroot))] == [longname[:200] + "-9f8e7d"]
        # A session in another git worktree of the same repository belongs to the lab (needs git).
        repo, wt = os.path.join(tmp, "repo"), os.path.join(tmp, "repo-wt")
        try:
            os.makedirs(repo)
            for cmd in (["init", "-q"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x"],
                        ["worktree", "add", "-q", wt]):
                subprocess.run(["git", "-C", repo] + cmd, check=True, capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            print("skipped: git worktree check (git is not usable here)")
        else:
            real_repo, real_wt = os.path.realpath(repo), os.path.realpath(wt)
            _write(os.path.join(cfg, "projects", encode(real_repo), "r1.jsonl"),
                   head("r1", real_repo) + record("r1m", opus, 1000000, 0, sid="r1"))
            _write(os.path.join(cfg, "projects", encode(real_wt), "r2.jsonl"),
                   head("r2", real_wt) + record("r2m", opus, 1000000, 0, sid="r2") + cost_state("r2", 3.0))
            out = "\n".join(report_spend(repo))
            assert "TOTAL  USD 7.00 at least   (3.00 exact + 4.00 at list price for 1 session still open)" in out, out
            assert "this checkout " in out and "worktree repo-wt" in out, out
            assert "main checkout" in "\n".join(report_spend(wt)), "from the worktree the repository's main checkout is named"

        # git missing: the section says that only this folder's sessions were counted (a PATH with no git).
        notice = "only sessions started in this folder or below it were counted"
        assert notice in "\n".join(report_spend(root)), "a folder outside a repository gets the notice"
        saved_path = os.environ.get("PATH", "")
        os.environ["PATH"] = os.path.join(tmp, "no-such-dir")
        try:
            assert git_worktrees(repo) == [] and notice in "\n".join(report_spend(repo)), "git missing: notice"
        finally:
            os.environ["PATH"] = saved_path
        if os.path.isdir(wt):
            assert notice not in "\n".join(report_spend(repo)), "inside a repository there is no notice"

        # The reports together, and the spend section alone for a folder that is no lab.
        text = report(root)
        assert "## Spend" in text and "murmuration:explorer" in text and "claude-sonnet-5-5" not in text.split("## Spend")[0]
        assert "Current wave note: __statera__/wave-02.md" in text
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            assert main(["--spend", "--project", os.path.join(tmp, "elsewhere")]) == 0
        assert "TOTAL  USD 4.00 at least" in printed.getvalue(), printed.getvalue()

        # The transcript cache (w05-c5): the same report with it and without it, cold and warm; invalidated by a change of size or of modification time; a bad file is ignored; written atomically.
        cache_file = cache_path(root)
        assert cache_file == os.path.join(root, "__statera__", ".harness", "lab_status_cache.json"), cache_file
        spend = lambda: "\n".join(report_spend(root))
        os.environ["LAB_STATUS_CACHE"] = "off"
        plain = spend()
        del os.environ["LAB_STATUS_CACHE"]
        if os.path.exists(cache_file):
            os.unlink(cache_file)
        assert spend() == plain, "cold: the cache changes nothing"
        stored = json.load(open(cache_file))
        assert stored["v"] == CACHE_VERSION and len(stored["files"]) >= 6, sorted(stored)
        assert spend() == plain, "warm: the cache changes nothing"
        assert len(json.load(open(cache_file))["files"]) == len(stored["files"]), "a warm run keeps the entries it used"
        assert open(os.path.join(root, "__statera__", ".harness", ".gitignore")).read() == "*\n"
        assert [f for f in os.listdir(os.path.dirname(cache_file)) if f.endswith(".tmp")] == [], "the temporary file is renamed away"
        bbb = os.path.join(sub, "agent-bbb.jsonl")
        before = open(bbb).read()
        open(bbb, "a").write(record("b2", sonnet, 4, 40))
        grown = spend()
        assert grown != plain, "a longer file is read again"
        os.environ["LAB_STATUS_CACHE"] = "off"
        assert spend() == grown, "and equals the uncached report"
        del os.environ["LAB_STATUS_CACHE"]
        # a size or a time that differs, the other the same: read again (a mutant that compares only one of them must fail here)
        st_ = os.stat(bbb)
        open(bbb, "a").write(record("b3", sonnet, 4, 40))
        os.utime(bbb, ns=(st_.st_atime_ns, st_.st_mtime_ns))   # longer, with the time it had
        assert spend() != grown, "another size, the same time: read again"
        spend()
        cur = open(bbb).read()
        st_ = os.stat(bbb)
        open(bbb, "w").write(cur.replace('"output_tokens": 40', '"output_tokens": 41', 1))
        os.utime(bbb, ns=(st_.st_atime_ns, st_.st_mtime_ns + 5_000_000_000))   # the same size, another time
        os.environ["LAB_STATUS_CACHE"] = "off"
        fresh = spend()
        del os.environ["LAB_STATUS_CACHE"]
        assert spend() == fresh, "the same size, another time: read again"
        good = json.load(open(cache_file))
        for junk in ("{not json", '{"v": 0, "files": {}}', '{"v": %d, "files": 5}' % CACHE_VERSION, "[]",
                     json.dumps(dict(good, v=CACHE_VERSION + 1, files={p: e[:2] + [[], None, None] for p, e in good["files"].items()}))):   # the last: another version, with emptied entries of the right stamps
            open(cache_file, "w").write(junk)
            assert spend() == fresh, "a cache file that is unusable is ignored: " + junk[:40]
            assert json.load(open(cache_file))["v"] == CACHE_VERSION, "and replaced"
        number = os.path.join(tmp, "nokey.jsonl")   # a message with no id, request id or uuid is keyed by its position, a number that a JSON object key would turn into text
        _write(number, json.dumps({"type": "assistant", "sessionId": "k", "message": {"model": sonnet, "usage": {"input_tokens": 1, "output_tokens": 2}}}) + "\n")
        direct = parse_transcript(number, [])
        c1 = Cache(os.path.join(tmp, "k.json"))
        assert c1.read(number, []) == direct and list(direct[0]) == [0]
        c1.save()
        c2 = Cache(os.path.join(tmp, "k.json"))
        assert c2.read(number, []) == direct and list(c2.read(number, [])[0]) == [0] and not c2.dirty, "read back from the file: equal, and the key is still a number"
        elsewhere = os.path.join(tmp, "elsewhere")
        report_spend(elsewhere)
        assert not os.path.exists(os.path.join(elsewhere, "__statera__")), "a folder that is no lab gets no cache folder"
        if os.geteuid() != 0:   # a cache that cannot be written is not an error
            os.unlink(cache_file)
            os.chmod(os.path.dirname(cache_file), 0o500)
            try:
                assert spend() == fresh
            finally:
                os.chmod(os.path.dirname(cache_file), 0o700)

        # No transcripts: say so.
        os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(tmp, "empty")
        assert "no transcripts found" in report(root)
    print("PASS lab_status")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    root = project_root()
    if "--project" in argv:
        i = argv.index("--project")
        if i + 1 >= len(argv):
            print("lab_status.py: --project needs a directory", file=sys.stderr)
            return 2
        root = argv[i + 1]
    print("\n".join(report_spend(root)) if "--spend" in argv else report(root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
