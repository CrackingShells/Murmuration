#!/usr/bin/env python3
"""Runs the Grep tool headless in a lab made by lab_init.py and lists which files holding a needle it returns; input: a scratch folder outside the worktree, output: ignore_grep_probe.json and a table.

    python3 -I ignore_grep_probe.py SCRATCH

The lab holds the needle in files under derived/, runs/, raw/, the saved hand-backs, a package.json, a requirements.txt and an instrument.
The model session loads only the project and local settings (`--setting-sources project,local`), so the colgrep plugin's
hook that denies Grep is not loaded and `--tools Grep` is the only tool (without the user settings the session has no Grep otherwise); the lab's `.ignore` is what is under test. COLGREP_DATA_DIR is inside SCRATCH.
Cost: one `claude -p` call, about USD 0.1. Stdlib only.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.join(HERE, "..", "..", "..", "..")
NEEDLE = "needle_alpha"
FILES = ["__instrumenta__/s.py", "derived/table.json", "derived/notes.txt", "package.json", "requirements.txt",
         "runs/run1.json", "raw/r.md", "__statera__/handbacks/author-1.md", "__reports__/w01/a/report.md", "generated/g.py"]
PROMPT = ("Make exactly one Grep call: pattern \"%s\", output_mode files_with_matches, no path, no glob. No other tools. "
          "Then print the files it returned, one per line." % NEEDLE)


def main(scratch):
    scratch = os.path.abspath(scratch)
    lab = os.path.join(scratch, "ignore_lab")
    shutil.rmtree(lab, ignore_errors=True)
    os.makedirs(lab)
    env = dict(os.environ, COLGREP_DATA_DIR=os.path.join(lab, ".colgrep"))
    subprocess.run(["python3", os.path.join(PLUGIN, "scripts", "lab_init.py"), "--project", lab], input="probe question", text=True,
                   capture_output=True, env=env, check=True)
    for rel in FILES:
        path = os.path.join(lab, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write("%s in %s\n" % (NEEDLE, rel))
    out = subprocess.run(["claude", "-p", "--setting-sources", "project,local", "--tools", "Grep", "--permission-mode", "auto", "--max-budget-usd", "0.4",
                          "--output-format", "stream-json", "--verbose", PROMPT], cwd=lab, env=env, capture_output=True, text=True, timeout=300).stdout
    result = {"ignore": open(os.path.join(lab, ".ignore")).read(), "grep_calls": [], "returned": None, "cost": None}
    ids = {}
    for line in out.splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        c = (r.get("message") or {}).get("content")
        if r.get("type") == "result":
            result["cost"] = r.get("total_cost_usd")
        if isinstance(c, list):
            for b in c:
                if b.get("type") == "tool_use":
                    result["grep_calls"].append((b["name"], b.get("input")))
                    ids[b["id"]] = b["name"]
                if b.get("type") == "tool_result" and ids.get(b.get("tool_use_id")) == "Grep":
                    result["returned"] = b.get("content")
    print(json.dumps(result, indent=1))
    with open(os.path.join(HERE, "ignore_grep_probe.json"), "w") as fh:
        json.dump(result, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
