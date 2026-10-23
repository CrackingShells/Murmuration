#!/usr/bin/env python3
"""Deny the direct forms of skipping or loosening Claude Code's permission layer, from a PreToolUse hook.

Python standard library only. hooks.json starts it as `python3 -S -I permission_guard.py` (no `site`, no PYTHON* variables; the script imports only the
standard library and reads MURMURATION_GUARD_LOG through os.environ, which -I leaves alone). The Bash row has no `if` rule: the guard starts on every
Bash call (v3), and the Write/Edit/NotebookEdit rows start it only when a cheap `if` rule has matched (`Write(**/.claude/settings*.json)`, `Write(**/*.py)`, ...),
so an ordinary Write or Edit starts no process. The `if` rules over-approximate; this script is the exact judge. It reads the event on stdin and answers with a
`permissionDecision: deny` and a reason, or says nothing (allow).
The rows carry `"onFailure": "block"`: if this script cannot run (unreadable, crashes, no python3, timeout), the call is blocked.
Inside the script, any exception also becomes a deny (fail closed).

    permission_guard.py              read a PreToolUse event from stdin
    permission_guard.py --selftest   check the decision function on the committed lists of w06-c7 and on small cases

Denied (the user's yes is needed; the message says so):
  G1  (v3: only when the command text, heredoc bodies included, also names `claude` or `claude_agent_sdk`) a Bash command that, outside a read-only search, carries the words of the bypass: `bypassPermissions`, `--permission-mode bypass...`,
      `--dangerously-...` flags, `skipDangerousModePermissionPrompt`. Commands that only search for the words (grep, rg, jq, git log, ...) pass.
  G2  a `claude` child that leaves the user's settings and hooks: `--setting-sources` without `user`, `--bare`, `--safe-mode`,
      `--settings` carrying `disableAllHooks`; and any `CLAUDE_CONFIG_DIR=` assignment.
  G3  Write, Edit or MultiEdit of a Claude Code settings file (`.claude/settings.json`, `.claude/settings.local.json`, `managed-settings.json`,
      `managed-settings.d/*`), and a Bash command that writes one (redirection, tee, sed -i, cp, mv, rm, ln, dd, truncate, an interpreter's write).
      Reading stays allowed.
  G4  Write or Edit of a script file (.py .sh .bash .zsh .js .ts .mjs) that ADDS the bypass words or a literal `--setting-sources` value without
      `user`: Edit, more of them in new_string than in old_string; Write over an existing file, more than the file holds now; a new file, any.
      This is the form that happened in wave 6 (the flag sat in a script run with `python3`, which no Bash text rule sees). Edits that leave the
      count alone (handback.py, this file) pass.
Reading of the command (w08-c10): a command substitution (`$( )`, backticks) is cut out of the command and its inside is read as commands of their own, as before, AND the command is read once more with each substitution
replaced by one word, so `claude -p "$(cat f)" <flag>` is seen with its flag on the `claude` command; the options of a wrapper that take a value (`env -u VAR`, `timeout -s SIG`, `ionice -c N`, `exec -a NAME`, ...) are
skipped with their value, and the string of `env -S` is read as a command. Every reading that was made before is still made, so nothing that was denied is allowed by this.
This is a guard for the direct and the casual cases. A script file that holds the flag, a variable built from pieces, base64, a symlink: not seen.
Only a managed setting (`disableBypassPermissionsMode`) holds against those; a plugin cannot set it.

Optional: with MURMURATION_GUARD_LOG set to a file, each run appends one JSON line (the test of w06-c7 counts spawns with it).
"""
import json
import os
import re
import shlex
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MSG = ("permission_guard (%s): %s. Skipping or loosening Claude Code's permission layer is the user's decision, not the lab's. "
       "Do not run it in another form or through a script; tell the user what you wanted and wait for their yes in their own message.")

