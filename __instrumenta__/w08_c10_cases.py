# w08-c10: builds the hole-form cases (a flag after a substitution, a substitution as program, a claude inside a substitution, a wrapper with a value-taking option in front) from the base strings of w08_c10_bases.json, runs them through scripts/permission_guard.py of a repo (in process) and the Rust binary of that repo (one process per case), and prints the metamorphic test: a hole-form case whose plain form is denied must be denied; a control (ordinary flag) must be allowed.
# inputs: --repo DIR (a lab checkout: scripts/permission_guard.py, bin/<target>/murmuration), bases JSON next to this file; outputs: stdout table, --out FILE (JSON, one record per case: id, kind, shape, command, py, rs). Selftest: python3 -I w08_c10_cases.py --selftest (checks the generator's counts and that the plain forms of every hole-form base are denied by the repo's Python guard).
# usage: python3 -I w08_c10_cases.py --repo DIR [--rust BIN|none] [--out FILE] [--jobs N] [--quick]
import argparse, concurrent.futures, importlib.util, itertools, json, os, platform, random, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASES = json.load(open(os.path.join(HERE, "w08_c10_bases.json")))

# shapes of a claude command with the flag part {F}; each is shell text
SHAPES = {
    "plain": "claude -p hi {F}",
    "dq_subst_before": 'claude -p "$(cat f)" {F}',
    "subst_before": "claude -p $(cat f) {F}",
    "dq_bt_before": 'claude -p "`cat f`" {F}',
    "bt_before": "claude -p `cat f` {F}",
    "subst_pipe_inside": 'claude -p "$(cat f | head -5)" {F}',
    "subst_before_model": 'claude --model "$(cat m)" -p hi {F}',
    "nested_subst": 'claude -p "$(cat "$(echo f)")" {F}',
    "subst_heredoc": "claude \"$(cat <<'EOF'\nhello\nEOF\n)\" {F}",
    "subst_infix": 'claude -p "pre $(cat f) post" {F}',
    "subst_grep": 'claude -p "$(grep x f)" {F}',
    "subst_ls": 'claude -p "$(ls)" {F}',
    "two_subst": 'claude -p "$(cat f)" "$(cat g)" {F}',
    "subst_program_which": '"$(which claude)" -p hi {F}',
    "subst_program_cmdv": "$(command -v claude) -p hi {F}",
    "subst_program_bt": "`which claude` -p hi {F}",
    "claude_inside_dq_subst": 'echo "$(claude -p hi {F})"',
    "claude_inside_assign": "x=$(claude -p hi {F})",
    "claude_inside_bt_assign": "x=`claude -p hi {F}`",
    "claude_inside_dq_assign": 'out="$(claude -p hi {F})"; echo $out',
    "after_pipe": 'cat f | claude -p "$(cat g)" {F}',
    "subshell": '(claude -p "$(cat f)" {F})',
    "after_cd": 'cd /tmp && claude -p "$(cat f)" {F}',
    "before_pipe": 'claude -p "$(cat f)" {F} | tee out.txt',
    "sh_c": "bash -c 'claude -p \"$(cat f)\" {F}'",
    "timeout_subst": 'timeout 10 claude -p "$(cat f)" {F}',
    "procsubst_before": "claude -p <(cat f) {F}",
    "procsubst_out": "claude -p x >(cat) {F}",
    "claude_inside_procsubst": "diff <(claude -p hi {F}) f",
    "claude_inside_procsubst2": "cat <(echo a) <(claude -p hi {F})",
    "dq_procsubst_literal": 'claude -p "<(cat f)" {F}',
    "dq_escaped_subst": 'claude -p "\\$(cat f)" {F}',
    "sh_c_dq": 'bash -c "claude -p \\"\\$(cat f)\\" {F}"',
    "flag_then_subst": 'claude -p hi {F} "$(cat f)"',
}
SHAPE_NOTE = {"plain": "control of the old forms", "flag_then_subst": "flag before the substitution (was denied)"}


