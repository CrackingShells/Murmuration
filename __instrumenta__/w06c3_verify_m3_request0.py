# w06-c3 verifier: first-request input tokens (input + cache read + cache creation) of the main thread and of each worker from session transcripts, per run directory; independent of the author's analyzer; inputs: project folder name under ~/.claude/projects, run dirs; output: one line per thread
import json, sys, os, glob
proj = os.path.expanduser("~/.claude/projects/") + sys.argv[1]
def first_usage(path):
    for l in open(path):
        x = json.loads(l)
        if x.get("type") == "assistant":
            u = x["message"]["usage"]
            return u["input_tokens"] + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0), u
for d in sys.argv[2:]:
    sid = json.load(open(d + "/run.json"))["session_id"]
    n, u = first_usage("%s/%s.jsonl" % (proj, sid))
    print(os.path.basename(d), "main", n)
    for w in sorted(glob.glob("%s/%s/subagents/agent-*.jsonl" % (proj, sid))):
        n, u = first_usage(w); print(os.path.basename(d), "worker", os.path.basename(w)[6:12], n)
