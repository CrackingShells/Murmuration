#!/usr/bin/env python3
"""Lists which files of a sample lab colgrep indexes under each ignore setup; input: none (builds the lab in a temp folder, keeps its index in the same folder), output: one table of file x setup.

    python3 -I colgrep_scope_probe.py [--json out.json]

Setups: a git repo with nothing; a git repo with .gitignore; no git with .gitignore; no git with .ignore (the
block `scripts/lab_init.py` writes); no git with .colgrepignore. Every search runs with COLGREP_DATA_DIR set
inside the temp folder, so the user's index store is not touched. Needs `colgrep` on PATH.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
import lab_init  # noqa: E402  (the block that /lab writes)

TEXT = "Walks transcript files and tallies tool calls."
FILES = {
    "__instrumenta__/walk_transcripts.py": '"""%s"""\ndef walk(): pass\n' % TEXT,
    "__pondus__/w01-c1.md": "# w01-c1\n%s\n" % TEXT,
    "__statera__/wave-01.md": "# Wave 01\n%s\n" % TEXT,
    "__statera__/handbacks/author-x.md": "# hand-back copy\n%s\n" % TEXT,
    "__reports__/w01/a/00-findings_v0.md": "# findings\n%s\n" % TEXT,
    "__reports__/w01/a/walk.sh": "#!/bin/sh\n# %s\nfor f in *.x; do echo $f; done\n" % TEXT,
    "__reports__/w01/a/rows.json": json.dumps({"note": TEXT}) + "\n",
    "__reports__/w01/a/run.txt": "stdout of a run: %s\n" % TEXT,
    "__reports__/w01/a/run.jsonl": json.dumps({"note": TEXT}) + "\n",
    "__reports__/w01/a/table.csv": "n,note\n1,%s\n" % TEXT.replace(",", ""),
    "data/raw/notes.md": "# raw run notes\n%s\n" % TEXT,
    "data/raw/run_script.py": '"""%s"""\ndef raw(): pass\n' % TEXT,
    "data/derived/derive.py": '"""%s"""\ndef derived(): pass\n' % TEXT,
    "gen/generated.py": '"""generated: %s"""\ndef gen(): pass\n' % TEXT,
    "generated/g.py": '"""generated: %s"""\ndef gen2(): pass\n' % TEXT,
    "build/b.py": '"""build output: %s"""\ndef b(): pass\n' % TEXT,
    "dist/bundle.js": "// compiled bundle: %s\nfunction w(){}\n" % TEXT,
    "target/t.py": '"""%s"""\ndef t(): pass\n' % TEXT,
    "out/o.py": '"""%s"""\ndef o(): pass\n' % TEXT,
    "__pycache__/walk.cpython-312.pyc": TEXT + "\n",
    ".hidden/h.py": '"""%s"""\ndef h(): pass\n' % TEXT,
    "__statera__/.harness/n.md": "# harness note\n%s\n" % TEXT,
}
SETUPS = [
    ("git, no ignore file", True, {}),
    ("git + .gitignore", True, {".gitignore": "gen/\ndata/\n__statera__/handbacks/\n"}),
    ("no git + .gitignore", False, {".gitignore": "gen/\ndata/\n__statera__/handbacks/\n"}),
    ("no git + .ignore (lab block)", False, {".ignore": lab_init.IGNORE_BLOCK}),
    ("no git + .colgrepignore", False, {".colgrepignore": "gen/\ndata/\n__statera__/handbacks/\n"}),
]


def indexed(folder, data_dir):
    env = dict(os.environ, COLGREP_DATA_DIR=data_dir)
    out = subprocess.run(["colgrep", "search", TEXT, "-k", "1000", "-l", "--color", "never", folder],
                         capture_output=True, text=True, env=env).stdout
    real = os.path.realpath(folder)
    return {os.path.relpath(x.strip(), real) for x in out.splitlines()
            if x.strip() and not x.startswith(("📂", "🤖"))}


def main(argv):
    if not shutil.which("colgrep"):
        print("colgrep is not installed")
        return 1
    result = {}
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = os.path.join(tmp, "colgrep-data")
        for i, (label, git, extra) in enumerate(SETUPS):
            folder = os.path.join(tmp, "lab%d" % i)
            for rel, text in dict(FILES, **extra).items():
                path = os.path.join(folder, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as fh:
                    fh.write(text)
            if git:
                subprocess.run(["git", "init", "-q", folder], check=True)
            result[label] = indexed(folder, data_dir)
    labels = [s[0] for s in SETUPS]
    print("%-40s" % "file" + " ".join("%-3d" % (i + 1) for i in range(len(labels))))
    for rel in FILES:
        print("%-40s" % rel + " ".join("%-3s" % ("x" if rel in result[l] else ".") for l in labels))
    for i, l in enumerate(labels):
        print("%d = %s: %d of %d files indexed" % (i + 1, l, len([r for r in result[l] if r in FILES]), len(FILES)))
    if "--json" in argv:
        with open(argv[argv.index("--json") + 1], "w") as fh:
            json.dump({k: sorted(v) for k, v in result.items()}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
