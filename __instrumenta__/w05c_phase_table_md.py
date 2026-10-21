# turns worker_phase_detail.json (from w05c_worker_phases.py) into one markdown table per worker with mutually exclusive phases (USD at list price and active seconds); input: the detail json; output: markdown on stdout
import json, sys
d = json.load(open(sys.argv[1]))
P = (2.0, 10.0, 0.10, 2.5)
def phase(x):
    if x["n"] == 0 and x["run"] == 0: return "start"
    if x["n"] < 3 and x["run"] == 0 and x["cat"] in ("doc", "search", "outside"): return "orient"
    if x["cat"] == "handback": return "handback"
    if x["cat"] == "exchange": return "exchange"
    if x["cat"] == "deliver": return "deliver"
    return "work"
PH = ["start", "orient", "work", "deliver", "exchange", "handback"]
print("| worker | req | runs | USD | s | " + " | ".join("%s USD / s" % p for p in PH) + " | resume-run USD (runs 1+) | cold premium USD | failed calls |")
print("|:--|--:|--:|--:|--:|" + "--:|" * len(PH) + "--:|--:|--:|")
for n, a in d.items():
    R = a["reqs"]
    U = sum(x["usd"] for x in R); S = sum(x["model_s"] + x["tool_s"] for x in R)
    cells = []
    for p in PH:
        xs = [x for x in R if phase(x) == p]
        cells.append("%.3f / %.0f" % (sum(x["usd"] for x in xs), sum(x["model_s"] + x["tool_s"] for x in xs)))
    ru = sum(x["usd"] for x in R if x["run"] > 0)
    cold = sum(r["first_cw"] * (P[3] - P[2]) / 1e6 for r in a["resumes"] if r["first_cw"] > 20000) + sum(m["usd_extra"] for m in a["misses"])
    print("| %s | %d | %d | %.2f | %.0f | %s | %.2f | %.2f | %d |" % (n, len(R), 1 + len(a["resumes"]), U, S, " | ".join(cells), ru, cold, len(a["fails"])))
