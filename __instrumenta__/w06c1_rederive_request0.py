# Re-derives, from a Desktop session transcript JSONL (argv: AGENT.md TRANSCRIPT [TRANSCRIPT ...]), request 0's linkage (api-request -> shape -> first assistant records by requestRef), its usage sum, its loaded tool names, and which names of the agent file's disallowedTools: line occur in the loaded tools, the deferred-tools listing and the raw first-request text; own code (does not import the author's w06_request0_check.py); stdout, no ids printed.
import fnmatch, json, re, sys

agent = sys.argv[1]
line = [l for l in open(agent) if l.startswith("disallowedTools:")][0]
pats = [p.strip() for p in line.split(":", 1)[1].split(",") if p.strip()]
print("denied patterns:", len(pats))

def hit(name):
    return [p for p in pats if fnmatch.fnmatchcase(name, p)]

def rawhit(text):
    # literal occurrence of a denied name (prefix before '*' for globs) in raw text
    out = {}
    for p in pats:
        key = p.rstrip("*")
        n = len(re.findall(re.escape(key) + (r"" if p.endswith("*") else r"(?![A-Za-z0-9_])"), text))
        if n: out[p] = n
    return out

for path in sys.argv[2:]:
    R = [json.loads(l) for l in open(path)]
    print("\n==", path.split("/")[-1][:8], "records", len(R))
    ver = sorted({r["version"] for r in R if r.get("version")})
    ents = sorted({r["entrypoint"] for r in R if r.get("entrypoint")})
    ags = sorted({r["agentSetting"] for r in R if r["type"] == "agent-setting"})
    first_ts = next((r["timestamp"] for r in R if r.get("timestamp")), None)
    print("version", ver, "entrypoint", ents, "agent", ags, "first ts", first_ts)
    side = sum(1 for r in R if r["type"] in ("assistant", "user") and r.get("isSidechain"))
    print("sidechain assistant/user records in this file:", side)
    reqs = [(i, r) for i, r in enumerate(R) if r["type"] == "api-request"]
    firsta = next(((i, r) for i, r in enumerate(R) if r["type"] == "assistant"), None)
    i0u = firsta[1]["message"]["usage"]
    tot = lambda u: u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"]
    print("first assistant record: usage sum", tot(i0u), "(in %d, write %d, read %d)" % (i0u["input_tokens"], i0u["cache_creation_input_tokens"], i0u["cache_read_input_tokens"]), "model", firsta[1]["message"]["model"])
    if not reqs:
        print("no api-request records (older format): tool list not recorded")
        # deferred names listing in attachments before first assistant
        for r in R[:firsta[0]]:
            a = r.get("attachment") if r["type"] == "attachment" else None
            if a and a.get("type") == "deferred_tools_delta":
                names = a.get("addedNames", [])
                print("deferred addedNames", len(names), "denied among them:", sorted({n for n in names if hit(n)}))
        txt = json.dumps(R[:firsta[0]])
        print("raw denied-name occurrences before first assistant record:", rawhit(txt))
        continue
    i, rq = reqs[0]
    print("n api-request", len(reqs), "querySources", sorted({q.get("querySource") for _, q in reqs}))
    print("first api-request precedes first assistant record:", i < firsta[0], "; its id == assistant.requestRef:", rq["id"] == firsta[1].get("requestRef"))
    blocks = [r for r in R if r["type"] == "assistant" and r.get("requestRef") == rq["id"]]
    mids = {b["message"]["id"] for b in blocks}
    us = {json.dumps(b["message"]["usage"], sort_keys=True) for b in blocks}
    print("assistant records of request 0:", len(blocks), "message ids:", len(mids), "distinct usage:", len(us))
    shapes = [r for r in R if r["type"] == "api-request-shape" and r["shapeHash"] == rq["shapeHash"]]
    print("shape records matching request 0 shapeHash:", len(shapes))
    sh = shapes[0]["shape"]
    names = [t.get("name") for t in sh["tools"]]
    print("loaded tools:", len(names))
    print(" ", ", ".join(n if not n.startswith("mcp__") or len(n) < 30 else n[:12] + "..." + n[-18:] for n in names))
    print("denied among loaded:", sorted({n for n in names if hit(n)}))
    print("tools JSON chars", len(json.dumps(sh["tools"])), "system JSON chars", len(json.dumps(sh["system"])))
    # deferred listing: attachments before request 0
    for r in R[:i]:
        a = r.get("attachment") if r["type"] == "attachment" else None
        if a and a.get("type") == "deferred_tools_delta":
            dn = a.get("addedNames", [])
            print("deferred addedNames", len(dn), "denied among them:", sorted({n for n in dn if hit(n)}), "; deferred ∩ loaded:", sorted(set(dn) & set(names)))
    # raw text of everything sent in request 0: shape + blobs in tail
    blobs = {r["hash"]: r["message"] for r in R if r["type"] == "api-request-blob"}
    sent = json.dumps(sh) + json.dumps([blobs.get(h) for h in rq["tail"]])
    print("tail blobs found:", sum(h in blobs for h in rq["tail"]), "of", len(rq["tail"]))
    print("raw denied-name occurrences in everything sent with request 0 (shape + tail blobs):", rawhit(sent))
