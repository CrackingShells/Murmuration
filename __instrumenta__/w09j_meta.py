# w09-j: reduces the private cases.jsonl (case text) to a text-free metadata table, one JSON line per refusal, natural allow and pair member (cid, group, label, tool, stratum, weight, opaque session number, era, month, reason category, risky flag, pair id, refusal id of a pair), so the figure script needs no case text. Usage: python3 -I w09j_meta.py CASES_JSONL OUT_JSONL
import sys, json, collections
cases = [json.loads(l) for l in open(sys.argv[1])]
sess = {}
def sn(s):
    if s not in sess: sess[s] = len(sess)
    return sess[s]
out = []
for c in sorted(cases, key=lambda c: c["cid"]):
    g = c["group"]
    if g == "synthetic": continue
    if g == "allow" and c["source"] != "natural" and c["source"] != "arena": continue
    r = {"cid": c["cid"], "group": g, "label": c["label"], "tool": c["tool"], "weight": float(c["weight"])}
    if "session" in c: r["session"] = sn(c["session"])
    if g == "refusal": r.update(era=str(c["era"]) == "True", month=c["month"], reason=c["reason"])
    if g == "allow": r.update(source=c["source"], stratum=c["stratum"], risky=str(c["risky"]) == "True", N_h=int(c["N_h"]), m_h=int(c["m_h"]))
    if g.startswith("pair"): r["pair"] = c["pair"]; r["ref_id"] = c.get("ref_id")
    out.append(r)
with open(sys.argv[2], "w") as f:
    for r in out: f.write(json.dumps(r, sort_keys=True) + "\n")
print(len(out), "rows;", dict(collections.Counter((r["group"], r.get("source")) for r in out)), "; sessions", len(sess))
