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
import glob
import json
import os
import re
import sys

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
    import subprocess   # here and not at the top: only the spend report asks git, and a session resumed by resume_brief.py never does
    try:
        out = subprocess.run(["git", "-C", root, "worktree", "list", "--porcelain"], capture_output=True,
                             text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return [line[9:] for line in out.splitlines() if line.startswith("worktree ")]


def lab_roots(root):
    """The lab's directory, its real path, and every git worktree of its repository (and their real paths)."""
    roots = [os.path.abspath(root), os.path.realpath(root)]
    for path in git_worktrees(root):
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


def read_transcript(path, warnings):
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
    roots = lab_roots(root)
    warnings = []
    sessions, copies = load_sessions(find_sessions(roots), warnings)
    out = ["## Spend (USD: Claude Code's cost-state where a session has ended, else list price of 2026-10-19)"]
    if not git_worktrees(root):
        out.append("! git is not available, or this folder is not in a git repository: only sessions started in this "
                   "folder or below it were counted")
    if not sessions:
        out.append("no transcripts found for %s (looked for sessions whose cwd is the lab or one of its git worktrees, "
                   "under %s)" % (os.path.abspath(root), os.path.join(config_dir(), "projects")))
        return out
    here = os.path.realpath(root)
    trees = git_worktrees(root)
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


def main(argv):
    if "--selftest" in argv:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import lab_status_selftest
        lab_status_selftest.selftest()
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
