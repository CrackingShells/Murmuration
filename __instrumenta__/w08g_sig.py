# Second pass over the transcripts parsed by w07b_loop_parse.py: per request (assistant message id, same order as the parsed turns) the thinking signature characters, and whether every specific token of every call of the request occurs in the worker's first prompt (the brief); inputs: LABEL=MAIN_JSONL pairs; output: <outdir>/<label>_<agent>.sig.json = {"sig": [...], "brief": [...]}.
# the sig file also holds, per request, the first 120 characters of each call (head, for hand audits only; not committed).
# usage: w08g_sig.py OUTDIR LABEL=MAIN_JSONL [...]   (workers read from <MAIN minus .jsonl>/subagents; no transcript text is written)
import json, sys, os, glob
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w07b_loop_parse as P

def one(args):
    label, path, agent = args
    order, msgs, first_prompt = [], {}, None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(P.SKIP): continue
            try: r = json.loads(line)
            except ValueError: continue
            t = r.get("type")
            if t == "assistant" and isinstance(r.get("message"), dict):
                m = r["message"]
                if m.get("model") == "<synthetic>": continue
                e = msgs.get(m.get("id"))
                if e is None:
                    e = msgs[m.get("id")] = {"sig": 0, "calls": []}; order.append(m.get("id"))
                for b in m.get("content") or []:
                    if b.get("type") == "thinking": e["sig"] += len(b.get("signature") or "")
                    elif b.get("type") == "tool_use": e["calls"].append((b["name"], b.get("input") or {}))
            elif t == "user" and first_prompt is None:
                c = (r.get("message") or {}).get("content")
                if not (isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c)):
                    first_prompt = P.text_of(c)
    bt = P.specific_tokens(first_prompt or "")
    sig, brief, heads = [], [], []
    for mid in order:
        e = msgs[mid]; sig.append(e["sig"])
        ok = bool(e["calls"])
        for n, i in e["calls"]:
            tk = P.specific_tokens(P.call_text(n, i))
            if not tk or any(x not in bt for x in tk): ok = False
        brief.append(ok)
        heads.append([n + ": " + (i.get("command") or i.get("file_path") or i.get("path") or i.get("pattern") or i.get("query") or str(i))[:120].replace("\n", " ") for n, i in e["calls"]])
    return label, agent, {"sig": sig, "brief": brief, "heads": heads}

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); jobs = []
    for spec in sys.argv[2:]:
        label, mp = spec.split("=", 1)
        jobs.append((label, mp, "PI"))
        for f in sorted(glob.glob(mp[:-6] + "/subagents/agent-*.jsonl")): jobs.append((label, f, os.path.basename(f)[6:-6]))
    jobs.sort(key=lambda j: -os.path.getsize(j[1]))
    with Pool(8) as p: res = p.map(one, jobs, chunksize=1)
    for label, agent, d in res: json.dump(d, open(os.path.join(out, "%s_%s.sig.json" % (label, agent)), "w"))
    print("wrote", len(res))
if __name__ == "__main__":
    main()
