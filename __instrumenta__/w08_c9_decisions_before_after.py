#!/usr/bin/env python3
"""Compute what a PI decision section does to lab_status on the real claims, from `__pondus__/` + `__statera__/` of a lab and proposed_decisions.json, to tables and before/after reports under an output folder.

    w08_c9_decisions_before_after.py [--lab DIR] [--old-script FILE] [--out DIR] [--specs FILE] [--quick]

Reads the lab (never writes it), copies `__pondus__/` and `__statera__/wave-*.md` into scratch folders, appends the proposed
`## decision: research-pi` sections to a copy, and runs
  1. the OLD lab_status.py (--old-script, default: `git show abe428f:scripts/lab_status.py`) on the copy without sections,
  2. the NEW lab_status.py (the one beside this script's repo) on the same copy and on the copy with sections,
  3. a probe: a blanket `stands at <the author's label>` appended to every claim, to see which claims the cap lets through.
It asserts: old and new report the same claim lines on the copy without sections; every claim without a proposed section has the
same file bytes and the same claim line after; the claims with a section keep their file bytes as a prefix.
--quick runs the same code on the decided claims and 4 others (no assertion on the other 62).
No seeds (deterministic); about 10 seconds; no network, no model tokens.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import lab_status  # noqa: E402

BASE = "abe428f"  # the commit this work branched from: the lab_status.py of "today"


def run_cli(script, project):
    out = subprocess.run([sys.executable, script, "--project", project], capture_output=True, text=True, check=True).stdout
    return claims_section(out)


def claims_section(text):
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("## Claims"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def claim_lines(section):
    """{claim id: [its line and its warning lines]} from the claims section."""
    out, cur = {}, None
    for l in section[1:]:
        if l.startswith("- "):
            cur = l[2:].split()[0]
            out[cur] = [l]
        elif l.strip() and cur:
            out[cur].append(l)
    return out


def block(cid, spec):
    return ("\n## decision: research-pi\n\ndecision: %s\nref: %s\nstatement: %s\nreason: %s\n"
            % (spec["decision"], spec["ref"], spec["statement"], spec["reason"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", default=REPO)
    ap.add_argument("--old-script")
    ap.add_argument("--out", default=os.path.join(REPO, "__reports__", "wave-08", "author-w08-9"))
    ap.add_argument("--specs", default=os.path.join(REPO, "__reports__", "wave-08", "author-w08-9", "proposed_decisions.json"))
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    specs = json.load(open(args.specs))
    os.makedirs(args.out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        old = args.old_script or os.path.join(tmp, "old_lab_status.py")
        if not args.old_script:
            with open(old, "w") as fh:
                fh.write(subprocess.run(["git", "-C", REPO, "show", "%s:scripts/lab_status.py" % BASE],
                                        capture_output=True, text=True, check=True).stdout)
        new = os.path.join(REPO, "scripts", "lab_status.py")
        ids = sorted((os.path.basename(p)[:-3] for p in glob.glob(os.path.join(args.lab, "__pondus__", "*.md"))),
                     key=lab_status.natural)
        if args.quick:
            ids = [c for c in ids if c in specs] + [c for c in ids if c not in specs][:4]
        before, after, probe = (os.path.join(tmp, n) for n in ("before", "after", "probe"))
        for d in (before, after, probe):
            os.makedirs(os.path.join(d, "__pondus__"))
            os.makedirs(os.path.join(d, "__statera__"))
            for w in glob.glob(os.path.join(args.lab, "__statera__", "wave-*.md")):
                shutil.copy(w, os.path.join(d, "__statera__"))
            for c in ids:
                shutil.copy(os.path.join(args.lab, "__pondus__", c + ".md"), os.path.join(d, "__pondus__"))
        # the probe's wave note names every claim, so the ref check passes and only the cap can refuse
        with open(os.path.join(probe, "__statera__", "wave-99.md"), "w") as fh:
            fh.write("\n".join("%s is named here" % c for c in ids) + "\n")
        for c, spec in specs.items():
            if c in ids:
                with open(os.path.join(after, "__pondus__", c + ".md"), "a") as fh:
                    fh.write(block(c, spec))
        for c in ids:
            label = lab_status.current_label(open(os.path.join(before, "__pondus__", c + ".md")).read())["label"]
            word = re.match(r"[*`_]*([A-Za-z]+)", label).group(1).upper()
            with open(os.path.join(probe, "__pondus__", c + ".md"), "a") as fh:
                fh.write("\n## decision: research-pi\n\ndecision: stands at %s\nref: __statera__/wave-99.md:%d\n"
                         % (word if word in lab_status.STRENGTH else "MEASURED", ids.index(c) + 1))
        old_before = claims_section_of(old, before)
        new_before = claims_section_of(new, before)
        new_after = claims_section_of(new, after)
        new_probe = claims_section_of(new, probe)
        # 1. the new tool reads a lab without decision sections as the old one did
        assert old_before == new_before, "new lab_status differs from the old one on claims without decisions"
        b, a = claim_lines(new_before), claim_lines(new_after)
        changed, same = [], []
        for c in ids:
            fb = open(os.path.join(before, "__pondus__", c + ".md"), "rb").read()
            fa = open(os.path.join(after, "__pondus__", c + ".md"), "rb").read()
            if c in specs:
                assert fa.startswith(fb) and fa != fb, c
                changed.append(c)
            else:
                assert fa == fb and a[c] == b[c], "unrelated claim changed: " + c
                same.append(c)
        # the diff of the two reports: exactly the 11 claim lines change, no warning appears, the header is the same
        import difflib
        diff = list(difflib.unified_diff(new_before, new_after, "before", "after", lineterm="", n=0))
        changed_lines = [l for l in diff if l.startswith("-") and not l.startswith("---")]
        assert new_before[0] == new_after[0], (new_before[0], new_after[0])
        if not args.quick:
            assert len(changed_lines) == len(specs) == 9, changed_lines
        with open(os.path.join(args.out, "before_after.diff"), "w") as fh:
            fh.write("\n".join(diff) + "\n")
        # raise probe: `stands at CHECKED` (one step above MEASURED) on the 11, with a ref that resolves
        raise_dir = os.path.join(tmp, "raise")
        shutil.copytree(before, raise_dir)
        shutil.copy(os.path.join(probe, "__statera__", "wave-99.md"), os.path.join(raise_dir, "__statera__"))
        for c in specs:
            if c in ids:
                with open(os.path.join(raise_dir, "__pondus__", c + ".md"), "a") as fh:
                    fh.write("\n## decision: research-pi\n\ndecision: stands at CHECKED\nref: __statera__/wave-99.md:%d\n" % (ids.index(c) + 1))
        r = claim_lines(claims_section_of(new, raise_dir))
        raise_refused = [c for c in specs if c in ids and r[c][0] == b[c][0]
                         and any("raises the label from MEASURED to CHECKED" in w for w in r[c][1:])]
        assert len(raise_refused) == len([c for c in specs if c in ids]), "a raising decision was applied"
        # 2. tables
        with open(os.path.join(args.out, "before.txt"), "w") as fh:
            fh.write("\n".join(new_before) + "\n")
        with open(os.path.join(args.out, "after.txt"), "w") as fh:
            fh.write("\n".join(new_after) + "\n")
        with open(os.path.join(args.out, "probe_blanket_stands.txt"), "w") as fh:
            fh.write("\n".join(new_probe) + "\n")
        with open(os.path.join(args.out, "proposed_decision_sections.md"), "w") as fh:
            fh.write("# Proposed decision sections (append each to its claim file with a shell append)\n\n"
                     "Each block below is appended as is. Written by author-w08-9 for the PI; not applied to any real claim file.\n\n")
            for c in specs:
                fh.write("## %s\n\n```markdown%s```\n\n" % (c, block(c, specs[c])))
        rows = []
        for c in specs:
            if c not in ids:
                continue
            ref_path, ref_line = specs[c]["ref"].rsplit(":", 1)
            line = open(os.path.join(args.lab, ref_path), encoding="utf-8").read().splitlines()[int(ref_line) - 1]
            rows.append((c, b[c][0][2:].split("  ", 1)[1].split("  <-")[0], a[c][0][2:].split("  ", 1)[1].split("  <-")[0],
                         "%s" % specs[c]["ref"], line.strip()[:110], specs[c]["decision"]))
        with open(os.path.join(args.out, "decisions_table.md"), "w") as fh:
            fh.write("| claim | state today | state with the proposed section | wave-note line | text of that line (first 110 characters) | proposed `decision:` |\n"
                     "|:--|:--|:--|:--|:--|:--|\n")
            for r in rows:
                fh.write("| %s | %s | %s | `%s` | %s | `%s` |\n" % tuple(x.replace("|", "\\|") for x in r))
        # 3. the probe: which claims does a blanket `stands at <label>` get through
        p = claim_lines(new_probe)
        applied = [c for c in ids if "[PI decision:" in p[c][0]]
        refused = [c for c in ids if c not in applied]
        kinds = {}  # the state before supersession is applied: what the verdicts alone say
        for c in ids:
            state = lab_status.current_label(open(os.path.join(before, "__pondus__", c + ".md")).read())["current"]
            state = re.sub(r"(unverified|below) .*", r"\1 <LABEL>", state) if state.startswith(("unverified", "below")) else \
                ("<LABEL>" if state in lab_status.LABELS or state.split(" ")[0] in lab_status.LABELS and "(" not in state else state)
            kinds.setdefault(state, []).append(c in applied)
        with open(os.path.join(args.out, "probe_summary.txt"), "w") as fh:
            fh.write("blanket `stands at <author's label>` appended to %d real claims (probe copy, not the lab)\n" % len(ids))
            fh.write("applied: %d  %s\nrefused: %d\n" % (len(applied), " ".join(applied), len(refused)))
            fh.write("raise probe: `stands at CHECKED` (above MEASURED) on the %d claims with a proposed section: refused %d, "
                     "state unchanged, warning 'raises the label from MEASURED to CHECKED'\n" % (len(raise_refused), len(raise_refused)))
            for k, v in sorted(kinds.items()):
                fh.write("  state today %-34s applied %d of %d\n" % (k, sum(v), len(v)))
        print("claims %d; sections added to %d; unchanged and identical %d; old == new on the copy without sections"
              % (len(ids), len(changed), len(same)))
        print(open(os.path.join(args.out, "probe_summary.txt")).read())
        print(open(os.path.join(args.out, "decisions_table.md")).read())


def claims_section_of(script, project):
    return run_cli(script, project)


if __name__ == "__main__":
    main()
