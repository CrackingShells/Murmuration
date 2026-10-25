"""Lists, for each subagent transcript of the 4 lab worktrees whose last tool call is not SubagentHandback, its metadata and its last N records in compact form (type, tool, stop_reason, text head); reads ~/.claude/projects/*Murmuration-murmuration-*/*/subagents/agent-*.jsonl (read only), writes a JSON list to stdout (or TSV with --tsv)."""
import json, glob, os, sys
root = os.path.expanduser("~/.claude/projects")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
def brief(r):
    t = r.get("type"); m = r.get("message") or {}
    c = m.get("content")
    d = {"type": t, "ts": r.get("timestamp"), "uuid": (r.get("uuid") or "")[:8]}
    if t == "assistant":
        d["stop"] = m.get("stop_reason"); d["model"] = m.get("model")
        if r.get("isApiErrorMessage") or r.get("error"): d["api_error"] = str(r.get("error"))[:80]
    if isinstance(c, str):
        d["text"] = c[:200]
    elif isinstance(c, list):
        parts = []
        for b in c:
            if not isinstance(b, dict): continue
            if b["type"] == "text": parts.append("T:" + b["text"][:200])
            elif b["type"] == "tool_use": parts.append("TU:%s:%s" % (b["name"], json.dumps(b.get("input"))[:160]))
            elif b["type"] == "tool_result": parts.append("TR:" + str(b.get("content"))[:160])
            elif b["type"] == "thinking": parts.append("TH")
        d["parts"] = parts
    if r.get("subtype"): d["subtype"] = r["subtype"]
    if r.get("isSidechain") is False: d["sidechain"] = False
    return d
def info(f):
    recs = []
    for l in open(f, errors="replace"):
        try: recs.append(json.loads(l))
        except Exception: pass
    last = None
    for r in recs:
        if r.get("type") == "assistant":
            for b in r.get("message", {}).get("content", []):
                if isinstance(b, dict) and b.get("type") == "tool_use": last = b["name"]
    meta = {}
    try: meta = json.load(open(f[:-6] + ".meta.json"))
    except Exception: pass
    ts = [r["timestamp"] for r in recs if r.get("timestamp")]
    return dict(file=f, proj=f.split("/")[-4], sess=f.split("/")[-3][:8], agent=os.path.basename(f)[6:-6], meta=meta, last_tool=last, n=len(recs), start=ts[0] if ts else None, end=ts[-1] if ts else None, tail=[brief(r) for r in recs[-N:]])
if __name__ == "__main__":
    out = []
    for f in sorted(glob.glob(root + "/*Murmuration-murmuration-*/*/subagents/agent-*.jsonl")):
        if "---reports" in f: continue
        i = info(f)
        if i["last_tool"] != "SubagentHandback": out.append(i)
    json.dump(out, sys.stdout, indent=1)
