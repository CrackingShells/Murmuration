#!/usr/bin/env python3
"""Replay events through scripts/permission_guard.py and the Rust `murmuration guard`, each started as the hook starts it, and fail on any difference in exit code, stdout or log line.

Sets, all from files or fixed seeds: the registered cases (scripts/fixtures/guard_lists/*.json, copied from __reports__/wave-06/author-w06-5), the 4 malformed events, the lab's recorded Bash/Write/Edit/MultiEdit/NotebookEdit calls
(~/.claude/projects/*Murmuration*), a fuzz set (default 10,000 Bash commands and 2,000 Write/Edit/NotebookEdit events built from rust/tests/fuzz_vocab.json), and a "typeconf"
set of events with odd JSON types and sizes that is reported apart (the port denies a float, array or object where a string is expected; Python may not).

    python3 -I scripts/check_guard_equal.py [--rust BIN] [--python-guard FILE] [--fuzz N] [--fuzz-write N] [--seed S] [--jobs J] [--quick] [--no-recorded] [--out DIR]

Exit 0 when every gated set is equal; 1 otherwise. Intended for the dev git hook (scripts/git-hooks/pre-commit) and for CI.
"""
import argparse
import concurrent.futures
import glob
import json
import os
import platform
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LISTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "guard_lists")   # the registered cases, copied from __reports__/wave-06/author-w06-5
ENV_BASE = dict(os.environ, LC_ALL="en_US.UTF-8")
for k in [k for k in ENV_BASE if k.startswith("PYTHON")]:
    del ENV_BASE[k]


