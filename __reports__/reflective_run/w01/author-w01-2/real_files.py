"""CHECKED: share of requests whose last record has stop_reason null, per transcript file, in the real sessions.
usage: python3 -I real_files.py <main-session.jsonl> ...   (read-only)"""
import sys, glob, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sumtx
tot = collections.Counter()
for main in sys.argv[1:]:
    files = [main] + sorted(glob.glob(main[:-6] + "/subagents/agent-*.jsonl"))
    for f in files:
        s = sumtx.summarize(f)
        kind = "main" if f == main else "agent"
        # a trailing request that is the very last record may legitimately be in flight; count it separately
        nulls = s["n_null_stop_last"]
        meta = {}
        mp = f[:-6] + ".meta.json"
        if os.path.exists(mp):
            try: meta = json.load(open(mp))
            except Exception: pass
        tot[(os.path.basename(main)[:8], kind, "files")] += 1
        tot[(os.path.basename(main)[:8], kind, "requests")] += s["requests"]
        tot[(os.path.basename(main)[:8], kind, "null_requests")] += nulls
        if kind == "agent" and nulls == 0:
            tot[(os.path.basename(main)[:8], kind, "files_all_final")] += 1
            print("  all-final agent file:", os.path.basename(f), meta.get("agentType"), "requests", s["requests"])
for k in sorted(tot): print(k, tot[k])
