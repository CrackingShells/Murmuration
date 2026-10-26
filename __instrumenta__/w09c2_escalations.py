# Finds the hand-backs that carry an ESCALATE verdict in the PI main-thread transcripts (via w09d_turns.parse) and, for each, the PI turns up to the next 8 that state a decision about that claim and whether a claim file (__pondus__/<id>.md) was opened between the hand-back and that decision; prints one block per escalation hand-back for hand-checking.
# usage: python3 -I w09c2_escalations.py <label>=<transcript.jsonl> [...]   (same pairs as w09d_turns.py)
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w09d_turns import parse, analyse, hhmm

ESC = re.compile(r"\bESCALATE\b")
DEC = re.compile(r"(my decision|i decide|i('| a)m deciding|decision:|decided|i('ll| will) decide|## decision: research-pi|restate|supersed)", re.I)

def claim_ids(body):
    return sorted(set(re.findall(r"\bw\d\d-c\d+\b", body)))

def opens_claim(tn, ids):
    hits = []
    for st in tn["steps"]:
        for c in st["calls"]:
            if c["kind"] in ("read-whole", "read-part", "bash-view", "bash-query") or c.get("reads_too"):
                for p in c["paths"]:
                    if "__pondus__" in p and (not ids or any(i in p for i in ids)):
                        hits.append(os.path.basename(p))
    return hits

def writes_decision(tn):
    for st in tn["steps"]:
        for c in st["calls"]:
            if c["kind"] == "write" and "__pondus__" in c.get("key", "") + " ".join(c["paths"]) and "decision: research-pi" in c.get("cmd", ""):
                return True
    return False

for arg in sys.argv[1:]:
    label, path = arg.split("=", 1)
    turns, *_ = parse(label, path)
    analyse(turns)
    for i, tn in enumerate(turns):
        for g in tn["triggers"]:
            if g["kind"] == "B" and ESC.search(g.get("body") or ""):
                body = g["body"]
                # keep only hand-backs whose verdict line says ESCALATE (not a mention such as "no ESCALATE needed")
                m = re.search(r"(verdict[: ]+|\*\*)ESCALATE|ESCALATE\b", body)
                ids = claim_ids(body)
                print("=== %s T%03d %s from=%s ids=%s  (first ESCALATE context: %r)" % (label, tn["n"], hhmm(tn["t0"]), g.get("agent"), ids, body[max(0, m.start() - 60):m.start() + 80].replace("\n", " ")))
                if (g.get("agent") or "").startswith(("reproducer", "proof-adversary")) and ids:
                    cid = [i for i in ids if i in (g.get("head") or "")] or ids[:1]
                    ear = [(t3["n"], hhmm(t3["t0"])) for t3 in turns[:i + 1] if opens_claim(t3, cid[:1])]
                    print("   VERIFIER ESCALATION on %s: turns up to and including the wake that opened __pondus__/%s*: %s" % (cid[0], cid[0], ear or "none"))
                opened = opens_claim(tn, ids)
                print("   wake turn: opens claim file(s): %s ; raw_here=%s" % (opened or "none", tn["raw_here"]))
                for j in range(i, min(i + 9, len(turns))):
                    t2 = turns[j]
                    txt = " ".join(" ".join(s["text"]) for s in t2["steps"])
                    dec = bool(DEC.search(txt)) and any(x in txt for x in ids)
                    if j > i:
                        oc = opens_claim(t2, ids)
                        if oc: print("   T%03d opens claim file(s): %s" % (t2["n"], oc))
                    if dec or writes_decision(t2):
                        mm = DEC.search(txt)
                        print("   T%03d %s decision-text=%s writes-decision-section=%s: %r" % (t2["n"], hhmm(t2["t0"]), dec, writes_decision(t2), re.sub(r"\s+", " ", txt[max(0, mm.start() - 80):mm.start() + 160]) if mm else ""))
