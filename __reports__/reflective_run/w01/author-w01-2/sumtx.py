"""Token sums from Claude Code transcripts, by dedup method.  Read-only, stdlib only.

usage: python3 -I sumtx.py <main-session.jsonl>            # main + its subagents/*.jsonl, JSON to stdout
       python3 -I sumtx.py --file <any.jsonl>               # one file

A request is keyed by `requestId` (fallback `message.id`).  One request is written as several
`assistant` records (one per content block).  For each request we keep three views of its usage:
first record, last record, max-output record.  Input, cache-read and cache-write are identical
across the records of a request; only `output_tokens` differs.
"""
import json, sys, os, glob, collections

KINDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def read_requests(path):
    """-> list of dict per request, in order of first appearance."""
    reqs = collections.OrderedDict()
    cost_state = None
    for line in open(path, errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") == "cost-state":
            cost_state = d
        if d.get("type") != "assistant":
            continue
        m = d.get("message", {})
        u = m.get("usage") or {}
        key = d.get("requestId") or m.get("id")
        r = reqs.setdefault(key, dict(key=key, msg_ids=set(), model=m.get("model"), recs=[]))
        r["msg_ids"].add(m.get("id"))
        r["recs"].append(dict(
            out=u.get("output_tokens", 0), stop=m.get("stop_reason"),
            kinds=[b.get("type") for b in m.get("content", [])],
            think=(u.get("output_tokens_details") or {}).get("thinking_tokens"),
            inp=u.get("input_tokens", 0), cr=u.get("cache_read_input_tokens", 0),
            cw=u.get("cache_creation_input_tokens", 0),
            ts=d.get("timestamp")))
    return list(reqs.values()), cost_state


def summarize(path):
    reqs, cs = read_requests(path)
    s = {"first": collections.Counter(), "last": collections.Counter(), "max": collections.Counter(),
         "records": 0}
    thinking_chars_blocks = 0
    n_null_stop_last = 0
    inconsistent_in = 0
    per_req = []
    for r in reqs:
        recs = r["recs"]
        s["records"] += len(recs)
        f, l = recs[0], recs[-1]
        mx = max(recs, key=lambda x: x["out"])
        if len({(x["inp"], x["cr"], x["cw"]) for x in recs}) > 1:
            inconsistent_in += 1
        for name, x in (("first", f), ("last", l), ("max", mx)):
            s[name]["input_tokens"] += x["inp"]
            s[name]["output_tokens"] += x["out"]
            s[name]["cache_read_input_tokens"] += x["cr"]
            s[name]["cache_creation_input_tokens"] += x["cw"]
        n_null_stop_last += l["stop"] is None
        per_req.append(dict(key=r["key"][-8:], model=r["model"], n_rec=len(recs), first_out=f["out"],
                            last_out=l["out"], max_out=mx["out"], last_stop=l["stop"],
                            any_stop=[x["stop"] for x in recs if x["stop"]],
                            kinds=[k for x in recs for k in x["kinds"]],
                            think_tokens=[x["think"] for x in recs if x["think"] is not None]))
    return dict(path=path, requests=len(reqs), records=s["records"],
                n_null_stop_last=n_null_stop_last, input_inconsistent_requests=inconsistent_in,
                sums={k: dict(s[k]) for k in ("first", "last", "max")}, per_request=per_req,
                msg_id_to_request_1to1=all(len(r["msg_ids"]) == 1 for r in reqs),
                cost_state=cs)


def session(main_path):
    out = {"main": summarize(main_path), "subagents": {}}
    sub = os.path.join(main_path[:-6], "subagents")
    for p in sorted(glob.glob(os.path.join(sub, "agent-*.jsonl"))):
        out["subagents"][os.path.basename(p)[6:-6]] = summarize(p)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--file":
        print(json.dumps(summarize(sys.argv[2]), indent=1, default=list))
    else:
        print(json.dumps(session(sys.argv[1]), indent=1, default=list))
