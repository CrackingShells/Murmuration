# w08-c14 verifier: independent hole and control test for shell `-c` forms; builds its own cases (clusters with c in any position, `-o name` before it, long options, 5 shells with path spellings, 12 wrappers, substitutions, `;`, pipe, nesting depth 1-4, `+c` and zsh `-O` forms) around the claude flag strings and settings writes of w08_v10_flags.json, decides each with the Python guard and the Rust guard of a BASE and a NEW tree; prints per kind: variants whose plain `<shell> -c <script>` form is denied on NEW but the variant is allowed (holes), the same on BASE, controls (ordinary flags, clusters without c) newly denied, base-denied new-allowed (loosened), Python vs Rust differences; inputs: BASE_TREE NEW_TREE, w08_v10_flags.json; output: stdout, --out JSON. Usage: python3 -I w08_v14_holes.py BASE_TREE NEW_TREE [--out F] [--jobs N]
import concurrent.futures, importlib.util, json, os, shlex, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "w08_v10_flags.json")))
FLAGS, WRITES = D["flags"], D["g3_writes"]
CONTROL_FLAGS = ["--model opus", "--verbose", "--print", "--setting-sources user", "--resume abc", "--output-format json", "--max-turns 3"]
SHELLS = ["sh", "bash", "zsh", "dash", "ksh", "/bin/bash", "/usr/bin/zsh", "/bin/sh"]
# (options before the string, with the string placed after them; {S} is the quoted script)
OPTS = {
    "lc": "-lc {S}", "ec": "-ec {S}", "xc": "-xc {S}", "ic": "-ic {S}", "cl": "-cl {S}", "ce": "-ce {S}", "cx": "-cx {S}", "lec": "-lec {S}", "elc": "-elc {S}", "euc": "-euc {S}", "xec": "-xec {S}", "cu": "-cu {S}", "vc": "-vc {S}", "fc": "-fc {S}", "ac": "-ac {S}", "hc": "-hc {S}", "Ec": "-Ec {S}",
    "l_c": "-l -c {S}", "e_c": "-e -c {S}", "x_lc": "-x -lc {S}", "l_e_c": "-l -e -c {S}", "l_x_ec": "-l -x -ec {S}",
    "o_pipe_c": "-o pipefail -c {S}", "eo_pipe_c": "-eo pipefail -c {S}", "oc_pipe": "-oc pipefail {S}", "co_pipe": "-co pipefail {S}", "O_ext_c": "-O extglob -c {S}", "Oc_ext": "-Oc extglob {S}", "plus_o_c": "+o pipefail -c {S}", "plus_O_c": "+O extglob -c {S}", "o_o_c": "-o noglob -o pipefail -c {S}", "o_pipe_lc": "-o pipefail -lc {S}",
    "login": "--login -c {S}", "norc": "--norc -c {S}", "noprofile": "--noprofile --norc -lc {S}", "posix": "--posix -c {S}", "rcfile": "--rcfile /dev/null -c {S}", "initfile": "--init-file /dev/null -ic {S}", "rcfile_lc": "--rcfile /dev/null -lc {S}",
    "c_x": "-c -x {S}", "c_dd": "-c -- {S}", "c_o_pipe": "-c -o pipefail {S}", "lc_dash": "-lc - {S}", "lc_dd": "-lc -- {S}", "c_c": "-c -c {S}", "c_lc": "-c -lc {S}", "c_l": "-c -l {S}",
    "quoted_lc": "'-lc' {S}", "dq_lc": '"-lc" {S}', "split_quote": "-l'c' {S}", "bs_lc": "-l\\c {S}",
    "plain_c": "-c {S}",
}
GAPS = {"plus_c": "+c {S}", "plus_lc": "+lc {S}", "l_plus_c": "-l +c {S}", "zsh_O_lc": "-O -lc {S}", "zsh_Oc": "-Oc {S}"}   # forms the claim does not name (real shells run the string); reported apart
WRAPS = ["", "env ", "env -u V ", "env A=1 ", "sudo ", "sudo -u root ", "nohup ", "timeout 5 ", "command ", "exec ", "nice -n 5 ", "time ", "xargs ", "setsid "]
POST = ["{C}", "x=$({C})", 'echo "$({C})"', "true; {C}", "true && {C}", "echo a | {C}", "( {C} )", "{{ {C}; }}", "{C} &"]


