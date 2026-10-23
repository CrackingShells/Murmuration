# w08-c14 verifier: wall time and decision of the Python guard (one process per call) and the Rust guard (binary) of a BASE and a NEW tree on long `bash -lc` / `bash -c` inputs built here (200 KB script, 20,000 option words, 5,000 segments, nesting depth 1-4 with long scripts, long words, many substitutions); inputs: BASE_TREE NEW_TREE; output: table on stdout (median of --reps runs; each run limited to --limit s), --out JSON. No claude flag appears here. Usage: python3 -I w08_v14_time.py BASE_TREE NEW_TREE [--out F] [--limit S] [--reps N]
import json, os, statistics, subprocess, sys, time

PYSNIP = "import json,sys,importlib.util\ns=importlib.util.spec_from_file_location('pg',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\ne=json.load(sys.stdin)\ntry:\n    print('deny' if m.decide(e) else 'allow')\nexcept Exception as x:\n    print('deny-exc')\n"


def cases():
    big = "; ".join("echo line %d && ls -la /tmp | wc -l" % i for i in range(6000))
    c = {}
    c["lc_200KB_script"] = "bash -lc '%s'" % big[:200000]
    c["c_200KB_script"] = "bash -c '%s'" % big[:200000]
    c["lc_20000_opts"] = "bash " + "-x " * 20000 + "-lc 'make test'"
    c["c_20000_opts"] = "bash " + "-x " * 20000 + "-c 'make test'"
    c["lc_20000_l_before"] = "bash " + "-l " * 20000 + "-c 'make test'"
    c["o_chain_5000"] = "bash " + "-o noglob " * 5000 + "-lc 'make test'"
    c["segments_5000"] = "; ".join("bash -lc 'echo %d'" % i for i in range(5000))
    c["segments_5000_c"] = "; ".join("bash -c 'echo %d'" % i for i in range(5000))
    for d in (1, 2, 3, 4):
        s = "make test; " + "echo x; " * 3000
        for _ in range(d):
            s = "bash -lc " + "'" + s.replace("'", "'\\''") + "'"
        c["nest_lc_depth%d_24KB" % d] = s
        s = "make test; " + "echo x; " * 3000
        for _ in range(d):
            s = "bash -c " + "'" + s.replace("'", "'\\''") + "'"
        c["nest_c_depth%d_24KB" % d] = s
    c["lc_long_word_300K"] = "bash -lc 'echo %s'" % ("a" * 300000)
    c["lc_many_subst"] = "bash -lc '%s'" % " ".join("$(echo %d)" % i for i in range(5000))
    c["lc_heredoc_200KB"] = "bash -lc 'cat <<EOF\n%s\nEOF\n'" % ("text (x $(y\n" * 12000)
    c["lc_unmatched_quotes"] = "bash -lc 'echo \"" + "it'\\''s " * 20000 + "'"
    c["lc_dash_dash_many"] = "bash -lc " + "-- " * 5000 + "'make test'"
    return c


def run(argv, payload, limit):
    t = time.time()
    try:
        p = subprocess.run(argv, input=payload, capture_output=True, text=True, timeout=limit)
        o = p.stdout.strip()          # the python snippet prints allow/deny; the Rust guard prints nothing for allow
        return time.time() - t, (o if o in ("allow", "deny", "deny-exc") else ("deny" if o else "allow")) if p.returncode == 0 else "rc%d" % p.returncode
    except subprocess.TimeoutExpired:
        return float(limit), "TIMEOUT"


def main():
    a = sys.argv[1:]
    base, new = a[0], a[1]
    limit = float(a[a.index("--limit") + 1]) if "--limit" in a else 40
    reps = int(a[a.index("--reps") + 1]) if "--reps" in a else 2
    out = a[a.index("--out") + 1] if "--out" in a else ""
    res = {}
    print("%-26s %5s | %-18s %-18s | %-18s %-18s" % ("case", "KB", "base py", "base rs", "new py", "new rs"))
    for name, cmd in cases().items():
        payload = json.dumps(dict(tool_name="Bash", tool_input=dict(command=cmd), cwd="/private/tmp"))
        row = []
        for tree in (base, new):
            for kind in ("py", "rs"):
                argv = [sys.executable, "-I", "-c", PYSNIP, os.path.join(tree, "scripts", "permission_guard.py")] if kind == "py" else [os.path.join(tree, "bin", "aarch64-apple-darwin", "murmuration"), "guard"]
                rr = [run(argv, payload, limit) for _ in range(reps)]
                row.append((round(statistics.median(r[0] for r in rr), 2), rr[0][1]))
        res[name] = row
        print("%-26s %5d | %-18s %-18s | %-18s %-18s" % (name, len(cmd) // 1000, *["%.2fs %s" % r for r in row]))
    if out:
        json.dump(res, open(out, "w"))


if "--selftest" in sys.argv:
    cs = cases()
    assert len(cs) >= 20 and all(len(v) > 100 for v in cs.values())
    print("selftest ok", len(cs))
    sys.exit(0)
main()
