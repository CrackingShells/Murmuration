#!/usr/bin/env python3
"""Static check: every script here reads and writes text as UTF-8 on every OS.

    python3 -I scripts/check_text_io.py [DIR]        exit 0 when clean, 1 with one line per finding
    python3 -I scripts/check_text_io.py --selftest   the check catches each kind of finding, and the guard reads a UTF-8 payload under a non-UTF-8 locale

Python opens a text file, and reads a text-mode subprocess pipe, in the locale's code page unless told otherwise (cp1252 on a Windows runner), so a UTF-8 file with one non-ASCII
byte fails there and passes on macOS and Linux. Findings, for each *.py in DIR (default: this folder):
  open: a text-mode open(), io.open(), read_text() or write_text() without encoding=
  subprocess: a subprocess call with text=True or universal_newlines=True and no encoding=
  stdio: a def main( that does not start with _utf8_stdio(), or a _utf8_stdio that does not reconfigure the streams to UTF-8
A mode that is not a literal string, or a call that passes **kwargs, cannot be checked and is a finding. Binary opens (a "b" in the mode) are exempt.
"""
import ast
import glob
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SUBPROCESS_CALLS = ("run", "Popen", "check_output", "check_call", "call")


def _call_name(fn):
    if isinstance(fn, ast.Name):
        return fn.id, None
    if isinstance(fn, ast.Attribute):
        return fn.attr, fn.value.id if isinstance(fn.value, ast.Name) else None
    return None, None


def _findings_for_call(n):
    name, owner = _call_name(n.func)
    kws = {k.arg: k.value for k in n.keywords}
    if name is None:
        return []
    is_open = (name == "open" and owner in (None, "io")) or name in ("read_text", "write_text")
    is_run = name in SUBPROCESS_CALLS and owner in ("subprocess", "sp")
    if not (is_open or is_run):
        return []
    if None in kws:
        return [("open" if is_open else "subprocess", n.lineno, "%s(**kwargs) cannot be checked" % name)]
    if is_open:
        if name == "open":
            mode = n.args[1] if len(n.args) > 1 else kws.get("mode")
            if mode is not None and not (isinstance(mode, ast.Constant) and isinstance(mode.value, str)):
                return [("open", n.lineno, "open() with a mode that is not a literal string")]
            if mode is not None and "b" in mode.value:
                return []
        elif name == "read_text" and len(n.args) > 0 or name == "write_text" and len(n.args) > 1:
            return []           # encoding given positionally
        if "encoding" not in kws:
            return [("open", n.lineno, "%s() without encoding=" % name)]
        return []
    t = kws.get("text") or kws.get("universal_newlines")
    if isinstance(t, ast.Constant) and t.value is True and "encoding" not in kws:
        return [("subprocess", n.lineno, "subprocess.%s with text=True and no encoding=" % name)]
    return []


def _calls(node, name):
    return [c for c in ast.walk(node) if isinstance(c, ast.Call) and _call_name(c.func)[0] == name]


def check_source(src, label):
    """The findings, as (kind, line, text), for one source text."""
    tree = ast.parse(src)
    found = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            found += _findings_for_call(n)
    mains = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"]
    helper = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_utf8_stdio"]
    for m in mains:
        body = [s for s in m.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))]
        first = body[0] if body else None
        if not (isinstance(first, ast.Expr) and isinstance(first.value, ast.Call) and _call_name(first.value.func)[0] == "_utf8_stdio"):
            found.append(("stdio", m.lineno, "main() does not start with _utf8_stdio()"))
    if mains:
        ok = False
        for h in helper:
            for c in _calls(h, "reconfigure"):
                enc = [k.value for k in c.keywords if k.arg == "encoding"]
                ok = ok or (len(enc) == 1 and isinstance(enc[0], ast.Constant) and enc[0].value == "utf-8")
        if not ok:
            found.append(("stdio", mains[0].lineno, "_utf8_stdio is missing or does not reconfigure the streams with encoding=\"utf-8\""))
    return sorted(found, key=lambda f: f[1])


