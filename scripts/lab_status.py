#!/usr/bin/env python3
"""Report the state of a lab project: open puzzles, the current label of each claim, and spend.

Read-only. Python standard library only.

    lab_status.py [--project DIR]   print the report for DIR (default: the project directory)
    lab_status.py --selftest        check the three reports on a temporary project

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
                           heading, whose first `verdict:` line counts when it is exactly a verdict
                           (case, bold and a trailing period tolerated; extra text warns).
    ~/.claude/projects/<project-path>/   Claude Code's transcripts for this project (the main
                           thread and every subagent); `usage` fields are summed. Set
                           CLAUDE_CONFIG_DIR to use another configuration directory.

Claim states shown: `unverified <LABEL>`, `<LABEL>`, `<LABEL> (gap)`, `below <LABEL>: restate`,
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
        for line in read(path).splitlines():
            level2 = re.match(r"^##(?!#)\s+(.*?)\s*$", line)
            if level2:
                heading = re.sub(r"[*`]", "", level2.group(1)).strip()
                match = PUZZLE_HEADING_RE.match(heading)
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
    out = ["## Open puzzles (%d)" % len(puzzles)]
    if not puzzles:
        out.append("none: every raised puzzle has a disposition in a closed wave note")
    for p in puzzles:
        text = p["text"] if len(p["text"]) <= 160 else p["text"][:157] + "..."
        out.append("- %s (%s) %s" % (p["id"], p["file"], text))
    out += ["! " + w for w in puzzle_warnings(root)]
    return out


# ---------------------------------------------------------------- claims

def field_re(name):
    """A `name: value` line, tolerating a list bullet, bold around the name or colon, and case."""
    return re.compile(r"^\s*(?:[-*>]\s+)?(?:\*\*|__)?%s\s*(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(.*)$" % name, re.I)


LABEL_RE, SUPERSEDES_RE, VERDICT_RE = field_re("label"), field_re("supersedes"), field_re("verdict")
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
    standing = {}
    for name, lines in claim["sections"]:
        value = next((m.group(1) for m in map(VERDICT_RE.match, lines) if m), None)
        if value is None:
            warnings.append("verdict section '%s' has no `verdict:` line" % name)
            continue
        verdict, extra = normalise_verdict(value)
        if verdict is None and extra is not None:
            warnings.append("verdict section '%s': '%s' has text after the verdict phrase, so it is not counted; "
                            "write only the verdict on the `verdict:` line and the explanation on `reason:`"
                            % (name, clean_value(value)))
            continue
        if verdict is None:
            warnings.append("verdict section '%s': '%s' is not a recognised verdict" % (name, clean_value(value)))
            continue
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

def config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def project_folder_names(root):
    """Names Claude Code gives a project's transcript folder: its path with every non-alphanumeric a dash."""
    names = []
    for path in (os.path.abspath(root), os.path.realpath(root)):
        name = re.sub(r"[^A-Za-z0-9]", "-", path)
        if name not in names:
            names.append(name)
    return names


def records_have_cwd(folder, cwds, limit=200):
    """True when an early record of one of the folder's transcripts says it ran in one of `cwds`."""
    try:
        files = sorted(glob.glob(os.path.join(folder, "*.jsonl")))[:5]
        for path in files:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for _, line in zip(range(limit), fh):
                    if '"cwd"' in line:
                        try:
                            if json.loads(line).get("cwd") in cwds:
                                return True
                        except ValueError:
                            pass
    except OSError:
        pass
    return False


def transcript_dirs(root):
    """Transcript folders for a project: the folder named after its path, else (for paths too long
    to be named in full) a folder sharing the start of that name whose records say they ran there."""
    base = os.path.join(config_dir(), "projects")
    names = project_folder_names(root)
    found = [os.path.join(base, n) for n in names if os.path.isdir(os.path.join(base, n))]
    if found:
        return found
    cwds = {os.path.abspath(root), os.path.realpath(root)}
    try:
        entries = sorted(os.listdir(base))
    except OSError:
        return []
    prefixes = tuple(n[:100] for n in names)
    near = [e for e in entries if e.startswith(prefixes)][:20]
    return [os.path.join(base, e) for e in near if records_have_cwd(os.path.join(base, e), cwds)]


