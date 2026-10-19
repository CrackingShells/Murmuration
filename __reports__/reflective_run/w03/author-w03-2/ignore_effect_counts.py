#!/usr/bin/env python3
"""Counts the files colgrep lists for a copy of a folder before and after the lab's .ignore block, by kind; input: the two file lists, output: ignore_effect_counts.json.

    cp -R __reports__/reflective_run SCRATCH/wtcopy/ ; cd SCRATCH/wtcopy      (no .git there)
    export COLGREP_DATA_DIR=SCRATCH/wtcopy-index
    python3 -c "import sys; sys.path.insert(0,'<worktree>/scripts'); import lab_init; open('.ignore','w').write(lab_init.IGNORE_BLOCK)"
    colgrep search "script or note" -k 100000 -l --color never . > SCRATCH/wtcopy_indexed_after.txt ; rm .ignore
    colgrep search "script or note" -k 100000 -l --color never . > SCRATCH/wtcopy_indexed_before.txt
    python3 -I ignore_effect_counts.py SCRATCH
"""
import collections
import json
import os
import re
import sys


def kind(p):
    if "/handbacks/" in p:
        return "handbacks copy"
    if re.search(r"(^|/)(raw|derived|runs|generated)/", p):
        return "raw/derived/runs/generated dir"
    name = p.rsplit("/", 1)[-1]
    return name.rsplit(".", 1)[-1] if "." in name else "none"


def main(scratch):
    out = {}
    for n in ("before", "after"):
        lines = [x.strip() for x in open(os.path.join(scratch, "wtcopy_indexed_%s.txt" % n)) if x.strip() and not x.startswith(("📂", "🤖"))]
        out[n] = {"files": len(lines), "by_kind": dict(collections.Counter(kind(p) for p in lines).most_common())}
    out["note"] = "a non-git copy of __reports__/reflective_run, files listed by colgrep; after = with the .ignore block of lab_init.py at its root"
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore_effect_counts.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