def check_dir(folder):
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "*.py"))):
        with open(path, "rb") as fh:
            src = fh.read()
        for kind, line, text in check_source(src, path):
            out.append("%s:%d: %s: %s" % (os.path.basename(path), line, kind, text))
    return out


def selftest():
    bad = {
        "open": ("def f():\n    open('x')\n", "open('x', 'w')\n", "open('x', mode='a')\n", "import io\nio.open('x')\n", "p.read_text()\n", "p.write_text('x')\n", "open('x', m)\n", "open('x', **kw)\n"),
        "subprocess": ("import subprocess\nsubprocess.run(['x'], text=True)\n", "import subprocess\nsubprocess.Popen(['x'], universal_newlines=True)\n", "import subprocess\nsubprocess.check_output(['x'], text=True, errors='replace')\n"),
        "stdio": ("def main():\n    pass\n", "def _utf8_stdio():\n    pass\ndef main():\n    _utf8_stdio()\n",
                  "def _utf8_stdio():\n    sys.stdin.reconfigure(encoding='ascii')\ndef main():\n    _utf8_stdio()\n",
                  "def _utf8_stdio():\n    sys.stdin.reconfigure(encoding='utf-8')\ndef main():\n    x = 1\n    _utf8_stdio()\n"),
    }
    good = ("open('x', 'rb')\n", "open('x', 'wb')\n", "open('x', encoding='utf-8')\n", "open('x', 'w', encoding='utf-8', errors='replace')\n", "p.read_text(encoding='utf-8')\n", "p.read_text('utf-8')\n",
            "import subprocess\nsubprocess.run(['x'], capture_output=True)\n", "import subprocess\nsubprocess.run(['x'], text=True, encoding='utf-8')\n", "os.open('x', 0)\n",
            "def _utf8_stdio():\n    sys.stdin.reconfigure(encoding='utf-8')\ndef main():\n    '''doc'''\n    _utf8_stdio()\n")
    ok = True
    for kind, sources in bad.items():
        for s in sources:
            kinds = {f[0] for f in check_source(s, "<mutation>")}
            if kind not in kinds:
                ok = False
                print("FAIL: not caught as %s: %r (caught %s)" % (kind, s, sorted(kinds)))
    for s in good:
        if check_source(s, "<control>"):
            ok = False
            print("FAIL: flagged without cause: %r -> %s" % (s, check_source(s, "<control>")))
    # the guard, started as the hook starts it but under the C locale with no UTF-8 mode, reads a UTF-8 payload as UTF-8: the log shows the code points, not their bytes
    payload = '{"tool_name": "Bash", "tool_input": {"command": "echo é日"}, "cwd": "/tmp"}'.encode("utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, "g.log")
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        env.update(LC_ALL="C", LANG="C", PYTHONCOERCECLOCALE="0", PYTHONUTF8="0", MURMURATION_GUARD_LOG=log)
        p = subprocess.run([sys.executable, "-X", "utf8=0", os.path.join(HERE, "permission_guard.py")], input=payload, capture_output=True, env=env)
        with open(log, "rb") as fh:
            line = fh.read().decode("ascii")
        if p.returncode != 0 or "echo \\u00e9\\u65e5" not in line:
            ok = False
            print("FAIL: the guard under the C locale: exit %s, log %r, stderr %r" % (p.returncode, line, p.stderr[-200:]))
    print("selftest check_text_io: %s" % ("ok" if ok else "FAILED"))
    return 0 if ok else 1


def _utf8_stdio():
    """Hook JSON and reports are UTF-8 on every OS, whatever the locale: `python -I` ignores PYTHONUTF8 and PYTHONIOENCODING, and a Windows pipe is otherwise read and written in the ANSI code page."""
    for stream, extra in ((sys.stdin, {}), (sys.stdout, {"newline": "\n"}), (sys.stderr, {"newline": "\n"})):
        try:
            stream.reconfigure(encoding="utf-8", **extra)
        except (AttributeError, ValueError, OSError):
            pass


def main():
    _utf8_stdio()
    if "--selftest" in sys.argv[1:]:
        return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    findings = check_dir(args[0] if args else HERE)
    for line in findings:
        print(line)
    print("check_text_io: %s" % ("clean" if not findings else "%d findings" % len(findings)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
