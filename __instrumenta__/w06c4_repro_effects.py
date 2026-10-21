# w06-c4 verifier: for runs of w06c4_run.py (argv: run names) counts the harness.jsonl events of the run's lab and the mcp_tool hook_success records with and without output, per hook event; output: stdout
import collections, glob, json, os, sys
S = "/private/tmp/murmuration-w06/author-w06-4/runs"; H = os.path.expanduser("~")
for name in sys.argv[1:]:
    c = collections.Counter()
    try:
        for l in open(f"{S}/{name}/lab/__statera__/harness.jsonl"):
            try: r = json.loads(l)
            except ValueError: continue
            c[r.get("event")] += 1
    except OSError: pass
    sid = json.load(open(f"{S}/{name}/run.json"))["session_id"]
    d = glob.glob(f"{H}/.claude/projects/*author-w06-4-runs-{name.replace('_','-')}-lab")[0]
    m = collections.Counter()
    for f in [f"{d}/{sid}.jsonl"] + glob.glob(f"{d}/{sid}/subagents/*.jsonl"):
        for l in open(f, errors="replace"):
            if '"hook_success"' in l and "plugin:murmuration:hooks" in l:
                a = json.loads(l)["attachment"]; m[(a["hookEvent"], "out" if (a.get("content") or a.get("stdout")) else "empty")] += 1
    print(name, "harness:", dict(c), "\n   mcp:", dict(m))
    hb = glob.glob(f"{S}/{name}/lab/__statera__/handbacks/*")
    print("   handback files:", [os.path.basename(x) for x in hb])