def usage_rows(path, agent, warnings):
    """Yield (agent, model, usage dict) once per distinct assistant message id in a transcript file."""
    last = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                msg = rec.get("message") if isinstance(rec, dict) else None
                if rec.get("type") == "assistant" and isinstance(msg, dict) and isinstance(msg.get("usage"), dict):
                    last[msg.get("id") or rec.get("uuid") or len(last)] = msg  # streamed copies: keep the last
    except OSError as err:
        warnings.append("could not read %s: %s" % (path, err.strerror or err))
    for msg in last.values():
        model = msg.get("model") or "unknown"
        if model != "<synthetic>":
            yield agent, model, msg["usage"]


def subagent_type(path):
    meta = path[:-len(".jsonl")] + ".meta.json"
    try:
        value = json.loads(read(meta)).get("agentType")
        if value:
            return str(value)
    except (OSError, ValueError, AttributeError):
        pass
    return "subagent"


def main_agent(path):
    """The agent the session ran as (`agent-setting` record), else 'main thread'."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"agent-setting"' in line:
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    if rec.get("type") == "agent-setting" and rec.get("agentSetting"):
                        return "%s (main thread)" % rec["agentSetting"]
    except OSError:
        pass
    return "main thread"


def spend(root):
    """Token usage per (agent, model) for this project's transcripts.

    Returns (rows, folders, warnings): rows is a list of dicts with agent, model, runs, messages,
    input, cache_write, cache_read, output; folders lists the transcript folders read (empty: none
    found); warnings lists files that could not be read.
    """
    folders = transcript_dirs(root)
    totals = collections.OrderedDict()
    runs = collections.defaultdict(set)
    warnings = []
    for folder in folders:
        try:
            names = sorted(os.listdir(folder))
        except OSError as err:
            warnings.append("could not list %s: %s" % (folder, err.strerror or err))
            continue
        for name in names:
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(folder, name)
            sources = [(main_agent(path), path, None)]
            session = path[:-len(".jsonl")]
            for sub in sorted(glob.glob(os.path.join(session, "subagents", "**", "agent-*.jsonl"), recursive=True)):
                sources.append((subagent_type(sub), sub, os.path.basename(sub)[:-len(".jsonl")]))
            for agent, file, run in sources:
                for who, model, use in usage_rows(file, agent, warnings):
                    row = totals.setdefault((who, model), collections.Counter())
                    row["messages"] += 1
                    row["input"] += int(use.get("input_tokens") or 0)
                    row["cache_write"] += int(use.get("cache_creation_input_tokens") or 0)
                    row["cache_read"] += int(use.get("cache_read_input_tokens") or 0)
                    row["output"] += int(use.get("output_tokens") or 0)
                    runs[(who, model)].add(run or path)
    rows = []
    for (who, model), c in totals.items():
        rows.append({"agent": who, "model": model, "runs": len(runs[(who, model)]), **c})
    rows.sort(key=lambda r: -(r["input"] + r["cache_write"] + r["output"]))
    return rows, folders, warnings


def report_spend(root):
    rows, folders, warnings = spend(root)
    out = ["## Spend (tokens, from Claude Code's transcripts for this project)"]
    if not folders:
        out.append("no transcripts found for %s under %s" % (os.path.abspath(root),
                   os.path.join(config_dir(), "projects")))
        return out
    out.append("read: " + ", ".join(folders))
    if not rows:
        out.append("no usage records in those transcripts")
    else:
        head = ("agent", "model", "runs", "msgs", "input", "cache-write", "cache-read", "output")

        def fmt(n):
            return "{:,}".format(n)

        table = [head] + [(r["agent"], r["model"], str(r["runs"]), str(r["messages"]), fmt(r["input"]),
                           fmt(r["cache_write"]), fmt(r["cache_read"]), fmt(r["output"])) for r in rows]
        table.append(("total", "", "", str(sum(r["messages"] for r in rows)),
                      fmt(sum(r["input"] for r in rows)), fmt(sum(r["cache_write"] for r in rows)),
                      fmt(sum(r["cache_read"] for r in rows)), fmt(sum(r["output"] for r in rows))))
        widths = [max(len(row[i]) for row in table) for i in range(len(head))]
        for n, row in enumerate(table):
            out.append("  ".join(cell.ljust(widths[i]) if i < 2 else cell.rjust(widths[i])
                                 for i, cell in enumerate(row)))
            if n == 0:
                out.append("  ".join("-" * w for w in widths))
        out.append("runs = distinct sessions or subagent runs. Prices are not applied; multiply by your rates.")
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
        assert len(warnings) == 6, warnings
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
        # The verdict may follow other level-2 headings inside the section; the first verdict line counts.
        text = ("# w01-c21: s\n\nlabel: CHECKED\n\n## verdict: v1\n\nverdict: OVERSTATED\n\n## notes\n\nverdict: SUPPORTED\n")
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

        # ---- Spend: a main thread and two subagents, with streamed duplicates and a synthetic record.
        # The folder is the project path with every non-alphanumeric character as a dash.
        name = re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(root))  # Claude Code names it by the real path
        assert name.endswith("my-project-x"), name
        folder = os.path.join(cfg, "projects", name)

        def record(mid, model, i, o, cw=0, cr=0, kind="assistant", **extra):
            rec = {"type": kind, "message": {"id": mid, "model": model, "usage": {
                "input_tokens": i, "output_tokens": o, "cache_creation_input_tokens": cw,
                "cache_read_input_tokens": cr}}}
            rec.update(extra)
            return json.dumps(rec) + "\n"

        _write(os.path.join(folder, "s1.jsonl"),
               json.dumps({"type": "agent-setting", "agentSetting": "murmuration:research-pi"}) + "\n"
               + record("m1", "claude-opus-x", 1, 5, 100, 0) + record("m1", "claude-opus-x", 1, 50, 100, 0)
               + record("m2", "claude-opus-x", 2, 20, 0, 100) + record("m3", "<synthetic>", 0, 0)
               + "not json\n" + record("u1", "claude-opus-x", 9, 9, kind="user"))
        _write(os.path.join(folder, "s2.jsonl"), record("n1", "claude-opus-x", 1, 1))  # no agent-setting
        sub = os.path.join(folder, "s1", "subagents")
        _write(os.path.join(sub, "agent-aaa.jsonl"), record("a1", "claude-sonnet-x", 3, 30, 10, 10))
        _write(os.path.join(sub, "agent-aaa.meta.json"), json.dumps({"agentType": "murmuration:explorer"}))
        _write(os.path.join(sub, "agent-bbb.jsonl"), record("b1", "claude-sonnet-x", 4, 40, 0, 0))
        _write(os.path.join(sub, "agent-bbb.meta.json"), json.dumps({"agentType": "murmuration:explorer"}))
        rows, folders, warns = spend(root)
        by = {(r["agent"], r["model"]): r for r in rows}
        main = by[("murmuration:research-pi (main thread)", "claude-opus-x")]
        assert (main["messages"], main["input"], main["output"], main["cache_write"], main["cache_read"]) \
            == (2, 3, 70, 100, 100), main
        assert by[("main thread", "claude-opus-x")]["messages"] == 1
        expl = by[("murmuration:explorer", "claude-sonnet-x")]
        assert (expl["runs"], expl["messages"], expl["input"], expl["output"]) == (2, 2, 7, 70), expl
        assert len(rows) == 3 and folders == [folder] and warns == [], (rows, folders, warns)
        # The same folder is found through a symlinked project path.
        link = os.path.join(tmp, "link")
        os.symlink(root, link)
        assert spend(link)[1] == [folder]
        # An unreadable transcript is reported, not silently counted as empty.
        locked = os.path.join(sub, "agent-bbb.jsonl")
        os.chmod(locked, 0)
        try:
            if not os.access(locked, os.R_OK):
                rows2, _, warns2 = spend(root)
                assert any("could not read" in w and "agent-bbb.jsonl" in w for w in warns2), warns2
                assert "! could not read" in report(root)
        finally:
            os.chmod(locked, 0o644)
        # A path too long to name in full: found by the start of its name plus the records' cwd.
        longroot = os.path.join(tmp, "x" * 210)
        os.makedirs(longroot)
        longname = re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(longroot))
        _write(os.path.join(cfg, "projects", longname[:200] + "-9f8e7d", "s9.jsonl"),
               record("l1", "claude-opus-x", 1, 1, cwd=longroot))
        _write(os.path.join(cfg, "projects", longname[:200] + "-000000", "s9.jsonl"),
               record("l2", "claude-opus-x", 5, 5, cwd="/somewhere/else"))
        assert [os.path.basename(f) for f in spend(longroot)[1]] == [longname[:200] + "-9f8e7d"]

        # The three reports together.
        text = report(root)
        assert "## Spend" in text and "murmuration:explorer" in text and "claude-sonnet-x" in text
        assert "Current wave note: __statera__/wave-02.md" in text

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
    print(report(root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
