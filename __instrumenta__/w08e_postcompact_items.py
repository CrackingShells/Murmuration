# Lists, per entry after each compact_boundary in one session transcript, its type, attachment kind and character length (no text), from a session .jsonl path to a table on stdout: what the platform re-injects after a compaction.
"""usage: w08e_postcompact_items.py TRANSCRIPT.jsonl [N entries after each boundary, default 14]"""
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip() and "api-request-blob" not in l[:100]]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 14
def size(d):
    m = d.get("message")
    c = m.get("content") if isinstance(m, dict) else None
    if isinstance(c, str): return len(c)
    if isinstance(c, list): return sum(len(json.dumps(x)) if x.get("type") != "text" else len(x.get("text", "")) for x in c if isinstance(x, dict))
    a = d.get("attachment")
    return len(json.dumps(a)) if a else 0
for i, d in enumerate(rows):
    if d.get("subtype") == "compact_boundary":
        print("boundary at row %d: %s" % (i, json.dumps({k: v for k, v in (d.get("compactMetadata") or {}).items() if k in ("trigger", "preTokens", "postTokens", "durationMs")})))
        for j in range(i + 1, min(len(rows), i + 1 + N)):
            e = rows[j]; a = e.get("attachment") or {}
            tool = ""
            m = e.get("message")
            if isinstance(m, dict) and isinstance(m.get("content"), list):
                tool = ",".join(x.get("type", "") + (":" + x.get("name", "") if x.get("type") == "tool_use" else "") for x in m["content"] if isinstance(x, dict))
            print("  row %d type=%s sub=%s attach=%s summary=%s chars=%d %s" % (j, e.get("type"), e.get("subtype"), a.get("type"), e.get("isCompactSummary"), size(e), tool))
