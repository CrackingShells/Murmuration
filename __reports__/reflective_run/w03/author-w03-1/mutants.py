#!/usr/bin/env python3
"""Mutation check of scripts/budget.py's selftest: each mutant changes one behaviour of the script; the selftest must fail on it.
usage: python3 -I mutants.py     Prints one line per mutant and a last line `N mutants, M survive`. Stdlib only; about 2 s per mutant."""
import os, shutil, subprocess, sys, tempfile
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
SRC = open(os.path.join(W, "scripts", "budget.py")).read()
M = [
 ("schedule has only 0.8", "SCHEDULE = (0.5, 0.75, 0.875, 0.9375)", "SCHEDULE = (0.8,)"),
 ("0.875 becomes 0.85", "SCHEDULE = (0.5, 0.75, 0.875, 0.9375)", "SCHEDULE = (0.5, 0.75, 0.85, 0.9375)"),
 ("the sentence from 1.1, not 1.0", "OVER_AT, HARD_AT = 1.0, 1.5", "OVER_AT, HARD_AT = 1.1, 1.5"),
 ("ceiling at 2.0", "OVER_AT, HARD_AT = 1.0, 1.5", "OVER_AT, HARD_AT = 1.0, 2.0"),
 ("the sentence below 1.0 too", 'OVER_SENTENCE if frac >= OVER_AT else ""', 'OVER_SENTENCE if True else ""'),
 ("one note per skipped threshold", 'st["k"] = n\n        save_state', 'st["k"] += 1\n        save_state'),
 ("no dedupe of the block per batch", 'and st["ceil_req"] != seen["requests"]:', ':'),
 ("PostToolBatch also speaks at the ceiling", 'if frac >= HARD_AT and st["ceil_req"] == seen["requests"]:', 'if False:'),
 ("no file lock", "import fcntl\nexcept ImportError:", "raise ImportError\nexcept ImportError:"),
 ("a batch with the hand-back gets a note", 'if "SubagentHandback" in calls:', 'if False:'),
 ("the hand-back call can be blocked", 'event.get("tool_name") != "SubagentHandback" and frac >= HARD_AT', 'frac >= HARD_AT'),
 ("raise adds to the old limit only", 'st["B"] = max(st["B"], used_at) + r["x"]', 'st["B"] = st["B"] + r["x"]'),
 ("time raise adds to the old limit only", 'st["T"] = max(st["T"], mins_at) + r["t"]', 'st["T"] = st["T"] + r["t"]'),
 ("schedule not restarted after a raise", 'st["k"] = due(frac)   # the schedule restarts above the new fraction', 'pass'),
 ("the idle gap counts as active time", 'st.update(run_start=now, run_open=True, last_seen=now)\n        save_state', 'st.update(run_open=True, last_seen=now)\n        save_state'),
 ("any origin raises", '(origin or {}).get("kind") == "coordinator"', 'True'),
 ("a peer's message to a running worker raises", 'text, origin = att.get("prompt") if isinstance(att.get("prompt"), str) else None, att.get("origin")', 'text, origin = att.get("prompt") if isinstance(att.get("prompt"), str) else None, {"kind": "coordinator"}'),
 ("a message to a running worker is not read", 'elif att.get("type") == "queued_command":', 'elif False:'),
 ("the later claimant of a mixed pair is not warned", 'json.dump(dict(r, ambiguous=True), fh)', 'json.dump(r, fh)'),
 ("a tool result raises", 'if any(b.get("type") == "tool_result" for b in blocks):', 'if False:'),
 ("100 percent shown below 1.0", "return min(p, 99) if frac < 1.0 else max(p, 100)", "return p"),
 ("USD with one decimal", '"Spent %.2f of USD %.2f', '"Spent %.1f of USD %.2f'),
 ("a figure below the floor is not logged", "if value is not None and value < floor:", "if False:"),
 ("the backstop after one block", "HALT_AFTER = 3", "HALT_AFTER = 1"),
 ("no ceiling block", 'return {"decision": "block", "reason": stop_text(used, st["B"], mins, st["T"])}', 'return None'),
 ("the check on the wrong event name", 'return reply(kind, additionalContext=note_text(used, st["B"], mins, st["T"], frac))', 'return reply("PostToolUse", additionalContext=note_text(used, st["B"], mins, st["T"], frac))'),
 ("the time budget ignored", "return used, mins, usd_frac, t_frac, max(usd_frac, t_frac), which", "return used, mins, usd_frac, t_frac, usd_frac, which"),
 ("a plain resume restarts the baseline", 'st.update(run_start=now, run_open=True, last_seen=now)\n        save_state', 'st.update(run_start=now, run_open=True, last_seen=now, base=seen["usd"] if seen else 0)\n        save_state'),
 ("the brief's lines do not win over the dispatch record", 'if not st["brief_read"]:', 'if False:'),
]
bad = 0
for name, old, new in M:
    if SRC.count(old) != 1:
        print("MUTANT NOT APPLICABLE (%d matches): %s" % (SRC.count(old), name)); bad += 1; continue
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "scripts")); os.makedirs(os.path.join(tmp, "hooks"))
        for f in ("handback.py", "lab_status.py"):
            shutil.copy(os.path.join(W, "scripts", f), os.path.join(tmp, "scripts", f))
        shutil.copy(os.path.join(W, "hooks", "hooks.json"), os.path.join(tmp, "hooks", "hooks.json"))
        open(os.path.join(tmp, "scripts", "budget.py"), "w").write(SRC.replace(old, new))
        r = subprocess.run([sys.executable, os.path.join(tmp, "scripts", "budget.py"), "--selftest"], capture_output=True, text=True)
    killed = r.returncode != 0
    print("%s  %s" % ("killed  " if killed else "SURVIVES", name))
    bad += not killed
print("%d mutants, %d survive" % (len(M), bad))
sys.exit(1 if bad else 0)