def inner_claude(f):
    return "claude -p hi " + f


def build():
    cs = []
    scripts = [("claude", inner_claude(f)) for f in FLAGS] + [("g3", w) for w in WRITES]
    scripts += [("claude", 'claude -p "$(cat f)" ' + f) for f in FLAGS[:4]]
    for sh in SHELLS:
        for sc_kind, sc in scripts:
            plain = "%s -c %s" % (sh, shlex.quote(sc))
            for on, o in list(OPTS.items()) + list(GAPS.items()):
                cmd = sh + " " + o.replace("{S}", shlex.quote(sc))
                cs.append(dict(id="%s|%s|%s" % (sh, on, sc[:40]), kind=("gap" if on in GAPS else sc_kind), shape=on, command=cmd, plain=plain))
    # wrappers and positions (subset of shells / options / scripts to keep the count near 30k)
    for w in WRAPS:
        for pi, p in enumerate(POST):
            for on in ("lc", "l_c", "oc_pipe", "c_x", "c_dd", "eo_pipe_c", "lc_dash"):
                for sh in ("bash", "/bin/zsh", "dash"):
                    for fi in (0, 3, 5, 7, 9):
                        sc = inner_claude(FLAGS[fi])
                        core = w + sh + " " + OPTS[on].replace("{S}", shlex.quote(sc))
                        cs.append(dict(id="P:%s|%d|%s|%s|%d" % (w, pi, on, sh, fi), kind="claude", shape="wrap_pos", command=p.replace("{C}", core), plain=p.replace("{C}", w + sh + " -c " + shlex.quote(sc))))
    # nesting: the string of an outer shell starts an inner shell; depth 1..4; plain nested uses -c everywhere
    for depth in (1, 2, 3, 4):
        for fi in (0, 4, 7):
            for on in ("lc", "c_x", "oc_pipe"):
                s = inner_claude(FLAGS[fi]); sp = s
                for _ in range(depth):
                    s = "bash " + OPTS[on].replace("{S}", shlex.quote(s))
                    sp = "bash -c " + shlex.quote(sp)
                cs.append(dict(id="N%d|%s|%d" % (depth, on, fi), kind="claude", shape="nest%d" % depth, command=s, plain=sp))
    # controls: ordinary flags in the claude shapes, ordinary commands, clusters without c, scripts after the options that carry the flag as an argument
    for cf in CONTROL_FLAGS:
        for sh in ("bash", "zsh", "/bin/sh"):
            for on, o in OPTS.items():
                cs.append(dict(id="K|%s|%s|%s" % (sh, on, cf), kind="control", shape=on, command=sh + " " + o.replace("{S}", shlex.quote("claude -p hi " + cf)), plain=None))
    for sc in ("make test", "echo hi", "ls -la | wc -l", "git status && git diff", "python3 -c 'print(1)'", "echo '{}' > out.json", "cat ~/.claude/settings.json", "claude --version"):
        for sh in ("bash", "zsh", "sh"):
            for on, o in OPTS.items():
                cs.append(dict(id="K2|%s|%s|%s" % (sh, on, sc), kind="control", shape=on, command=sh + " " + o.replace("{S}", shlex.quote(sc)), plain=None))
    for f in FLAGS:
        for form in ("bash -lx run.sh {F}", "bash -l {F}", "bash -lc", "bash -lc 'echo hi' {F}", "bash -c 'echo \"$@\"' name {F}", "bash -x -e run.sh {F}", "sh -ex script.sh {F}", "bash --norc run.sh {F}", "zsh -l run.sh {F}", "bash -o pipefail run.sh {F}", "bash -ec 'echo hi' x {F}", "bash -n run.sh {F}", "bash script.sh -c {F}"):
            cs.append(dict(id="Z|%s|%s" % (form, f), kind="nonc", shape=form.split()[1] if " " in form else form, command=form.replace("{F}", f), plain=None))
    return cs


