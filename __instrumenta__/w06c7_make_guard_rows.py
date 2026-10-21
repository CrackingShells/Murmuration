# w06-c7: puts the permission-guard rows (one `command` handler per `if` rule, each with onFailure block) into hooks/hooks.json under PreToolUse; inputs: hooks/hooks.json (any other rows are kept as they are; earlier guard rows are replaced, so it can be re-run on top of someone else's edit); outputs: hooks/hooks.json rewritten, and the number of rows on stdout. Run from the repository root: python3 -I __instrumenta__/w06c7_make_guard_rows.py [--check]
import json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CMD = 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/permission_guard.py"'

# Bash rules. The matcher normalises each subcommand (quotes removed, env assignments, redirections and `timeout`/`nohup` wrappers stripped) and
# treats a command with an expansion it cannot resolve (`$(...)`, backticks, `$VAR` other than a few) as matching EVERY rule: the guard then runs once per row.
BASH = [
    # G1: the words of the bypass
    "*bypass*", "*dangerously*",
    # G2: a child that leaves the user's settings and hooks (--setting-sources with a first value other than `user`, an empty value before a flag, `=` with nothing)
    "*--setting-sources p*", "*--setting-sources l*", "*--setting-sources -*", "*--setting-sources=p*", "*--setting-sources=l*", "*--setting-sources=)",
    "*claude*--bare*", "*claude*--safe-mode*", "*disableAllHooks*", "*CLAUDE_CONFIG_DIR=*",
    # G3: writes by program, naming a settings file (redirections are not visible to `if`; see the claim)
    "*tee *settings*", "*cp *settings*", "*mv *settings*", "*rm *settings*", "*sed *-i*settings*", "*open(*settings*", "*writeFile*settings*",
]
# File tools: one rule per tool (an Edit rule does not match Write).
FILES = ["**/.claude/settings*.json", "**/managed-settings*", "**/managed-settings.d/**"]


def handler(rule):
    return {"type": "command", "if": rule, "command": CMD, "timeout": 5, "onFailure": "block"}


def groups():
    g = [{"matcher": "Bash", "hooks": [handler("Bash(%s)" % r) for r in BASH]}]
    g.append({"matcher": "Write|Edit", "hooks": [handler("%s(%s)" % (t, p)) for t in ("Write", "Edit") for p in FILES]})
    return g


def main():
    path = os.path.join(ROOT, "hooks", "hooks.json")
    cfg = json.load(open(path))
    pre = [g for g in cfg["hooks"].get("PreToolUse", []) if not any("permission_guard" in h.get("command", "") for h in g.get("hooks", []))]
    cfg["hooks"]["PreToolUse"] = groups() + pre
    if "--check" in sys.argv:
        print("rows:", sum(len(g["hooks"]) for g in groups()), "(guard rows present)" if cfg == json.load(open(path)) else "(hooks.json differs)")
        return
    json.dump(cfg, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print("rows:", sum(len(g["hooks"]) for g in groups()))


main()
