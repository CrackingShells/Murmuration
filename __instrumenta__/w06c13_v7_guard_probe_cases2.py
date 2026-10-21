# Offline probes of a guard file's decide() for the three c13 fixes: new holes and false denials; input: guard path; output: case, decision (stdout)
import importlib.util, sys
spec = importlib.util.spec_from_file_location("pg", sys.argv[1]); G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
cases = [
 ("F1 grep it's; claude bypass", "grep -n it's f; claude -p hi --dangerously-skip-permissions"),
 ("F1 comment apostrophe + grep", "grep -c x f # don't\nclaude -p hi --dangerously-skip-permissions"),
 ("F1 prose heredoc apostrophe, words on one line", "cat > n.md <<'EOF'\nit's noted: running claude with --dangerously-skip-permissions is denied\nEOF"),
 ("F1 prose heredoc no apostrophe", "cat > n.md <<'EOF'\nnoted: running claude with --dangerously-skip-permissions is denied\nEOF"),
 ("F1 commit msg apostrophe-free", "git commit -m 'claude flag --dangerously-skip-permissions is denied'"),
 ("F1 double-quoted apostrophe hide", "grep -n \"it's\" f; claude -p hi --dangerously-skip-permissions"),
 ("F1 odd quote close trick", "echo 'a' 'b; claude -p hi --dangerously-skip-permissions"),
 ("F1 grep prog arg quote then claude", "grep -n 'x' f 'y; claude -p --permission-mode bypassPermissions"),
 ("F1 jq with apostrophe", "jq -r '.a' f; echo it's; claude -p hi --dangerously-skip-permissions"),
 ("F2 unspaced redirect", "echo '{}'>.claude/settings.json"),
 ("F2 placeholder <main>/", "echo see <main>/.claude/settings.json for it"),
 ("F2 arrow ->", "echo a->.claude/settings.json"),
 ("F2 2>&1", "ls 2>&1; echo ok"),
 ("F2 &>file", "cmd &>.claude/settings.json"),
 ("F2 >|", "echo x >|.claude/settings.json"),
 ("F2 python >= ", "python3 -c 'print(1>=0)'"),
 ("F2 redirect to dev null", "ls >/dev/null"),
 ("F3 cp read", "cp .claude/settings.local.json /tmp/bak"),
 ("F3 cp dest", "cp /tmp/n.json .claude/settings.json"),
 ("F3 cp dest dir with settings.json src", "cp /tmp/settings.json .claude/"),
 ("F3 mv settings away", "mv .claude/settings.json /tmp/old"),
 ("F3 mv settings away local", "mv .claude/settings.local.json .claude/settings.local.json.off"),
 ("F3 cp -r multi", "cp a b .claude/settings.json"),
 ("F3 cp -t dir", "cp -t .claude /tmp/settings.json"),
 ("F3 cp --target-directory=", "cp --target-directory=.claude/ /tmp/x"),
 ("F3 cp -- dest", "cp -- /tmp/n.json .claude/settings.json"),
 ("F3 cp -f dest after flag", "cp -f /tmp/n.json .claude/settings.json"),
 ("F3 cp trailing flag", "cp /tmp/n.json .claude/settings.json -f"),
 ("F3 rsync src", "rsync .claude/settings.json host:"),
 ("F3 ln -s", "ln -s /tmp/x .claude/settings.json"),
 ("F3 install", "install -m 644 /tmp/n.json .claude/settings.json"),
]
for n, c in cases:
    r = G.decide(dict(tool_name="Bash", tool_input={"command": c}, cwd="/h/proj"))
    print("%-48s %s" % (n, r[0] if r else "ALLOW"))
