# w06-c9: e1, process mode: runs the hook commands of hooks/hooks.json of two plugin trees as the platform starts them (`sh -c <command>`, payload on stdin, CLAUDE_PLUGIN_ROOT set, cwd = lab) over one scripted worker life (dispatch, start, quiet calls, a note at 50%, the over-budget note, the 150% block, a hand-back denied once and then saved, stop); inputs: --old ROOT, --new ROOT, --out DIR (scratch, must not exist), optional --mutate; output: one line per command start with exit code and stdout of each tree, and EQUAL or DIFF; exit 1 on a difference
"""The clock is the machine's, so the fixture keeps time out of the text: T = 100000 minutes (the note reads `0.0 of 100000 min (0%)`), and the log's `active_s` and `t` are dropped from the comparison.
Compared per start: exit code, stdout. At the end: harness.jsonl lines (without `t`, `active_s`), the hand-back files, the `.denied` marker. --mutate: the new tree's `hooks.json` row for PostToolUse(SubagentHandback) is
changed to start `budget` instead of `handback` (it must give a DIFF)."""
import argparse, json, os, shlex, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--old", required=True)
ap.add_argument("--new", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--mutate", action="store_true")
args = ap.parse_args()
os.makedirs(args.out)


def rows(root, event, tool=None):
    import re
    for g in json.load(open(root + "/hooks/hooks.json"))["hooks"].get(event, []):
        if g.get("matcher") is None or re.fullmatch(g["matcher"], tool or ""):
            for h in g["hooks"]:
                yield h["command"].replace("${CLAUDE_PLUGIN_ROOT}", root)


def asst(rid, out, model="claude-sonnet-5-5"):
    return json.dumps({"type": "assistant", "requestId": rid, "message": {"id": "m" + rid, "model": model, "content": [{"type": "text", "text": "x"}],
                                                                          "usage": dict(input_tokens=2, output_tokens=out, cache_read_input_tokens=0, cache_creation_input_tokens=0)}}) + "\n"


def life(tag, root):
    lab = "%s/%s/lab" % (args.out, tag)
    sess = "%s/%s/sess" % (args.out, tag)
    os.makedirs(lab + "/__statera__"); os.makedirs(lab + "/__reports__"); os.makedirs(sess + "/subagents")
    aid, tx = "ex1", sess + "/subagents/agent-ex1.jsonl"
    json.dump({"name": "explorer-w99-1"}, open(sess + "/subagents/agent-ex1.meta.json", "w"))
    brief = "Your name is explorer-w99-1.\nBudget: USD 1.00\nTime: min 100000\nGo."
    open(tx, "w").write(json.dumps({"type": "user", "message": {"role": "user", "content": brief}}) + "\n" + asst("r0", 1000))
    base = dict(cwd=lab, session_id="s", transcript_path=sess + ".jsonl", permission_mode="auto")
    wk = dict(base, agent_id=aid, agent_type="murmuration:explorer")
    seq = [("dispatch", dict(base, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="tu1", tool_input=dict(subagent_type="murmuration:explorer", name="explorer-w99-1", prompt=brief)), None),
           ("start", dict(wk, hook_event_name="SubagentStart"), None),
           ("quiet", dict(wk, hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": "ls"}), None),
           ("quiet-batch", dict(wk, hook_event_name="PostToolBatch", tool_calls=[{"tool_name": "Bash"}]), None),
           ("half", dict(wk, hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": "ls"}), asst("r1", 50000)),
           ("half-batch", dict(wk, hook_event_name="PostToolBatch", tool_calls=[{"tool_name": "Bash"}]), None),
           ("over", dict(wk, hook_event_name="PostToolBatch", tool_calls=[{"tool_name": "Bash"}]), asst("r2", 60000)),
           ("block", dict(wk, hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": "ls"}), asst("r3", 50000)),
           ("deny", dict(wk, hook_event_name="PreToolUse", tool_name="SubagentHandback", tool_input={"message": "done é"}), None),
           ("deny-again", dict(wk, hook_event_name="PreToolUse", tool_name="SubagentHandback", tool_input={"message": "done é"}), None),
           ("save", dict(wk, hook_event_name="PostToolUse", tool_name="SubagentHandback", tool_input={"message": "done é"}), None),
           ("stop", dict(wk, hook_event_name="SubagentStop", agent_transcript_path=tx, last_assistant_message="done é"), None),
           ("main", dict(base, hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": "ls"}), None),
           ("not-json", "this is not json", None)]
    out = []
    for name, payload, grow in seq:
        if grow:
            open(tx, "a").write(grow)
        ev = payload if isinstance(payload, dict) else {}
        for k, cmd in enumerate(rows(root, ev.get("hook_event_name", "PostToolUse"), ev.get("tool_name"))):
            if args.mutate and tag == "new" and name == "save" and "handback" in cmd:
                cmd = cmd.replace("handback", "budget")
            p = subprocess.run(["sh", "-c", cmd], input=payload if isinstance(payload, str) else json.dumps(payload), capture_output=True, text=True, cwd=lab,
                               env={**{k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}, "CLAUDE_PLUGIN_ROOT": root})
            out.append(("%s#%d" % (name, k), p.returncode, p.stdout, p.stderr))
    snap = {}
    log = lab + "/__statera__/harness.jsonl"
    snap["log"] = [json.dumps({k: v for k, v in json.loads(l).items() if k not in ("t", "active_s")}) for l in open(log)] if os.path.exists(log) else []
    hb = lab + "/__statera__/handbacks"
    snap["handbacks"] = {n: [l for l in open(hb + "/" + n).read().splitlines() if not l.startswith("## hand-back")] for n in sorted(os.listdir(hb))} if os.path.isdir(hb) else {}
    snap["denied"] = sorted(n for n in os.listdir(lab + "/__statera__/.harness") if n.endswith(".denied")) if os.path.isdir(lab + "/__statera__/.harness") else []
    return out, snap


old, so = life("old", os.path.abspath(args.old))
new, sn = life("new", os.path.abspath(args.new))
bad = 0
for a, b in zip(old, new):
    same = a == b
    bad += not same
    print("%-14s rc %d/%d stdout %4d/%4d bytes stderr %d/%d %s" % (a[0], a[1], b[1], len(a[2]), len(b[2]), len(a[3]), len(b[3]), "EQUAL" if same else "DIFF"))
for key in ("log", "handbacks", "denied"):
    same = so[key] == sn[key]
    bad += not same
    print("%-14s %s (%d entries)" % (key, "EQUAL" if same else "DIFF", len(so[key])))
print("starts %d / %d, differences %d" % (len(old), len(new), bad + (len(old) != len(new))))
sys.exit(1 if bad or len(old) != len(new) else 0)
