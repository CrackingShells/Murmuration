# w06-c14 verifier check: runs hand-picked PreToolUse events through the hooks.json row command (read from each tree's own hooks.json, run via `sh -c` with CLAUDE_PLUGIN_ROOT and MURMURATION_GUARD_LOG set) of two plugin trees and prints exit code, stdout, stderr and log line side by side; inputs: old tree dir, new tree dir; output: table on stdout; independent of the author's w06c14_cmd_equal.py
import json, os, subprocess, sys, tempfile

old, new = sys.argv[1:3]


def rows(tree):
    h = json.load(open(tree + "/hooks/hooks.json"))["hooks"]["PreToolUse"]
    out = {}
    for g in h:
        for hk in g["hooks"]:
            if "permission_guard" in hk["command"]:
                out[(g["matcher"], hk.get("if"))] = hk["command"]
    return out


def ev(tool, **inp):
    return json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": inp, "cwd": "/tmp", "session_id": "x"})


CASES = [
    ("Bash", "deny: bypass flag", ev("Bash", command="claude -p hi --permission-mode bypassPermissions")),
    ("Bash", "deny: skip flag + prose apostrophe", ev("Bash", command="grep -n it's f; claude -p hi --dangerously-skip-permissions")),
    ("Bash", "deny: settings write", ev("Bash", command="echo '{}' > .claude/settings.json")),
    ("Bash", "deny: config dir", ev("Bash", command="CLAUDE_CONFIG_DIR=/tmp/x claude -p hi")),
    ("Bash", "allow: ordinary", ev("Bash", command="git status --short")),
    ("Bash", "allow: $() and heredoc", ev("Bash", command="echo today-$(date +%Y)\ncat > n.md <<'EOF'\nx $(y)\nEOF")),
    ("Bash", "allow: mention only", ev("Bash", command="grep -rn bypassPermissions docs")),
    ("Bash", "allow: unicode", ev("Bash", command="echo 'héllo ☃'")),
    ("Bash", "malformed: empty stdin", ""),
    ("Bash", "malformed: not json", "not json{"),
    ("Bash", "malformed: list", "[]"),
    ("Bash", "malformed: null tool_input", json.dumps({"tool_name": "Bash", "tool_input": None})),
    ("Bash", "malformed: command is int", json.dumps({"tool_name": "Bash", "tool_input": {"command": 5}})),
    ("Write|Edit|NotebookEdit", "deny: Write py adding bypass", ev("Write", file_path="/tmp/lab/s.py", content="import subprocess\nsubprocess.run(['claude','--dangerously-skip-permissions'])\n")),
    ("Write|Edit|NotebookEdit", "deny: Write settings.local.json", ev("Write", file_path="/tmp/lab/.claude/settings.local.json", content='{"permissions":{"defaultMode":"bypassPermissions"}}')),
    ("Write|Edit|NotebookEdit", "deny: Edit sh adding bypass", ev("Edit", file_path="/tmp/lab/r.sh", old_string="echo hi", new_string="claude -p x --dangerously-skip-permissions")),
    ("Write|Edit|NotebookEdit", "allow: Write py ordinary", ev("Write", file_path="/tmp/lab/ok.py", content="print('hello')\n")),
    ("Write|Edit|NotebookEdit", "allow: Edit py ordinary", ev("Edit", file_path="/tmp/lab/ok.py", old_string="hello", new_string="world")),
]


def run(tree, matcher, payload, log):
    r = rows(tree)
    cmd = next(c for (m, i), c in r.items() if m == matcher)   # the first row of that matcher (Bash: the only one; Write: the settings row, same command string)
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=tree, MURMURATION_GUARD_LOG=log)
    p = subprocess.run(["sh", "-c", cmd], input=payload, capture_output=True, text=True, env=env, cwd="/tmp")
    ll = open(log).read() if os.path.exists(log) else ""
    return p.returncode, p.stdout, p.stderr.replace(tree, "TREE"), ll


ro, rn = rows(old), rows(new)
print("rows with the guard: old %d, new %d; commands old: %s; new: %s" % (len(ro), len(rn), sorted(set(ro.values())), sorted(set(rn.values()))))
nd = 0
for matcher, label, payload in CASES:
    res = []
    for tree in (old, new):
        log = tempfile.mktemp()
        res.append(run(tree, matcher, payload, log))
    same = res[0] == res[1]
    nd += not same
    dec = "deny" if '"deny"' in res[1][1] else "allow/none"
    print("%-5s rc=%d/%d %-10s log-lines=%d/%d  %s" % ("EQUAL" if same else "DIFF", res[0][0], res[1][0], dec, res[0][3].count("\n"), res[1][3].count("\n"), label))
    if not same:
        print("   old:", res[0]); print("   new:", res[1])
print("cases", len(CASES), "differing", nd)
