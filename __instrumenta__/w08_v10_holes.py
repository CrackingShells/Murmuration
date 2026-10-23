# w08-c10 verifier: independent hole test; builds its own forms (a flag after a substitution, substitutions elsewhere, claude inside a substitution, 100+ wrapper forms with value options, G3 writes behind them) from w08_v10_flags.json, decides each with the Python guard and the Rust guard of a BASE tree and a NEW tree; prints holes (plain form denied, variant allowed) per tree, controls (ordinary flags) and the base-vs-new monotonicity (base deny => new deny), Python vs Rust differences; output: stdout, --out JSON. Usage: python3 -I w08_v10_holes.py BASE_TREE NEW_TREE [--out F] [--jobs N]
import concurrent.futures, importlib.util, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "w08_v10_flags.json")))
FLAGS, WRITES = D["flags"], D["g3_writes"]
CONTROL_FLAGS = ["--model opus", "--verbose", "--print", "--setting-sources user", "--setting-sources=user,project", "--resume abc", "-c", "--output-format json", "--max-turns 3"]

# claude-command shapes with {F} (the flag part)
CLAUDE_SHAPES = {
    "plain": "claude -p hi {F}",
    "dq_subst": 'claude -p "$(cat f)" {F}',
    "dq_subst_first": 'claude "$(cat f)" {F}',
    "subst_bare": "claude -p $(cat f) {F}",
    "bt": "claude -p `cat f` {F}",
    "bt_dq": 'claude -p "`cat f`" {F}',
    "subst_mid_word": 'claude -p "pre$(cat f)post" {F}',
    "subst_model": "claude --model $(cat m) -p hi {F}",
    "subst_sysprompt": 'claude --append-system-prompt "$(cat sp.md)" -p hi {F}',
    "procsub": "claude <(echo x) {F}",
    "procsub_out": "claude >(cat) {F}",
    "subst_semicolon": 'claude -p "$(a; b)" {F}',
    "subst_pipe": 'claude -p "$(a | b)" {F}',
    "subst_subshell": 'claude -p "$( (a) )" {F}',
    "subst_quote_in": "claude -p \"$(echo 'a)b')\" {F}",
    "subst_dq_in": 'claude -p "$(echo "a)b")" {F}',
    "nested": 'claude -p "$(cat "$(echo f)")" {F}',
    "nested3": 'claude -p "$(a "$(b "$(c)")")" {F}',
    "two": 'claude -p "$(cat f)" "$(cat g)" {F}',
    "subst_after_flag_pos": 'claude -p hi "$(cat f)" {F} tail',
    "subst_after": 'claude -p hi {F} "$(cat f)"',
    "subst_in_flag_value": 'claude -p hi {F} "$(cat f)" more',
    "heredoc_subst": "claude -p \"$(cat <<'EOF'\nhello (x\nEOF\n)\" {F}",
    "env_assign_subst": 'X="$(cat f)" claude -p hi {F}',
    "env_assign_subst2": 'env X="$(cat f)" claude -p hi {F}',
    "path_claude": '/usr/local/bin/claude -p "$(cat f)" {F}',
    "tilde_claude": '~/.local/bin/claude -p "$(cat f)" {F}',
    "quoted_claude": '"claude" -p "$(cat f)" {F}',
    "pipe_into": "cat f | claude -p $(cat g) {F}",
    "and_then": 'true && claude -p "$(cat f)" {F}',
    "or_else": 'false || claude -p "$(cat f)" {F}',
    "bg": 'claude -p "$(cat f)" {F} &',
    "subshell": '( claude -p "$(cat f)" {F} )',
    "brace": '{ claude -p "$(cat f)" {F}; }',
    "if_then": 'if true; then claude -p "$(cat f)" {F}; fi',
    "for_do": 'for i in 1 2; do claude -p "$(cat $i)" {F}; done',
    "while": 'while read l; do claude -p "$(echo $l)" {F}; done < in',
    "redirect_in": 'claude -p "$(cat f)" {F} < in > out 2>&1',
    "redirect_before": 'claude < in -p "$(cat f)" {F}',
    "subst_in_redirect": 'claude -p hi {F} > "$(mktemp)"',
    "in_dq_outer": 'echo "x $(claude -p "$(cat f)" {F})"',
    "in_subst": 'x=$(claude -p "$(cat f)" {F})',
    "in_bt": 'x=`claude -p "$(cat f)" {F}`',
    "sh_c": "sh -c 'claude -p \"$(cat f)\" {F}'",
    "bash_lc": "bash -lc 'claude -p \"$(cat f)\" {F}'",
    "eval": "eval 'claude -p \"$(cat f)\" {F}'",
    "program_which": '"$(which claude)" -p hi {F}',
    "program_cmdv": "$(command -v claude) -p hi {F}",
    "program_bt": "`which claude` -p hi {F}",
    "program_typep": "$(type -p claude) -p hi {F}",
    "program_echo": "$(echo claude) -p hi {F}",
    "program_printf": "$(printf claude) -p hi {F}",
    "program_cat_subst": '$(cat bin.txt) -p hi {F}',
    "program_subst_nonclaude": '$(echo c)laude -p hi {F}',
    "subst_prog_dq_nested": '"$($(which claude) --version)" {F}',
}
WRAPS = {
    "env_u": "env -u V claude", "env_uV": "env -uV claude", "env_unset": "env --unset V claude", "env_unset_eq": "env --unset=V claude", "env_unset_prefix": "env --unse V claude",
    "env_i": "env -i claude", "env_i_assign": "env -i A=1 claude", "env_dashdash": "env -- claude", "env_assign": "env A=1 claude", "env_C": "env -C /tmp claude", "env_Cdir": "env -C/tmp claude",
    "env_u_u": "env -u V -u W claude", "env_iu": "env -iu V claude", "env_ui": "env -ui claude", "env_u_assign": "env -u V A=1 claude", "env_assign_u": "env A=1 -u V claude",
    "env_P": "env -P /usr/bin claude", "env_a": "env -a name claude", "env_0": "env -0 claude", "env_v": "env -v claude", "env_u_dashdash": "env -u V -- claude",
    "env_S": "env -S 'claude'", "env_S_adj": "env -Sclaude", "env_S_dq": 'env -S "claude"', "env_S_assign": "env -S 'A=1 claude'", "env_split": "env --split-string='claude'", "env_split2": "env --split-string 'claude'",
    "env_S_after_u": "env -u V -S 'claude'", "env_S_env": "env -S 'env -u V claude'", "env_S_sh": "env -S 'sh -c claude'",
    "usr_bin_env": "/usr/bin/env -u V claude", "command": "command claude", "command_p": "command -p claude", "command_dashdash": "command -- claude",
    "exec": "exec claude", "exec_a": "exec -a name claude", "exec_c": "exec -c claude", "exec_l": "exec -l claude", "exec_cl": "exec -cl claude", "exec_env_u": "exec env -u V claude",
    "nohup": "nohup claude", "nohup_env_u": "nohup env -u V claude",
    "nice_n": "nice -n 5 claude", "nice_n5": "nice -n5 claude", "nice_num": "nice -5 claude", "nice_adj": "nice --adjustment=5 claude", "nice_adj_sep": "nice --adjustment 5 claude",
    "timeout": "timeout 5 claude", "timeout_s": "timeout -s KILL 5 claude", "timeout_s9": "timeout -s 9 5 claude", "timeout_k": "timeout -k 1 5 claude", "timeout_signal_eq": "timeout --signal=KILL 5 claude",
    "timeout_signal": "timeout --signal KILL 5 claude", "timeout_kafter": "timeout --kill-after=1 5 claude", "timeout_fg": "timeout --foreground 5 claude", "timeout_p": "timeout --preserve-status 5 claude", "timeout_v": "timeout -v 5 claude",
    "timeout_sk": "timeout -s KILL -k 1 5 claude", "gtimeout_s": "gtimeout -s KILL 5 claude", "timeout_5s": "timeout 5s claude", "timeout_s_env_u": "timeout -s KILL 5 env -u V claude",
    "xargs": "xargs claude", "xargs_n1": "xargs -n1 claude", "xargs_n_1": "xargs -n 1 claude", "xargs_I": "xargs -I{} claude", "xargs_I_sp": "xargs -I {} claude", "xargs_0": "xargs -0 claude", "xargs_P": "xargs -P 4 claude",
    "xargs_a": "xargs -a file claude", "xargs_d": "xargs -d '\\n' claude", "xargs_L": "xargs -L 1 claude", "xargs_s": "xargs -s 100 claude", "xargs_E": "xargs -E eof claude", "xargs_r": "xargs -r claude", "xargs_t": "xargs -t claude",
    "xargs_long": "xargs --max-args 1 claude", "xargs_long_eq": "xargs --max-args=1 claude", "xargs_replace": "xargs --replace claude", "xargs_n1_P": "xargs -n1 -P2 claude", "echo_xargs": "echo x | xargs -I % claude",
    "sudo": "sudo claude", "sudo_u": "sudo -u root claude", "sudo_E": "sudo -E claude", "sudo_user": "sudo --user root claude", "sudo_user_eq": "sudo --user=root claude", "sudo_n": "sudo -n claude", "sudo_H_u": "sudo -H -u root claude",
    "time": "time claude", "time_p": "time -p claude", "time_f": "time -f %e claude", "time_o": "time -o out claude",
    "stdbuf_oL": "stdbuf -oL claude", "stdbuf_o_L": "stdbuf -o L claude", "stdbuf_i0": "stdbuf -i0 -o0 claude", "stdbuf_long": "stdbuf --output=L claude",
    "setsid": "setsid claude", "setsid_w": "setsid -w claude", "setsid_f": "setsid -f claude",
    "caffeinate": "caffeinate claude", "caffeinate_i": "caffeinate -i claude", "caffeinate_t": "caffeinate -t 5 claude", "caffeinate_it": "caffeinate -i -t 5 claude", "caffeinate_w": "caffeinate -w 123 claude",
    "ionice_c": "ionice -c 3 claude", "ionice_c3": "ionice -c3 claude", "ionice_n": "ionice -n 7 claude", "ionice_cn": "ionice -c 2 -n 7 claude",
    "chain": "nohup nice -n 5 timeout -s KILL 5 env -u V claude", "chain2": "env -u V nohup timeout 5 claude", "chain3": "timeout 9 xargs -n1 env -u V claude", "chain4": "command env -u V claude",
    "chain5": "sudo -u x env -S 'claude'", "chain6": "exec -a n env -u V nice -n 5 claude",
    "builtin": "builtin claude", "arch": "arch -arm64 claude", "doas": "doas claude", "find_exec": "find . -maxdepth 0 -exec claude", "unbuffer": "unbuffer claude", "watch": "watch claude", "script": "script -q /dev/null claude",
    "taskset": "taskset 1 claude", "chroot": "chroot / claude", "su_c": "su -c claude", "ssh": "ssh host claude", "parallel": "parallel claude ::: a", "ulimit_first": "ulimit -n 10; claude",
}
# wrapper forms are combined with a plain and a substitution-before tail
WRAP_TAILS = ["-p hi {F}", '-p "$(cat f)" {F}']
G3_SHAPES = {
    "plain": "{W}",
    "after_subst": 'echo "$(date)" ; {W}',
    "subst_first": 'x="$(pwd)"; {W}',
    "env_u": "env -u V {W}", "timeout_s": "timeout -s KILL 5 {W}", "nice_n": "nice -n 5 {W}", "xargs_n1": "xargs -n1 {W}", "sudo_u": "sudo -u root {W}", "env_S": "env -S '{W}'", "nohup": "nohup {W}", "exec_a": "exec -a n {W}",
    "heredoc_subst": 'x="$(cat <<EOF\nhello\nEOF\n)"; {W}',
    "dq_subst_cmd": 'echo "$({W})"',
    "bt_cmd": "echo `{W}`",
}


