#!/usr/bin/env python3
"""Re-derives w05-c3 request-0 context, tool-call sequence, explorer reply and error results from raw run transcripts (~/.claude/projects/<slug>/*.jsonl), independent of the author's table script; input: run-folder names under a scratch dir (default author-w05-2 runs), e.g. A1 B1; output: one TSV row per cell on stdout.
usage: w05c3_verify_transcripts.py <scratch> <cell> [<cell> ...]. Stdlib only."""
import glob, json, os, sys
scratch = os.path.abspath(sys.argv[1]); home = os.path.expanduser("~/.claude/projects")
print("cell\treq0_ctx\tn_main_req\tmain_tool_calls\texplorer_final_text\terror_results\tsnapshot_tools\tsnapshot_chars")
for cell in sys.argv[2:]:
    slug = (scratch + "/runs/" + cell + "/lab").replace("/", "-").replace(".", "-")
    fs = glob.glob(f"{home}/{slug}/*.jsonl")
    assert len(fs) == 1, (slug, fs)
    recs = [json.loads(l) for l in open(fs[0]) if l.strip()]
    main = [r for r in recs if r.get("type") == "assistant" and not r.get("isSidechain")]
    u = main[0]["message"]["usage"]
    req0 = u["input_tokens"] + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    calls = [b["name"] for r in main for b in r["message"]["content"] if b.get("type") == "tool_use"]
    errs = []; expl = []
    for r in recs:
        if r.get("type") == "user" and isinstance(r["message"].get("content"), list):
            for b in r["message"]["content"]:
                if b.get("type") == "tool_result":
                    t = json.dumps(b.get("content"))
                    if b.get("is_error") or "No such tool" in t: errs.append(t[:100])
                    if not r.get("isSidechain") and "beta" in t and "explorer" in t.lower(): expl.append(t[:80])
    sub = glob.glob(f"{home}/{slug}/*/subagents/*.jsonl")
    sub_text = ""
    for s in sub:
        for l in open(s):
            r = json.loads(l)
            if r.get("type") == "assistant":
                for b in r["message"]["content"]:
                    if b.get("type") == "text": sub_text = b["text"][:40]
    snap = [r for r in recs if r.get("attachment", {}).get("type") == "prompt_snapshot"] if any("attachment" in r for r in recs) else []
    tools = chars = ""
    if snap:
        a = snap[0]["attachment"]; ts = a.get("tools") or a.get("tool_schemas") or []
        tools = len(ts); chars = len(json.dumps(ts))
    print(cell, req0, len(main), ">".join(calls), repr(sub_text), len(errs), tools, chars, sep="\t")
