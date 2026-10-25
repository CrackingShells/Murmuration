# Cuts, for each claim file with a `verdict: ESCALATE` line, the PI turns around the escalating verifier's hand-back (via w09d_turns.parse) and the claim file as it stood at that verdict; inputs: <label>=<transcript.jsonl> pairs, __pondus__/*.md; outputs: <outdir>/wakes.json (per claim: triggers naming the verifier or the claim, hand-back body, PI text and claim-file opens of the next 3 turns) and <outdir>/claim_at_verdict/<id>.md (the file cut at the end of the escalating section, i.e. at the next level-2 heading, so before any PI decision section; reason: lines after the verdict line included).
# usage: python3 -I w09h_extract.py <outdir> <label>=<transcript.jsonl> [...]
import sys, os, re, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w09d_turns import parse, analyse, hhmm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1]
os.makedirs(os.path.join(out, "claim_at_verdict"), exist_ok=True)

def cut(path):
    """(id, verifier, text up to and including the escalating verdict line)"""
    lines = open(path, encoding="utf-8").read().split("\n")
    cid = os.path.basename(path)[:-3]
    sec = None; fence = False; last = None
    for i, l in enumerate(lines):
        if l.startswith(("```", "~~~")): fence = not fence
        if fence: continue
        if l.startswith("## verdict:"): sec = l.split(":", 1)[1].strip()
        if l.startswith("verdict: ESCALATE"): last = (i, sec)
    if last is None: return None
    end = len(lines)   # the section runs to the next level-2 heading outside a fence: the `reason:` and `changed_by:` lines after the verdict line belong to it
    fence = False
    for k in range(last[0] + 1, len(lines)):
        if lines[k].startswith(("```", "~~~")): fence = not fence
        if not fence and lines[k].startswith("## "):
            end = k; break
    return cid, last[1], "\n".join(lines[:end]).rstrip("\n") + "\n", len(lines)

def opened(tn, cid):
    hits = []
    for st in tn["steps"]:
        for c in st["calls"]:
            if c["kind"] in ("read-whole", "read-part", "bash-view", "bash-query") or c.get("reads_too"):
                for p in c["paths"]:
                    if "__pondus__" in p and cid in p: hits.append(os.path.basename(p))
    return hits

allturns = []
for arg in sys.argv[2:]:
    label, path = arg.split("=", 1)
    turns, *_ = parse(label, path); analyse(turns); allturns.append((label, turns))

res = {}
for p in sorted(glob.glob(os.path.join(ROOT, "__pondus__", "w*.md"))):
    c = cut(p)
    if not c: continue
    cid, ver, txt, nl = c
    open(os.path.join(out, "claim_at_verdict", cid + ".md"), "w").write(txt)
    rec = dict(claim=cid, verifier=ver, chars_at_verdict=len(txt), chars_final=len(open(p, encoding="utf-8").read()), wakes=[])
    for label, turns in allturns:
        for i, tn in enumerate(turns):
            for g in tn["triggers"]:
                body = g.get("body") or g.get("head") or ""
                hit = (g.get("agent") == ver) or (cid in body and re.search(r"\bESCALATE\b", body))
                if not hit: continue
                w = dict(label=label, turn=tn["n"], t=hhmm(tn["t0"]), kind=g["kind"], agent=g.get("agent"), body_chars=len(body), body=body, follow=[])
                for j in range(i, min(i + 4, len(turns))):
                    t2 = turns[j]
                    txt2 = "\n".join("\n".join(s["text"]) for s in t2["steps"])
                    calls = [(c["name"], (c.get("cmd") or c.get("key") or "")[:200], c["paths"]) for s in t2["steps"] for c in s["calls"]]
                    w["follow"].append(dict(turn=t2["n"], t=hhmm(t2["t0"]), trig=[x["kind"] + ":" + str(x.get("agent")) for x in t2["triggers"]], pi_text=txt2, opens_claim=opened(t2, cid), calls=calls))
                rec["wakes"].append(w)
    res[cid] = rec
json.dump(res, open(os.path.join(out, "wakes.json"), "w"), indent=1)
for cid, r in res.items():
    print(cid, r["verifier"], "wakes:", [(w["label"], w["turn"], w["t"], w["kind"], w["agent"], w["body_chars"]) for w in r["wakes"]])