BYPASS = re.compile(r"(?i)bypassPermissions|(?:--permission-mode|defaultMode)\W+bypass|dangerously-skip|--(?:allow-)?dangerously|skipDangerousModePermissionPrompt")
INERT = {"grep", "egrep", "fgrep", "rg", "jq", "wc", "head", "tail", "cat", "ls", "diff", "sort", "uniq", "cut", "tr", "nl", "less"}
GIT_INERT = {"log", "grep", "show", "diff", "status", "blame", "shortlog"}
WRAP = {"env", "command", "nohup", "exec", "time", "sudo", "nice", "ionice", "stdbuf", "xargs", "timeout", "gtimeout", "setsid", "caffeinate"}
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}", "fi", "done"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
INTERP = re.compile(r"\b(?:python[\d.]*|node|ruby|perl|php|osascript|deno|bun)\b")
WRITEISH = re.compile(r"""\bwrite|writeFile|\.dump\(|,\s*['"][wax]\+?b?['"]|mode\s*=\s*['"][wax]|\bopen\s*\([^)]*['"][wax]""")
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def _split(cmd, quotes):
    """One pass of the splitter; returns (segments, quote state at the end). With quotes=False a quote character is an ordinary character."""
    segs, cur, i, q = [], [], 0, None
    while i < len(cmd):
        c = cmd[i]
        if q == "'":
            cur.append(c)
            q = None if c == "'" else q
        elif c == "\\" and i + 1 < len(cmd):
            cur.append(c + cmd[i + 1])
            i += 1
        elif q == '"':
            if c == '"':
                q = None
                cur.append(c)
            elif c == "`" or cmd.startswith("$(", i):
                segs.append("".join(cur)); cur = []
                if c != "`":
                    i += 1
            else:
                cur.append(c)
        elif quotes and c in "'\"":
            q = c
            cur.append(c)
        elif c in "\n;|()`" or (c == "&" and not (cmd[i - 1:i] == ">" or cmd[i + 1:i + 2] == ">")):
            segs.append("".join(cur)); cur = []
        else:
            cur.append(c)
        i += 1
    segs.append("".join(cur))
    return [x.strip() for x in segs if x.strip()], q


def split_segments(cmd):
    """Split a shell command into simple-command strings: on newline ; & | ( ) backticks and $( ) (not on >& or &>); quotes respected (substitutions inside double
    quotes too). If a quote is left open (an apostrophe in prose, a stray quote), the text cannot be split safely: split again ignoring quotes, so that no
    later segment hides inside the unclosed one."""
    segs, q = _split(cmd, True)
    if q is not None:
        segs, _ = _split(cmd, False)
    return segs


def words(seg):
    try:
        return shlex.split(seg, posix=True)
    except ValueError:
        return seg.split()


# the options of each wrapper that take a value (short letters; long names, which getopt accepts as unique prefixes): the value is not the program
VALUE_OPTS = {
    "env": ("uCSPa", ("--unset", "--chdir", "--split-string", "--argv0")),
    "exec": ("a", ()),
    "timeout": ("ks", ("--kill-after", "--signal")),
    "gtimeout": ("ks", ("--kill-after", "--signal")),
    "nice": ("n", ("--adjustment",)),
    "ionice": ("cnpPu", ("--class", "--classdata", "--pid", "--pgid", "--uid")),
    "stdbuf": ("ioe", ("--input", "--output", "--error")),
    "xargs": ("nILPsdaERS", ("--max-args", "--max-lines", "--max-procs", "--max-chars", "--delimiter", "--arg-file", "--eof")),
    "caffeinate": ("tw", ()),
    "sudo": ("ugCDhprtTUR", ("--user", "--group", "--close-from", "--chdir", "--host", "--prompt", "--role", "--type", "--command-timeout", "--other-user", "--chroot")),
    "time": ("fo", ("--format", "--output")),
}


def _value_option(w, t):
    """True when the option word t of wrapper w takes its value from the next word (not joined `-uX`, not `--opt=X`)."""
    shorts, longs = VALUE_OPTS.get(w, ("", ()))
    if t.startswith("--"):
        return "=" not in t and len(t) > 2 and any(name.startswith(t) for name in longs)
    for k, ch in enumerate(t[1:], 1):
        if ch in shorts:
            return k == len(t) - 1
    return False


