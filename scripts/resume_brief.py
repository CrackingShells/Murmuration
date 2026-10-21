#!/usr/bin/env python3
"""Hand a resumed or compacted session what it needs to pick the work back up.

Runs as a SessionStart hook (matcher `resume|compact`). In an initialized lab project (one with a
`__statera__/` folder, found from the session's first recorded `cwd`, else the payload `cwd`, else
CLAUDE_PROJECT_DIR: see `user_words.project_root`) it prints, on stdout, the current wave note and the open puzzles; the
platform adds that output to the session's context. Anywhere else it prints nothing.

The current wave note is the highest-numbered `__statera__/wave-NN.md` without a `closed:` date,
else the latest. Open puzzles are those raised in `__scrupuli__/` that no closed wave note has
disposed of.

The script never fails the session: it always exits 0.

Usage:
    resume_brief.py              read a hook event from stdin, print the brief
    resume_brief.py --selftest   check the script on a temporary project
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_status  # noqa: E402  (a sibling script, imported for the puzzle and wave readers)
import user_words  # noqa: E402  (a sibling script: one rule for which lab a hook event belongs to)

project_root = user_words.project_root  # session's first cwd, else payload cwd, else CLAUDE_PROJECT_DIR; None outside a lab


def brief(root):
    """The brief for a project as text, or '' when the project is not a lab."""
    if not root or not os.path.isdir(os.path.join(root, "__statera__")):
        return ""
    out = ["# Lab brief (resumed session)", ""]
    wave = lab_status.current_wave(root)
    if wave:
        number, path, text = wave
        out += ["## Current wave note: %s" % os.path.relpath(path, root), "", text.rstrip(), ""]
    else:
        out += ["No wave note yet in `__statera__/`.", ""]
    puzzles = lab_status.open_puzzles(root)
    out.append("## Open puzzles (%d)" % len(puzzles))
    if puzzles:
        out.append("Each needs a disposition (followed or parked, with a reason) in a wave note at close.")
    for p in puzzles:
        text = p["text"] if len(p["text"]) <= 300 else p["text"][:297] + "..."
        out.append("- %s (%s): %s" % (p["id"], p["file"], text))
    warnings = lab_status.puzzle_warnings(root)
    if not puzzles:
        out.append("none among the puzzles that could be read: see the warnings below" if warnings else "none")
    out += ["! " + w for w in warnings]
    out += ["", "Claim labels and spend: run `/lab-status`."]
    return "\n".join(out)


def selftest():
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        def run(extra_env=None):
            env = dict(os.environ)
            env.pop("CLAUDE_PROJECT_DIR", None)
            env.update(extra_env or {})
            proc = subprocess.run([sys.executable, os.path.abspath(__file__)],
                                  input=json.dumps({"cwd": tmp, "source": "resume"}),
                                  capture_output=True, text=True, env=env)
            assert proc.returncode == 0, proc.stderr
            return proc.stdout

        assert run() == "", "must be silent outside a lab"
        os.makedirs(os.path.join(tmp, "__statera__"))
        out = run()
        assert "No wave note yet" in out and "none" in out
        with open(os.path.join(tmp, "__statera__", "wave-01.md"), "w") as fh:
            fh.write("# Wave 01\n\nopened: 2026-01-01\n\nWAVE ONE BODY\n\nclosed: 2026-01-05\n")
        with open(os.path.join(tmp, "__statera__", "wave-02.md"), "w") as fh:
            fh.write("# Wave 02\n\nopened: 2026-01-06\n\nWAVE TWO BODY\n")
        os.makedirs(os.path.join(tmp, "__scrupuli__"))
        with open(os.path.join(tmp, "__scrupuli__", "wave-01-explorer.md"), "w") as fh:
            fh.write("## S-w01-explorer-1\nodd rows\nrefs: a.csv\n\n## S-w01-explorer-2\nodd figure\nrefs: b.png\n")
        with open(os.path.join(tmp, "__statera__", "wave-01.md"), "a") as fh:
            fh.write("\n| S-w01-explorer-2 | parked: cosmetic |\n")
        out = run()
        assert "WAVE TWO BODY" in out and "WAVE ONE BODY" not in out, out
        assert "S-w01-explorer-1" in out and "odd rows" in out and "S-w01-explorer-2" not in out, out
        assert "! " not in out, out
        with open(os.path.join(tmp, "__scrupuli__", "wave-02-explorer-w02-a.md"), "w") as fh:
            fh.write("## Puzzle without an id\nbody\n\n## S-w02-explorer-w02-a-1\nsecond explorer\n")
        out = run()
        assert "S-w02-explorer-w02-a-1" in out and "! " in out and "'## Puzzle without an id' is not a puzzle id" in out, out
        with open(os.path.join(tmp, "__scrupuli__", "wave-02-explorer-w02-a.md"), "w") as fh:
            fh.write("1. numbered prose, no heading\n")
        os.remove(os.path.join(tmp, "__scrupuli__", "wave-01-explorer.md"))
        out = run()
        assert "none among the puzzles that could be read" in out and "has text but no `## S-wNN" in out, out
        # CLAUDE_PROJECT_DIR no longer outranks the payload cwd (the lab above cwd is found first)
        assert "WAVE TWO BODY" in run({"CLAUDE_PROJECT_DIR": os.path.join(tmp, "elsewhere")})
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input="not json",
                              capture_output=True, text=True, cwd=tmp, env={**os.environ, "CLAUDE_PROJECT_DIR": ""})
        assert proc.returncode == 0
    selftest_e0()
    print("PASS resume_brief")


def selftest_e0():
    """The E0 cases for a resumed session: the brief comes from the session's lab, not from CLAUDE_PROJECT_DIR or the shell's cwd."""
    import subprocess
    import tempfile

    def lab(path, body, git):
        os.makedirs(os.path.join(path, "__statera__"))
        with open(os.path.join(path, "__statera__", "wave-01.md"), "w") as fh:
            fh.write("# Wave 01\n\nopened: 2026-01-01\n\n%s\n" % body)
        if git == "dir":
            os.makedirs(os.path.join(path, ".git"))
        else:
            with open(os.path.join(path, ".git"), "w") as fh:
                fh.write("gitdir: /elsewhere/.git/worktrees/x\n")

    def session(path, cwds):
        with open(path, "w") as fh:
            fh.write(json.dumps({"type": "queue-operation"}) + "\n")
            for cwd in cwds:
                fh.write(json.dumps({"type": "user", "cwd": cwd}) + "\n")
        return path

    with tempfile.TemporaryDirectory() as tmp:
        main, wt, other = (os.path.join(tmp, d) for d in ("main", "wt", "other"))
        lab(main, "MAIN BODY", "dir")
        lab(wt, "WT BODY", "file")
        lab(other, "OTHER BODY", "dir")
        plain = os.path.join(tmp, "plain")
        os.makedirs(os.path.join(plain, ".git"))

        def run(cwd, transcript=None, project_dir=None, source="compact"):
            env = dict(os.environ)
            env.pop("CLAUDE_PROJECT_DIR", None)
            if project_dir:
                env["CLAUDE_PROJECT_DIR"] = project_dir
            event = {"cwd": cwd, "source": source}
            if transcript:
                event["transcript_path"] = transcript
            proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input=json.dumps(event),
                                  capture_output=True, text=True, env=env, cwd=tmp)
            assert proc.returncode == 0, proc.stderr
            return proc.stdout

        who = lambda out: sorted(w for w in ("MAIN BODY", "WT BODY", "OTHER BODY") if w in out)
        # Desktop worktree pair: CLAUDE_PROJECT_DIR = main checkout, session started in the worktree
        assert who(run(wt, session(os.path.join(tmp, "a"), [wt]), main)) == ["WT BODY"]
        assert who(run(wt, None, main)) == ["WT BODY"]  # no transcript path in the payload
        # the shell sits in another checkout when the session is compacted
        for moved in (main, other, plain):
            assert who(run(moved, session(os.path.join(tmp, "b"), [wt, moved]), main)) == ["WT BODY"], moved
        # started in main, shell now in the worktree
        assert who(run(wt, session(os.path.join(tmp, "c"), [main, wt]), main)) == ["MAIN BODY"]
        # headless start in a lab, with and without CLAUDE_PROJECT_DIR
        assert who(run(main, session(os.path.join(tmp, "d"), [main]))) == ["MAIN BODY"]
        assert who(run(main, session(os.path.join(tmp, "d"), [main]), main, "resume")) == ["MAIN BODY"]
        # no lab anywhere: silent
        assert run(plain, session(os.path.join(tmp, "e"), [plain]), plain) == ""
        assert run(plain) == ""
        assert run(plain, None, os.path.join(tmp, "nowhere")) == ""


def main():
    if "--selftest" in sys.argv[1:]:
        selftest()
        return 0
    try:
        raw = sys.stdin.read()
        try:
            event = json.loads(raw) if raw.strip() else {}
        except ValueError:
            event = {}
        text = brief(project_root(event))
        if text:
            print(text)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except AssertionError:
        raise
    except Exception:
        code = 0
    sys.exit(code)
