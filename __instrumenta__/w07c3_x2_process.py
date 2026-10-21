# w07-c3: x2 offline half: runs every hook handler of two plugin trees (A: shell form through `sh -c`, B: exec form spawned directly, no shell, as the platform does) over one scripted life (user prompt, resume, PI dispatch, worker start, quiet calls, a note at 50%, over budget, the 150% block, hand-back denied once then saved, stop, guard attack and ordinary events, malformed input) and compares exit code, stdout, stderr, log files, hand-back files, user_words.md; inputs: --a ROOT --b ROOT --out DIR [--mutate]; output: one line per handler start with EQUAL or DIFF, exit 1 on a difference
"""usage: w07c3_x2_process.py --a TREE_A --b TREE_B --out SCRATCH   (SCRATCH must not exist)
Time is kept out of the text as in w06c9_e2e_commands.py (T = 100000 minutes). For an event the script starts every handler of every matching group (the `if` rule only decides whether the platform starts the
guard; the guard decides on its own, so running them all over-approximates and checks each row). A: ['sh','-c', command with ${CLAUDE_PLUGIN_ROOT} replaced]; B: [command, *args] with the same replacement, no shell.
CLAUDE_PLUGIN_ROOT and MURMURATION_GUARD_LOG are in the environment of both. --mutate: B's guard rows start run_hook.py budget instead (they must then DIFF). The attack flag is built from parts."""
import argparse, json, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--a", required=True); ap.add_argument("--b", required=True); ap.add_argument("--out", required=True); ap.add_argument("--mutate", action="store_true")
args = ap.parse_args()
args.out = os.path.abspath(args.out)
os.makedirs(args.out)
FLAG = "--" + "danger" + "ously-skip-permissions"


def handlers(root, event, tool=None):
    for g in json.load(open(root + "/hooks/hooks.json"))["hooks"].get(event, []):
        if g.get("matcher") is None or re.fullmatch(g["matcher"], tool or ""):
            yield from g["hooks"]


def start(root, h, payload, lab, env, form, mutate):
    sub = lambda s: s.replace("${CLAUDE_PLUGIN_ROOT}", root)
    if form == "A":
        argv = ["sh", "-c", sub(h["command"])]
    else:
        argv = [sub(h["command"])] + [sub(t) for t in h["args"]]
        if mutate and "permission_guard" in " ".join(argv):
            argv = [sub(h["command"]), "-S", "-I", root + "/scripts/run_hook.py", "budget"]
    return subprocess.run(argv, input=payload, capture_output=True, text=True, cwd=lab, env=env)


def asst(rid, out):
    return json.dumps({"type": "assistant", "requestId": rid, "message": {"id": "m" + rid, "model": "claude-sonnet-5-5", "content": [{"type": "text", "text": "x"}],
                                                                          "usage": dict(input_tokens=2, output_tokens=out, cache_read_input_tokens=0, cache_creation_input_tokens=0)}}) + "\n"


