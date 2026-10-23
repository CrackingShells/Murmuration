# w08-c10 verifier: wall time and decision of the Python guard (script, one process per call) and the Rust guard (binary) for baseline and branch trees on ordinary and long commands built here; inputs: two tree dirs (each with scripts/ and bin/) and w08_v10_flags.json, output: a table on stdout and a JSON to --out. Usage: python3 -I w08_v10_time.py BASE_TREE NEW_TREE [--out F] [--limit S] [--reps N] [--only SUBSTR]
import json, os, subprocess, sys, time, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
FLAG = json.load(open(os.path.join(HERE, "w08_v10_flags.json")))["flags"][0]


def cases():
    c = {}
    c["ord:ls"] = "ls -la"
    c["ord:git-status"] = "git status --short && git log --oneline | head -5"
    c["ord:py"] = "python3 -I scripts/budget.py --selftest 2>&1 | tail -3"
    c["ord:commit-heredoc"] = 'git commit -m "$(cat <<\'EOF\'\nfix: a thing\n\nlonger body $(not run)\nEOF\n)"'
    c["ord:subst"] = 'echo "$(date)" > out.txt; ls $(pwd)'
    c["ord:claude-ordinary"] = "claude -p \"$(cat prompt.txt)\" --model opus"
    for n in (20000, 100000, 300000, 1000000):
        c["long_word:%d" % n] = "echo " + "a" * n
    c["long_word_cmd:300000"] = "a" * 300000
    c["long_dq:300000"] = 'echo "' + "word " * 60000 + '"'
    c["long_sq:300000"] = "echo '" + "word " * 60000 + "'"
    for n in (1000, 20000):
        c["heredoc:%d_lines" % n] = "cat > f.txt <<'EOF'\n" + "".join("line %d of some prose text here\n" % i for i in range(n)) + "EOF"
    c["heredoc_subst:5000_lines"] = "cat > f.txt <<'EOF'\n" + "".join("line %d $(not run) `nor this` (paren) ; amp &\n" % i for i in range(5000)) + "EOF"
    c["commit_heredoc:5000_lines"] = 'git commit -m "$(cat <<\'EOF\'\n' + "".join("line %d of body (x) $(y)\n" % i for i in range(5000)) + "EOF\n)\""
    for d in (20, 200, 2000, 20000):
        c["nest_dollar:%d" % d] = "echo " + "$(echo " * d + "x" + ")" * d
    for d in (20, 200, 2000):
        c["nest_dq:%d" % d] = "echo " + '"$(echo ' * d + "x" + ')"' * d
    for d in (200, 2000):
        c["nest_paren:%d" % d] = "echo " + "(" * d + "x" + ")" * d
    for n in (1000, 10000, 100000):
        c["semis:%d" % n] = "; ".join(["echo %d" % i for i in range(n)])
    for n in (1000, 10000):
        c["semis_subst:%d" % n] = "; ".join(["echo $(echo %d)" % i for i in range(n)])
    c["andand:20000"] = " && ".join(["true"] * 20000)
    c["pipes:20000"] = " | ".join(["cat"] * 20000)
    c["many_args:50000"] = "git add " + " ".join("file%d.txt" % i for i in range(50000))
    for n in (3000, 30000):
        c["unmatched_open:%d" % n] = "echo " + "$(" * n
    c["unmatched_dq_open:5000"] = 'echo "' + "$(" * 5000
    c["backticks:20000"] = "echo " + "`x` " * 20000
    c["backtick_unclosed:100000"] = "echo `" + "a" * 100000
    c["many_dollar_in_long_word:200000"] = "echo " + "$x" * 100000
    c["dq_with_many_subst:20000"] = 'echo "' + "$(a) " * 20000 + '"'
    c["wrapper_chain:5000"] = "env " * 5000 + "ls"
    c["wrapper_opts:5000"] = "env " + "-u X " * 5000 + "ls"
    c["env_S_long"] = "env -S '" + "a " * 50000 + "'"
    s = "echo hi"
    for _ in range(12):
        s = "sh -c " + json.dumps(s)
    c["sh_c_nested_quote:12"] = s
    c["hole:flag_after_subst"] = 'claude -p "$(cat f)" ' + FLAG
    c["hole:env_u"] = "env -u VAR claude -p hi " + FLAG
    return c


def run(impl, tree, cmd, limit):
    ev = json.dumps(dict(tool_name="Bash", tool_input=dict(command=cmd), cwd="/private/tmp"))
    if impl == "py":
        argv = ["python3", "-S", "-I", os.path.join(tree, "scripts", "permission_guard.py")]
    else:
        argv = [os.path.join(tree, "bin", "aarch64-apple-darwin", "murmuration"), "guard"]
    t = time.perf_counter()
    try:
        p = subprocess.run(argv, input=ev, capture_output=True, text=True, timeout=limit)
    except subprocess.TimeoutExpired:
        return limit, "TIMEOUT"
    dt = time.perf_counter() - t
    out = p.stdout.strip()
    if p.returncode != 0 and not out:
        return dt, "rc%d" % p.returncode
    return dt, ("deny" if out else "allow")


def main():
    a = sys.argv[1:]
    base, new = a[0], a[1]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    limit, reps, only, out = float(opt("--limit", 30)), int(opt("--reps", 3)), opt("--only", ""), opt("--out", "")
    res = []
    print("%-34s %-5s %9s %9s  %-8s %-8s" % ("case", "impl", "base_s", "new_s", "base", "new"))
    for name, cmd in cases().items():
        if only and only not in name:
            continue
        for impl in ("py", "rs"):
            row = {}
            for lab, tree in (("base", base), ("new", new)):
                ts, dec = [], None
                for r in range(reps):
                    dt, dec = run(impl, tree, cmd, limit)
                    ts.append(dt)
                    if dec == "TIMEOUT":
                        break
                row[lab] = (statistics.median(ts), dec)
            res.append(dict(case=name, impl=impl, chars=len(cmd), base_s=row["base"][0], new_s=row["new"][0], base=row["base"][1], new=row["new"][1]))
            print("%-34s %-5s %9.3f %9.3f  %-8s %-8s" % (name, impl, row["base"][0], row["new"][0], row["base"][1], row["new"][1]), flush=True)
    if out:
        json.dump(res, open(out, "w"), indent=1)


if "--selftest" in sys.argv:
    cs = cases()
    assert len(cs) > 40 and all(isinstance(v, str) for v in cs.values())
    print("selftest ok", len(cs))
    sys.exit(0)
main()
