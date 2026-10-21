# Flattens the per-agent JSON of w07b_loop_parse.py into one TSV row per request (label, agent name, turn, calls, model/first-block/tool/gap/wait seconds, tokens, USD, tool names); inputs: parse output folder; output: one TSV. Usage: w07b_turns_tsv.py PARSED_DIR OUT_TSV
import json, glob, sys, os
parsed, out = sys.argv[1:3]
n = 0
with open(out, "w") as fh:
    fh.write("label\tname\tk\tncalls\tmodel_s\tttfb_s\ttool_s\tgap_prev_s\twait_s\tpre_s\tcache_read\tcache_write\tinput\toutput_lb\tusd\tthink_ms\tcalls\n")
    for f in sorted(glob.glob(os.path.join(parsed, "*.json"))):
        a = json.load(open(f))
        for t in a["turns"]:
            g = lambda v: "" if v is None else "%.3f" % v
            fh.write("\t".join(str(x) for x in (a["label"], a["name"], t["k"], t["ncalls"], g(t["model_s"]), g(t["ttfb_s"]), g(t["tool_s"]), g(t["gap_prev_s"]), g(t["wait_s"]), g(t["pre_s"]), t["cr"], t["cw5"] + t["cw1"], t["inp"], t["out"], "%.4f" % t["usd"], t["think_ms"], ",".join(c["name"] + (":" + c["cmd0"] if c["cmd0"] else "") for c in t["calls"]))) + "\n")
            n += 1
print(n, "rows")
