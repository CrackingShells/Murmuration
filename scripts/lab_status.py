#!/usr/bin/env python3
"""Report the state of a lab project: open puzzles, the current label of each claim, and spend.

Read-only. Python standard library only.

    lab_status.py [--project DIR]   print the report for DIR (default: the project directory)
    lab_status.py --selftest        check the three reports on a temporary project

The project directory is CLAUDE_PROJECT_DIR, else the current directory.

What it reads
    __scrupuli__/*.md      puzzles: `## S-wNN-<agent>-<n>` headings
    __statera__/wave-NN.md wave notes; a note is closed when it has a `closed: YYYY-MM-DD` line.
                           A puzzle is disposed when a closed note has a line holding its id and
                           `followed` or `parked`. (If the note has a heading containing
                           "disposition", only the lines under it count.)
    __pondus__/*.md        claims: a head (`# <id>: <statement>`, `label:`) then one
                           `## verdict: <verifier>` section per verifier with a `verdict:` line
    ~/.claude/projects/<project-path>/   Claude Code's transcripts for this project (the main
                           thread and every subagent); `usage` fields are summed. Set
                           CLAUDE_CONFIG_DIR to use another configuration directory.
"""
import collections
import glob
import json
import os
import re
import sys
import tempfile

PUZZLE_ID = r"S-w\d+-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*-\d+"
PUZZLE_RE = re.compile(PUZZLE_ID)
PUZZLE_HEADING_RE = re.compile(r"^#{2,6}\s+(%s)\b" % PUZZLE_ID)
CLOSED_RE = re.compile(r"^\s*closed:\s*\d{4}-\d{2}-\d{2}", re.M | re.I)
DISPOSITION_RE = re.compile(r"\b(?:followed|parked)\b", re.I)
WAVE_RE = re.compile(r"wave-(\d+)\.md$")

# Verdict -> family. The label rules: SUPPORTED/SOUND keep the label, SOUND WITH GAP keeps it marked
# gap, OVERSTATED/LABEL TOO STRONG need a lower label, LABEL TOO WEAK allows a higher one,
# UNSUPPORTED/WRONG withdraw the claim, ESCALATE leaves it with the PI.
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
# Weakest first: the weakest standing verdict decides the current label.
WEAKNESS = ["withdraw", "lower", "escalate", "gap", "accept", "higher"]
# Verdicts that say "the claim stands as stated or better" / "it does not" / "it is stronger".
STANCE = {"accept": "stands", "gap": "stands", "lower": "rejected", "withdraw": "rejected",
          "higher": "stronger"}


def project_root():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


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
    """Ids with a disposition (`followed` or `parked`) in a closed wave note."""
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
            if DISPOSITION_RE.search(line):
                disposed.update(PUZZLE_RE.findall(line))
    return disposed


def raised_puzzles(root):
    """[{id, file, text}] for each puzzle heading in `__scrupuli__/*.md`, first occurrence only."""
    puzzles, seen = [], set()
    for path in sorted(glob.glob(os.path.join(root, "__scrupuli__", "*.md"))):
        current = None
        for line in read(path).splitlines():
            heading = PUZZLE_HEADING_RE.match(line)
            if heading:
                pid = heading.group(1)
                current = None
                if pid not in seen:
                    seen.add(pid)
                    current = {"id": pid, "file": os.path.relpath(path, root), "lines": []}
                    puzzles.append(current)
            elif re.match(r"#{1,6}\s", line):
                current = None
            elif current is not None:
                current["lines"].append(line)
    for p in puzzles:
        body = [l.strip() for l in p.pop("lines") if l.strip() and not l.strip().lower().startswith("refs:")]
        p["text"] = " ".join(body)
    return puzzles


def open_puzzles(root):
    """Puzzles raised in `__scrupuli__/` that no closed wave note has disposed of."""
    disposed = disposed_puzzles(root)
    return [p for p in raised_puzzles(root) if p["id"] not in disposed]


