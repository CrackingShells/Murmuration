# measures the size of one colgrep `search` result (paths __instrumenta__, limit 5) in a fresh lab of the E3b scripts, for two queries, and the size of `ls -1 __instrumenta__`; input: export dir, scripts dir, run root; output: lines with the result characters on stdout and e3b_search_probe.json in the run root
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e3_run_workers as R  # noqa: E402

export, scripts, root = [os.path.abspath(a) for a in sys.argv[1:4]]
res = {"ls_1_chars": sum(len(n) + 1 for n in os.listdir(scripts))}
QUERIES = (("probe1", "maximum number of distinct substrings of binary strings"), ("probe2", "Collatz trajectory highest peak value"))
for rid, query in QUERIES[: int(sys.argv[4]) if len(sys.argv) > 4 else 2]:
    lab, env = R.build_lab(rid, scripts, root, export)
    env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "0"
    prompt = ("Call the colgrep search tool once with query \"%s\", paths [\"__instrumenta__\"], limit 5, and then answer with the single word done. "
              "If the tool is not loaded, load it first with ToolSearch." % query)
    out = subprocess.run(["claude", "-p", "--plugin-dir", export, "--permission-mode", "auto", "--max-budget-usd", "0.5", "--output-format", "stream-json", "--verbose", prompt],
                         cwd=lab, env=env, capture_output=True, text=True, timeout=300).stdout
    calls, chars, cost = {}, [], None
    for line in out.splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("type") == "result":
            cost = r.get("total_cost_usd")
        c = (r.get("message") or {}).get("content")
        if isinstance(c, list):
            for b in c:
                if b.get("type") == "tool_use" and b["name"].endswith("colgrep__search"):
                    calls[b["id"]] = b["input"]
                if b.get("type") == "tool_result" and b["tool_use_id"] in calls:
                    x = b.get("content")
                    chars.append(len(x) if isinstance(x, str) else sum(len(t.get("text", "")) for t in x))
    res[rid] = {"query": query, "search_result_chars": chars, "total_cost_usd": cost}
    print(rid, res[rid])
json.dump(res, open(os.path.join(root, "e3b_search_probe.json"), "w"), indent=1)