def build():
    cs = []
    for sn, sh in CLAUDE_SHAPES.items():
        for fi, f in enumerate(FLAGS):
            cs.append(dict(id="C:%s:f%d" % (sn, fi), kind="claude", shape=sn, command=sh.replace("{F}", f), plain=("claude -p hi " + f)))
    for wn, w in WRAPS.items():
        for ti, t in enumerate(WRAP_TAILS):
            for fi, f in enumerate(FLAGS):
                cs.append(dict(id="W:%s:t%d:f%d" % (wn, ti, fi), kind="wrap", shape=wn, command=w + " " + t.replace("{F}", f), plain=("claude " + t.replace("{F}", f))))
    for sn, sh in G3_SHAPES.items():
        for wi, w in enumerate(WRITES):
            cs.append(dict(id="G3:%s:w%d" % (sn, wi), kind="g3", shape=sn, command=sh.replace("{W}", w), plain=w))
    for cf in CONTROL_FLAGS:
        for sn, sh in CLAUDE_SHAPES.items():
            cs.append(dict(id="K:%s:%s" % (sn, cf), kind="control", shape=sn, command=sh.replace("{F}", cf), plain=None))
        for wn, w in WRAPS.items():
            cs.append(dict(id="KW:%s:%s" % (wn, cf), kind="control", shape=wn, command=w + ' -p "$(cat f)" ' + cf, plain=None))
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
    rows = []
    for c in cs:
        d = dec[c["command"]]
        c.update(d)
        c["plain_denied_new"] = dec[c["plain"]]["pn"] if c["plain"] else None
        c["plain_denied_base"] = dec[c["plain"]]["pb"] if c["plain"] else None
        rows.append(c)
    print("cases", len(rows), "unique commands", len(uniq))
    print("python!=rust:  base %d  new %d" % (sum(1 for r in rows if r["pb"] != r["rb"]), sum(1 for r in rows if r["pn"] != r["rn"])))
    print("monotone violations (base denies, new allows) py/rs:", sum(1 for r in rows if r["pb"] and not r["pn"]), sum(1 for r in rows if r["rb"] and not r["rn"]))
    for kind in ("claude", "wrap", "g3"):
        k = [r for r in rows if r["kind"] == kind and r["plain_denied_new"]]
        print("%-7s variants with denied plain form: %5d | allowed base py/rs: %4d/%4d | allowed NEW py/rs: %3d/%3d" % (kind, len(k), sum(1 for r in k if not r["pb"]), sum(1 for r in k if not r["rb"]), sum(1 for r in k if not r["pn"]), sum(1 for r in k if not r["rn"])))
    ctl = [r for r in rows if r["kind"] == "control"]
    print("controls %d: denied base py/rs %d/%d, new py/rs %d/%d; newly denied py/rs %d/%d" % (len(ctl), sum(r["pb"] for r in ctl), sum(bool(r["rb"]) for r in ctl), sum(r["pn"] for r in ctl), sum(bool(r["rn"]) for r in ctl), sum(1 for r in ctl if r["pn"] and not r["pb"]), sum(1 for r in ctl if r["rn"] and not r["rb"])))
    for r in rows:
        if r["kind"] != "control" and r["plain_denied_new"] and not (r["pn"] and r["rn"]):
            print("HOLE(new) %s py=%s rs=%s base py=%s rs=%s: %r" % (r["id"], r["pn"], r["rn"], r["pb"], r["rb"], r["command"][:110]))
    for r in ctl:
        if r["pn"] != r["pb"] or r["rn"] != r["rb"] or r["pn"]:
            print("CONTROL-DENIED %s new py=%s rs=%s base py=%s rs=%s: %r" % (r["id"], r["pn"], r["rn"], r["pb"], r["rb"], r["command"][:110]))
    if out:
        json.dump(rows, open(out, "w"))


if "--selftest" in sys.argv:
    cs = build()
    assert len(cs) > 3000 and len({c["id"] for c in cs}) == len(cs)
    assert all("{F}" not in c["command"] and "{W}" not in c["command"] for c in cs)
    print("selftest ok", len(cs))
    sys.exit(0)
main()
