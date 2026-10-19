#!/usr/bin/env python3
"""explorer-w01-b: hand-coded tables. The codes below were assigned by reading the first lines of the
hand-backs (handbacks.csv: first_line) and the PI's first text and tool targets (reactions.csv); they are
NOT script output. The script only joins the codes to the measured columns and prints the counts.
Run: python3 -I coded_tables.py   (after extract_comm.py and analyze.py)
"""
import csv, collections

# first-line class of each agent hand-back, keyed by (session, delivery_line)
# STATUS = opens with done/pass/blocked-style status; RESULT = opens with the headline finding;
# PATH = opens with the report path only; HEADING = opens with a title / report body
FIRST = {}
def put(s, lines, cls):
    for l in lines: FIRST[(s, str(l))] = cls
put("genesis", [229, 295, 367, 557, 615, 674, 701, 746, 774], "STATUS")
put("genesis", [426, 583, 720, 1644], "RESULT")
put("design", [1567, 1632, 1726, 1928, 1997, 2090, 2127, 2157], "STATUS")
put("design", [1165, 1173, 1717, 1903], "RESULT")
put("design", [1048, 1067, 1284], "PATH")
put("design", [1255, 1580], "HEADING")

# PI independently checked something (own computation, raw-evidence read, fetch) BEFORE relaying or acting
OWN_CHECK = {("genesis", "295"), ("genesis", "367"), ("genesis", "557"), ("genesis", "583"), ("genesis", "774"),
             ("genesis", "1644"), ("design", "1048"), ("design", "1567"), ("design", "1632"), ("design", "1726")}

hb = list(csv.DictReader(open("handbacks.csv")))
rx = {(r["session"], r["delivery_line"]): r for r in csv.DictReader(open("reactions.csv"))}
rows = []
for h in hb:
    k = (h["session"], h["delivery_line"])
    r = rx.get(k, {})
    rows.append(dict(session=h["session"], delivery_line=h["delivery_line"], agent=h["agent"], description=h["description"],
                     words=h["words"], brief_limit=h["brief_limit"], harness_flag=h["harness_flag"],
                     first_line_class=FIRST.get(k, "?"),
                     pi_followed_pointer=int(bool(r.get("followed_pointer_at_step"))),
                     pi_sent_message=int(bool(r.get("sent_to"))), pi_dispatched_next=int(int(r.get("spawned_after") or 0) > 0),
                     pi_own_check=int(k in OWN_CHECK), pi_mentions_harness_flag=0 if h["harness_flag"] == "1" else ""))
with open("handbacks_coded.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
n = len(rows)
print("N hand-backs", n)
print("first-line class:", dict(collections.Counter(r["first_line_class"] for r in rows)))
for c in ("pi_followed_pointer", "pi_sent_message", "pi_dispatched_next", "pi_own_check"):
    print(c, sum(r[c] for r in rows), "of", n)
print("none of the four:", sum(1 for r in rows if not any(r[c] for c in ("pi_followed_pointer", "pi_sent_message", "pi_dispatched_next", "pi_own_check"))))

# follow-up messages (SendMessage, PI -> agent), hand-coded purpose
FU = [
 ("genesis", 319, "a04ebecba85274ac9", "new_input", "PI-verified fact from another agent (count law) relayed to the atlas agent"),
 ("genesis", 346, "a04ebecba85274ac9", "scope_addition", "compositional completeness added after the PI defined it in the framing"),
 ("genesis", 398, "a04ebecba85274ac9", "new_assignment", "atlas accepted; next roadmap node assigned to the same warm agent"),
 ("genesis", 677, "a4ad7c71400d5bc3b", "correction", "verifier found overstated rows and 2 number slips; PI relays with fix instructions and file-naming rule"),
 ("genesis", 678, "a3f3fa3fc477f4cd5", "correction", "verifier found 4 number slips; PI relays"),
 ("design", 1616, "aff153770869d2a23", "unblock", "CLI logged in; rerun the model-backed probes"),
 ("design", 1880, "aff72ee628b60b2fb", "brief_omission", "22 s after the brief: branch and commit rules the brief lacked (the human had just said so)"),
 ("design", 2013, "aff72ee628b60b2fb", "correction", "script fixes from cold review round 1"),
 ("design", 2039, "aff72ee628b60b2fb", "spec_change", "id format changed in SKILL.md after the brief"),
 ("design", 2131, "aff72ee628b60b2fb", "correction", "round 2 of fixes, new worktree path"),
]
import json, re, os, sys
sys.path.insert(0, ".")
d = {(r["session"], int(r["line"])): r for r in csv.DictReader(open("dispatches.csv"))}
with open("followups.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["session", "line", "agent", "purpose", "note", "chars", "ts"])
    for s, l, a, p, note in FU:
        r = d.get((s, l), {})
        w.writerow([s, l, a, p, note, r.get("chars", ""), r.get("ts", "")])
print("follow-ups by purpose:", dict(collections.Counter(p for _, _, _, p, _ in FU)))