def _env_string(t, toks, i):
    """The string of `env -S` / `--split-string` in option word t (toks[i] is the word after t), or None."""
    if t.startswith("--"):
        name, eq, val = t.partition("=")
        if len(name) > 2 and "--split-string".startswith(name):
            return val if eq else (toks[i] if i < len(toks) else None)
        return None
    for k, ch in enumerate(t[1:], 1):
        if ch in "uCSPa":
            if ch != "S":
                return None
            return t[k + 1:] if k < len(t) - 1 else (toks[i] if i < len(toks) else None)
    return None


def _scan(toks):
    """(index of the program word, assignments before it, the strings of `env -S`, whether a wrapper option's value was skipped) after env assignments, wrappers (env, timeout N, nohup, ...) and shell keywords."""
    i, assigns, strings, skipped = 0, [], [], False
    while i < len(toks):
        t = toks[i]
        if t in KEYWORDS:
            i += 1
        elif ASSIGN.match(t):
            assigns.append(t); i += 1
        elif os.path.basename(t) in WRAP:
            w = os.path.basename(t); i += 1
            while i < len(toks) and (toks[i].startswith("-") or ASSIGN.match(toks[i]) or (w in ("timeout", "gtimeout", "nice") and re.fullmatch(r"[\d.]+[smhd]?", toks[i]))):
                o = toks[i]
                if ASSIGN.match(o):
                    assigns.append(o)
                i += 1
                if w == "env" and o.startswith("-"):
                    st = _env_string(o, toks, i)
                    if st is not None:
                        strings.append(st)
                if o.startswith("-") and _value_option(w, o):
                    if i < len(toks) and os.path.basename(toks[i]) != "claude":     # a value is never taken for the program, but `claude` is never taken for a value
                        i += 1
                        skipped = True
        else:
            return i, assigns, strings, skipped
    return len(toks), assigns, strings, skipped


def program(toks):
    """(index of the program word, assignments before it) after env assignments, wrappers (env, timeout N, nohup, ...), their options (and the values of those) and shell keywords."""
    k, assigns, _, _ = _scan(toks)
    return k, assigns


def flag_value(toks, flag):
    """Values given to --flag (separate or =), as a list of strings; a flag at the very end gives ''."""
    out = []
    for k, t in enumerate(toks):
        if t == flag:
            out.append(toks[k + 1] if k + 1 < len(toks) else "")
        elif t.startswith(flag + "="):
            out.append(t[len(flag) + 1:])
    return out


class TooComplex(Exception):
    """More characters scanned while masking command substitutions than WORK allows (a text scanned once costs its length; each nesting level scans its inside again): the command is denied rather than half checked."""


WORK = 10000000


def _heredoc(s, i):
    """At s[i:i+2] == '<<' (not '<<<'): (delimiter, tabs stripped, index after the delimiter word), or None."""
    n, j, strip = len(s), i + 2, False
    if j < n and s[j] == "-":
        strip, j = True, j + 1
    while j < n and s[j] in " \t":
        j += 1
    if j >= n:
        return None
    if s[j] in "'\"":
        k = s.find(s[j], j + 1)
        return None if k < 0 else (s[j + 1:k], strip, k + 1)
    if s[j] == "\\":
        j += 1
    k = j
    while k < n and s[k] not in " \t\n;&|<>()`":
        k += 1
    return (s[j:k], strip, k) if k > j else None


def _skip_bodies(s, i, pend):
    """s[i] is a newline that ends a line with heredoc operators: the index just after the last delimiter line (or the end of s)."""
    n, pos = len(s), i + 1
    for delim, strip in pend:
        while True:
            e = s.find("\n", pos)
            e = n if e < 0 else e
            line = s[pos:e].lstrip("\t") if strip else s[pos:e]
            pos = min(e + 1, n)
            if line == delim or e == n:
                break
    return pos