def report_puzzles(root):
    puzzles = open_puzzles(root)
    out = ["## Open puzzles (%d)" % len(puzzles)]
    if not puzzles:
        out.append("none: every raised puzzle has a disposition in a closed wave note")
    for p in puzzles:
        text = p["text"] if len(p["text"]) <= 160 else p["text"][:157] + "..."
        out.append("- %s (%s) %s" % (p["id"], p["file"], text))
    return out


# ---------------------------------------------------------------- claims

def parse_claim(text):
    """Split a claim file into (id, statement, author_label, [(verifier, verdict_text)])."""
    lines = text.splitlines()
    cid, statement, label = "", "", ""
    verdicts = []  # (verifier, raw verdict value), in file order
    section = None  # None while in the head, else the verifier name
    for line in lines:
        heading = re.match(r"^##\s+verdict\s*:\s*(.*\S)?\s*$", line, re.I)
        if heading:
            section = heading.group(1) or "verifier"
            continue
        if re.match(r"^#{1,2}\s", line) and section is not None and not heading:
            if re.match(r"^##\s", line):
                section = None  # another kind of section: not a verdict
                continue
        if section is None:
            title = re.match(r"^#\s+(\S+?)\s*:\s*(.*)$", line)
            if title and not cid:
                cid, statement = title.group(1), title.group(2).strip()
                continue
            lab = re.match(r"^label\s*:\s*(.*\S)\s*$", line, re.I)
            if lab and not label:
                label = lab.group(1)
        else:
            ver = re.match(r"^verdict\s*:\s*(.*\S)\s*$", line, re.I)
            if ver:
                verdicts.append((section, ver.group(1)))
    return cid, statement, label, verdicts


def normalise_verdict(raw):
    """The recognised verdict at the start of `raw` (longest match), else the raw text upper-cased."""
    upper = re.sub(r"[\s_]+", " ", raw.strip().upper())
    for name in sorted(VERDICTS, key=len, reverse=True):
        if upper == name or upper.startswith(name + " ") or upper.startswith(name + ":") \
                or upper.startswith(name + "("):
            return name
    return upper


def current_label(text):
    """The standing state of one claim, from the text of its `__pondus__/<id>.md` file.

    Returns a dict: id, statement, author_label, current (a short string), flags (list of
    'unverified', 'gap', 'disputed', 'escalated', 'restate lower', 'withdrawn', 'may restate higher',
    'unrecognised verdict'), verdicts ({verifier: verdict}, each verifier's latest).
    """
    cid, statement, label, raw = parse_claim(text)
    label = label or "UNLABELLED"
    standing = {}
    for verifier, value in raw:  # later sections and later lines replace earlier ones
        standing[verifier] = normalise_verdict(value)
    result = {"id": cid, "statement": statement, "author_label": label, "verdicts": standing,
              "flags": [], "current": label}
    if not standing:
        result["flags"] = ["unverified"]
        return result
    families = {v: VERDICTS.get(v) for v in standing.values()}
    if any(f is None for f in families.values()):
        result["flags"].append("unrecognised verdict")
    known = [f for f in families.values() if f]
    stances = {STANCE[f] for f in known if f in STANCE}
    if len(stances) > 1:
        result["flags"].append("disputed")
    weakest = next((f for f in WEAKNESS if f in known), None)
    if weakest == "withdraw":
        result["current"] = "WITHDRAWN"
        result["flags"].append("withdrawn")
    elif weakest == "lower":
        result["flags"].append("restate lower")
    elif weakest == "escalate":
        result["flags"].append("escalated")
    elif weakest == "gap":
        result["flags"].append("gap")
    elif weakest == "higher":
        result["flags"].append("may restate higher")
    return result


def report_claims(root):
    files = sorted(glob.glob(os.path.join(root, "__pondus__", "*.md")))
    claims = []
    for path in files:
        info = current_label(read(path))
        info["id"] = info["id"] or os.path.splitext(os.path.basename(path))[0]
        claims.append(info)
    disputed = [c for c in claims if "disputed" in c["flags"]]
    out = ["## Claims (%d, %d disputed)" % (len(claims), len(disputed))]
    if not claims:
        out.append("none: `__pondus__/` holds no claim files")
    for c in claims:
        flags = ", ".join(c["flags"])
        verdicts = "; ".join("%s: %s" % kv for kv in sorted(c["verdicts"].items()))
        line = "- %s  %s" % (c["id"], c["current"])
        if c["current"] != c["author_label"]:
            line += " (author: %s)" % c["author_label"]
        if flags:
            line += "  [%s]" % flags
        if verdicts:
            line += "  <- %s" % verdicts
        out.append(line)
    return out


