# w08-c14: builds the shell `-c` variant cases (combined clusters such as `bash -lc`, options before and after `-c`, wrappers, nested shells) around inner scripts that the guard denies in the plain form `bash -c '<script>'`, runs them through scripts/permission_guard.py and the Rust binary, and reports the holes (variant allowed while its plain form is denied).
# inputs: --repo DIR (a checkout: scripts/permission_guard.py, bin/<target>/murmuration), the bases JSON w08_c10_bases.json next to this file (flag strings stay in that data file); outputs: stdout table, --out FILE (JSON, one record per case: id, kind, shape, command, plain, py, rs, py_plain, rs_plain). Selftest: python3 -I w08_c14_cases.py --selftest
# usage: python3 -I w08_c14_cases.py --repo DIR [--rust BIN|none] [--out FILE] [--jobs N] [--quick] [--shapes]
import argparse, concurrent.futures, importlib.util, json, os, platform, random, shlex, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASES = json.load(open(os.path.join(HERE, "w08_c10_bases.json")))
EXTRA = json.load(open(os.path.join(HERE, "w08_c14_bases.json")))

SHELLS = ["bash", "sh", "zsh", "dash", "ksh", "/bin/bash", "/usr/bin/zsh"]
# (name, words before the script word, words between `-c`-word and the script)  -- the script word comes last; the plain form is `<shell> -c <script>`
OUTERS = [
    ("c", "-c"), ("lc", "-lc"), ("ec", "-ec"), ("xc", "-xc"), ("ic", "-ic"), ("euc", "-euc"), ("uc", "-uc"), ("Cc", "-Cc"), ("pc", "-pc"), ("vc", "-vc"), ("fc", "-fc"), ("euxc", "-euxc"),
    ("cl", "-cl"), ("ce", "-ce"), ("cx", "-cx"), ("lec", "-lec"), ("ilc", "-ilc"),
    ("l_c", "-l -c"), ("l_ec", "-l -ec"), ("e_lc", "-e -lc"), ("x_e_lc", "-x -e -lc"), ("login_c", "--login -c"), ("login_ec", "--login -ec"), ("norc_lc", "--norc -lc"),
    ("noprofile_norc_lc", "--noprofile --norc -lc"), ("posix_ec", "--posix -ec"), ("rcfile_ic", "--rcfile /dev/null -ic"), ("o_lc", "-o pipefail -lc"), ("o_c", "-o pipefail -c"),
    ("O_lc", "-O extglob -lc"), ("O_c", "-O extglob -c"), ("po_lc", "+o history -lc"), ("PO_lc", "+O extglob -lc"), ("eo_c", "-eo pipefail -c"), ("eoc", "-eoc pipefail"), ("oec", "-oec pipefail"),
    ("c_x", "-c -x"), ("c_e", "-c -e"), ("c_l", "-c -l"), ("c_dd", "-c --"), ("c_o", "-c -o pipefail"), ("c_O", "-c -O extglob"), ("lc_x", "-lc -x"), ("ec_o", "-ec -o pipefail"), ("c_x_e", "-c -x -e"),
    ("l_c_dd", "-l -c --"), ("lc_dd", "-lc --"), ("lc_dash", "-lc -"), ("c_norc", "-c --norc"),
]
WRAPS = ["", "env ", "env -u X ", "sudo ", "timeout 5 ", "nohup ", "exec ", "command ", "env X=1 ", "time "]
SHAPE_INNER = {
    "plain": "claude -p hi {F}",
    "dq_subst": 'claude -p "$(cat f)" {F}',
    "subst_prog": '"$(which claude)" -p hi {F}',
    "env_u": "env -u X claude -p hi {F}",
    "cd_and": "cd /tmp && claude -p hi {F}",
    "pipe": "cat f | claude -p hi {F}",
    "heredoc": "claude -p \"$(cat <<'EOF'\nhi (x\nEOF\n)\" {F}",
    "env_S": "env -S 'claude -p hi {F}'",
    "inner_shell": "bash -c 'claude -p hi {F}'",
}