def _spans(s, quotes, work):
    """(spans, open_quote): one pass over s with a stack of what is open (quotes, backticks, parentheses). A span (start, end, inside_start, inside_end) is a matched `$( )`, `<( )`, `>( )` or backtick pair, at any depth outside backticks.
    Inside a `$( )`, a heredoc body is skipped as data when the pass looks for the closing `)`: a body with an unmatched parenthesis or quote does not hide the `)`. With quotes=False a quote character is an ordinary character.
    open_quote: a quote was still open at the end."""
    work[0] += len(s)
    if work[0] > WORK:
        raise TooComplex()
    stack, spans, pend, nsub, i, n = [], [], [], 0, 0, len(s)
    while i < n:
        c = s[i]
        top = stack[-1][0] if stack else None
        if top == "S":
            if c == "'":
                stack.pop()
        elif c == "\\":
            i += 1
        elif top == "B":
            if c == "`":
                f = stack.pop()
                spans.append((f[1], i + 1, f[1] + 1, i))
        elif top == "D":
            if c == '"':
                stack.pop()
            elif s.startswith("$(", i):
                stack.append(("P", i, 1))
                nsub += 1
                i += 1
            elif c == "`":
                stack.append(("B", i, 0))
        elif quotes and c in "'\"":
            stack.append(("S" if c == "'" else "D", i, 0))
        elif c == "`":
            stack.append(("B", i, 0))
        elif nsub and c == "<" and s.startswith("<<", i) and not s.startswith("<<<", i) and _heredoc(s, i):
            d, strip, j = _heredoc(s, i)
            pend.append((d, strip))
            i = j - 1
        elif nsub and c == "\n" and pend:
            i = _skip_bodies(s, i, pend) - 1
            pend = []
        elif (c == "$" or c in "<>") and s.startswith("(", i + 1):
            stack.append(("P", i, 1))
            nsub += 1
            i += 1
        elif c == "(":
            stack.append(("P", i, 0))
        elif c == ")" and stack:
            f = stack.pop()
            if f[2]:
                nsub -= 1
                spans.append((f[1], i + 1, f[1] + 2, i))
        i += 1
    return spans, any(f[0] in "SD" for f in stack)


def _mask(s, work):
    """(s with every outermost matched substitution replaced by one word, the insides that were replaced). The word is `claude` when the inside names claude (`$(which claude) --flag`), else `SUBST`. Single quotes and backslashes are respected
    (as the plain splitter does, a quote left open makes the pass run again with quotes as ordinary characters); an unclosed substitution stays as it is."""
    spans, open_quote = _spans(s, True, work)
    if open_quote:
        spans, _ = _spans(s, False, work)
    spans.sort(key=lambda t: (t[0], -t[1]))
    out, inners, prev = [], [], 0
    for st, en, a, b in spans:
        if st < prev:
            continue
        inner = s[a:b]
        out.append(s[prev:st])
        out.append("claude" if NAMES_CLAUDE.search(inner) else "SUBST")
        inners.append(inner)
        prev = en
    out.append(s[prev:])
    return "".join(out), inners


def substitution_texts(cmd, work):
    """The texts to split in addition to cmd itself: cmd and the inside of each of its substitutions (nested ones too), each with its own substitutions replaced by one word. Empty when cmd has none."""
    if "$(" not in cmd and "`" not in cmd and "<(" not in cmd and ">(" not in cmd:
        return []
    texts, queue = [], [cmd]
    while queue:
        m, inners = _mask(queue.pop(0), work)
        texts.append(m)
        queue += inners
    return texts if len(texts) > 1 or texts[0] != cmd else []