# ---------------------------------------------------------------- spend

def config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def transcript_dirs(root):
    """Candidate transcript folders for a project: its path with every non-alphanumeric as a dash."""
    base = os.path.join(config_dir(), "projects")
    names = []
    for path in (os.path.abspath(root), os.path.realpath(root)):
        for name in (re.sub(r"[^A-Za-z0-9]", "-", path), path.replace("/", "-")):
            if name not in names:
                names.append(name)
    return [os.path.join(base, n) for n in names if os.path.isdir(os.path.join(base, n))]


def usage_rows(path, agent):
    """Yield (agent, model, usage dict) once per distinct assistant message id in a transcript file."""
    last = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            msg = rec.get("message") if isinstance(rec, dict) else None
            if rec.get("type") == "assistant" and isinstance(msg, dict) and isinstance(msg.get("usage"), dict):
                last[msg.get("id") or rec.get("uuid") or len(last)] = msg  # streamed copies: keep the last
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


def spend(root):
    """Token usage per (agent, model) for this project's transcripts.

    Returns (rows, folders): rows is a list of dicts with agent, model, runs, messages, input,
    cache_write, cache_read, output; folders lists the transcript folders read (empty: none found).
    """
    folders = transcript_dirs(root)
    totals = collections.OrderedDict()
    runs = collections.defaultdict(set)
    for folder in folders:
        for path in sorted(glob.glob(os.path.join(folder, "*.jsonl"))):
            sources = [("main thread", path, None)]
            session = path[:-len(".jsonl")]
            for sub in sorted(glob.glob(os.path.join(session, "subagents", "**", "agent-*.jsonl"), recursive=True)):
                sources.append((subagent_type(sub), sub, os.path.basename(sub)[:-len(".jsonl")]))
            for agent, file, run in sources:
                for name, model, use in usage_rows(file, agent):
                    row = totals.setdefault((name, model), collections.Counter())
                    row["messages"] += 1
                    row["input"] += int(use.get("input_tokens") or 0)
                    row["cache_write"] += int(use.get("cache_creation_input_tokens") or 0)
                    row["cache_read"] += int(use.get("cache_read_input_tokens") or 0)
                    row["output"] += int(use.get("output_tokens") or 0)
                    runs[(name, model)].add(run or path)
    rows = []
    for (name, model), c in totals.items():
        rows.append({"agent": name, "model": model, "runs": len(runs[(name, model)]), **c})
    rows.sort(key=lambda r: -(r["input"] + r["cache_write"] + r["output"]))
    return rows, folders


