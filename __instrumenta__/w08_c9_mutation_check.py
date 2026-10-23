#!/usr/bin/env python3
"""Check that `lab_status.py --selftest` can fail: from scripts/lab_status.py and a list of one-line mutations of the decision code, to one line per mutation (caught or SURVIVED), exit 1 if any survives.

    w08_c9_mutation_check.py     (about 10 seconds; no seeds, no network)
"""
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(REPO, "scripts", "lab_status.py")).read()
MUTATIONS = {
    "no raise check": ('        elif said < head:', '        elif False:'),
    "later verdicts ignored": ('live = latest(entries, applied["after"])', 'live = {}'),
    "decision lines leak into the verdict section": (
        '        elif decision is not None:\n            decision["lines"].append(line)',
        '        elif decision is not None:\n            decision["lines"].append(line)\n'
        '            if out["sections"]: out["sections"][-1][1].append(line)'),
    "any writer may decide": ('    if dec["name"].lower() != DECISION_WRITER:', '    if False:'),
    "decision over UNSUPPORTED applies": ('        elif "withdraw" in families:', '        elif False:'),
    "decision on an unverified claim applies": ('        elif not families & {"escalate", "lower"}:', '        elif False:'),
    "ref to a note that never names the claim": ('    if not any(names_claim(l, cid) for l in lines):', '    if False:'),
    "decision over OVERSTATED at the same label": ('        elif "lower" in families and said == head:', '        elif False:'),
    "ref id matched as a substring": ('    return re.search(r"(?<![\\w-])%s(?![\\w-])" % re.escape(cid), line) is not None', '    return cid in line'),
    "fenced block read as headings": ('        literal = fence is not None or toggled', '        literal = False'),
    "superseded by a missing claim file": ('        if root is not None and not os.path.isfile(os.path.join(root, "__pondus__", arg + ".md")):', '        if False:'),
    "superseded by itself": ('        if arg == cid:', '        if False:'),
    "restated without a statement": ('    if kind == "restated" and not any(statements):', '    if False:'),
    "several decision lines": ('    if len(found) != 1:', '    if len(found) < 1:'),
    "a later decision that fails replaces the earlier": ('        if decision:\n            applied = decision', '        applied = decision'),
}
survived = 0
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "lab_status.py")
    for name, (old, new) in MUTATIONS.items():
        assert SRC.count(old) == 1, "mutation target not found exactly once: " + name
        open(path, "w").write(SRC.replace(old, new))
        r = subprocess.run([sys.executable, path, "--selftest"], capture_output=True, text=True)
        print("%-52s %s" % (name, "caught" if r.returncode else "SURVIVED"))
        survived += r.returncode == 0
sys.exit(1 if survived else 0)
