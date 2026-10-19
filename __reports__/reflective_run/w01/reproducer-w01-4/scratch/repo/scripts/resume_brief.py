#!/usr/bin/env python3
"""Hand a resumed or compacted session what it needs to pick the work back up.

Runs as a SessionStart hook (matcher `resume|compact`). In an initialized lab project (one with a
`__statera__/` folder) it prints, on stdout, the current wave note and the open puzzles; the
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
import user_words  # noqa: E402  (a sibling script, imported for lab_root)


def project_root(event_cwd=None):
    """The lab the session works in (see user_words.lab_root), else the project directory as before."""
    return user_words.lab_root(event_cwd) or os.environ.get("CLAUDE_PROJECT_DIR") or event_cwd or os.getcwd()


def brief(root):
    """The brief for a project as text, or '' when the project is not a lab."""
    if not os.path.isdir(os.path.join(root, "__statera__")):
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
        # the lab at the hook's cwd wins over CLAUDE_PROJECT_DIR (a worktree session started in another checkout)
        assert "WAVE TWO BODY" in run({"CLAUDE_PROJECT_DIR": os.path.join(tmp, "elsewhere")})
        os.makedirs(os.path.join(tmp, "wt"))
        with open(os.path.join(tmp, "wt", ".git"), "w") as fh:
            fh.write("gitdir: x\n")
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)],
                              input=json.dumps({"cwd": os.path.join(tmp, "wt"), "source": "resume"}),
                              capture_output=True, text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": tmp})
        assert "WAVE TWO BODY" in proc.stdout, "worktree without a lab falls back to CLAUDE_PROJECT_DIR"
        os.makedirs(os.path.join(tmp, "wt", "__statera__"))
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)],
                              input=json.dumps({"cwd": os.path.join(tmp, "wt"), "source": "resume"}),
                              capture_output=True, text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": tmp})
        assert "WAVE TWO BODY" not in proc.stdout and "No wave note yet" in proc.stdout, proc.stdout
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input="not json",
                              capture_output=True, text=True, cwd=tmp, env={**os.environ, "CLAUDE_PROJECT_DIR": ""})
        assert proc.returncode == 0
    print("PASS resume_brief")


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
        text = brief(project_root(event.get("cwd") if isinstance(event, dict) else None))
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