def load(tree):
    s = importlib.util.spec_from_file_location("pg" + str(abs(hash(tree))), os.path.join(tree, "scripts", "permission_guard.py"))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def py(m, cmd):
    try:
        return bool(m.decide(dict(tool_name="Bash", tool_input=dict(command=cmd), cwd="/private/tmp")))
    except Exception:
        return True


def rs(tree, cmd):
    p = subprocess.run([os.path.join(tree, "bin", "aarch64-apple-darwin", "murmuration"), "guard"], input=json.dumps(dict(tool_name="Bash", tool_input=dict(command=cmd), cwd="/private/tmp")), capture_output=True, text=True, timeout=60)
    return bool(p.stdout.strip()) if p.returncode == 0 else None


def main():
    a = sys.argv[1:]
    base, new = a[0], a[1]
    jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 8
    out = a[a.index("--out") + 1] if "--out" in a else ""
    PB, PN = load(base), load(new)
    cs = build()
    uniq = sorted({c["command"] for c in cs} | {c["plain"] for c in cs if c["plain"]})
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        rb = dict(zip(uniq, ex.map(lambda x: rs(base, x), uniq)))
        rn = dict(zip(uniq, ex.map(lambda x: rs(new, x), uniq)))
    dec = {x: dict(pb=py(PB, x), pn=py(PN, x), rb=rb[x], rn=rn[x]) for x in uniq}
    for c in cs:
        c.update(dec[c["command"]])
        c["plain_new"] = dec[c["plain"]]["pn"] if c["plain"] else None
    print("cases", len(cs), "unique", len(uniq))
    print("python!=rust: base %d new %d" % (sum(c["pb"] != bool(c["rb"]) for c in cs), sum(c["pn"] != bool(c["rn"]) for c in cs)))
    print("loosened (base denies, new allows) py/rs:", sum(c["pb"] and not c["pn"] for c in cs), sum(bool(c["rb"]) and not c["rn"] for c in cs))
    for kind in ("claude", "g3", "gap"):
        k = [c for c in cs if c["kind"] == kind and c["plain_new"]]
        print("%-6s plain denied: %5d | allowed base py/rs %5d/%5d | allowed NEW py/rs %4d/%4d" % (kind, len(k), sum(not c["pb"] for c in k), sum(not c["rb"] for c in k), sum(not c["pn"] for c in k), sum(not c["rn"] for c in k)))
    for kind in ("control", "nonc"):
        k = [c for c in cs if c["kind"] == kind]
        print("%-7s %5d: denied base py/rs %d/%d, new py/rs %d/%d; newly denied py/rs %d/%d" % (kind, len(k), sum(c["pb"] for c in k), sum(bool(c["rb"]) for c in k), sum(c["pn"] for c in k), sum(bool(c["rn"]) for c in k), sum(c["pn"] and not c["pb"] for c in k), sum(bool(c["rn"]) and not c["rb"] for c in k)))
    holes = [c for c in cs if c["kind"] in ("claude", "g3", "gap") and c["plain_new"] and not (c["pn"] and c["rn"])]
    shapes = {}
    for c in holes:
        shapes.setdefault((c["kind"], c["shape"]), []).append(c)
    for (kd, sp), l in sorted(shapes.items()):
        print("HOLE %s %-12s n=%3d e.g. %r py=%s rs=%s" % (kd, sp, len(l), l[0]["command"][:100], l[0]["pn"], l[0]["rn"]))
    for c in cs:
        if c["kind"] in ("control", "nonc") and (c["pn"] != c["pb"] or c["rn"] != c["rb"] or c["pn"] or c["rn"]):
            print("CONTROL-DENIED/CHANGED %s new py=%s rs=%s base py=%s rs=%s: %r" % (c["id"], c["pn"], c["rn"], c["pb"], c["rb"], c["command"][:100]))
    if out:
        json.dump(cs, open(out, "w"))


if "--selftest" in sys.argv:
    cs = build()
    assert len(cs) > 5000 and len({c["id"] for c in cs}) == len(cs), (len(cs), len({c["id"] for c in cs}))
    assert all("{S}" not in c["command"] and "{C}" not in c["command"] for c in cs)
    print("selftest ok", len(cs))
    sys.exit(0)
main()
