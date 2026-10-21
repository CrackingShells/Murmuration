#!/usr/bin/env python3
"""The selftest of lab_status.py, kept out of it so that resume_brief.py, which imports lab_status, does not compile it. Run: `python3 scripts/lab_status.py --selftest`."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lab_status  # noqa: E402
from lab_status import *  # noqa: E402,F401,F403  (the names the checks use)
from lab_status import __doc__ as _unused  # noqa: E402,F401


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

        # No transcripts: say so.
        os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(tmp, "empty")
        assert "no transcripts found" in report(root)
    print("PASS lab_status")
