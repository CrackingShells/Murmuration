#!/usr/bin/env python3
"""Runs the author agent headless on a one-line computation in a lab that already holds scripts, REPS times per wording, and tallies what it did with its tools; input: a scratch folder (lab, backup, two plugin exports), output: a table and a JSON file.

    python3 -I author_probe_runs.py SCRATCH REPS [--variant-file FILE]

SCRATCH holds `export/` (the plugin), `lab1/` (the lab, with its `.colgrep` index) and `lab1-after-run1/`
(the lab's `__instrumenta__/` as it should be at the start of each run). Variant B is `export/` with the
paragraph of `agents/author.md` that starts "Helper code is a file" replaced by the text of FILE.
Each run: `claude -p --agent murmuration:author`, USD 0.6 cap, seed none (the model samples). Stdlib only.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bash_practice_measure as m  # noqa: E402

PROMPT = ("Your name is author-w03-p. Compute by brute force the maximum number of distinct non-empty substrings over all "
          "binary strings of length n, for n = 1 to 14, and print the table.")


def variant_export(scratch, text):
    dst = os.path.join(scratch, "export-b")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(scratch, "export"), dst)
    path = os.path.join(dst, "agents", "author.md")
    s = open(path).read()
    start = s.index("Helper code is a file")
    end = s.index("A claim's `evidence:`")
    open(path, "w").write(s[:start] + text.rstrip("\n") + "\n" + s[end:])
    return dst


def one_run(scratch, plugin):
    lab = os.path.join(scratch, "lab1")
    shutil.rmtree(os.path.join(lab, "__instrumenta__"))
    shutil.copytree(os.path.join(scratch, "lab1-after-run1", "__instrumenta__"), os.path.join(lab, "__instrumenta__"))
    env = dict(os.environ, COLGREP_DATA_DIR=os.path.join(lab, ".colgrep"))
    out = subprocess.run(["claude", "-p", "--plugin-dir", plugin, "--agent", "murmuration:author", "--permission-mode", "auto",
                          "--max-budget-usd", "0.6", "--output-format", "stream-json", "--verbose", PROMPT],
                         cwd=lab, env=env, capture_output=True, text=True, timeout=400).stdout
    calls, cost = [], None
    for line in out.splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("type") == "result":
            cost = r.get("total_cost_usd")
        for b in (r.get("message") or {}).get("content", []) if r.get("type") == "assistant" and isinstance(r["message"].get("content"), list) else []:
            if b.get("type") == "tool_use":
                calls.append((b["name"], b.get("input", {})))
    row = {"calls": len(calls), "cost": cost, "sequence": [(t, json.dumps(i)[:140]) for t, i in calls], "colgrep": 0, "instr_listing": 0, "inline_py": 0, "wrote_instr": 0, "ran_existing": 0}
    for tool, inp in calls:
        if tool.startswith(m.COLGREP):
            row["colgrep"] += 1
        if tool == "Bash":
            cmd = inp.get("command", "")
            f = m.classify_bash(cmd)
            row["inline_py"] += int(f["inline_py"] and not any(k == "write" for k, _ in m.instrument_events(tool, inp)))
            if "ls" in cmd.split() and m.INSTR in cmd:
                row["instr_listing"] += 1
            for kind, _ in m.instrument_events(tool, inp):
                row["wrote_instr"] += int(kind == "write")
                row["ran_existing"] += int(kind == "use")
        if tool == "Write" and m.INSTR in str(inp.get("file_path", "")):
            row["wrote_instr"] += 1
        if tool == "Glob" and m.INSTR in json.dumps(inp):
            row["instr_listing"] += 1
    return row


def main(argv):
    scratch, reps = os.path.abspath(argv[0]), int(argv[1])
    plugins = {"A_shipped": os.path.join(scratch, "export")}
    if "--variant-file" in argv:
        plugins["B_variant"] = variant_export(scratch, open(argv[argv.index("--variant-file") + 1]).read())
    result = {}
    for name, plugin in plugins.items():
        result[name] = [one_run(scratch, plugin) for _ in range(reps)]
        for i, row in enumerate(result[name]):
            print(name, i + 1, row)
    with open(os.path.join(HERE, "author_probe_runs.json"), "w") as fh:
        json.dump(result, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