def load_guard(repo):
    spec = importlib.util.spec_from_file_location("pg_" + str(abs(hash(repo))), os.path.join(repo, "scripts", "permission_guard.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def default_rust(repo):
    arch = "aarch64" if platform.machine() in ("arm64", "aarch64") else platform.machine()
    return os.path.join(repo, "bin", "%s-apple-darwin" % arch, "murmuration")


def q(s):
    return shlex.quote(s)


def build_cases(quick=False):
    """List of dicts: id, kind (hole | control | g3hole | g3control | nonc), shape, command, plain. `plain` is the `<shell> -c <script>` form of the same script."""
    cases = []

    def add(kind, shape, cmd, plain):
        cases.append(dict(id="m%05d" % (len(cases) + 1), kind=kind, shape=shape, command=cmd, plain=plain))
    inners = []   # (kind, shape, script)
    for kind, flags in (("hole", BASES["deny_flags"]), ("control", BASES["ok_flags"])):
        for sh, tpl in SHAPE_INNER.items():
            for f in flags[:: 1 if sh in ("plain", "dq_subst") else 3]:
                inners.append((kind, "inner:" + sh, tpl.replace("{F}", f)))
    for b in BASES["g3_deny"]:
        inners.append(("g3hole", "inner:g3", b))
    for b in BASES["g3_ok"]:
        inners.append(("g3control", "inner:g3", b))
    for shell in SHELLS:
        for oname, opts in OUTERS:
            for kind, shape, script in inners:
                plain = "%s -c %s" % (shell, q(script))
                # the script word stays last: for `-eoc pipefail` the value word comes between
                add(kind, "outer:%s:%s" % (oname, shape), "%s %s %s" % (shell, opts, q(script)), plain)
    # wrappers in front, a short list of inners
    for w in WRAPS[1:]:
        for oname, opts in OUTERS:
            for kind, shape, script in inners[:: 7]:
                add(kind, "wrap:%s:%s" % (w.strip(), oname), "%sbash %s %s" % (w, opts, q(script)), "%sbash -c %s" % (w, q(script)))
    # nested shells and other stacked forms
    for oname, opts in OUTERS[:20]:
        for kind, shape, script in inners[:: 5]:
            inner = "bash %s %s" % (opts, q(script))
            add(kind, "nested:%s" % oname, "bash %s %s" % (opts, q(inner)), "bash -c %s" % q("bash -c %s" % q(script)))
            add(kind, "after_semicolon:%s" % oname, "echo go; bash %s %s" % (opts, q(script)), "echo go; bash -c %s" % q(script))
            add(kind, "pipe:%s" % oname, "cat f | bash %s %s | tee out" % (opts, q(script)), "cat f | bash -c %s | tee out" % q(script))
            add(kind, "dq_script:%s" % oname, 'bash %s "%s"' % (opts, script.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`")), "bash -c " + q(script))
    # clusters without `c`: decided as on main (compared across repos by the caller); words are data in EXTRA
    for cmd in EXTRA["nonc"]:
        add("nonc", "nonc", cmd, cmd)
    if quick:
        r = random.Random(20261024)
        r.shuffle(cases)
        cases = cases[: max(300, len(cases) // 40)]
    return cases


def py_decide(guard, cmd):
    r = guard.decide(dict(tool_name="Bash", tool_input={"command": cmd}, cwd="/h/proj"))
    return r[0] if r else None


def rs_decide(binary, cmd):
    ev = json.dumps(dict(tool_name="Bash", tool_input={"command": cmd}, cwd="/h/proj"))
    p = subprocess.run([binary, "guard"], input=ev.encode(), capture_output=True, timeout=30, env=dict(os.environ, LC_ALL="en_US.UTF-8"))
    out = p.stdout.decode("utf-8", "replace")
    if not out:
        return None
    try:
        reason = json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]
    except (ValueError, KeyError):
        return "G?"
    return reason.split("(", 1)[1].split(")", 1)[0] if "(" in reason else "G?"


def run(repo, rust, jobs, quick):
    guard = load_guard(repo)
    cases = build_cases(quick)
    plains = sorted({c["plain"] for c in cases})
    pp = {p: py_decide(guard, p) for p in plains}
    for c in cases:
        c["py"] = py_decide(guard, c["command"])
        c["py_plain"] = pp[c["plain"]]
    if rust:
        todo = sorted({c["command"] for c in cases} | set(plains))
        with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
            rr = dict(zip(todo, ex.map(lambda x: rs_decide(rust, x), todo)))
        for c in cases:
            c["rs"] = rr[c["command"]]
            c["rs_plain"] = rr[c["plain"]]
    return cases


def summarize(cases, rust):
    out = []
    for kind in ("hole", "g3hole"):
        cs = [c for c in cases if c["kind"] == kind and c["py_plain"]]
        bad_py = [c for c in cs if not c["py"]]
        bad_rs = [c for c in cs if rust and not c["rs"]]
        out.append("%-9s %6d cases with plain form denied   variant allowed (a hole): python %5d%s" % (kind, len(cs), len(bad_py), "   rust %5d" % len(bad_rs) if rust else ""))
        nd = [c for c in cases if c["kind"] == kind and not c["py_plain"]]
        out.append("          (%d cases whose plain form is allowed, not counted)" % len(nd))
    for kind in ("control", "g3control"):
        cs = [c for c in cases if c["kind"] == kind]
        bad_py = [c for c in cs if c["py"]]
        bad_rs = [c for c in cs if rust and c["rs"]]
        out.append("%-9s %6d cases   denied (a false denial): python %5d%s" % (kind, len(cs), len(bad_py), "   rust %5d" % len(bad_rs) if rust else ""))
    cs = [c for c in cases if c["kind"] == "nonc"]
    out.append("nonc      %6d cases   denied: python %d%s" % (len(cs), sum(bool(c["py"]) for c in cs), "   rust %d" % sum(bool(c["rs"]) for c in cs) if rust else ""))
    if rust:
        diff = [c for c in cases if (c["py"] or None) != (c["rs"] or None)]
        out.append("python and rust differ on %d of %d cases" % (len(diff), len(cases)))
    return "\n".join(out)


def by_shape(cases):
    rows = {}
    for c in cases:
        if c["kind"] in ("hole", "g3hole") and c["py_plain"]:
            k = ":".join(c["shape"].split(":")[:2])
            r = rows.setdefault(k, [0, 0])
            r[0] += 1
            r[1] += not c["py"]
    return rows


def selftest():
    cases = build_cases()
    repo = os.path.abspath(os.path.join(HERE, ".."))
    guard = load_guard(repo)
    kinds = {}
    for c in cases:
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    # every plain form of a hole case must be denied (otherwise the case tests nothing) and of a control case allowed
    bad = []
    for p in sorted({c["plain"] for c in cases if c["kind"] in ("hole", "g3hole")}):
        if not py_decide(guard, p) and "heredoc" not in p:
            bad.append(p)
    badc = [c["plain"] for c in cases if c["kind"] in ("control", "g3control") and py_decide(guard, c["plain"])]
    print("selftest: %s; plain hole forms allowed (must be 0): %d; plain control forms denied (must be 0): %d" % (kinds, len(bad), len(badc)))
    for p in (bad + badc)[:5]:
        print("  ", p)
    return 0 if not bad and not badc and kinds.get("hole", 0) > 5000 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--rust", default=None, help="binary path, 'none', or default bin/<target>/murmuration of the repo")
    ap.add_argument("--out")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--shapes", action="store_true", help="print the per-shape table of holes")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    repo = os.path.abspath(a.repo)
    rust = None if a.rust == "none" else (a.rust or default_rust(repo))
    cases = run(repo, rust, a.jobs, a.quick)
    print("repo %s | rust %s | %d cases%s" % (repo, rust, len(cases), " (quick subset, seed 20261024)" if a.quick else ""))
    print(summarize(cases, rust))
    if a.shapes:
        for k, (n, h) in sorted(by_shape(cases).items(), key=lambda kv: -kv[1][1]):
            if h:
                print("  %-40s %5d cases, %5d allowed" % (k, n, h))
    if a.out:
        json.dump(cases, open(a.out, "w"), indent=0)


if __name__ == "__main__":
    main()