def default_rust():
    """The committed binary for this host (bin/<triple>/<binary name>, from build_manifest's contract), or None where no binary is built for it."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_manifest", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_manifest.py"))
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    target = tool.host_target()
    return None if target is None else os.path.join(REPO, "bin", target, tool.binary_name(target))


def make_arena(root, exists_py):
    T = os.path.join(root, "arena")
    shutil.rmtree(T, ignore_errors=True)
    for d in ("h6", "scripts", "out", "decoy/.claude"):
        os.makedirs(os.path.join(T, d))
    sh = lambda rev, p: subprocess.run(["git", "-C", REPO, "show", rev + ":" + p], capture_output=True, text=True, check=True, encoding="utf-8").stdout
    src, incident = sh("071fc53", "scripts/handback.py"), sh("c4aaebb", "__instrumenta__/w06c3_run_all.py")
    open(T + "/h6/handback.py", "w", encoding="utf-8").write(src)
    open(T + "/h6/permission_guard.py", "w", encoding="utf-8").write(sh("071fc53", "scripts/permission_guard.py"))
    open(T + "/scripts/hello.py", "w", encoding="utf-8").write("print('hello')\n")
    open(T + "/scripts/exists.py", "w", encoding="utf-8").write(exists_py)
    open(T + "/scripts/exists.sh", "w", encoding="utf-8").write("echo ok\n")
    return T, src, incident


def json_fragment(s):
    """s as it reads inside a JSON string literal: {T} is replaced in JSON text, and a Windows T (D:\\a\\...) pasted raw makes invalid escapes. On POSIX it is s itself, so the events are byte for byte what they were."""
    return json.dumps(s)[1:-1]


def registered_events(T, src, incident):
    out = []
    for name in ("e3_attacks", "e3_ordinary", "e3_mention", "e3_evasions", "e3v1_cases", "e3v2_cases", "e3v3_cases", "windows_paths", "redirects", "posix_gaps"):
        for c in json.loads(open("%s/%s.json" % (LISTS, name), encoding="utf-8").read().replace("{T}", json_fragment(T))):
            inp = c.get("input")
            if inp:
                inp = {k: (incident if v == "{INCIDENT}" else src if v == "{HANDBACK}" else v) for k, v in inp.items()}
            out.append(("reg:%s:%s" % (name, c["id"]), json.dumps(dict(tool_name=c["tool"], tool_input=inp if inp else {"command": c["command"]}, cwd=c.get("cwd", T)))))
    return out


def recorded_events(folders, sample):
    rec, seen = [], set()
    for folder in folders:
        for f in sorted(glob.glob(folder + "/**/*.jsonl", recursive=True)):
            for line in open(f, errors="replace", encoding="utf-8"):
                if '"tool_use"' not in line:
                    continue
                try:
                    m = json.loads(line)
                except ValueError:
                    continue
                if m.get("type") != "assistant":
                    continue
                for b in (m.get("message", {}).get("content") or []):
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Bash", "Write", "Edit", "MultiEdit", "NotebookEdit") and b["id"] not in seen:
                        seen.add(b["id"])
                        rec.append(json.dumps(dict(tool_name=b["name"], tool_input=b["input"], cwd=m.get("cwd") or "")))
    if sample and sample < len(rec):
        random.Random(0).shuffle(rec)
        rec = rec[:sample]
    return [("rec:%d" % i, e) for i, e in enumerate(rec)], len(seen)


class Fuzz:
    def __init__(self, seed, vocab, seeds):
        self.r = random.Random(seed)
        self.v = vocab
        self.seeds = seeds
        self.all_tokens = [t for k in ("bypass", "claude", "flags", "assigns", "paths", "writers", "inerts", "ops", "wrappers", "shells", "pipeshells", "procsubs", "quotes", "spaces", "unicode", "words") for t in vocab[k]]

    def pick(self, k):
        return self.r.choice(self.v[k])

    def quote(self, s):
        m = self.r.random()
        if m < 0.35:
            return "'" + s.replace("'", "'\\''") + "'"
        if m < 0.6:
            return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
        if m < 0.7:
            return "'" + s + "'"
        if m < 0.8:
            return '"' + s + '"'
        if m < 0.9:
            return "$'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"
        return s

    def sep(self):
        return self.r.choice(["", " ", " ", " ", "  ", "\t", self.pick("spaces")])

    def piece(self, depth=0):
        r = self.r
        k = r.random()
        if k < 0.22:
            parts = [self.pick("wrappers") if r.random() < 0.35 else "", self.pick("claude"), " ", self.pick("flags") if r.random() < 0.6 else "", " ", self.pick("bypass") if r.random() < 0.5 else "",
                     " ", self.pick("flags") if r.random() < 0.3 else ""]
            return "".join(parts)
        if k < 0.30:
            return self.pick("assigns") + " " + self.pick("claude") + " " + self.pick("flags")
        if k < 0.50:
            return (self.pick("cds") if r.random() < 0.3 else "") + self.pick("writers") + self.pick("paths")
        if k < 0.58:
            return self.pick("interps").replace("SETT", self.pick("paths"))
        if k < 0.68:
            return self.pick("inerts") + self.pick("bypass") + (" " + self.pick("claude") if r.random() < 0.5 else "")
        if k < 0.80 and depth < 3:
            inner = self.gen_cmd(depth + 1)
            if r.random() < 0.3:
                return self.shell_fed(inner)
            return self.pick("shells") + self.sep() + self.quote(inner)
        if k < 0.86:
            body = self.gen_cmd(depth + 1) if depth < 3 else "echo x"
            return self.r.choice(["cat <<'EOF'\n", "cat <<EOF\n", "python3 - <<'EOF'\n", "bash <<'EOF'\n"]) + body + "\nEOF"
        if k < 0.93:
            return " ".join(self.pick("words") for _ in range(r.randint(1, 5)))
        return self.pick("wrappers") + self.pick("inerts") + self.pick("paths")

    def shell_fed(self, inner):
        """A script that reaches a shell by its input: a pipe, a here-string, or a process substitution."""
        r = self.r
        m = r.random()
        if m < 0.4:
            return "echo " + self.quote(inner) + " | " + self.pick("pipeshells")
        if m < 0.6:
            return self.pick("pipeshells") + r.choice(["<<<", " <<< ", " <<<"]) + self.quote(inner)
        if m < 0.85:
            return self.pick("procsubs") + "<(echo " + self.quote(inner) + ")"
        return self.pick("shells") + '"$(echo ' + self.quote(inner) + ')"'

    def gen_cmd(self, depth=0):
        n = self.r.choice([1, 1, 2, 2, 3, 4])
        s = self.piece(depth)
        for _ in range(n - 1):
            s += self.pick("ops") + self.piece(depth)
        return s

    def mutate(self, s):
        r = self.r
        for _ in range(r.randint(1, 3)):
            i = r.randint(0, len(s))
            k = r.random()
            if k < 0.25 and s:
                j = min(len(s), i + r.randint(1, 3))
                s = s[:i] + s[j:]
            elif k < 0.55:
                s = s[:i] + r.choice(self.all_tokens) + s[i:]
            elif k < 0.7 and s:
                j = r.randint(0, len(s))
                a, b = sorted((i, j))
                s = s[:b] + s[a:b] + s[b:]
            elif k < 0.85:
                s = s[:i] + r.choice(["'", '"', "\\", "`", "$(", ")", ";", "&", ">", "\n"]) + s[i:]
            else:
                s = s[:i] + self.pick("spaces") + s[i:]
        return s

    def soup(self):
        r = self.r
        return "".join(r.choice(self.all_tokens) + self.sep() for _ in range(r.randint(2, 30)))

    def bash(self):
        k = self.r.random()
        if k < 0.45:
            return self.gen_cmd()
        if k < 0.75 and self.seeds:
            return self.mutate(self.r.choice(self.seeds))
        if k < 0.9:
            return self.mutate(self.gen_cmd())
        return self.soup()

    def cwd(self):
        return self.r.choice(["", "/h/proj", "/h/proj/.claude", "/x/.claude", "/", "relative/dir", "{T}", "{T}", "/h/proj/.claude/", "//h"])

    def write_event(self):
        r = self.r
        tool = r.choice(["Write", "Write", "Edit", "Edit", "MultiEdit", "NotebookEdit"])
        path = self.pick("write_paths")
        body, other = self.pick("write_bodies"), self.pick("write_bodies")
        if tool == "Write":
            inp = {"file_path": path, "content": body}
        elif tool == "Edit":
            inp = {"file_path": path, "old_string": other, "new_string": body}
        elif tool == "MultiEdit":
            inp = {"file_path": path, "edits": [{"old_string": self.pick("write_bodies"), "new_string": self.pick("write_bodies")} for _ in range(r.randint(0, 3))]}
            if r.random() < 0.3:
                inp.update(old_string=other, new_string=body)
        else:
            inp = {"notebook_path": path, "new_source": body}
        if r.random() < 0.15:
            inp = {("path" if k == "file_path" else k): x for k, x in inp.items()}
        if r.random() < 0.1 and tool == "Write":
            inp["file_path"] = r.choice(["scripts/exists.py", "scripts/exists.sh", "h6/handback.py", "scripts/hello.py", "{T}/scripts/exists.py", "{T}/h6/permission_guard.py"])
        return tool, inp, self.cwd()


def typeconf_events():
    ev = []
    add = lambda name, raw: ev.append(("tc:" + name, raw))
    dump = json.dumps
    for name, tool_input in [("ti_str", "x"), ("ti_list", [1]), ("ti_int", 5), ("ti_true", True), ("ti_zero", 0), ("ti_empty_str", ""), ("ti_null", None), ("ti_false", False), ("ti_empty_list", []), ("ti_empty_dict", {})]:
        for tool in ("Bash", "Write", "Read"):
            add("%s_%s" % (name, tool), dump(dict(tool_name=tool, tool_input=tool_input, cwd="/h")))
    for name, cmd in [("cmd_int", 5), ("cmd_float", 1.5), ("cmd_true", True), ("cmd_dict", {"a": 1}), ("cmd_empty_dict", {}), ("cmd_zero", 0), ("cmd_false", False), ("cmd_null", None), ("cmd_list_empty", []), ("cmd_list", ["ls"])]:
        add(name, dump(dict(tool_name="Bash", tool_input={"command": cmd}, cwd="/h")))
    for name, cwd in [("cwd_int", 5), ("cwd_list", ["a"]), ("cwd_dict", {"a": 1}), ("cwd_true", True), ("cwd_zero", 0), ("cwd_null", None), ("cwd_empty", ""), ("cwd_float", 2.5)]:
        for cmd in ("ls", "cd x; echo a > settings.json", "echo a > .claude/settings.json", "echo a > settings.json"):
            add("%s:%s" % (name, cmd[:12]), dump(dict(tool_name="Bash", tool_input={"command": cmd}, cwd=cwd)))
        add(name + "_write", dump(dict(tool_name="Write", tool_input={"file_path": "rel/x.py", "content": "x"}, cwd=cwd)))
        add(name + "_writeabs", dump(dict(tool_name="Write", tool_input={"file_path": "/abs/x.py", "content": "x"}, cwd=cwd)))
        add(name + "_edit", dump(dict(tool_name="Edit", tool_input={"file_path": "/abs/x.py", "old_string": "a", "new_string": "b"}, cwd=cwd)))
    for name, fp in [("fp_int", 5), ("fp_list", ["x.py"]), ("fp_dict", {"a": 1}), ("fp_true", True), ("fp_zero", 0), ("fp_null", None)]:
        add(name, dump(dict(tool_name="Write", tool_input={"file_path": fp, "content": "x"}, cwd="/h")))
        add(name + "_path", dump(dict(tool_name="Edit", tool_input={"path": fp, "new_string": "x"}, cwd="/h")))
    for name, val in [("content_int", 5), ("content_true", True), ("content_float", 1.5), ("content_list", ["x"]), ("content_dict", {"a": "x"}), ("content_zero", 0), ("content_null", None)]:
        add(name, dump(dict(tool_name="Write", tool_input={"file_path": "/h/x.py", "content": val}, cwd="/h")))
        add(name + "_ns", dump(dict(tool_name="NotebookEdit", tool_input={"notebook_path": "/h/x.ipynb", "new_source": val}, cwd="/h")))
        add(name + "_new", dump(dict(tool_name="Edit", tool_input={"file_path": "/h/x.py", "new_string": val, "old_string": ""}, cwd="/h")))
    for name, val in [("edits_int", 5), ("edits_true", True), ("edits_str", "abc"), ("edits_dict", {"a": 1}), ("edits_list_mixed", [1, "a", {"new_string": "x"}, None]), ("edits_zero", 0), ("edits_float", 1.5)]:
        add(name, dump(dict(tool_name="MultiEdit", tool_input={"file_path": "/h/x.py", "edits": val}, cwd="/h")))
    for name, tool in [("tool_int", 5), ("tool_null", None), ("tool_list", ["Bash"]), ("tool_lower", "bash"), ("tool_dict", {})]:
        add(name, dump(dict(tool_name=tool, tool_input={"command": "ls"}, cwd="/h")))
    add("no_keys", "{}")
    add("tool_name_only", '{"tool_name": "Bash"}')
    add("dup_keys", '{"tool_name": "Read", "tool_name": "Bash", "tool_input": {"command": "ls"}, "tool_input": {"command": "echo hi"}}')
    bash = lambda c: dump(dict(tool_name="Bash", tool_input={"command": c}, cwd="/h"))
    for name, raw in [("empty_ws", "  \n "), ("list", "[]"), ("null", "null"), ("str", '"x"'), ("int", "5"), ("true", "true"), ("bom", "\ufeff{}"), ("trailing", "{} x"), ("trailing_comma", '{"a": 1,}'),
                      ("nan", '{"tool_name": "Bash", "tool_input": {"command": NaN}}'), ("inf", '{"tool_name": "Read", "x": -Infinity, "y": Infinity}'), ("big_exp", '{"tool_name": 1e999, "tool_input": {"command": "ls"}}'),
                      ("neg_zero", '{"tool_name": "Bash", "tool_input": {"command": -0}}'), ("zero_float", '{"tool_name": "Bash", "tool_input": {"command": 0.0e5}}'), ("tiny", '{"tool_name": "Bash", "tool_input": {"command": 1e-999}}'),
                      ("lone_hi", '{"tool_name": "Bash", "tool_input": {"command": "echo \\ud800 x"}}'), ("lone_lo", '{"tool_name": "Bash", "tool_input": {"command": "echo \\udc80"}}'),
                      ("pair", '{"tool_name": "Bash", "tool_input": {"command": "echo \\ud83d\\ude00"}}'), ("hi_then_bad", '{"tool_name": "Bash", "tool_input": {"command": "\\ud800\\u0041"}}'),
                      ("bad_escape", '{"tool_name": "Bash", "tool_input": {"command": "\\x"}}'), ("ctrl_in_string", '{"tool_name": "Bash", "tool_input": {"command": "a\tb"}}'),
                      ("single_quotes", "{'a': 1}"), ("leading_zero", '{"a": 01}'), ("plus", '{"a": +1}'), ("dot", '{"a": 1.}'), ("exp_no_digits", '{"a": 1e}'), ("deep_ok", "[" * 5000 + "]" * 5000),
                      ("depth_9996", "[" * 9996 + "]" * 9996), ("depth_9997", "[" * 9997 + "]" * 9997), ("depth_9998", "[" * 9998 + "]" * 9998), ("depth_9999", "[" * 9999 + "]" * 9999), ("depth_20000", "[" * 20000),
                      ("obj_depth_9997", '{"a":' * 9997 + "1" + "}" * 9997), ("obj_depth_9998", '{"a":' * 9998 + "1" + "}" * 9998),
                      ("int_4300", '{"tool_name": 1' + "0" * 4299 + "}"), ("int_4301", '{"tool_name": 1' + "0" * 4300 + "}"), ("int_neg_4301", '{"tool_name": -1' + "0" * 4300 + "}"),
                      ("float_long", '{"tool_name": 1.' + "0" * 5000 + "}"), ("huge_cmd", bash("echo " + "x " * 200000)),
                      ("long_run_settings", bash("python3 -c \"open('w')\" " + "settings.json" * 20000)),
                      ("long_word", bash("python3 -c write " + "a" * 300000)),
                      ("many_quotes", bash("echo " + "'a' \"b\" " * 50000)),
                      ("unicode_key", '{"tool\\u005fname": "Bash", "tool_input": {"command": "ls"}}'), ("whitespace_exotic", '{"tool_name":\u00a0"Bash"}'), ("tab_ws", '\t{"tool_name"\t:\t"Read"\t}\r\n')]:
        add(name, raw)
    ev.append(("tc:invalid_utf8", b'{"tool_name": "Bash", "tool_input": {"command": "echo \xff"}}'))
    ev.append(("tc:overlong_utf8", b'{"tool_name": "Bash", "tool_input": {"command": "echo \xc0\xaf"}}'))
    ev.append(("tc:surrogate_utf8", b'{"tool_name": "Bash", "tool_input": {"command": "echo \xed\xa0\x80"}}'))
    ev.append(("tc:cr_bytes", b'{"tool_name": "Bash",\r"tool_input": {"command": "ls"}}'))
    return ev


MALFORMED = [("mal:empty", ""), ("mal:not_json", "not json"), ("mal:list", "[]"), ("mal:null_tool_input", json.dumps({"tool_name": "Bash", "tool_input": None}))]


def run_one(args):
    idx, name, payload, py_cmd, rust_cmd, wdir, T = args
    if isinstance(payload, str):
        payload = payload.replace("{T}", json_fragment(T)).encode("utf-8", "surrogatepass")
    res = []
    for tag, cmd in (("py", py_cmd), ("rs", rust_cmd)):
        log = os.path.join(wdir, "%s_%d.log" % (tag, threading.get_ident() % 100000))
        if os.path.exists(log):
            os.remove(log)
        t0 = time.time()
        try:
            p = subprocess.run(cmd, input=payload, capture_output=True, env=dict(ENV_BASE, MURMURATION_GUARD_LOG=log), timeout=40)
        except subprocess.TimeoutExpired:
            res.append(("timeout", "", None, False, 40.0))
            continue
        logtxt = open(log, "rb").read().decode("utf-8", "replace") if os.path.exists(log) else None
        res.append((p.returncode, p.stdout.decode("utf-8", "replace"), logtxt, bool(p.stderr), time.time() - t0))
    return idx, name, res


def _utf8_stdio():
    """Hook JSON and reports are UTF-8 on every OS, whatever the locale: `python -I` ignores PYTHONUTF8 and PYTHONIOENCODING, and a Windows pipe is otherwise read and written in the ANSI code page."""
    for stream, extra in ((sys.stdin, {}), (sys.stdout, {"newline": "\n"}), (sys.stderr, {"newline": "\n"})):
        try:
            stream.reconfigure(encoding="utf-8", **extra)
        except (AttributeError, ValueError, OSError):
            pass


def main():
    _utf8_stdio()
    ap = argparse.ArgumentParser()
    ap.add_argument("--rust", default=default_rust(), help="the murmuration binary to replay (default: the committed one for this host)")
    ap.add_argument("--python-guard", default=os.path.join(REPO, "scripts", "permission_guard.py"))
    ap.add_argument("--fuzz", type=int, default=10000)
    ap.add_argument("--fuzz-write", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--no-recorded", action="store_true")
    ap.add_argument("--recorded-sample", type=int, default=0)
    ap.add_argument("--recorded", nargs="*", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--sets", default=None, help="comma list of sets to run (registered,malformed,recorded,fuzz_bash,fuzz_write,typeconf,stress); default all")
    a = ap.parse_args()
    if a.rust is None:
        ap.error("no binary is built for this host (%s %s); pass --rust BIN" % (platform.system(), platform.machine()))
    if a.quick:
        a.fuzz, a.fuzz_write, a.recorded_sample = 300, 60, a.recorded_sample or 200
    work = a.out or tempfile.mkdtemp(prefix="guard_equal_")
    os.makedirs(work, exist_ok=True)
    vocab = json.load(open(os.path.join(REPO, "rust", "tests", "fuzz_vocab.json"), encoding="utf-8"))
    T, src, incident = make_arena(work, vocab["arena_exists_py"])
    sets = {}
    sets["registered"] = registered_events(T, src, incident)
    sets["malformed"] = MALFORMED
    n_rec_all = 0
    if not a.no_recorded:
        folders = a.recorded if a.recorded is not None else sorted(glob.glob(os.path.expanduser("~/.claude/projects/*Murmuration*")))
        sets["recorded"], n_rec_all = recorded_events(folders, a.recorded_sample)
    seeds = [json.loads(p)["tool_input"]["command"] for _, p in sets["registered"] if isinstance(json.loads(p).get("tool_input", {}).get("command"), str)]
    fz = Fuzz(a.seed, vocab, seeds)
    sets["fuzz_bash"] = [("fz:%d" % i, json.dumps(dict(tool_name="Bash", tool_input={"command": fz.bash()}, cwd=fz.cwd()))) for i in range(a.fuzz)]
    wr = []
    for i in range(a.fuzz_write):
        tool, inp, cwd = fz.write_event()
        wr.append(("fw:%d" % i, json.dumps(dict(tool_name=tool, tool_input=inp, cwd=cwd))))
    sets["fuzz_write"] = wr
    tc = typeconf_events()
    sets["typeconf"] = [e for e in tc if not e[0].startswith(("tc:huge", "tc:long_", "tc:many_"))]
    sets["stress"] = [e for e in tc if e[0].startswith(("tc:huge", "tc:long_", "tc:many_"))]
    if a.sets:
        sets = {k: v for k, v in sets.items() if k in a.sets.split(",")}
    py_cmd = [sys.executable, "-S", "-I", a.python_guard]
    rust_cmd = [a.rust, "guard"]
    jobs, owner = [], []
    for sname, evs in sets.items():
        for name, payload in evs:
            jobs.append((len(jobs), name, payload, py_cmd, rust_cmd, work, T))
            owner.append(sname)
    t0 = time.time()
    diffs = {s: [] for s in sets}
    denied = {s: 0 for s in sets}
    stderr_seen = {s: [0, 0] for s in sets}
    slow = []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for idx, name, (py, rs) in ex.map(run_one, jobs):
            s = owner[idx]
            denied[s] += bool(rs[1])
            stderr_seen[s][0] += py[3]
            stderr_seen[s][1] += rs[3]
            if s == "stress":
                slow.append((name, round(py[4], 2), round(rs[4], 2), py[0], rs[0]))
            if py[:3] != rs[:3]:
                diffs[s].append((name, py[:3], rs[:3]))
    print("rust %s | python %s | %.0f s | jobs %d | seed %d" % (a.rust, a.python_guard, time.time() - t0, a.jobs, a.seed))
    if n_rec_all:
        print("recorded calls found: %d (sample %s)" % (n_rec_all, a.recorded_sample or "all"))
    print("%-12s %8s %8s %8s  %s" % ("set", "events", "denied", "differ", "stderr non-empty (py, rs)"))
    bad = 0
    for s, evs in sets.items():
        print("%-12s %8d %8d %8d  %s" % (s, len(evs), denied[s], len(diffs[s]), tuple(stderr_seen[s])))
        if s not in ("typeconf", "stress"):
            bad += len(diffs[s])
    for x in slow:
        print("  STRESS %-28s python %6.2f s (rc %s)   rust %6.2f s (rc %s)" % (x[0], x[1], x[3], x[2], x[4]))
    json.dump(diffs, open(os.path.join(work, "differences.json"), "w", encoding="utf-8"), indent=1, default=str)
    for s, d in diffs.items():
        for name, py, rs in d[:12]:
            print("  DIFF", s, name, "\n     py", repr(py)[:300], "\n     rs", repr(rs)[:300])
    print("gated sets equal" if not bad else "FAIL: %d differences in gated sets" % bad, "| work folder", work)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
