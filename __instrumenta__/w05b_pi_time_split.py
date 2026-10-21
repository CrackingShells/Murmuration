#!/usr/bin/env python3
# Splits the wall-clock time of a PI main-thread session into model time (first to last assistant record of a request) and waiting time before the next request, by what the PI was waiting for (tool names of the previous request, peer message, human), from one transcript (.jsonl); idle gaps over 600 s are listed apart. Writes <outdir>/<label>_time_split.tsv. Usage: w05b_pi_time_split.py TRANSCRIPT LABEL OUTDIR
import json, sys, os, collections, datetime
F, label, out = sys.argv[1:4]
ts = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
recs = [json.loads(l) for l in open(F, errors="replace")]
order, R = [], {}
for i, d in enumerate(recs):
    if d["type"] == "assistant":
        m = d["message"]["id"]
        if m not in R:
            R[m] = dict(first=i, last=i, t0=ts(d["timestamp"]), t1=ts(d["timestamp"]), tools=[], inp=[]); order.append(m)
        R[m]["last"] = i; R[m]["t1"] = ts(d["timestamp"])
        for b in d["message"]["content"]:
            if b["type"] == "tool_use":
                R[m]["tools"].append(b["name"]); R[m]["inp"].append(b["input"])
model = sum(R[m]["t1"] - R[m]["t0"] for m in order)
wait = collections.defaultdict(lambda: [0.0, 0]); idle = []
for k in range(1, len(order)):
    a, b = R[order[k - 1]], R[order[k]]
    gap = b["t0"] - a["t1"]
    seg = recs[a["last"] + 1:b["first"]]
    kinds = {(d.get("origin") or {}).get("kind") for d in seg if d["type"] == "user"}
    tr = any(d["type"] == "user" and isinstance(d["message"]["content"], list) and d["message"]["content"] and d["message"]["content"][0].get("type") == "tool_result" for d in seg)
    if gap > 600:
        idle.append((k, gap, "+".join(sorted(x for x in kinds if x)) or ("tool_result" if tr else "?"), ",".join(a["tools"])[:60]))
        key = "idle > 600 s"
    elif tr:
        key = "tools: " + ",".join(sorted(set(a["tools"])))
        if "Agent" in a["tools"]: key = "tools incl. Agent (dispatch)"
    elif "peer" in kinds:
        key = "waiting for peer message (worker hand-back)"
    elif "human" in kinds:
        key = "waiting for human"
    else:
        key = "other/none"
    wait[key][0] += gap; wait[key][1] += 1
tot = model + sum(v[0] for v in wait.values())
with open(os.path.join(out, label + "_time_split.tsv"), "w") as f:
    f.write("what\tseconds\tcount\tshare_of_session_wall_time\n")
    f.write("model time within requests (first to last assistant record)\t%d\t%d\t%.3f\n" % (model, len(order), model / tot))
    for k, v in sorted(wait.items(), key=lambda kv: -kv[1][0]):
        f.write("%s\t%d\t%d\t%.3f\n" % (k, v[0], v[1], v[0] / tot))
    for k, g, kind, tl in idle:
        f.write("IDLE request %d\t%d\t1\t%s after tools=%s\n" % (k, g, kind, tl))
print(open(os.path.join(out, label + "_time_split.tsv")).read())
