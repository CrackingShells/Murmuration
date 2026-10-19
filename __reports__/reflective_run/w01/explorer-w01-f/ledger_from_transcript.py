"""Sum token usage per transcript, deduplicating assistant records by requestId.
usage: python3 -I ledger_from_transcript.py <transcript.jsonl> [more ...]
Prints raw-record sum, deduplicated sum, and per-model split. Read-only."""
import json, sys, collections
def load(path):
    raw = collections.Counter(); dd = collections.Counter(); seen = {}
    models = collections.defaultdict(collections.Counter)
    for l in open(path):
        try: d = json.loads(l)
        except Exception: continue
        if d.get("type") != "assistant": continue
        m = d.get("message", {}); u = m.get("usage") or {}
        rid = d.get("requestId") or m.get("id")
        for k in ("input_tokens","output_tokens","cache_read_input_tokens","cache_creation_input_tokens"):
            raw[k] += u.get(k, 0)
        raw["records"] += 1
        if rid not in seen:   # the last record of a request has the final output_tokens
            seen[rid] = u
        else:
            seen[rid] = u if u.get("output_tokens",0) >= seen[rid].get("output_tokens",0) else seen[rid]
            
        models[m.get("model")][rid] = 1
    for rid, u in seen.items():
        for k in ("input_tokens","output_tokens","cache_read_input_tokens","cache_creation_input_tokens"):
            dd[k] += u.get(k, 0)
    dd["requests"] = len(seen)
    return raw, dd, {k: len(v) for k, v in models.items()}
if __name__ == "__main__":
    for p in sys.argv[1:]:
        raw, dd, mo = load(p)
        print(p.split("/")[-1], "\n  raw records:", dict(raw), "\n  dedup by requestId:", dict(dd), "\n  models:", mo)