def expand(cmd, depth=0, work=None):
    """Every simple command (list of words) of cmd, descending into `sh -c '...'`, `eval '...'` and `env -S '...'` strings (depth 3). The simple commands of the plain splitter come first, in order; then those of
    the command and of each substitution inside it with the substitutions replaced by one word (so that `claude -p "$(cat f)" --flag` is also seen as `claude -p "SUBST" --flag`). Raises TooComplex."""
    work = [0] if work is None else work
    out = []
    segs = split_segments(cmd)
    for text in substitution_texts(cmd, work):
        segs += split_segments(text)
    for seg in segs:
        toks = words(seg)
        out.append((seg, toks))
        k, _, strings, _ = _scan(toks)
        if depth < 3:
            for st in strings:
                out += expand(" ".join([st] + toks[k:]), depth + 1, work)
        if depth < 3 and k < len(toks):
            prog = os.path.basename(toks[k])
            if prog in SHELLS and "-c" in toks[k + 1:]:
                j = toks.index("-c", k + 1)
                if j + 1 < len(toks):
                    out += expand(toks[j + 1], depth + 1, work)
            elif prog == "eval":
                out += expand(" ".join(toks[k + 1:]), depth + 1, work)
    return out


def inert(toks):
    k, _, _, skipped = _scan(toks)
    if skipped or k >= len(toks):         # a wrapper option's value was skipped: the program may be one the old reading took for `inert`, so it counts as not inert
        return False
    prog = os.path.basename(toks[k])
    rest = toks[k + 1:]
    if prog in INERT:
        return not any(t == "--pre" or t.startswith("--pre=") for t in rest)
    if prog == "git":
        sub = [t for t in rest if not t.startswith("-")][:1]
        return bool(sub) and sub[0] in GIT_INERT and "-c" not in rest and not any(t.startswith("--exec") for t in rest)
    return False


def protected(path, cwd, unknown_dir=False):
    """True when path names a Claude Code settings file."""
    p = os.path.expanduser(path)
    if not os.path.isabs(p):
        if "/" not in p and unknown_dir and os.path.basename(p) in ("settings.json", "settings.local.json"):
            return True
        p = os.path.join(cwd or "", p)
    p = os.path.normpath(p)
    base, parent = os.path.basename(p), os.path.basename(os.path.dirname(p))
    if base.startswith("managed-settings") or parent == "managed-settings.d":
        return True
    return base in ("settings.json", "settings.local.json") and parent == ".claude"


NAMES_CLAUDE = re.compile(r"(?<![\w.\-])claude(?![\w.\-/])|claude_agent_sdk")


def g1(cmd, segs):
    """G1 (v3): the bypass words, only when the same command text (heredoc bodies included) also names `claude` (the CLI) or `claude_agent_sdk`."""
    if not NAMES_CLAUDE.search(cmd) and not any(NAMES_CLAUDE.search(sg) for sg, _ in segs):      # also the strings of `env -S<word>` and `sh -c`, where `-Sclaude` glues the word to the option
        return None
    bad = [s for s, toks in segs if BYPASS.search(s) or BYPASS.search(" ".join(toks))]
    hit = [s for s, toks in segs if (BYPASS.search(s) or BYPASS.search(" ".join(toks))) and not inert(toks)]
    if hit:
        m = BYPASS.search(hit[0]) or BYPASS.search(" ".join(words(hit[0])))
        return "G1", "the command carries `%s`" % (m.group(0) if m else "a bypass flag")
    return None


def g2(cmd, segs):
    for seg, toks in segs:
        k, assigns = program(toks)
        for t in assigns + toks:
            if t.startswith("CLAUDE_CONFIG_DIR="):
                return "G2", "the command sets CLAUDE_CONFIG_DIR, which leaves the user's settings and hooks behind"
        if toks[:1] in (["export"], ["declare"], ["typeset"]) and any(t.startswith("CLAUDE_CONFIG_DIR=") for t in toks):
            return "G2", "the command sets CLAUDE_CONFIG_DIR"
        if k >= len(toks) or os.path.basename(toks[k]) != "claude":
            continue
        args = toks[k + 1:]
        for v in flag_value(args, "--setting-sources"):
            if "user" not in [x.strip() for x in v.split(",")]:
                return "G2", "the child `claude` is started with `--setting-sources %s`, which leaves out the user's settings" % v
        for f in ("--bare", "--safe-mode"):
            if f in args:
                return "G2", "the child `claude` is started with `%s`, which skips the user's hooks" % f
        for v in flag_value(args, "--settings"):
            if "disableAllHooks" in v:
                return "G2", "the child `claude` is started with settings that disable all hooks"
    return None


