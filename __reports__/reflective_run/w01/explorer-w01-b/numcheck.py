#!/usr/bin/env python3
"""explorer-w01-b: for every agent hand-back in the genesis and design sessions, list the numbers that the
PI's own text (assistant text blocks, SendMessage bodies) quotes in the window after delivery but that do
not occur in the hand-back text. Output: numcheck.csv (candidates for manual inspection, not verdicts).
Run: python3 -I numcheck.py OUTDIR
"""
import csv, json, re, sys
sys.path.insert(0, ".")
import extract_comm as E

NUM = re.compile(r"(?<![\w.])(\d+\.\d+|\d{3,}|\d+%|\d+×|\d+x)(?![\w])")

def norm(s):
    return s.replace(",", "")

def main(out):
    rows = []
    for label, jf, subdir, root in E.SESSIONS[:2]:
        ev = E.load(jf)
        by = {i: d for i, d in ev}
        order = [i for i, _ in ev]
        pos = {i: k for k, i in enumerate(order)}
        for i, d in ev:
            if d.get("type") == "queue-operation" and d.get("operation") == "enqueue":
                c = d.get("content") or ""
                if not c.startswith("<agent-message"):
                    continue
                p = E.parse_handback(c)
                if not p:
                    continue
                rep = norm(p["report"])
                repnums = set(NUM.findall(rep))
                # find delivery line
                dl = None
                for j in order[pos[i] + 1: pos[i] + 60]:
                    x = by[j]
                    if x.get("type") == "user" and isinstance(x.get("message", {}).get("content"), str) and p["agent"] in x["message"]["content"]:
                        dl = j
                        break
                if dl is None:
                    continue
                texts = []
                n = 0
                for j in order[pos[dl] + 1:]:
                    x = by[j]
                    if x.get("type") == "user" and isinstance(x.get("message", {}).get("content"), str):
                        break
                    if x.get("type") != "assistant":
                        continue
                    n += 1
                    if n > 60:
                        break
                    for b in E.blocks(x):
                        if b.get("type") == "text":
                            texts.append(("text", j, b["text"]))
                        if b.get("type") == "tool_use" and b["name"] == "SendMessage":
                            texts.append(("send", j, b["input"].get("message", "")))
                for kind, j, t in texts:
                    for m in NUM.finditer(norm(t)):
                        v = m.group(1)
                        if v not in repnums:
                            ctx = norm(t)[max(0, m.start() - 70): m.end() + 40].replace("\n", " ")
                            rows.append(dict(session=label, delivery_line=dl, agent=p["agent"], kind=kind, line=j, number=v, context=ctx))
    with open(out + "/numcheck.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["session", "delivery_line", "agent", "kind", "line", "number", "context"])
        w.writeheader(); w.writerows(rows)
    print(len(rows))

main(sys.argv[1])