def load_guard(repo):
    spec = importlib.util.spec_from_file_location("pg_" + str(abs(hash(repo))), os.path.join(repo, "scripts", "permission_guard.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def default_rust(repo):
    arch = "aarch64" if platform.machine() in ("arm64", "aarch64") else platform.machine()
    return os.path.join(repo, "bin", "%s-apple-darwin" % arch, "murmuration")


def build_cases(quick=False):
    """List of dicts: id, kind (hole | control | g3hole | g3control), shape, command. Hole cases are all denied in the plain form (checked by --selftest)."""
    cases = []
    n = 0

    def add(kind, shape, cmd):
        nonlocal n
        n += 1
        cases.append(dict(id="k%04d" % n, kind=kind, shape=shape, command=cmd))
    for kind, flags in (("hole", BASES["deny_flags"]), ("control", BASES["ok_flags"])):
        for shape, tpl in SHAPES.items():
            for f in flags:
                add(kind, shape, tpl.replace("{F}", f))
        for w in BASES["wrappers"]:
            for tag, tpl in (("wrap_plain", "claude -p hi {F}"), ("wrap_dq_subst", 'claude -p "$(cat f)" {F}')):
                for f in flags:
                    add(kind, "%s:%s" % (tag, w.strip()), (w + " " + tpl.replace("{F}", f)))
        for w in BASES["env_s"]:
            for f in flags:
                add(kind, "env_S:" + w, "%s 'claude -p hi %s'" % (w, f))
                add(kind, "env_S_eq:" + w, "env --split-string='claude -p hi %s'" % f if w == "env --split-string" else "%s 'claude -p hi %s'" % (w, f))
    for kind, bases in (("g3hole", BASES["g3_deny"]), ("g3control", BASES["g3_ok"])):
        for b in bases:
            add(kind, "plain", b)
            for w in BASES["wrappers"]:
                add(kind, "wrap:" + w.strip(), w + " " + b)
            add(kind, "subst_cd", 'cd "$(pwd)" && ' + b)
    for d in ('"$(git rev-parse --show-toplevel)"/.claude/settings.json', '"$(pwd)/.claude/settings.local.json"', '$(pwd)/.claude/settings.json', '"`pwd`/.claude/settings.json"'):
        add("g3hole", "subst_dest", "cp /tmp/x " + d)
        # a redirect target with a quoted prefix (`> "$X"/.claude/...`) is a gap of the redirect pattern, not of the splitter: reported apart (kind g3resid), not gating
        add("g3resid" if d.startswith('"') and not d.endswith('"') else "g3hole", "subst_dest_redirect", "echo '{}' > " + d)
    if quick:
        r = random.Random(20261024)
        r.shuffle(cases)
        cases = cases[: max(200, len(cases) // 8)]
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
    for c in cases:
        c["py"] = py_decide(guard, c["command"])
    if rust:
        with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
            for c, d in zip(cases, ex.map(lambda c: rs_decide(rust, c["command"]), cases)):
                c["rs"] = d
    return cases


def summarize(cases, rust):
    out = []
    want_deny = ("hole", "g3hole", "g3resid")
    for kind in ("hole", "g3hole", "g3resid", "control", "g3control"):
        cs = [c for c in cases if c["kind"] == kind]
        if kind in want_deny:
            bad_py = [c for c in cs if not c["py"]]
            bad_rs = [c for c in cs if rust and not c["rs"]]
            out.append("%-10s %5d cases   allowed (a hole): python %4d%s" % (kind, len(cs), len(bad_py), "   rust %4d" % len(bad_rs) if rust else ""))
        else:
            bad_py = [c for c in cs if c["py"]]
            bad_rs = [c for c in cs if rust and c["rs"]]
            out.append("%-10s %5d cases   denied (a false denial): python %4d%s" % (kind, len(cs), len(bad_py), "   rust %4d" % len(bad_rs) if rust else ""))
    if rust:
        diff = [c for c in cases if (c["py"] or None) != (c["rs"] or None)]
        out.append("python and rust differ on %d of %d cases" % (len(diff), len(cases)))
    return "\n".join(out)


def by_shape(cases):
    rows = {}
    for c in cases:
        if c["kind"] in ("hole", "g3hole"):
            k = c["shape"].split(":")[0] if not c["shape"].startswith("wrap") else c["shape"]
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
    plain_bad = [c for c in cases if c["kind"] in ("hole", "g3hole") and c["shape"] == "plain" and not py_decide(guard, c["command"])]
    print("selftest: %s; plain forms allowed (must be 0 on the baseline; the heredoc shape needs `cat` first line): %d" % (kinds, len(plain_bad)))
    for c in plain_bad[:5]:
        print("  ", c["command"])
    return 0 if not plain_bad and kinds.get("hole", 0) > 1000 else 1


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
                print("  %-40s %4d cases, %4d allowed" % (k, n, h))
    if a.out:
        json.dump(cases, open(a.out, "w"), indent=0)


if __name__ == "__main__":
    main()
