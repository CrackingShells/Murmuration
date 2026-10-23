# Replays three w08-c5 scenarios (starts that arrive in the other order than their dispatches) through the Python budget.py of two git revisions, and tabulates each start line's name against the true one (the scenario's agent-to-name map): right, WRONG, or unconfirmed (the line says so).
# usage: python3 -I w08_c5_before_after.py REPO OLD_REV NEW_REV SCRATCH > table.md   (same fixed clock and scenario runner as w08c1_replay.py; Python only)
import json, os, shutil, subprocess, sys, types, io, tarfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w08c1_replay as r, w08_c5_replay_extra as x
repo, old, new, scratch = sys.argv[1], sys.argv[2], sys.argv[3], os.path.abspath(sys.argv[4])
TRUTH = {"c5_noans": {"x1": "explorer-w09-f", "x2": "explorer-w09-e"}, "c5_bg": {"x4": "explorer-w09-h", "x3": "explorer-w09-g"}, "c5_half": {"x3": "g", "x4": "h"}}
print("| revision | scenario | start (agent id) | line says | true name | verdict |\n|:--|:--|:--|:--|:--|:--|")
for rev in (old, new):
    d = os.path.join(scratch, rev[:7]); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    tar = subprocess.run(["git", "-C", repo, "archive", rev, "scripts"], capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(d, filter="fully_trusted")
    os.makedirs(d + "/__instrumenta__"); shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "w08c1_pyshim.py"), d + "/__instrumenta__/")
    a = types.SimpleNamespace(repo=d, rust=None, realclock=False)
    for scn in x.fixed():
        if scn.name not in TRUTH:
            continue
        ctx = r.Ctx(scn, "py", os.path.join(d, "runs", scn.name), a)
        for st in scn.steps:
            ctx.do(st)
        for l in open(os.path.join(ctx.lab, "__statera__", "harness.jsonl")):
            e = json.loads(l)
            if e["event"] != "start":
                continue
            true = TRUTH[scn.name][e["agent_id"]]
            says = "unconfirmed (%s)" % e["name_candidates"] if e.get("name_unconfirmed") else e["name"]
            print("| %s | %s | %s | %s | %s | %s |" % (rev[:7], scn.name, e["agent_id"], says, true, "unconfirmed" if e.get("name_unconfirmed") else ("right" if e["name"] == true else "WRONG")))
