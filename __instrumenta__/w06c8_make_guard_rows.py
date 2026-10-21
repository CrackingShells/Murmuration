# w06-c8 (E3 v1): puts the v1 permission-guard rows into hooks/hooks.json under PreToolUse (replacing any earlier guard rows, keeping every other row); inputs: hooks/hooks.json, `--arm A` (registered: three Bash rows) or `--arm B` (reported variant: the `--setting-sources` row replaced by four rows that spare `user` first); outputs: hooks/hooks.json rewritten, or with `--out FILE` a copy written there; prints the row count. Run from the repository root: python3 -I __instrumenta__/w06c8_make_guard_rows.py [--arm A|B] [--out FILE]
import json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CMD = 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/permission_guard.py"'
BASH_A = ["*bypassPermissions*", "*dangerously-skip-permissions*", "*setting-sources*"]
BASH_B = ["*bypassPermissions*", "*dangerously-skip-permissions*", "*--setting-sources p*", "*--setting-sources l*", "*--setting-sources=p*", "*--setting-sources=l*"]
SETTINGS = ["**/.claude/settings*.json", "**/managed-settings*", "**/managed-settings.d/**"]
SCRIPTS = ["**/*.py", "**/*.sh", "**/*.bash", "**/*.zsh", "**/*.js", "**/*.ts", "**/*.mjs"]


def handler(rule):
    return {"type": "command", "if": rule, "command": CMD, "timeout": 10, "onFailure": "block"}


def groups(arm="A"):
    bash = BASH_A if arm == "A" else BASH_B
    return [{"matcher": "Bash", "hooks": [handler("Bash(%s)" % r) for r in bash]},
            {"matcher": "Write|Edit", "hooks": [handler("%s(%s)" % (t, p)) for t in ("Write", "Edit") for p in SETTINGS + SCRIPTS]}]


def apply(cfg, arm="A"):
    pre = [g for g in cfg["hooks"].get("PreToolUse", []) if not any("permission_guard" in h.get("command", "") for h in g.get("hooks", []))]
    cfg["hooks"]["PreToolUse"] = groups(arm) + pre
    return cfg


if __name__ == "__main__":
    arm = sys.argv[sys.argv.index("--arm") + 1] if "--arm" in sys.argv else "A"
    path = os.path.join(ROOT, "hooks", "hooks.json")
    cfg = apply(json.load(open(path)), arm)
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else path
    json.dump(cfg, open(out, "w"), indent=2)
    open(out, "a").write("\n")
    print("rows:", sum(len(g["hooks"]) for g in groups(arm)))