def g3_bash(cmd, segs, cwd):
    unknown, cur = False, cwd
    for seg, toks in segs:
        k, _ = program(toks)
        prog = os.path.basename(toks[k]) if k < len(toks) else ""
        if prog in ("cd", "pushd") and k + 1 < len(toks):
            t = os.path.expanduser(toks[k + 1])
            if "$" in t or "`" in t or t == "-":
                unknown = True
            else:
                cur = os.path.normpath(t if os.path.isabs(t) else os.path.join(cur or "", t))
            continue
        targets = []
        for m in re.finditer(r"""(?:>>?|>\|)\s*(['"]?)([^\s;&|<>'"]+)\1""", seg):
            targets.append(m.group(2))
        args = toks[k + 1:] if k < len(toks) else []
        if prog == "tee":
            targets += [t for t in args if not t.startswith("-")]
        elif prog in ("sed", "perl", "awk", "gawk", "ruby") and any(t.startswith(("-i", "--in-place", "-pi", "-ni")) or t == "inplace" for t in args):
            targets += [t for t in args if not t.startswith("-")]
        elif prog == "cp":                # only the destination is written: the last argument, or the value of -t / --target-directory
            plain = [t for t in args if not t.startswith("-")]
            tdir = [args[j + 1] for j, t in enumerate(args[:-1]) if t in ("-t", "--target-directory")] + [t.split("=", 1)[1] for t in args if t.startswith("--target-directory=")]
            targets += tdir if tdir else plain[-1:]
        elif prog in ("mv", "install", "ln", "rsync", "rm", "truncate", "unlink", "shred", "chmod", "chown", "touch"):    # mv removes its source: every argument is a target
            targets += [t for t in args if not t.startswith("-")]
        elif prog == "dd":
            targets += [t[3:] for t in args if t.startswith("of=")]
        for t in targets:
            if protected(t, cur, unknown):
                return "G3", "the command writes `%s`, a Claude Code settings file" % t
    if INTERP.search(cmd) or any(os.path.basename(t) in ("python", "python3") for _, ts in segs for t in ts[:1]):
        names = re.findall(r"[^\s'\"=,()]*(?:managed-settings[^\s'\"),]*|settings(?:\.local)?\.json)", cmd)
        if names and WRITEISH.search(cmd) and any(protected(n, cur, True) or "/" in n and protected(n, cwd) for n in names):
            return "G3", "a script in the command writes a Claude Code settings file"
    return None


def g3_edit(inp, cwd):
    p = inp.get("file_path") or inp.get("path") or inp.get("notebook_path") or ""
    if p and protected(p, cwd):
        return "G3", "the edit targets `%s`, a Claude Code settings file" % p
    return None


