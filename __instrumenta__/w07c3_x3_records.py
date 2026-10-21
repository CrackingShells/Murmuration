# w07-c3: x3 records: for two failure runs (arm A, arm B of crash or nopy) lists what the platform recorded for each tool call and each murmuration hook (tool_result text, hook attachments with type, event, exit code, stderr head; debug-file lines of murmuration hooks that did not finish with status 0), paths and run names masked, and says whether the two arms agree; inputs: RUN_A RUN_B; output: text on stdout
"""usage: w07c3_x3_records.py RUN_A RUN_B
Per arm: (1) every tool_result of the main transcript in order with its is_error flag; (2) the sequence of hook attachments `hook_blocking_error`, `hook_non_blocking_error`, `hook_cancelled`, `hook_success` with hookEvent, exit code and
the first 160 characters of stderr (the export path and the run name are masked); (3) debug-file lines `Hooks:` of murmuration hooks that did not finish with status 0, or that failed to start; (4) whether the echo marker commands ran (the stub-free marker
text appears in a tool_result) and the final answer. A line-by-line verdict: SAME text, SAME up to the command's display form (quotes), or DIFFERENT."""
import json, os, re, sys

def collect(d):
    rn = os.path.basename(d.rstrip("/"))
    clean = lambda s: re.sub(r"/private/tmp/murmuration-w07/author-w07-3/export_[0-9a-f]+_\w+", "<EXPORT>", s.replace(rn, "RUN"))
    out = {"tool_results": [], "attachments": [], "debug": [], "answer": ""}
    for l in open(d + "/transcripts/main.jsonl"):
        r = json.loads(l)
        ty = r.get("type")
        if ty == "attachment":
            a = r["attachment"]; at = a.get("type", "")
            if at in ("hook_blocking_error", "hook_non_blocking_error", "hook_cancelled"):
                out["attachments"].append("%s %s exit=%s stderr=%s" % (at, a.get("hookEvent") or a.get("hookName"), a.get("exitCode"), clean(str(a.get("stderr") or a.get("blockingError") or a.get("content") or ""))[:160].replace("\n", " | ")))
            elif at == "hook_success" and a.get("hookEvent") in ("PreToolUse", "PostToolUse", "PostToolBatch", "UserPromptSubmit") and "export_" in json.dumps(a):
                out["attachments"].append("hook_success %s exit=%s" % (a.get("hookEvent"), a.get("exitCode")))
        elif ty == "user":
            m = r.get("message", {}).get("content")
            if isinstance(m, list):
                for c in m:
                    if isinstance(c, dict) and c.get("type") == "tool_result":
                        t = c.get("content"); t = t if isinstance(t, str) else json.dumps(t)
                        out["tool_results"].append(("ERR " if c.get("is_error") else "OK  ") + clean(t)[:700].replace("\n", " | "))
    for l in open(d + "/dbg.log", errors="replace"):
        if "Hooks:" in l and "murmuration@inline" in l and "finished with status 0" not in l and "(plugin murmuration@inline)" in l:
            out["debug"].append(clean(re.sub(r"^\S+ \[DEBUG\] ", "", l.strip()))[:260])
    try:
        out["answer"] = clean(json.load(open(d + "/run.json")).get("result", ""))[:500]
    except Exception:
        pass
    return out

a, b = collect(sys.argv[1]), collect(sys.argv[2])
for key in ("tool_results", "attachments", "debug"):
    print("== %s" % key)
    for arm, x in (("A", a), ("B", b)):
        print(" %s (%d):" % (arm, len(x[key])))
        for i, line in enumerate(x[key]):
            print("   %2d  %s" % (i, line))
    q = lambda v: [re.sub(r"\(\d+ms\)", "(#ms)", x.replace('"', "")) for x in v]
    print(" -> %s" % ("SAME text" if a[key] == b[key] else ("SAME up to quotes/spacing" if q(a[key]) == q(b[key]) else "DIFFERENT")))
print("== final answer\n A: %s\n B: %s" % (a["answer"], b["answer"]))
