# w06-c4 verifier: for one outage run of w06c4_run.py (argv: run name), lists in the PI's and each worker's transcript the records that mention 'Hooks down' or 'HOOKS DOWN' (line number, type, attachment type, role, first 160 chars) and the assistant records after them that quote it; output: stdout. Prints no identifiers beyond the run's own ids.
import glob, json, os, sys
S = "/private/tmp/murmuration-w06/author-w06-4/runs"; H = os.path.expanduser("~")
name = sys.argv[1]
sid = json.load(open(f"{S}/{name}/run.json"))["session_id"]
d = glob.glob(f"{H}/.claude/projects/*author-w06-4-runs-{name.replace('_','-')}-lab")[0]
files = [("PI", f"{d}/{sid}.jsonl")] + [("W" + os.path.basename(f)[6:12], f) for f in sorted(glob.glob(f"{d}/{sid}/subagents/agent-*.jsonl"))]
for who, f in files:
    print("==", who, os.path.basename(f))
    for i, line in enumerate(open(f, errors="replace"), 1):
        if "Hooks down" in line or "HOOKS DOWN" in line:
            r = json.loads(line); a = r.get("attachment") or {}
            msg = r.get("message") or {}
            role = msg.get("role")
            txt = json.dumps(a if a else msg)[:260]
            print(f"  L{i} type={r.get('type')} att={a.get('type')} role={role} {txt}")
