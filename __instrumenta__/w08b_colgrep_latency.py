# Lists each real colgrep call of the wave-4..7 workers (and of a given session file, e.g. this explorer's own) with its tool latency (tool_use to tool_result timestamps), the tool's own elapsed_ms and index_updated flag, result size, whether paths was relative or absolute, hit count; inputs: the session transcripts; output: printed table, no raw text. Usage: python3 -I w08b_colgrep_latency.py [EXTRA_JSONL ...]
import glob, json, os, re, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w08b_calls as C


def ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


files = []
for w, s in C.SESS.items():
    for f in sorted(glob.glob(os.path.join(C.H, s, "subagents", "agent-*.jsonl"))):
        files.append((w, os.path.basename(f)[6:14], f))
for f in sys.argv[1:]:
    files.append(("me", os.path.basename(f)[:8], f))
print("wave\tagent\ttool\tpaths_form\ttool_s\telapsed_ms\tindex_updated\tresult_chars\thits\terror")
for w, a, f in files:
    pend = {}
    for l in open(f):
        if l.startswith(C.SKIP) or "colgrep" not in l and "tool_result" not in l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        c = (r.get("message") or {}).get("content")
        if not isinstance(c, list):
            continue
        for b in c:
            if b.get("type") == "tool_use" and "colgrep" in b.get("name", ""):
                p = (b["input"].get("paths") or [b["input"].get("path") or ""])
                form = "none" if not p or not p[0] else ("absolute" if p[0].startswith("/") else "relative")
                pend[b["id"]] = (r["timestamp"], b["name"].split("__")[-1], form)
            if b.get("type") == "tool_result" and b.get("tool_use_id") in pend:
                t0, name, form = pend.pop(b["tool_use_id"])
                txt = json.dumps(b.get("content"))
                el = re.search(r'elapsed_ms\\*"?:\s*(\d+)', txt)
                iu = re.search(r'index_updated\\*"?:\s*(true|false)', txt)
                nh = len(re.findall(r'hit_id', txt)) // 1
                print("\t".join(map(str, [w, a, name, form, round(ts(r["timestamp"]) - ts(t0), 1), el.group(1) if el else "", iu.group(1) if iu else "", len(txt), nh, int(bool(b.get("is_error")))])))
