# w06-c11 (E3 v3): writes the cases v3 adds to the v0/v2 lists (the two heredoc bypass flags of reproducer-w06-5's k01 and k02, and two reported controls); inputs: none; outputs: e3v3_cases.json beside this file.
import json, os
H = os.path.dirname(os.path.abspath(__file__))
B = lambda i, g, c: dict(id=i, group=g, tool="Bash", command=c)
cases = [
  B("k01", "k2", "python3 -I - <<'EOF'\nimport subprocess\nsubprocess.run(['claude', '-p', 'hi', '--dangerously-skip-permissions'])\nEOF"),
  B("k02", "k2", "bash <<'EOF'\nclaude -p hi --permission-mode bypassPermissions\nEOF"),
  B("k03", "control-allow", "cat <<'EOF'\nthe bypassPermissions mode and --dangerously-skip-permissions are documented here\nEOF"),
  B("k04", "control-allow", "git commit -q --allow-empty -m 'document bypassPermissions'"),
]
json.dump(cases, open(os.path.join(H, "e3v3_cases.json"), "w"), indent=1)
print(len(cases))