def report_spend(root):
    rows, folders = spend(root)
    out = ["## Spend (tokens, from Claude Code's transcripts for this project)"]
    if not folders:
        out.append("no transcripts found for %s under %s" % (os.path.abspath(root),
                   os.path.join(config_dir(), "projects")))
        return out
    if not rows:
        out.append("transcripts found in %s, but no usage records in them" % ", ".join(folders))
        return out
    head = ("agent", "model", "runs", "msgs", "input", "cache-write", "cache-read", "output")
    table = [head] + [(r["agent"], r["model"], str(r["runs"]), str(r["messages"]), "{:,}".format(r["input"]),
                       "{:,}".format(r["cache_write"]), "{:,}".format(r["cache_read"]),
                       "{:,}".format(r["output"])) for r in rows]
    total = ("total", "", "", str(sum(r["messages"] for r in rows)), "{:,}".format(sum(r["input"] for r in rows)),
             "{:,}".format(sum(r["cache_write"] for r in rows)), "{:,}".format(sum(r["cache_read"] for r in rows)),
             "{:,}".format(sum(r["output"] for r in rows)))
    table.append(total)
    widths = [max(len(row[i]) for row in table) for i in range(len(head))]
    for n, row in enumerate(table):
        out.append("  ".join(cell.ljust(widths[i]) if i < 2 else cell.rjust(widths[i]) for i, cell in enumerate(row)))
        if n == 0:
            out.append("  ".join("-" * w for w in widths))
    out.append("runs = distinct sessions or subagent runs. Prices are not applied; multiply by your rates.")
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
        root = os.path.join(tmp, "my.project")
        cfg = os.path.join(tmp, "config")
        os.environ["CLAUDE_CONFIG_DIR"] = cfg
        os.environ.pop("CLAUDE_PROJECT_DIR", None)

        # Without a lab: say so.
        os.makedirs(root)
        assert "No lab" in report(root)

        # Puzzles: four raised, one followed and one parked in a closed note, one mentioned only,
        # one raised after the closed note.
        _write(os.path.join(root, "__scrupuli__", "wave-01-explorer.md"),
               "## S-w01-explorer-1\nthe 3-bit rows vanish\nrefs: data/a.csv:12\n\n"
               "## S-w01-explorer-2\nfigure 2 has a kink\nrefs: figs/2.png\n\n"
               "## S-w01-explorer-3\nrunning time drops at n=9\nrefs: logs/run.log:88\n")
        _write(os.path.join(root, "__scrupuli__", "wave-02-author-b.md"),
               "## S-w02-author-b-1\nfactor of two between the tables\nrefs: t.md\n")
        _write(os.path.join(root, "__statera__", "wave-01.md"),
               "# Wave 01\n\nopened: 2026-01-02\n\n## Notes\n\nWe looked at S-w01-explorer-3 again.\n\n"
               "## Puzzle dispositions (at close)\n\n| Puzzle | Disposition |\n|:--|:--|\n"
               "| S-w01-explorer-1 | followed: w02-author-1 |\n"
               "| S-w01-explorer-2 | parked: cosmetic |\n"
               "| S-wNN-<agent>-<n> | followed: <brief or claim id> |\n\nclosed: 2026-01-09\n")
        _write(os.path.join(root, "__statera__", "wave-02.md"),
               "# Wave 02\n\nopened: 2026-01-10\n\n## Puzzle dispositions (at close)\n\n"
               "| S-w02-author-b-1 | followed: w03-x |\n")  # open note: does not count
        ids = [p["id"] for p in open_puzzles(root)]
        assert ids == ["S-w01-explorer-3", "S-w02-author-b-1"], ids
        assert current_wave(root)[0] == 2
        _write(os.path.join(root, "__statera__", "wave-02.md"),
               "# Wave 02\n\nopened: 2026-01-10\n\n## Puzzle dispositions (at close)\n\n"
               "| S-w02-author-b-1 | followed: w03-x |\n\nclosed: 2026-01-20\n")
        assert [p["id"] for p in open_puzzles(root)] == ["S-w01-explorer-3"]
        assert current_wave(root)[0] == 2  # all closed: the latest

        # Labels.
        def claim(cid, label, *verdicts):
            text = "# %s: some statement\n\nlabel: %s\nscope: s\nevidence: e\nauthor: a\n" % (cid, label)
            for who, verdict in verdicts:
                text += "\n## verdict: %s\n\nindependent result: r\nverdict: %s\nreason: because\n" % (who, verdict)
            return text

        cases = [
            (claim("w01-author-1", "MEASURED"), "MEASURED", ["unverified"]),
            (claim("w01-author-2", "MEASURED", ("verifier-w01-1", "SUPPORTED")), "MEASURED", []),
            (claim("w01-author-3", "THEOREM", ("v", "SOUND WITH GAP")), "THEOREM", ["gap"]),
            (claim("w01-author-4", "MEASURED", ("v", "OVERSTATED")), "MEASURED", ["restate lower"]),
            (claim("w01-author-5", "THEOREM", ("v", "LABEL TOO STRONG")), "THEOREM", ["restate lower"]),
            (claim("w01-author-6", "CONJECTURE", ("v", "LABEL TOO WEAK")), "CONJECTURE", ["may restate higher"]),
            (claim("w01-author-7", "MEASURED", ("v", "UNSUPPORTED")), "WITHDRAWN", ["withdrawn"]),
            (claim("w01-author-8", "THEOREM", ("v", "WRONG")), "WITHDRAWN", ["withdrawn"]),
            (claim("w01-author-9", "MEASURED", ("v", "ESCALATE")), "MEASURED", ["escalated"]),
            # the latest verdict of the same verifier stands
            (claim("w01-author-10", "MEASURED", ("v", "UNSUPPORTED"), ("v", "SUPPORTED")), "MEASURED", []),
            # the weakest of two agreeing-in-stance verdicts
            (claim("w01-author-11", "THEOREM", ("v1", "SOUND"), ("v2", "SOUND WITH GAP")), "THEOREM", ["gap"]),
            # disagreement
            (claim("w01-author-12", "MEASURED", ("v1", "SUPPORTED"), ("v2", "UNSUPPORTED")), "WITHDRAWN",
             ["disputed", "withdrawn"]),
            (claim("w01-author-13", "MEASURED", ("v1", "SUPPORTED"), ("v2", "OVERSTATED")), "MEASURED",
             ["disputed", "restate lower"]),
            (claim("w01-author-14", "MEASURED", ("v", "supported")), "MEASURED", []),
        ]
        for text, current, flags in cases:
            got = current_label(text)
            assert (got["current"], sorted(got["flags"])) == (current, sorted(flags)), (got, current, flags)
            assert got["id"].startswith("w01-author-")
        for n, (text, _, _) in enumerate(cases, 1):
            _write(os.path.join(root, "__pondus__", "w01-author-%d.md" % n), text)

        # Spend: a main thread and two subagents, with streamed duplicates and a synthetic record.
        name = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(root))
        folder = os.path.join(cfg, "projects", name)

        def record(mid, model, i, o, cw=0, cr=0, kind="assistant"):
            return json.dumps({"type": kind, "message": {"id": mid, "model": model, "usage": {
                "input_tokens": i, "output_tokens": o, "cache_creation_input_tokens": cw,
                "cache_read_input_tokens": cr}}}) + "\n"

        _write(os.path.join(folder, "s1.jsonl"),
               record("m1", "claude-opus-x", 1, 5, 100, 0) + record("m1", "claude-opus-x", 1, 50, 100, 0)
               + record("m2", "claude-opus-x", 2, 20, 0, 100) + record("m3", "<synthetic>", 0, 0)
               + "not json\n" + record("u1", "claude-opus-x", 9, 9, kind="user"))
        sub = os.path.join(folder, "s1", "subagents")
        _write(os.path.join(sub, "agent-aaa.jsonl"), record("a1", "claude-sonnet-x", 3, 30, 10, 10))
        _write(os.path.join(sub, "agent-aaa.meta.json"), json.dumps({"agentType": "murmuration:explorer"}))
        _write(os.path.join(sub, "agent-bbb.jsonl"), record("b1", "claude-sonnet-x", 4, 40, 0, 0))
        _write(os.path.join(sub, "agent-bbb.meta.json"), json.dumps({"agentType": "murmuration:explorer"}))
        rows, folders = spend(root)
        by = {(r["agent"], r["model"]): r for r in rows}
        main = by[("main thread", "claude-opus-x")]
        assert (main["messages"], main["input"], main["output"], main["cache_write"], main["cache_read"]) \
            == (2, 3, 70, 100, 100), main
        expl = by[("murmuration:explorer", "claude-sonnet-x")]
        assert (expl["runs"], expl["messages"], expl["input"], expl["output"]) == (2, 2, 7, 70), expl
        assert len(rows) == 2 and folders

        # The three outputs together.
        text = report(root)
        assert "## Open puzzles (1)" in text and "S-w01-explorer-3" in text and "S-w01-explorer-1 (" not in text
        assert "## Claims (14, 2 disputed)" in text
        assert "w01-author-12  WITHDRAWN (author: MEASURED)  [disputed, withdrawn]" in text
        assert "w01-author-1  MEASURED  [unverified]" in text
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
