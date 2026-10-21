# Parses the transcripts (read-only) of the P6 sessions into one row per author request (deduplicated by requestId): tokens read, written as 5-minute and as 1-hour cache, uncached input, gap since the previous request, tool names, plus per session the author's tool list, system and tools hashes, request 0 size and hand-back text; inputs: S (the runner's scratch folder holding work/<label>) and the labels; outputs: <S>/parsed.json and, on stdout, markdown tables for c1, c2, c3.
# usage: w07c7_parse.py S label[,label...] [--home ~/.claude/projects]
import json, glob, os, sys, datetime
S = os.path.abspath(sys.argv[1]); labels = sys.argv[2].split(",")
home = os.path.expanduser("~/.claude/projects")
def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
out = {}
for lab in labels:
    proj = os.path.join(home, "-private-tmp-" + os.path.relpath(os.path.join(S, "work", lab), "/private/tmp").replace("/", "-"))
    fs = glob.glob(proj + "/*/subagents/agent-*.jsonl")
    assert len(fs) == 1, (lab, fs)
    f = fs[0]; reqs = {}; order = []; shape = None; handback = None; tools_used = []
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        if d.get("type") == "api-request-shape" and shape is None: shape = d.get("shape", {})
        if d.get("type") != "assistant": continue
        m = d["message"]; rid = d.get("requestId"); u = m.get("usage") or {}
        if rid not in reqs:
            cc = u.get("cache_creation") or {}
            reqs[rid] = dict(t=ts(d["timestamp"]), input=u.get("input_tokens", 0), read=u.get("cache_read_input_tokens", 0),
                             w5=cc.get("ephemeral_5m_input_tokens", 0), w1=cc.get("ephemeral_1h_input_tokens", 0),
                             wtot=u.get("cache_creation_input_tokens", 0), tools=[])
            order.append(rid)
        for b in m.get("content") or []:
            if b.get("type") == "tool_use":
                reqs[rid]["tools"].append(b["name"])
                if b["name"] == "SubagentHandback": handback = b["input"].get("message")
            elif b.get("type") == "text" and b.get("text"): handback = handback or b["text"]
    rows = [reqs[r] for r in order]
    pf = glob.glob(os.path.dirname(f) + "/*.prefix.json")
    st = json.load(open(pf[0]))["state"] if pf else {}
    for i, r in enumerate(rows):
        r["ctx"] = r["input"] + r["read"] + r["wtot"]
        r["gap"] = (r["t"] - rows[i - 1]["t"]) if i else None
        r["read_frac_prev"] = (r["read"] / rows[i - 1]["ctx"]) if i else None
    out[lab] = dict(file=f, rows=rows, tool_names=st.get("toolNames"), tools_hash=st.get("toolsHash"), system_hash=st.get("systemHash"),
                    system_chars=st.get("systemCharCount"), handback=handback, n_tools_shape=len((shape or {}).get("tools") or []))
json.dump(out, open(os.path.join(S, "parsed.json"), "w"), indent=1)
print("| session | req | gap s | input | cache read | write 5m | write 1h | ctx | read/prev ctx | tools |\n|:--|--:|--:|--:|--:|--:|--:|--:|--:|:--|")
for lab, o in out.items():
    for i, r in enumerate(o["rows"]):
        print("| %s | %d | %s | %d | %d | %d | %d | %d | %s | %s |" % (lab, i, "" if r["gap"] is None else "%.1f" % r["gap"], r["input"], r["read"], r["w5"], r["w1"], r["ctx"],
              "" if r["read_frac_prev"] is None else "%.3f" % r["read_frac_prev"], ",".join(r["tools"])))
print("\n| session | tool names | tools hash | system hash | system chars | request 0 ctx | requests | hand-back |\n|:--|:--|--:|--:|--:|--:|--:|:--|")
for lab, o in out.items():
    print("| %s | %s | %s | %s | %s | %d | %d | %s |" % (lab, ",".join(o["tool_names"] or []), o["tools_hash"], o["system_hash"], o["system_chars"], o["rows"][0]["ctx"], len(o["rows"]), (o["handback"] or "").replace("\n", " ")[:120]))
