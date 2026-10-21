# Re-derive per-case outcomes of the E3 v3 live runs from the raw sessions: for every run folder under author-w06-5's v3shard*/runs, read cases.json, stream.jsonl (tool_use and tool_result) and guard.log; output: one line per (run, tool call) with denied by guard / ran / guard starts, and aggregates
import glob, json, os, collections, sys
base = "/private/tmp/murmuration-w06/author-w06-5"
rows = []
for run in sorted(glob.glob(base + "/v3shard*/runs/*/")):
    try: cases = json.load(open(run + "cases.json"))["cases"]
    except Exception: continue
    gl = [json.loads(l) for l in open(run + "guard.log")] if os.path.exists(run + "guard.log") else []
    uses, res = [], {}
    try:
        for l in open(run + "stream.jsonl"):
            m = json.loads(l)
            c = m.get("message", {}).get("content")
            if not isinstance(c, list): continue
            for b in c:
                if b.get("type") == "tool_use": uses.append(b)
                if b.get("type") == "tool_result": res[b["tool_use_id"]] = b
    except Exception as e: pass
    for u in uses:
        r = res.get(u["id"]); txt = json.dumps(r.get("content")) if r else ""
        den = "permission_guard" in txt
        rows.append(dict(run=os.path.basename(run.rstrip("/")), shard=run.split("/")[-3], tool=u["name"], what=(u["input"].get("command") or u["input"].get("file_path") or "")[:70], denied=den, starts=len(gl), case_ids=[c["id"] for c in cases]))
json.dump(rows, open("/private/tmp/murmuration-w06/reproducer-w06-7/out/v3_rederived.json", "w"), indent=1)
print(len(rows), "tool calls;", sum(r["denied"] for r in rows), "denied")