SCRIPT_EXT = (".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".mjs", ".ipynb")
SRC = re.compile(r"""--setting-sources["'\s=,\[\]]*([A-Za-z,]*)""")


def _hits(text):
    """The bypass words and the `--setting-sources` values without `user` that a text carries, in order."""
    out = [m.group(0) for m in BYPASS.finditer(text)]
    out += ["--setting-sources " + v for v in SRC.findall(text) if v and "user" not in v.split(",")]
    return out


def g4_script(inp, cwd=""):
    """G4 (v2): Write or Edit of a script file that ADDS the bypass words or a literal `--setting-sources` value without `user`.
    Edit: more of them in `new_string` than in `old_string`. Write over an existing file: more than the file holds now. Write of a new file: any."""
    p = inp.get("file_path") or inp.get("path") or inp.get("notebook_path") or ""
    if not p.lower().endswith(SCRIPT_EXT):
        return None
    if "new_source" in inp:         # NotebookEdit: the replaced cell is not known to the hook, so any occurrence counts
        new, old = _hits(str(inp.get("new_source") or "")), []
    elif "content" in inp:
        new, old = _hits(str(inp.get("content") or "")), []
        try:
            with open(os.path.join(cwd or "", os.path.expanduser(p)), errors="replace") as fh:
                old = _hits(fh.read())
        except OSError:
            old = []
    else:
        edits = [inp] + [e for e in (inp.get("edits") or []) if isinstance(e, dict)]
        new = [h for e in edits for h in _hits(str(e.get("new_string") or ""))]
        old = [h for e in edits for h in _hits(str(e.get("old_string") or ""))]
    if len(new) > len(old):
        h = new[len(old)] if len(new) > len(old) else new[0]
        return "G4", "the edit adds `%s` to the script `%s`" % (h, os.path.basename(p))
    return None


def decide(event):
    """(group, why) when the event is to be denied, else None."""
    tool, inp, cwd = event.get("tool_name"), event.get("tool_input") or {}, event.get("cwd") or ""
    if tool == "Bash":
        cmd = inp.get("command") or ""
        try:
            segs = expand(cmd)
        except TooComplex:
            return "G?", "the command has too many command substitutions to be checked"
        return g1(cmd, segs) or g2(cmd, segs) or g3_bash(cmd, segs, cwd)
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        return g3_edit(inp, cwd) or g4_script(inp, cwd)
    return None


def run(raw, log=None):
    """The hook's answer for the raw stdin text: a dict (deny) or None. Never raises."""
    what = ""
    try:
        event = json.loads(raw)
        hit = decide(event)
        tool = event.get("tool_name")
        ti = event.get("tool_input") or {}
        what = str(ti.get("command") or ti.get("file_path") or "")[:120]
    except Exception as exc:        # fail closed
        hit, tool = ("G?", "the guard could not read the event (%s)" % type(exc).__name__), None
    if log:
        try:
            with open(log, "a") as fh:
                fh.write(json.dumps(dict(tool=tool, what=what, decision="deny" if hit else "allow", group=hit[0] if hit else None)) + "\n")
        except OSError:
            pass
    if not hit:
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": MSG % hit}}


def selftest():
    import tempfile
    T = tempfile.mkdtemp()
    ok = True
    lists = os.path.join(HERE, "..", "__reports__", "wave-06", "author-w06-5")

    def load(n):
        return json.loads(open(os.path.join(lists, "e3_%s.json" % n)).read().replace("{T}", T)) if os.path.exists(os.path.join(lists, "e3_%s.json" % n)) else []

    def ev(c):
        if c["tool"] == "Bash":
            return dict(tool_name="Bash", tool_input={"command": c["command"]}, cwd=T)
        return dict(tool_name=c["tool"], tool_input=c["input"], cwd=T)

    def check(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print("FAIL", name)
    for c in load("attacks"):
        check("attack " + c["id"], decide(ev(c)))
    for c in load("ordinary"):
        check("ordinary " + c["id"], not decide(ev(c)))
    holes = json.load(open(os.path.join(HERE, "guard_selftest_holes.json")))        # w08-c10: the forms that hid a flag after a substitution or behind an option of a wrapper, and controls
    for c in holes:
        check("hole-form %s (%s)" % (c["id"], "deny" if c["deny"] else "allow"), bool(decide(dict(tool_name="Bash", tool_input={"command": c["command"]}, cwd=T))) == c["deny"])
    ev_pass = [c["id"] for c in load("evasions") if decide(ev(c))]
    mention_denied = [c["id"] for c in load("mention") if decide(ev(c))]
    small = [
        ("Bash", {"command": "claude -p x --permission-mode auto"}, False),
        ("Bash", {"command": "claude -p x --permission-mode bypassPermissions"}, True),
        ("Bash", {"command": "grep -rn bypassPermissions docs"}, False),
        ("Bash", {"command": "grep bypassPermissions x | claude --dangerously-skip-permissions"}, True),
        ("Bash", {"command": "git commit -m 'bypassPermissions'"}, False),
        ("Bash", {"command": "python3 - <<'EOF'\nimport subprocess\nsubprocess.run(['claude','-p','hi','--dangerously-skip-permissions'])\nEOF"}, True),
        ("Bash", {"command": "bash <<'EOF'\nclaude -p hi --permission-mode bypassPermissions\nEOF"}, True),
        ("Bash", {"command": "cat <<'EOF'\nthe bypassPermissions mode is documented\nEOF"}, False),
        ("NotebookEdit", {"notebook_path": "/h/n.ipynb", "new_source": "mode = 'bypassPermissions'"}, True),
        ("NotebookEdit", {"notebook_path": "/h/n.ipynb", "new_source": "print(1)"}, False),
        ("Bash", {"command": "echo $CLAUDE_CONFIG_DIR"}, False),
        ("Bash", {"command": "grep -n it's f; claude -p hi --dangerously-skip-permissions"}, True),
        ("Bash", {"command": "echo '{}'>.claude/settings.json"}, True),
        ("Bash", {"command": "echo '{}'>>.claude/settings.local.json"}, True),
        ("Bash", {"command": "cp .claude/settings.local.json /tmp/bak"}, False),
        ("Bash", {"command": "cp /tmp/new.json .claude/settings.json"}, True),
        ("Bash", {"command": "cp -t .claude /tmp/settings.json"}, False),
        ("Bash", {"command": "cp -t /h/proj/.claude/settings.json /tmp/a"}, True),
        ("Bash", {"command": "mv /tmp/x .claude/settings.json"}, True),
        ("Bash", {"command": "mv .claude/settings.json /tmp/old"}, True),
        ("Bash", {"command": "mv .claude/settings.local.json .claude/settings.local.json.off"}, True),
        ("Bash", {"command": "mv /tmp/a /tmp/b"}, False),
        ("Bash", {"command": "rm .claude/settings.json"}, True),
        ("Bash", {"command": "ls 2>&1; echo ok"}, False),
        ("Bash", {"command": "CLAUDE_CONFIG_DIR=/x claude -p y"}, True),
        ("Bash", {"command": "claude -p y --setting-sources local,user"}, False),
        ("Bash", {"command": "git init --bare x"}, False),
        ("Bash", {"command": "jq . /h/.claude/settings.json 2>/dev/null"}, False),
        ("Bash", {"command": "echo x > /h/.claude/settings.json"}, True),
        ("Bash", {"command": "echo x > /h/out/settings.json"}, False),
        ("Bash", {"command": "cp a '/Library/Application Support/ClaudeCode/managed-settings.json'"}, True),
        ("Write", {"file_path": "/Library/Application Support/ClaudeCode/managed-settings.json", "content": ""}, True),
        ("Write", {"file_path": "/h/proj/.claude/settings.local.json", "content": ""}, True),
        ("Write", {"file_path": "/h/proj/.claude/agents/x.md", "content": ""}, False),
        ("Write", {"file_path": "/h/proj/settings.json", "content": ""}, False),
        ("Read", {"file_path": "/h/proj/.claude/settings.json"}, False),
    ]
    for tool, inp, want in small:
        check("small %s %s" % (tool, json.dumps(inp)[:60]), bool(decide(dict(tool_name=tool, tool_input=inp, cwd="/h/proj"))) == want)
    for raw in ("", "not json", "[]", json.dumps({"tool_name": "Bash", "tool_input": None})):   # malformed events never allow a bypass word silently
        r = run(raw)
        check("malformed %r" % raw[:20], r is None or r["hookSpecificOutput"]["permissionDecision"] == "deny")
    check("empty event is a deny (fail closed)", run("not json") is not None)
    print("selftest %s: attacks %d denied, ordinary %d allowed; not-gated: evasions caught %s, mention-only denied %s" % (
        "ok" if ok else "FAILED", len(load("attacks")), len(load("ordinary")), ev_pass, mention_denied))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    ans = run(sys.stdin.read(), os.environ.get("MURMURATION_GUARD_LOG"))
    if ans:
        sys.stdout.write(json.dumps(ans))


if __name__ == "__main__":
    main()
