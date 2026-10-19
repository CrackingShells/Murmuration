#!/usr/bin/env python3
"""Mutation check of scripts/budget.py and scripts/handback.py: each mutant must make that script's --selftest fail.

usage: python3 -I mutants.py [--scripts DIR]     (default: the shipped scripts/ of this worktree)
Stdlib only; no model calls; about 25 s."""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "..", "..", "..", "scripts")
if "--scripts" in sys.argv:
    SCRIPTS = sys.argv[sys.argv.index("--scripts") + 1]

MUTANTS = [
    # (script, label, old, new)
    ("budget.py", "note at 0.9 instead of 0.8", "NOTE_AT, STOP_AT, HARD_AT = 0.8, 1.0, 1.5", "NOTE_AT, STOP_AT, HARD_AT = 0.9, 1.0, 1.5"),
    ("budget.py", "stop at 1.2 instead of 1.0", "NOTE_AT, STOP_AT, HARD_AT = 0.8, 1.0, 1.5", "NOTE_AT, STOP_AT, HARD_AT = 0.8, 1.2, 1.5"),
    ("budget.py", "halt at 1.8 instead of 1.5", "NOTE_AT, STOP_AT, HARD_AT = 0.8, 1.0, 1.5", "NOTE_AT, STOP_AT, HARD_AT = 0.8, 1.0, 1.8"),
    ("budget.py", "the stop ends the run (continue false) instead of blocking", '{"decision": "block", "reason": stop_text(which, B, T)}', '{"continue": False, "stopReason": stop_text(which, B, T)}'),
    ("budget.py", "no backstop", "if frac >= HARD_AT and st[\"stops\"] >= HALT_AFTER:", "if False:"),
    ("budget.py", "backstop without the notice count", "HALT_AFTER = 3", "HALT_AFTER = 0"),
    ("budget.py", "note every time, not once", 'and not st["noted"]:', ":"),
    ("budget.py", "streamed records of one request add up", "old[k] = max(old[k], v)", "old[k] = old[k] + v"),
    ("budget.py", "no baseline for a resumed agent", 'base = seen["usd"] if seen else 0.0', "base = 0.0"),
    ("budget.py", "any agent type, not murmuration:*", 'return kind.split(":", 1)[1] if kind.startswith("murmuration:") and event.get("agent_id") else None', 'return kind.split(":")[-1] if event.get("agent_id") else None'),
    ("budget.py", "the hand-back call can be stopped", ' or event.get("tool_name") == "SubagentHandback"', ""),
    ("budget.py", "cache read priced 10x", '"claude-sonnet-5-5": (2.0, 10.0, 0.10,', '"claude-sonnet-5-5": (2.0, 10.0, 1.0,'),
    ("budget.py", "1 hour cache write priced as 5 minutes", 'req["cw1"] * p[4]', 'req["cw1"] * p[3]'),
    ("budget.py", "the brief's budget line is ignored", "if found and float(found.group(1)) > 0:", "if False:"),
    ("budget.py", "a later user message can set the budget", """if brief is None and '"user"' in line:""", """if '"user"' in line:"""),
    ("budget.py", "the backstop does not stop", '"continue": False, "stopReason": halt_text(which, B, T)', '"continue": True, "stopReason": halt_text(which, B, T)'),
    ("budget.py", "acts outside a lab (uses cwd)", "role, root = role_of(event), handback.lab_root(event)", 'role, root = role_of(event), handback.lab_root(event) or event.get("cwd")'),
    ("budget.py", "the 'resumed' flag is never set", "resumed=bool(old or seen)", "resumed=False"),
    ("budget.py", "synthetic records are priced as a model call", 'r["model"] != "<synthetic>" or r["in"] + r["out"] + r["cr"] + r["cw"]', "True"),
    ("budget.py", "no output estimate (recorded count only)", "CHARS_PER_TOKEN = 1.3", "CHARS_PER_TOKEN = 0"),
    ("budget.py", "the estimate replaces the recorded count", 'out=max(r["out"], int(sum(len(b) for b in r["blocks"]) / CHARS_PER_TOKEN) if CHARS_PER_TOKEN else 0)', 'out=int(sum(len(b) for b in r["blocks"]) / CHARS_PER_TOKEN)'),
    ("budget.py", "minutes counted as seconds", "elapsed / (60 * T)", "elapsed / T"),
    ("budget.py", "the time budget never decides", '(usd_frac, "USD") if usd_frac >= t_frac else (t_frac, "time")', '(usd_frac, "USD")'),
    ("budget.py", "the note always says USD", '(usd_frac, "USD") if usd_frac >= t_frac else (t_frac, "time")', '(max(usd_frac, t_frac), "USD")'),
    ("budget.py", "the brief's Time line is ignored", 'found = TIME_LINE.search(brief or "")\n    if found and float(found.group(1)) > 0:', 'found = TIME_LINE.search(brief or "")\n    if False:'),
    ("budget.py", "explorer time default 200", '"explorer": 20.0, "author": 20.0', '"explorer": 200.0, "author": 20.0'),
    ("budget.py", "the clock is not restarted on resume", 'start=now, noted=False, stops=0))\n        handback.log_line', 'start=(old or {}).get("start", now), noted=False, stops=0))\n        handback.log_line'),
    ("budget.py", "no t_frac in the log", "t_frac=round(t_frac, 4), T=T,", "T=T,"),
    ("handback.py", "deny on every hand-back, not once", "os.O_WRONLY | os.O_CREAT | os.O_EXCL", "os.O_WRONLY | os.O_CREAT"),
    ("handback.py", "deny every agent type", 'event.get("agent_type") != EXPLORER', "False"),
    ("handback.py", "a longer name counts as our report", r'(?<![a-z0-9])%s(?![a-z0-9])', "%s"),
    ("handback.py", "a report is never found", "return any(mine.search(", "return False and any(mine.search("),
    ("handback.py", "no .gitignore for the state folder", 'fh.write("*\\n")', 'fh.write("")'),
    ("handback.py", "deny is not logged", 'log_line(root, dict(event="deny"', 'dict(root, dict(event="deny"'),
    ("handback.py", "wrong convention path", '"wave-%s/"', '"w%s/"'),
    ("handback.py", "saving: a stop with no text is not recorded", 'status = "missing"', 'return None'),
    ("handback.py", "saving: dedup of the same text dropped", "if mine and mine[-1][\"sha\"] == sha and mine[-1][\"status\"] == status:", "if False:"),
]


def run(script, root):
    p = subprocess.run([sys.executable, "-I", os.path.join(root, script), "--selftest"], capture_output=True, text=True, timeout=120)
    return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1:] 


def main():
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        # -I drops the script folder from sys.path; the scripts add it themselves, so this is safe
        for script in ("budget.py", "handback.py"):
            rc, last = run(script, os.path.abspath(SCRIPTS))
            print("baseline %-11s rc=%d %s" % (script, rc, last))
            bad += rc != 0
        for i, (script, label, old, new) in enumerate(MUTANTS, 1):
            d = os.path.join(tmp, "m%d" % i)
            shutil.copytree(SCRIPTS, d, ignore=shutil.ignore_patterns("__pycache__"))
            src = open(os.path.join(d, script)).read()
            assert src.count(old) >= 1, "mutant %d does not apply: %s" % (i, label)
            open(os.path.join(d, script), "w").write(src.replace(old, new, 1))
            rc, last = run(script, d)
            ok = rc != 0
            print("mutant %2d %-11s %-52s %s" % (i, script, label, "killed" if ok else "SURVIVED"))
            bad += not ok
    print("%d mutants, %d problem(s)" % (len(MUTANTS), bad))
    return 1 if bad else 0


sys.exit(main())
