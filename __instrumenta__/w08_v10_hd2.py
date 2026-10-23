# w08-c13 verifier: adversarial heredoc / here-string / shift / quote forms inside `$( )` before a flag, decided by the Python and Rust guard of a BASE and a NEW tree; inputs: two trees, w08_v10_flags.json; output: stdout, one line per case that is ALLOWED on NEW (and a count). Usage: python3 -I w08_v10_hd2.py BASE_TREE NEW_TREE
import importlib.util, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FL = json.load(open(os.path.join(HERE, "w08_v10_flags.json")))["flags"]
def load(t):
    s = importlib.util.spec_from_file_location("pg" + str(abs(hash(t))), os.path.join(t, "scripts", "permission_guard.py")); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def rs(t, c):
    p = subprocess.run([os.path.join(t, "bin", "aarch64-apple-darwin", "murmuration"), "guard"], input=json.dumps(dict(tool_name="Bash", tool_input=dict(command=c))), capture_output=True, text=True, timeout=60)
    return bool(p.stdout.strip())
B, N = sys.argv[1], sys.argv[2]
PB, PN = load(B), load(N)
subs = [
 '$(cat <<<"hello")', '$(cat <<< hello)', "$(cat <<<'(')", '$(cat <<<"x)")', '$(( 1 << 2 ))', '$(echo $((1<<2)))', '$(echo "a<<b")', "$(echo 'a<<EOF')", '$(echo a \\<<EOF)',
 "$(cat <<EOF )", "$(cat <<'EOF'\nx\nEOF\n)", "$(cat <<'EOF'\n)\nEOF\n)", "$(cat <<'EOF'\n(\nEOF\n)", "$(cat <<'EOF'\nEOF)\nEOF\n)", "$(cat <<'EOF'\n EOF\n)\nEOF\n)", "$(cat <<-'EOF'\n\t(\n\tEOF\n)",
 '$(cat <<"EOF"\n(\nEOF\n)', '$(cat <<\\EOF\n(\nEOF\n)', "$(cat <<EOF\n\\(\nEOF\n)", "$(cat <<'EOF' | tr a b\n(\nEOF\n)", "$(cat <<'EOF'; echo )\n(\nEOF\n)", "$(cat <<A <<B\n(\nA\n)\nB\n)",
 "$(cat <<'EOF'\n$(\nEOF\n)", "$(cat <<'EOF'\n`\nEOF\n)", "$(cat <<'EOF'\n'\nEOF\n)", '$(cat <<\'EOF\'\n"\nEOF\n)', "$(cat <<EOF\n$(echo ')')\nEOF\n)", "$(cat <<'EOF'\nEOF\n)", "$(cat <<'EOF'\n\nEOF\n)",
 "$(cat <<'EOF'\n(\nEOF\n; echo x)", "$(cat <<'EOF'\n(\nEOF\n) $(cat <<'EOF'\n(\nEOF\n)", "$(echo it's)", "$(echo it's) it's", "$(echo \"\n(\n\")", "$(cat <<'E OF'\n(\nE OF\n)", "$(cat <<''\n(\n\n)", "$(cat << EOF\n(\nEOF\n)", "$(cat 0<<EOF\n(\nEOF\n)", "$(cat <<'EOF'\n(\nEOF\n)\n",
 "$(<f)", "$(< f)", "$(cat <(echo '('))", "$(cat <(echo ')'))",
]
outs = ['claude -p "%s" {F}', 'claude -p %s {F}', 'echo it\'s; claude -p "%s" {F}', 'x="a b"; claude -p "%s" {F}', 'claude -p "%s" "%s" {F}', 'sh -c \'echo it\'"\'"\'s\'; claude -p "%s" {F}']
bad = tot = diff = mono = 0
for o in outs:
    for s in subs:
        for f in (FL[0], FL[4], FL[7]):
            c = (o % ((s,) * o.count("%s"))).replace("{F}", f)
            pb, pn, rb, rn = bool(PB.decide(dict(tool_name="Bash", tool_input=dict(command=c)))), bool(PN.decide(dict(tool_name="Bash", tool_input=dict(command=c)))), rs(B, c), rs(N, c)
            tot += 1; diff += (pn != rn); mono += (pb and not pn)
            if not pn or not rn:
                bad += 1; print("ALLOWED new py=%s rs=%s base py=%s: %r" % (not pn, not rn, not pb, c[:120]))
print("cases", tot, "allowed on new (either impl)", bad, "py!=rs", diff, "monotone violations", mono)