def life(tag, root, form):
    base_dir = "%s/%s" % (args.out, tag)
    lab, sess, glog = base_dir + "/lab", base_dir + "/sess", base_dir + "/guard.log"
    os.makedirs(lab + "/__statera__"); os.makedirs(lab + "/__reports__"); os.makedirs(sess + "/subagents")
    aid, tx = "ex1", sess + "/subagents/agent-ex1.jsonl"
    json.dump({"name": "explorer-w99-1"}, open(sess + "/subagents/agent-ex1.meta.json", "w"))
    brief = "Your name is explorer-w99-1.\nBudget: USD 1.00\nTime: min 100000\nGo."
    open(tx, "w").write(json.dumps({"type": "user", "message": {"role": "user", "content": brief}}) + "\n" + asst("r0", 1000))
    open(sess + ".jsonl", "w").write(json.dumps({"type": "user", "cwd": lab, "message": {"role": "user", "content": "hi"}}) + "\n")
    base = dict(cwd=lab, session_id="s", transcript_path=sess + ".jsonl", permission_mode="auto")
    wk = dict(base, agent_id=aid, agent_type="murmuration:explorer")
    bash = lambda c: dict(base, hook_event_name="PreToolUse", tool_name="Bash", tool_input={"command": c})
    wr = lambda tool, p, extra=None: dict(base, hook_event_name="PreToolUse", tool_name=tool, tool_input=dict({"file_path": p}, **(extra or {})))
    post = dict(wk, hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": "ls"})
    batch = dict(wk, hook_event_name="PostToolBatch", tool_calls=[{"tool_name": "Bash"}])
    seq = [("prompt", dict(base, hook_event_name="UserPromptSubmit", prompt="Please look at the plan. é ü 'quoted' $HOME `x`"), None),
           ("prompt-injected", dict(base, hook_event_name="UserPromptSubmit", prompt="<task-notification>x</task-notification>"), None),
           ("resume", dict(base, hook_event_name="SessionStart", source="resume"), None),
           ("dispatch", dict(base, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="tu1", tool_input=dict(subagent_type="murmuration:explorer", name="explorer-w99-1", prompt=brief)), None),
           ("start", dict(wk, hook_event_name="SubagentStart"), None),
           ("quiet", post, None), ("quiet-batch", batch, None),
           ("half", post, asst("r1", 50000)), ("half-batch", batch, None),
           ("over", batch, asst("r2", 60000)),
           ("block", post, asst("r3", 50000)),
           ("deny", dict(wk, hook_event_name="PreToolUse", tool_name="SubagentHandback", tool_input={"message": "done é"}), None),
           ("deny-again", dict(wk, hook_event_name="PreToolUse", tool_name="SubagentHandback", tool_input={"message": "done é"}), None),
           ("save", dict(wk, hook_event_name="PostToolUse", tool_name="SubagentHandback", tool_input={"message": "done é"}), None),
           ("stop", dict(wk, hook_event_name="SubagentStop", agent_transcript_path=tx, last_assistant_message="done é"), None),
           ("main-post", dict(base, hook_event_name="PostToolUse", tool_name="Bash", tool_input={"command": "ls"}), None),
           ("g-bypass", bash("claude %s -p hi" % FLAG), None),
           ("g-bypass-quoted", bash("echo ok; claude -p 'x' '%s'" % FLAG), None),
           ("g-settings-redirect", bash("echo '{}' > .claude/settings.json"), None),
           ("g-config-dir", bash("CLAUDE_CONFIG_DIR=/tmp/x claude -p hi"), None),
           ("g-ordinary", bash("git status --short"), None),
           ("g-heredoc", bash("cat > f.txt <<'EOF'\n$(date) `id`\nEOF"), None),
           ("g-mention", bash("grep -n 'dangerously' notes.md"), None),
           ("g-unicode", bash("echo é ü '☃'"), None),
           ("w-settings", wr("Write", lab + "/probe/.claude/settings.json", {"content": "{}"}), None),
           ("w-managed", wr("Write", "/etc/claude-code/managed-settings.json", {"content": "{}"}), None),
           ("w-py-bypass", wr("Write", lab + "/t.py", {"content": "import subprocess\nsubprocess.run(['claude', '%s'])\n" % FLAG}), None),
           ("e-sh-bypass", wr("Edit", lab + "/t.sh", {"old_string": "x", "new_string": "claude %s" % FLAG}), None),
           ("w-py-ordinary", wr("Write", lab + "/t.py", {"content": "print(1)\n"}), None),
           ("nb-ordinary", wr("NotebookEdit", lab + "/n.ipynb", {"new_source": "1+1"}), None),
           ("not-json", "this is not json", None), ("empty", "", None), ("array", "[]", None), ("null-input", dict(base, hook_event_name="PreToolUse", tool_name="Bash", tool_input=None), None)]
    out = []
    env = {**{k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}, "CLAUDE_PLUGIN_ROOT": root, "MURMURATION_GUARD_LOG": glog}
    for name, payload, grow in seq:
        if grow:
            open(tx, "a").write(grow)
        ev = payload if isinstance(payload, dict) else {}
        event = ev.get("hook_event_name") or ("PreToolUse" if name in ("not-json", "empty", "array") else "PostToolUse")
        hs = list(handlers(root, event, ev.get("tool_name") if name not in ("not-json", "empty", "array") else "Bash"))
        for k, h in enumerate(hs):
            p = start(root, h, payload if isinstance(payload, str) else json.dumps(payload), lab, env, form, args.mutate and tag == "new")
            out.append(("%s#%d" % (name, k), p.returncode, p.stdout.replace(root, "<ROOT>").replace(lab, "<LAB>"), p.stderr.replace(root, "<ROOT>").replace(lab, "<LAB>")))
    snap = {}
    log = lab + "/__statera__/harness.jsonl"
    snap["harness.jsonl"] = [json.dumps({k: v for k, v in json.loads(l).items() if k not in ("t", "active_s")}) for l in open(log)] if os.path.exists(log) else []
    snap["guard.log"] = [l.replace(lab, "<LAB>") for l in open(glog).read().splitlines()] if os.path.exists(glog) else []
    uw = lab + "/__statera__/user_words.md"
    snap["user_words.md"] = [l for l in open(uw).read().splitlines() if not re.match(r"^#+ .*\d{4}-\d\d-\d\d", l)] if os.path.exists(uw) else []
    hb = lab + "/__statera__/handbacks"
    snap["handbacks"] = {n: [l for l in open(hb + "/" + n).read().splitlines() if not l.startswith("## hand-back")] for n in sorted(os.listdir(hb))} if os.path.isdir(hb) else {}
    snap["denied"] = sorted(n for n in os.listdir(lab + "/__statera__/.harness") if n.endswith(".denied")) if os.path.isdir(lab + "/__statera__/.harness") else []
    return out, snap


old, so = life("old", os.path.abspath(args.a), "A")
new, sn = life("new", os.path.abspath(args.b), "B")
bad = 0
shown = 0
for a, b in zip(old, new):
    same = a == b
    bad += not same
    print("%-24s rc %d/%d stdout %4d/%4d bytes stderr %3d/%3d %s" % (a[0], a[1], b[1], len(a[2]), len(b[2]), len(a[3]), len(b[3]), "EQUAL" if same else "DIFF"))
for key in so:
    same = so[key] == sn[key]
    bad += not same
    print("%-24s %s (%d entries)" % (key, "EQUAL" if same else "DIFF", len(so[key])))
denies = sum(1 for a in old if '"permissionDecision": "deny"' in a[2] or '"permissionDecision":"deny"' in a[2])
print("starts %d / %d, differences %d; handler starts whose stdout is a guard deny (A): %d; starts with stdout text (A): %d" % (len(old), len(new), bad + (len(old) != len(new)), denies, sum(1 for a in old if a[2].strip())))
sys.exit(1 if bad or len(old) != len(new) else 0)
