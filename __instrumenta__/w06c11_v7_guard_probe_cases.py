# Offline probes of scripts/permission_guard.py decide(): own cases for holes (unbalanced quote, inert first word, uppercase, env tricks) and false denials; input: guard path; output: case, decision (stdout)
import importlib.util, sys
spec = importlib.util.spec_from_file_location("pg", sys.argv[1]); G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
cases = [
 ("quote-hole grep it's; claude bypass", "grep -n it's f; claude -p hi --dangerously-skip-permissions"),
 ("quote-hole echo it's; claude bypass", "echo it's; claude -p hi --dangerously-skip-permissions"),
 ("comment apostrophe then claude", "# don't\nclaude -p hi --dangerously-skip-permissions"),
 ("comment apostrophe + grep first", "grep -c x f # don't\nclaude -p hi --dangerously-skip-permissions"),
 ("Claude capitalised alias", "Claude -p hi --dangerously-skip-permissions"),
 ("path claude", "/Users/x/.local/bin/claude -p hi --dangerously-skip-permissions"),
 ("alias via variable", "C=claude; $C -p hi --dangerously-skip-permissions"),
 ("cat | claude", "cat p | claude -p --permission-mode bypassPermissions"),
 ("cat head names claude no", "cat x | python3 -c 'import os;os.system(\"cl\"+\"aude --dangerously-skip-permissions\")'"),
 ("env var holds flag", "F=--dangerously-skip-permissions; claude -p hi $F"),
 ("split flag", "claude -p hi --dangerously-skip-perm''issions"),
 ("grep-first with claude", "grep -rn bypassPermissions . && claude -p hi"),
 ("commit msg mentions", "git commit -m 'document claude bypassPermissions mode'"),
 ("echo mention claude", "echo 'run claude with --dangerously-skip-permissions is forbidden'"),
 ("echo mention claude 2", "echo \"never use claude --permission-mode bypassPermissions\" >> notes.txt"),
 ("python -c claude word", "python3 -c \"print('claude bypassPermissions')\""),
 ("settings write rel", "echo '{}' > .claude/settings.local.json"),
 ("settings write via var", "F=.claude/settings.local.json; echo '{}' > $F"),
 ("cp read source", "cp .claude/settings.local.json /tmp/bak"),
 ("cat settings", "cat ~/.claude/settings.json"),
 ("export CLAUDE_CONFIG_DIR python", "CLAUDE_CONFIG_DIR=/tmp/x python3 s.py"),
 ("claude plugin list", "claude plugin list"),
 ("no-space redirect", "echo '{}'>.claude/settings.json"),
 ("node write", "node -e \"require('fs').writeFileSync('.claude/settings.json','{}')\""),
]
for n, c in cases:
    r = G.decide(dict(tool_name="Bash", tool_input={"command": c}, cwd="/h/proj"))
    print("%-38s %s" % (n, r[0] if r else "ALLOW"))
