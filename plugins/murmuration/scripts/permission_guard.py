#!/usr/bin/env python3
r"""Deny the direct forms of skipping or loosening Claude Code's permission layer, from a PreToolUse hook.

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
Redirections (leaf posix_redirects): the targets of a command's redirections are read twice, and every target of either reading is tested, the old reading first. The old reading is a pattern over the text (`>`, `>>`, `>|` and a target without a space or quote); it also
reads a `>` inside quotes, which only makes the guard stricter, and it stays. The new one is `redirect_targets`: it finds each output operator outside quotes (`>`, `>>`, `>|`, `&>`, `&>>`, `N>`, `N>>`, `N>|`, `>&` followed by a word that is not a number or `-`, `<>`) and takes the next
shell word with its quotes removed as bash removes them (`'..'`, `".."`, `$'..'` with its escapes, `$".."`, a backslash), so that a quoted target with a space, a backslash-escaped space, a target in pieces and an ANSI-C name are seen. A word that still holds a `$` or a backtick
is an unknown target and goes to `protected` as written, as before. The splitter cuts at the `|` of `>|` as it always did; when a segment ends in `>` the command is also split with `>|` whole (`expand(clobber=True)`) and that reading is checked for G3 as well.
Gaps after the redirections (leaf posix_gaps), each reading added after the older ones, so a command denied before is denied for the same reason: a second pass over the commands that also reads each word with ANSI-C quoting removed (`bash -c $'..'`, `eval $'..'`: shlex does not
know `$'..'`) and descends into shell strings to depth 8 (a deeper one in a command that names a settings file is denied: it cannot be read); a shell that reads its script from its input (`.. | sh`, `bash -s`, a here-doc, here-string or `<` to a shell with no `-c` and no script file) in a command that names a settings file
is denied (the script cannot be read in general); a redirect target or writer argument that the guard cannot expand (it holds `$` or a backtick, read as the whole word with nested quotes and substitutions: `"${F:-"a b"}"`, `$(echo ..)`) is denied when its text names a settings file, or when the command assigns a value naming
one with its folder (`F=.claude/settings.json`; also `export`, `declare`, `local`, `readonly`, `for F in ..`; a name alone, `B=settings.json`, is a piece); a target that holds `*`, `?` or `[` is denied when, read as a glob, it could match a settings file (`.claude/settings.j*`, `.cl*/settings.json`, `*.json` in a `.claude` folder; a glob that starts with `*` counts only when the rest could begin at `managed-settings`, `-settings` or `settings`, so `*.log` and `build/*.o` are allowed). A name built from pieces, base64 or a file's contents stays accepted.
A command that holds a NUL (a shell cannot receive one) is denied, and so is a Bash command, or a Write/Edit/MultiEdit/NotebookEdit input, longer than MAX_CHARS characters ("too long to be checked", like TooComplex): the guard is a process that Claude Code stops after a timeout, and what a timeout does depends on its version.
Flavours: every path and program-name decision takes a flavour, "posix" or "nt", chosen by the OS this runs on (os.name) and passed explicitly by the selftest, which runs both on any host
(fixtures/guard_lists/windows_paths.json holds the expected decision of each case under each; the Rust port reads the same file). posix is the reading of before: `/` separates, a backslash is a filename
character, names are case-sensitive. nt reads a path as Windows resolves it, written out in `_nt_*` (not ntpath): `/` and `\` both separate; the prefixes `\\?\`, `\\.\`, `\??\` and `UNC\` are cut off; `C:x` is drive-relative (the
directory of that drive is not known, so any settings-file name there is denied); an alternate data stream (`name:stream`) is cut off a component; trailing dots and spaces of a component are cut off; names compare
case-folded (ASCII, plus U+17F, U+130, U+131 and U+212A, which Windows does not fold: an over-deny); a program name is folded and loses one of `.exe .cmd .bat .com .ps1` (but only `grep.exe`, not `grep.cmd`, is the inert grep); a component made only of dots and spaces
(`...`) is read both as vanishing and as a name that a later `..` removes, and either reading reaching a settings file denies; `claude_config_dir=` matches in any case. On nt the Bash text is read a second time with
each backslash a slash (the shell reads `C:\a\claude.exe` as `C:aclaude.exe` when it is not quoted). nt fails closed: where it cannot tell, it denies.
This is a guard for the direct and the casual cases. A script file that holds the flag, a variable built from pieces, base64, a symlink: not seen. On Windows also not seen: 8.3 short names (`CLAUDE~1`, `SETTIN~1.JSON`),
junctions and symlinks to a settings directory, the builtins of cmd and PowerShell that write a file without a redirection (`copy`, `move`, `del`, `Set-Content`, `Out-File`, ...), a script whose extension is `.bat .cmd .ps1`.
Only a managed setting (`disableBypassPermissionsMode`) holds against those; a plugin cannot set it.

Optional: with MURMURATION_GUARD_LOG set to a file, each run appends one JSON line (the test of w06-c7 counts spawns with it).
"""
import functools
import json
import os
import posixpath
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
INTERP_NT = re.compile(r"(?i)\b(?:python[\d.]*|node|ruby|perl|php|osascript|deno|bun)\b")
NAMES_POSIX = re.compile(r"[^\s'\"=,()]*(?:managed-settings[^\s'\"),]*|settings(?:\.local)?\.json)")
NAMES_NT = re.compile(r"(?i)[^\s'\"=,()]*(?:managed-settings[^\s'\"),]*|settings(?:\.local)?\.json)")
WRITEISH = re.compile(r"""\bwrite|writeFile|\.dump\(|,\s*['"][wax]\+?b?['"]|mode\s*=\s*['"][wax]|\bopen\s*\([^)]*['"][wax]""")
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


# ---------------------------------------------------------------------------------------------------------------------------------------------------------
# Paths and program names, by flavour. "posix" is today's reading (posixpath: `/` separates, a backslash is a filename character, names are case-sensitive).
# "nt" is the reading of Windows, written out here and not taken from ntpath (whose isabs and join changed between Python versions), so that the Rust port can follow it one for one.
# The runtime flavour is chosen by the OS; both flavours run on any host, which is how the selftest and the Rust unit tests check them.
HOST = "nt" if os.name == "nt" else "posix"
NT_EXE = (".exe", ".cmd", ".bat", ".com", ".ps1")
# the case-folding of names: the ASCII letters, and the four characters outside ASCII that fold into it (dotted and dotless I, long S, Kelvin sign); a name is only ever compared with an ASCII literal
_NT_FOLD = {**{c: c + 32 for c in range(0x41, 0x5B)}, 0x17F: "s", 0x130: "i", 0x131: "i", 0x212A: "k"}
SETTINGS_NAMES = ("settings.json", "settings.local.json")


def nt_fold(s):
    return s.translate(_NT_FOLD)


def _is_drive(s):
    return len(s) >= 2 and s[1] == ":" and s[0].isascii() and s[0].isalpha()


def _nt_root(p):
    """(drive, rooted, rest, ext): the drive (`C:` or ''), whether the path starts at a root (`C:\\`, `\\`, a UNC `\\\\server`, or an extended prefix), the text after the drive with `/` read as `\\`, and whether an extended prefix
    (`\\\\?\\`, `\\\\.\\`, `\\??\\`, and `UNC\\` after it) was cut off. `C:x` is drive-relative: the drive and no root."""
    s = p.replace("/", "\\")
    ext = False
    for pre in ("\\\\?\\", "\\\\.\\", "\\??\\"):
        if s.startswith(pre):
            s, ext = s[len(pre):], True
            break
    if ext and nt_fold(s[:4]) == "unc\\":
        s = s[4:]
    drive = ""
    if _is_drive(s):
        drive, s = s[:2], s[2:]
    return drive, ext or s.startswith("\\"), s, ext


def _nt_walk(stack, rooted, rest, keep=False):
    """Fold the components of `rest` onto stack as Windows resolves them: an alternate data stream (`:name`) is cut off a component, `.` and empty components vanish, `..` removes the last component (and stays when
    there is none and the path is not rooted), and trailing dots and spaces are cut off (so `settings.json.` and `settings.json ` name what Win32 would open). A name that is only dots and spaces (`...`, three spaces)
    has two readings, because how Win32 treats it was not run: it vanishes (keep=False), or it stays as an opaque name that a later `..` removes (keep=True). The decisions test both."""
    for comp in rest.split("\\"):
        comp = comp.split(":", 1)[0]
        if comp == ".":
            continue
        if comp == "..":
            if stack and stack[-1] != "..":
                stack.pop()
            elif not rooted:
                stack.append("..")
            continue
        name = comp.rstrip(" .")
        if name:
            stack.append(name)
        elif comp and keep:
            stack.append(comp)
    return stack


def _nt_resolve(cwd, p, keep=False):
    """(drive, rooted, components) of the path p seen from the working directory cwd, in the reading `keep` of a name made of dots and spaces (see _nt_walk)."""
    drive, rooted, rest, ext = _nt_root(p)
    if rooted:
        return drive, True, _nt_walk([], True, rest, keep)
    if not isinstance(cwd, str):
        raise TypeError("cwd")
    cd, crooted, crest, _ = _nt_root(cwd)
    return cd, crooted, _nt_walk(_nt_walk([], crooted, crest, keep), crooted, rest, keep)


def _nt_str(drive, rooted, comps):
    return drive + ("\\" if rooted else "") + "\\".join(comps)


def _nt_join(a, p):
    """`os.path.join(a, p)` as Windows reads it, as text (used to open a file; decisions use _nt_resolve)."""
    drive, rooted, rest, ext = _nt_root(p)
    if rooted and (drive or ext):
        return p
    if not isinstance(a, str):
        raise TypeError("cwd")
    if rooted:
        return _nt_root(a)[0] + p
    if drive:
        p = rest
    if not a:
        return p
    return a + p if a[-1] in "\\/" else a + "\\" + p


def _nt_expanduser(p):
    """`~` and `~\\...` (or `~/...`) to the home directory (USERPROFILE, then HOME; neither set: left alone)."""
    if not p.startswith("~") or (len(p) > 1 and p[1] not in "\\/"):
        return p
    home = os.environ.get("USERPROFILE") or os.environ.get("HOME")
    if not home:
        return p
    return home.rstrip("\\/") + p[1:]


def expanduser(p, fl=HOST):
    return _nt_expanduser(p) if fl == "nt" else posixpath.expanduser(p)


def prog_name(t, fl=HOST, exts=NT_EXE):
    """The name of the program word t: its basename. On nt the last component after `\\` or `/` (no drive, no `:stream`, no trailing dots or spaces), case-folded, without one of `exts` (default `.exe .cmd .bat .com .ps1`)."""
    if fl != "nt":
        return posixpath.basename(t)
    name = t.replace("/", "\\").rsplit("\\", 1)[-1]
    if _is_drive(name):
        name = name[2:]
    name = nt_fold(name.split(":", 1)[0].rstrip(" ."))
    for ext in exts:
        if name.endswith(ext) and len(name) > len(ext):
            return name[:-len(ext)]
    return name


def display_name(p, fl=HOST):
    """The basename of p as a message shows it (nt: after the last `\\` or `/`, without a drive)."""
    if fl != "nt":
        return posixpath.basename(p)
    name = p.replace("/", "\\").rsplit("\\", 1)[-1]
    return name[2:] if "\\" not in p.replace("/", "\\") and _is_drive(name) else name


def _split(cmd, quotes, clobber=False):
    """One pass of the splitter; returns (segments, quote state at the end). With quotes=False a quote character is an ordinary character. With clobber=True the `|` of a `>|` is not a cut (the reading of `>|` as one operator)."""
    segs, cur, i, q, gt = [], [], 0, None, False
    while i < len(cmd):
        c = cmd[i]
        after_gt, gt = gt, False                 # the previous character was a plain `>` (not escaped, not quoted)
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
        elif clobber and c == "|" and after_gt:
            cur.append(c)
        elif c in "\n;|()`" or (c == "&" and not (cmd[i - 1:i] == ">" or cmd[i + 1:i + 2] == ">")):
            segs.append("".join(cur)); cur = []
        else:
            cur.append(c)
            gt = c == ">"
        i += 1
    segs.append("".join(cur))
    return [x.strip() for x in segs if x.strip()], q


def split_segments(cmd, clobber=False):
    """Split a shell command into simple-command strings: on newline ; & | ( ) backticks and $( ) (not on >& or &>); quotes respected (substitutions inside double
    quotes too). If a quote is left open (an apostrophe in prose, a stray quote), the text cannot be split safely: split again ignoring quotes, so that no
    later segment hides inside the unclosed one. The `|` of `>|` cuts, as it always did; with clobber=True it does not (see expand)."""
    segs, q = _split(cmd, True, clobber)
    if q is not None:
        segs, _ = _split(cmd, False, clobber)
    return segs


@functools.lru_cache(maxsize=32)
def _words(seg):
    try:
        return tuple(shlex.split(seg, posix=True))
    except ValueError:
        return tuple(seg.split())


def words(seg):
    """The words of seg as shlex reads them (a plain split when a quote is left open). Cached: the readings of nt and of the second pass split the same text again, and shlex costs most of a long command's time."""
    return list(_words(seg))


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


def _scan(toks, fl=HOST):
    """(index of the program word, assignments before it, the strings of `env -S`, whether a wrapper option's value was skipped) after env assignments, wrappers (env, timeout N, nohup, ...) and shell keywords."""
    i, assigns, strings, skipped = 0, [], [], False
    while i < len(toks):
        t = toks[i]
        if t in KEYWORDS:
            i += 1
        elif ASSIGN.match(t):
            assigns.append(t); i += 1
        elif prog_name(t, fl) in WRAP:
            w = prog_name(t, fl); i += 1
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
                    if i < len(toks) and prog_name(toks[i], fl) != "claude":     # a value is never taken for the program, but `claude` is never taken for a value
                        i += 1
                        skipped = True
        else:
            return i, assigns, strings, skipped
    return len(toks), assigns, strings, skipped


def program(toks, fl=HOST):
    """(index of the program word, assignments before it) after env assignments, wrappers (env, timeout N, nohup, ...), their options (and the values of those) and shell keywords."""
    k, assigns, _, _ = _scan(toks, fl)
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


_SQUASH = re.compile(r"[\s;&|<>()'\"`\\$*?\[]")


def _mask(s, work, fl=HOST, keep=False):
    """(s with every outermost matched substitution replaced by one word, the insides that were replaced). The word is `claude` when the inside names claude (`$(which claude) --flag`), else `SUBST`. Single quotes and backslashes are respected
    (as the plain splitter does, a quote left open makes the pass run again with quotes as ordinary characters); an unclosed substitution stays as it is. keep=True (the second pass, leaf posix_gaps): the word else is `SUBST_` and the inside with blanks, operators, quotes and glob
    characters turned to `,`, so that a target `$(echo .claude/settings.json)` still shows the name; `claude` only when the inside does not name a settings file as well."""
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
        if keep:
            out.append("claude" if _names_claude(fl).search(inner) and not _names_span(inner, fl) else "SUBST_" + _SQUASH.sub(",", inner))
        else:
            out.append("claude" if _names_claude(fl).search(inner) else "SUBST")
        inners.append(inner)
        prev = en
    out.append(s[prev:])
    return "".join(out), inners


def substitution_texts(cmd, work, fl=HOST, keep=False):
    """The texts to split in addition to cmd itself: cmd and the inside of each of its substitutions (nested ones too), each with its own substitutions replaced by one word. Empty when cmd has none."""
    if "$(" not in cmd and "`" not in cmd and "<(" not in cmd and ">(" not in cmd:
        return []
    texts, queue = [], [cmd]
    while queue:
        m, inners = _mask(queue.pop(0), work, fl, keep)
        texts.append(m)
        queue += inners
    return texts if len(texts) > 1 or texts[0] != cmd else []


def _shell_script(toks, i):
    """Index of the word a shell reads as the string of `-c` in toks[i:] (its arguments), or None. Options come first: a word of `-` and letters with a `c` among them sets -c (`-lc`, `-ec`, `-c`); a letter `o` or `O` in such a word, and `--rcfile`, `--init-file`, take the next word as their value;
    `--` or `-` ends the options; any other word is the first non-option, which is the string when -c was set."""
    c, pend = False, 0
    while i < len(toks):
        t = toks[i]
        if pend:
            pend -= 1
        elif t in ("--", "-"):
            return i + 1 if c and i + 1 < len(toks) else None
        elif len(t) > 1 and t[0] in "-+" and t[1:].isalpha() and t[1:].isascii():
            pend = t.count("o") + t.count("O")
            c = c or (t[0] == "-" and "c" in t)
        elif t in ("--rcfile", "--init-file"):
            pend = 1
        elif len(t) > 1 and t[0] in "-+":                                     # another option
            pass
        else:
            return i if c else None
        i += 1
    return None


def expand(cmd, depth=0, work=None, fl=HOST, clobber=False, ansi=False, limit=3, deep=None):
    """Every simple command (list of words) of cmd, descending into `sh -c '...'`, `eval '...'` and `env -S '...'` strings (depth 3). The simple commands of the plain splitter come first, in order; then those of
    the command and of each substitution inside it with the substitutions replaced by one word (so that `claude -p "$(cat f)" --flag` is also seen as `claude -p "SUBST" --flag`). clobber=True is the reading in which `>|` is
    one operator (see split_segments); decide makes it in addition to the plain one, never instead of it. ansi=True also reads a command whose text holds `$'` or `$"` with its words as bash removes the quotes (`_ansi_words`: the string of `bash -c $'..'`),
    and `limit` is the depth the strings are followed to; when a string lies deeper, one item is added to the list `deep`. Raises TooComplex."""
    work = [0] if work is None else work
    out = []
    segs = split_segments(cmd, clobber)
    for text in substitution_texts(cmd, work, fl, ansi):
        segs += split_segments(text, clobber)
    for seg in segs:
        toks = words(seg)
        variants = [toks]
        if ansi and ("$'" in seg or '$"' in seg):
            more = _ansi_words(seg)
            if more != toks:
                variants.append(more)
        for toks in variants:
            out.append((seg, toks))
            k, _, strings, _ = _scan(toks, fl)
            subs = [" ".join([st] + toks[k:]) for st in strings]
            if k < len(toks):
                prog = prog_name(toks[k], fl)
                if prog in SHELLS:
                    js = [toks.index("-c", k + 1) + 1] if "-c" in toks[k + 1:] else []      # the word after the first `-c`, as before
                    j = _shell_script(toks, k + 1)                                          # and the string of `-c` as the shell reads its options (`-lc`, `-c -x`, ...)
                    if j is not None and j not in js:
                        js.append(j)
                    subs += [toks[j] for j in js if j < len(toks)]
                elif prog == "eval":
                    subs.append(" ".join(toks[k + 1:]))
            if depth < limit:
                for st in subs:
                    out += expand(st, depth + 1, work, fl, clobber, ansi, limit, deep)
            elif subs and deep is not None:
                deep.append(depth)
    return out


def inert(toks, fl=HOST):
    k, _, _, skipped = _scan(toks, fl)
    if skipped or k >= len(toks):         # a wrapper option's value was skipped: the program may be one the old reading took for `inert`, so it counts as not inert
        return False
    prog = prog_name(toks[k], fl, (".exe",))     # only `grep.exe` is the grep; a `grep.cmd` or `ls.bat` can run anything
    rest = toks[k + 1:]
    if prog in INERT:
        return not any(t == "--pre" or t.startswith("--pre=") for t in rest)
    if prog == "git":
        sub = [t for t in rest if not t.startswith("-")][:1]
        return bool(sub) and sub[0] in GIT_INERT and "-c" not in rest and not any(t.startswith("--exec") for t in rest)
    return False


def _nt_test(comps):
    """The settings-file test on the resolved components of a Windows path, names case-folded."""
    base = nt_fold(comps[-1]) if comps else ""
    parent = nt_fold(comps[-2]) if len(comps) > 1 else ""
    if base.startswith("managed-settings") or parent == "managed-settings.d":
        return True
    return base in SETTINGS_NAMES and parent == ".claude"


def _nt_protected(path, cwd, unknown_dir, keep=False):
    if not isinstance(path, str):
        raise TypeError("path")
    p = _nt_expanduser(path)
    drive, rooted, rest, _ = _nt_root(p)
    if not rooted:
        if drive:                       # `C:x`: the working directory of that drive is not known
            unknown_dir = True
        if unknown_dir and "\\" not in rest:
            comps = _nt_walk([], False, rest, keep)
            if comps and nt_fold(comps[-1]) in SETTINGS_NAMES:
                return True
    return _nt_test(_nt_resolve(cwd or "", p, keep)[2])


def protected(path, cwd, unknown_dir=False, fl=HOST, keep=False):
    """True when path names a Claude Code settings file (`keep`: the reading of an nt name made of dots and spaces that keeps it, see _nt_walk)."""
    if fl == "nt":
        return _nt_protected(path, cwd, unknown_dir, keep)
    p = posixpath.expanduser(path)
    if not posixpath.isabs(p):
        if "/" not in p and unknown_dir and posixpath.basename(p) in ("settings.json", "settings.local.json"):
            return True
        p = posixpath.join(cwd or "", p)
    p = posixpath.normpath(p)
    base, parent = posixpath.basename(p), posixpath.basename(posixpath.dirname(p))
    if base.startswith("managed-settings") or parent == "managed-settings.d":
        return True
    return base in ("settings.json", "settings.local.json") and parent == ".claude"


NAMES_CLAUDE = re.compile(r"(?<![\w.\-])claude(?![\w.\-/])|claude_agent_sdk")
# nt: `CLAUDE`, `claude.exe`, `C:\...\claude.cmd`; a backslash after the name, as a slash, makes it a folder
NAMES_CLAUDE_NT = re.compile(r"(?i:(?<![\w.\-])claude(?:\.(?:exe|cmd|bat|com|ps1))?(?![\w.\-/\\]))|claude_agent_sdk")


def _names_claude(fl):
    return NAMES_CLAUDE_NT if fl == "nt" else NAMES_CLAUDE


def g1(cmd, segs, fl=HOST):
    """G1 (v3): the bypass words, only when the same command text (heredoc bodies included) also names `claude` (the CLI) or `claude_agent_sdk`."""
    names = _names_claude(fl)
    if not names.search(cmd) and not any(names.search(sg) for sg, _ in segs):      # also the strings of `env -S<word>` and `sh -c`, where `-Sclaude` glues the word to the option
        return None
    bad = [s for s, toks in segs if BYPASS.search(s) or BYPASS.search(" ".join(toks))]
    hit = [s for s, toks in segs if (BYPASS.search(s) or BYPASS.search(" ".join(toks))) and not inert(toks, fl)]
    if hit:
        m = BYPASS.search(hit[0]) or BYPASS.search(" ".join(words(hit[0])))
        return "G1", "the command carries `%s`" % (m.group(0) if m else "a bypass flag")
    return None


def _config_dir(t, fl):
    """t is a `CLAUDE_CONFIG_DIR=` assignment (nt: environment names are case-insensitive, so `claude_config_dir=` too)."""
    return (nt_fold(t[:18]) == "claude_config_dir=") if fl == "nt" else t.startswith("CLAUDE_CONFIG_DIR=")


def g2(cmd, segs, fl=HOST):
    for seg, toks in segs:
        k, assigns = program(toks, fl)
        for t in assigns + toks:
            if _config_dir(t, fl):
                return "G2", "the command sets CLAUDE_CONFIG_DIR, which leaves the user's settings and hooks behind"
        if toks[:1] in (["export"], ["declare"], ["typeset"]) and any(_config_dir(t, fl) for t in toks):
            return "G2", "the command sets CLAUDE_CONFIG_DIR"
        if k >= len(toks) or prog_name(toks[k], fl) != "claude":
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


def slashed(segs):
    """The simple commands read with every backslash a slash. A Windows path typed without quotes loses its backslashes when the shell reads the word (`C:\\a\\claude.exe` is `C:aclaude.exe`); on nt the commands are read a second time like this, so that the program or target is also seen as the path it was meant to be."""
    return [(t, words(t)) for t in (sg.replace("\\", "/") for sg, _ in segs)]


_ANSI_ESC = {"a": "\a", "b": "\b", "e": "\x1b", "E": "\x1b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v", "\\": "\\", "'": "'", '"': '"', "?": "?"}
_OCT, _HEX, _DIG = "01234567", "0123456789abcdefABCDEF", "0123456789"
_REDIR_SKIP = re.compile(r"""[\\'"$<>]""")


def _ansi_c(s, i):
    """s[i] is the first character after `$'`: (the text the shell makes of the string, the index after its closing quote, whether the quote was closed). Escapes as bash reads them (`\\n`, `\\xHH`, `\\NNN`, `\\uHHHH`, `\\UHHHHHHHH`, `\\cX`,
    ...; an unknown one keeps its backslash; a value that is not a code point keeps its text); a NUL ends the text, as it ends a C string."""
    out, n, cut = [], len(s), False
    while i < n:
        c = s[i]
        if c == "'":
            return "".join(out), i + 1, True
        piece, i, val = c, i + 1, None
        if c == "\\" and i < n:
            d = s[i]
            if d in _ANSI_ESC:
                piece, i = _ANSI_ESC[d], i + 1
            elif d in _OCT:
                j = i
                while j < n and j < i + 3 and s[j] in _OCT:
                    j += 1
                val, i = int(s[i:j], 8) & 255, j
            elif d in "xuU":
                j, top = i + 1, i + 1 + {"x": 2, "u": 4, "U": 8}[d]
                while j < n and j < top and s[j] in _HEX:
                    j += 1
                if j > i + 1 and int(s[i + 1:j], 16) <= 0x10FFFF:
                    val, i = int(s[i + 1:j], 16), j
                else:
                    piece, i = "\\" + d, i + 1
            elif d == "c" and i + 1 < n:
                val, i = (0x7F if s[i + 1] == "?" else ord(s[i + 1]) & 0x1F), i + 2
            else:
                piece, i = "\\" + d, i + 1
        if val is not None:
            if val == 0:
                cut = True
            else:
                piece = chr(val)
        if not cut:
            out.append(piece)
    return "".join(out), n, False


def _redirect_word(s, i, stop=" \t\n;&|<>()"):
    """(word, index after it, whether every quote in it was closed): the shell word at s[i:] with its quotes removed as bash removes them (`'...'`, `"..."` with a backslash before `$`, a backtick, `"` or a backslash only, `$'...'`, `$"..."`,
    a backslash before any other character). The word ends at an unquoted character of `stop` (default: a blank, newline or one of `;&|<>()`). A `$` that remains makes the word one the guard cannot expand; it is passed on as written, as every other unknown target is."""
    out, n, closed = [], len(s), True
    while i < n:
        c = s[i]
        if c in stop:
            break
        if c == "\\":
            if i + 1 < n and s[i + 1] != "\n":
                out.append(s[i + 1])
            i += 2 if i + 1 < n else 1
        elif c == "'":
            j = s.find("'", i + 1)
            out.append(s[i + 1:] if j < 0 else s[i + 1:j])
            closed, i = closed and j >= 0, n if j < 0 else j + 1
        elif c == '"' or s.startswith('$"', i):
            i += 1 if c == '"' else 2
            while True:
                if i >= n:
                    closed = False
                    break
                d = s[i]
                if d == '"':
                    i += 1
                    break
                if d == "\\" and i + 1 < n:
                    e = s[i + 1]
                    if e in '$`"\\':
                        out.append(e)
                    elif e != "\n":
                        out.append(d + e)
                    i += 2
                else:
                    out.append(d)
                    i += 1
        elif s.startswith("$'", i):
            text, i, ok = _ansi_c(s, i + 2)
            out.append(text)
            closed = closed and ok
        else:
            out.append(c)
            i += 1
    return "".join(out), i, closed


def _quote_end(s, i):
    """s[i] opens a quote (`'`, `"`, or the `$` of `$'`): the index after its closing quote, or -1."""
    if s[i] == "'":
        j = s.find("'", i + 1)
        return -1 if j < 0 else j + 1
    q = '"' if s[i] == '"' else "'"
    j, n = i + (1 if s[i] == '"' else 2), len(s)
    while j < n and s[j] != q:
        j += 2 if s[j] == "\\" else 1
    return j + 1 if j < n else -1


def _scan_redirects(seg, quotes):
    """(targets, a quote was left open): the words that follow each output redirection operator of seg that is outside quotes: `>`, `>>`, `>|`, `&>`, `&>>`, `N>`, `N>>`, `N>|` (the operator is `>`, `>>` or `>|`, whatever stands before it),
    `>&` and a word that is not a number or `-` (`2>&1`, `>&2`, `>&-` are not files), and `<>`. With quotes=False a quote character is an ordinary character in the search for operators (the words are still read with their quotes)."""
    out, i, n, opn = [], 0, len(seg), False
    while i < n:
        m = _REDIR_SKIP.search(seg, i)
        if not m:
            break
        i, c = m.start(), m.group(0)
        if c == "\\":
            i += 2
        elif c in "'\"" or (c == "$" and seg.startswith("$'", i)):
            if not quotes:
                i += 1
                continue
            j = _quote_end(seg, i)
            if j < 0:
                opn = True
                break
            i = j
        elif c == "<" and seg[i + 1:i + 2] != ">":
            i += 1
        elif c == "$":
            i += 1
        else:
            j, dup = i + (2 if c == "<" else 1), False
            nxt = seg[j:j + 1] if c == ">" else ""
            if nxt in (">", "|"):
                j += 1
            elif nxt == "&":
                j, dup = j + 1, True
            while j < n and seg[j] in " \t\n":
                j += 1
            w, j, closed = _redirect_word(seg, j)
            opn = opn or not closed
            k = 0
            while k < len(w) and w[k] in _DIG:
                k += 1
            if w and not (dup and (w == "-" or (k > 0 and w[k:] in ("", "-")))):
                out.append(w)
            i = j
    return out, opn


def redirect_targets(seg):
    """The files the redirections of the simple command seg open for writing, as words with their quotes removed (a quote-aware reading, as bash does, so that a quoted target with a space is seen). A quote left open
    makes the scan run again with quotes as ordinary characters, as the splitter does."""
    out, opn = _scan_redirects(seg, True)
    if opn:
        out += _scan_redirects(seg, False)[0]
    return out


def _word_end(s, i):
    """The index after the shell word at s[i:], taken whole: a `$( )`, `${ }`, backtick pair or quote is skipped with whatever blanks and operators it holds (`"${F:-"a b"}"` is one word). One pass with a stack of what is open; an unclosed one runs to the end."""
    n, stack = len(s), []
    while i < n:
        c, top = s[i], (stack[-1] if stack else "")
        if c == "\\":
            i += 2
            continue
        if top == '"':
            if c == '"':
                stack.pop()
            elif c == "`":
                stack.append("`")
            elif s.startswith("$(", i) or s.startswith("${", i):
                stack.append(")" if s[i + 1] == "(" else "}")
                i += 1
        elif top == "`":
            if c == "`":
                stack.pop()
        elif c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                return n
            i = j
        elif c in '"`':
            stack.append(c)
        elif s.startswith("$'", i):
            j = _quote_end(s, i)
            if j < 0:
                return n
            i = j - 1
        elif s.startswith("$(", i) or s.startswith("${", i):
            stack.append(")" if s[i + 1] == "(" else "}")
            i += 1
        elif top == ")" and c == "(":
            stack.append(")")
        elif top and c == top:
            stack.pop()
        elif not top and c in " \t\n;&|<>()":
            return i
        i += 1
    return n


def _scan_spans(seg, quotes):
    """(spans, a quote was left open): the text of the whole word (`_word_end`) after each output redirection operator that `_scan_redirects` finds, quotes and substitutions as written; the scan goes on after the word, so a text is read once."""
    out, i, n, opn = [], 0, len(seg), False
    while i < n:
        m = _REDIR_SKIP.search(seg, i)
        if not m:
            break
        i, c = m.start(), m.group(0)
        if c == "\\":
            i += 2
        elif c in "'\"" or (c == "$" and seg.startswith("$'", i)):
            if not quotes:
                i += 1
                continue
            j = _quote_end(seg, i)
            if j < 0:
                opn = True
                break
            i = j
        elif c == "<" and seg[i + 1:i + 2] != ">":
            i += 1
        elif c == "$":
            i += 1
        else:
            j, dup = i + (2 if c == "<" else 1), False
            nxt = seg[j:j + 1] if c == ">" else ""
            if nxt in (">", "|"):
                j += 1
            elif nxt == "&":
                j, dup = j + 1, True
            while j < n and seg[j] in " \t\n":
                j += 1
            e = _word_end(seg, j)
            w = seg[j:e]
            k = 0
            while k < len(w) and w[k] in _DIG:
                k += 1
            if w and not (dup and (w == "-" or (k > 0 and w[k:] in ("", "-")))):
                out.append(w)
            i = e
    return out, opn


def redirect_spans(seg):
    """The words after the output redirection operators of seg, as written (see `_scan_spans`); a quote left open makes the scan run again with quotes as ordinary characters."""
    out, opn = _scan_spans(seg, True)
    if opn:
        out += _scan_spans(seg, False)[0]
    return out


def _ansi_words(seg):
    """The words of seg as bash reads them, quotes removed (`$'..'` and `$".."` too; blanks separate words): shlex does not know the ANSI-C form, so `bash -c $'..'` hands it a word that is not the string the shell runs."""
    out, i, n = [], 0, len(seg)
    while i < n:
        if seg[i] in " \t\n":
            i += 1
            continue
        w, i, _ = _redirect_word(seg, i, " \t\n")
        out.append(w)
    return out


_GLOB = re.compile(r"[*?\[]")
_SPAN_NAMES = re.compile(r"managed-settings|settings(?:\.local)?\.json(?![A-Za-z0-9_.\-])")
_NAMES_ANY = re.compile(r"managed-settings|settings(?:\.local)?\.json")
_SPAN_PATHS = re.compile(r"managed-settings|\.claude[/\\]+settings(?:\.local)?\.json(?![A-Za-z0-9_.\-])")


def _names_span(t, fl):
    """True when the text t names a settings file: `managed-settings`, or `settings.json` / `settings.local.json` not followed by a name character (so `settings.json}` and `settings.json"` count, `settings.json.bak` does not)."""
    return bool(_SPAN_NAMES.search(nt_fold(t) if fl == "nt" else t))


def _names_path(t, fl):
    """True when the text t names a settings file with its folder (`.claude/settings.json`, `.claude/settings.local.json`) or is `managed-settings..`: the value of an assignment that makes a later `$F` target a settings file. `settings.json` alone is a piece (a name built from pieces stays accepted)."""
    return bool(_SPAN_PATHS.search(nt_fold(t) if fl == "nt" else t))


def _unquoted(t):
    """t without its quote characters and backslashes (the text of a word that holds a substitution, read as it would be without the quoting)."""
    return t.replace("'", "").replace('"', "").replace("\\", "")


def _glob_tokens(p):
    """The pattern p as shell filename patterns read it: `*` (runs collapse), `?`, a bracket expression `[..]` (with `!` or `^`, ranges; a class name `[:..:]` is any one character, an over-reading; an unclosed `[` is itself), any other character itself."""
    out, i, n = [], 0, len(p)
    while i < n:
        c = p[i]
        if c == "*":
            if not out or out[-1][0] != "*":
                out.append(("*", None))
        elif c == "?":
            out.append(("?", None))
        elif c == "[":
            j = i + 1
            neg = j < n and p[j] in "!^"
            j += neg
            k = j + 1 if j < n and p[j] == "]" else j
            while k < n and p[k] != "]":
                k += 1
            if k >= n:
                out.append(("l", "["))
            else:
                body = p[j:k]
                if "[:" in body or "[." in body or "[=" in body:
                    out.append(("?", None))
                else:
                    rng, x = [], 0
                    while x < len(body):
                        if x + 2 < len(body) and body[x + 1] == "-":
                            rng.append((body[x], body[x + 2]))
                            x += 3
                        else:
                            rng.append((body[x], body[x]))
                            x += 1
                    out.append(("[", (neg, rng)))
                i = k
        else:
            out.append(("l", c))
        i += 1
    return out


def _glob_match(toks, s, prefix=False):
    """True when the pattern toks matches the whole of s; with prefix=True, when it matches some text that starts with s (what follows s is free)."""
    n = len(toks)

    def close(states):
        out = set(states)
        for t in sorted(states):
            while t < n and toks[t][0] == "*":
                t += 1
                out.add(t)
        return out
    cur = close({0})
    for ch in s:
        nxt = set()
        for t in cur:
            if t >= n:
                continue
            kind, v = toks[t]
            if kind == "*":
                nxt.add(t)
            elif kind == "?" or (kind == "l" and v == ch):
                nxt.add(t + 1)
            elif kind == "[" and any(lo <= ch <= hi for lo, hi in v[1]) != v[0]:
                nxt.add(t + 1)
        cur = close(nxt)
        if not cur:
            return False
    return bool(cur) if prefix else n in cur


def _glob_managed(lt):
    """True when the pattern lt could match a name that starts with `managed-settings`. A pattern that starts with `*` counts only when what follows it could start at `managed-settings`, `-settings` or `settings` (so `*.log` and `*.o` do not, `*settings*` does)."""
    i = 0
    while i < len(lt) and lt[i][0] == "*":
        i += 1
    if i == 0:
        return _glob_match(lt, "managed-settings", True)
    return i < len(lt) and any(_glob_match(lt[i:], s, True) for s in ("managed-settings", "-settings", "settings"))


def _glob_protected(w, cwd, unknown_dir, fl=HOST, keep=False):
    """True when the word w, read as a shell filename pattern, could match a settings file: its last component could be `managed-settings...`, or its folder component `managed-settings.d`, or its last component `settings.json` / `settings.local.json` in a folder `.claude`. Only the last two components
    count, as in `protected`. The folder is the working directory's when w has no `/`, and any folder when it is unknown (`cd $X` was seen) or holds `$`, a backtick, `)` or `}`; a folder that is `.`, `..` or empty after a pattern is read as any. A folder pattern counts as `managed-settings.d` by the rule of `_glob_managed` (`*/x` does not), and where the folder is unknown a last component that starts with `*` does not count."""
    nt = fl == "nt"
    w = expanduser(w, fl)
    if nt:
        w = nt_fold(w.replace("\\", "/"))
    if w.strip("/") == "":
        return False
    w = w.rstrip("/")
    has_sep = "/" in w
    dirpart, _, last = w.rpartition("/")
    lt = _glob_tokens(last)
    if _glob_managed(lt):
        return True
    named = any(_glob_match(lt, name) for name in SETTINGS_NAMES)
    guess = named and lt[0][0] != "*"        # where the folder is not known, a name that starts with `*` is no sign (`cd $X; rm *`, `$O/*.json` are everyday commands)
    dl = dirpart.rstrip("/").rpartition("/")[2]
    if has_sep and (any(ch in dl for ch in "$`)}") or (_GLOB.search(dirpart) and dl in ("", ".", ".."))):
        return guess        # the folder is not known: only the last component decides
    if has_sep and _GLOB.search(dirpart):
        dt = _glob_tokens(dl)
        return _glob_managed(dt) or (named and _glob_match(dt, ".claude"))
    if not has_sep and unknown_dir:
        return guess
    rel = dirpart + "/x" if has_sep else "x"
    if nt:
        comps = _nt_resolve(cwd or "", rel.replace("/", "\\"), keep)[2]
        parent = nt_fold(comps[-2]) if len(comps) > 1 else ""
    else:
        parent = posixpath.basename(posixpath.dirname(posixpath.normpath(posixpath.join(cwd or "", rel))))
    return parent == "managed-settings.d" or (named and parent == ".claude")


def _assigns_settings(segs, fl):
    """True when a simple command assigns a value that names a settings file (`F=..`, in front of a command or after `export`, `declare`, `local`, `readonly`), or loops a variable over such words (`for F in ..`)."""
    for _, toks in segs:
        if any(ASSIGN.match(t) and _names_path(t.split("=", 1)[1], fl) for t in toks):
            return True
        if toks[:1] == ["for"] and "in" in toks and any(_names_path(t, fl) for t in toks[toks.index("in") + 1:]):
            return True
    return False


_REDIR_TOK = re.compile(r"\d*(?:<<<|<<-?|<>|<&|<|>>|>&|>\||>|&>>|&>)")


def _reads_stdin(args):
    """True when a shell started with these arguments reads its script from its input: `-s` or `-` was given, or no argument is a script file (redirection words and option values do not count)."""
    s_opt, files, i = False, False, 0
    while i < len(args):
        t = args[i]
        m = _REDIR_TOK.match(t)
        if m:
            i += 1 if m.end() < len(t) else 2
            continue
        if t == "-":
            return True
        if t == "--":
            files = files or any(not _REDIR_TOK.match(x) for x in args[i + 1:i + 2])
            break
        if len(t) > 1 and t[0] in "-+":
            if t[1] != "-":
                s_opt = s_opt or (t[0] == "-" and "s" in t)
                i += t.count("o") + t.count("O") if t[1:].isalpha() and t[1:].isascii() else 0
            elif t in ("--rcfile", "--init-file"):
                i += 1
        else:
            files = True
        i += 1
    return s_opt or not files


def _stdin_shell(segs, fl):
    """True when some simple command is a shell with no `-c` string that reads its script from its input (`.. | sh`, `bash -s`, `sh <<EOF`, `sh <<< ..`, `sh < file`): what it runs is not in the command text."""
    for _, toks in segs:
        k, _ = program(toks, fl)
        if k < len(toks) and prog_name(toks[k], fl) in SHELLS and "-c" not in toks[k + 1:] and _shell_script(toks, k + 1) is None and _reads_stdin(toks[k + 1:]):
            return True
    return False


def _writer_targets(prog, args):
    """The words that the program writes or removes, for the writers that G3 knows (`tee`, in-place editors, `cp`, `mv`, ..., `dd of=`)."""
    targets = []
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
    return targets


def _gap_hit(seg, toks, k, prog, cur, unknown_dir, assign, fl, keep):
    """The gap readings of one simple command (leaf posix_gaps): each redirect target (as written, whole) and each writer argument that the guard cannot expand is denied when its text names a settings file or when the command assigns such a value; each that holds a glob character,
    when it could match a settings file."""
    cands = [(t, True) for t in redirect_spans(seg)] + [(t, False) for t in _writer_targets(prog, toks[k + 1:] if k < len(toks) else [])]
    for t, raw in cands:
        if "$" in t or "`" in t or "SUBST_" in t:
            if _names_span(t, fl) or _names_span(_unquoted(t), fl):
                return "G3", "the command writes `%s`, a target the guard cannot expand that names a Claude Code settings file" % t
            if assign:
                return "G3", "the command writes `%s`, a target the guard cannot expand, and assigns a value that names a Claude Code settings file" % t
            w = _unquoted(t)
        else:
            w = _redirect_word(t, 0)[0] if raw else t
        if _GLOB.search(w) and _glob_protected(w, cur, unknown_dir, fl, keep):
            return "G3", "the command writes `%s`, which can match a Claude Code settings file" % t
    return None


def g3_bash(cmd, segs, cwd, fl=HOST, script=True, redirects=False, gaps=False):
    """redirects=False is the reading of before the leaf posix_redirects, unchanged; redirects=True tests only the targets of `redirect_targets` (and no script), so that a command denied before is denied for the same reason; gaps=True tests only what the leaf posix_gaps adds (`_gap_hit`)."""
    hit = _g3_bash(cmd, segs, cwd, fl, script, False, redirects, gaps)
    if hit or fl != "nt":
        return hit
    # nt: the text read as written with the other reading of a dots-and-spaces name, then with each backslash a slash under both readings
    return _g3_bash(cmd, segs, cwd, fl, script, True, redirects, gaps) or _g3_bash(cmd, slashed(segs), cwd, fl, False, False, redirects, gaps) or _g3_bash(cmd, slashed(segs), cwd, fl, False, True, redirects, gaps)


def _g3_bash(cmd, segs, cwd, fl, script, keep=False, redirects=False, gaps=False):
    unknown, cur = False, cwd
    assign = gaps and _assigns_settings(segs, fl)
    for seg, toks in segs:
        k, _ = program(toks, fl)
        prog = prog_name(toks[k], fl) if k < len(toks) else ""
        if prog in ("cd", "pushd") and k + 1 < len(toks):
            t = expanduser(toks[k + 1], fl)
            if "$" in t or "`" in t or t == "-":
                unknown = True
            elif fl == "nt":
                cur = _nt_str(*_nt_resolve(cur or "", t, keep))
            else:
                cur = posixpath.normpath(t if posixpath.isabs(t) else posixpath.join(cur or "", t))
            continue
        if gaps:
            hit = _gap_hit(seg, toks, k, prog, cur, unknown, assign, fl, keep)
            if hit:
                return hit
            continue
        if redirects:
            for t in redirect_targets(seg):
                if protected(t, cur, unknown, fl, keep):
                    return "G3", "the command writes `%s`, a Claude Code settings file" % t
            continue
        targets = []
        for m in re.finditer(r"""(?:>>?|>\|)\s*(['"]?)([^\s;&|<>'"]+)\1""", seg):
            targets.append(m.group(2))
        targets += _writer_targets(prog, toks[k + 1:] if k < len(toks) else [])
        for t in targets:
            if protected(t, cur, unknown, fl, keep):
                return "G3", "the command writes `%s`, a Claude Code settings file" % t
    if not script or redirects or gaps:
        return None
    nt = fl == "nt"
    if (INTERP_NT if nt else INTERP).search(cmd) or any(prog_name(t, fl) in (("python", "python3", "py", "pythonw") if nt else ("python", "python3")) for _, ts in segs for t in ts[:1]):
        names = (NAMES_NT if nt else NAMES_POSIX).findall(cmd)
        if names and WRITEISH.search(cmd) and any(protected(n, cur, True, fl, keep) or ("/" in n or (nt and "\\" in n)) and protected(n, cwd, False, fl, keep) for n in names):
            return "G3", "a script in the command writes a Claude Code settings file"
    return None


def g3_edit(inp, cwd, fl=HOST):
    p = inp.get("file_path") or inp.get("path") or inp.get("notebook_path") or ""
    if p and (protected(p, cwd, False, fl) or fl == "nt" and protected(p, cwd, False, fl, True)):
        return "G3", "the edit targets `%s`, a Claude Code settings file" % p
    return None


SCRIPT_EXT = (".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".mjs", ".ipynb")
SRC = re.compile(r"""--setting-sources["'\s=,\[\]]*([A-Za-z,]*)""")


def _hits(text):
    """The bypass words and the `--setting-sources` values without `user` that a text carries, in order."""
    out = [m.group(0) for m in BYPASS.finditer(text)]
    out += ["--setting-sources " + v for v in SRC.findall(text) if v and "user" not in v.split(",")]
    return out


def g4_script(inp, cwd="", fl=HOST):
    """G4 (v2): Write or Edit of a script file that ADDS the bypass words or a literal `--setting-sources` value without `user`.
    Edit: more of them in `new_string` than in `old_string`. Write over an existing file: more than the file holds now. Write of a new file: any."""
    p = inp.get("file_path") or inp.get("path") or inp.get("notebook_path") or ""
    if fl == "nt":                  # the file name as Windows resolves it: `X.PY`, `x.py.`, `x.py::$DATA` are scripts
        comps = _nt_resolve("", p)[2]
        if not (comps and nt_fold(comps[-1]).endswith(SCRIPT_EXT)):
            return None
    elif not p.lower().endswith(SCRIPT_EXT):
        return None
    if "new_source" in inp:         # NotebookEdit: the replaced cell is not known to the hook, so any occurrence counts
        new, old = _hits(str(inp.get("new_source") or "")), []
    elif "content" in inp:
        new, old = _hits(str(inp.get("content") or "")), []
        try:
            with open(_nt_join(cwd or "", _nt_expanduser(p)) if fl == "nt" else posixpath.join(cwd or "", posixpath.expanduser(p)), errors="replace", encoding="utf-8") as fh:
                old = _hits(fh.read())
        except OSError:
            old = []
    else:
        edits = [inp] + [e for e in (inp.get("edits") or []) if isinstance(e, dict)]
        new = [h for e in edits for h in _hits(str(e.get("new_string") or ""))]
        old = [h for e in edits for h in _hits(str(e.get("old_string") or ""))]
    if len(new) > len(old):
        h = new[len(old)] if len(new) > len(old) else new[0]
        return "G4", "the edit adds `%s` to the script `%s`" % (h, display_name(p, fl))
    return None


TOO_COMPLEX = "G?", "the command has too many command substitutions to be checked"
MAX_CHARS = 200000   # the longest Bash command, or Write/Edit input, that is read: 1.8x the longest real Bash command seen (113042) and 2x the longest Write input (99452); the slowest form reads in ~1.3 s (posix) / ~6.5 s (nt) at this size, a quarter of the hook's 20 s
NEST = 8              # the depth to which shell strings are followed in the second pass (the first pass follows 3)


def _bash_pass(cmd, cwd, fl, second):
    """(hit, the commands, the strings found deeper than the pass follows): the readings of G1 to G3 over the commands of `expand`. second=True is the pass of the leaf posix_gaps (ANSI-C words, strings to depth NEST); the first pass is that of before."""
    kw, deep = (dict(ansi=True, limit=NEST), []) if second else ({}, None)
    try:
        segs = expand(cmd, fl=fl, deep=deep, **kw)
    except TooComplex:
        return TOO_COMPLEX, [], []
    hit = g1(cmd, segs, fl) or g2(cmd, segs, fl) or (fl == "nt" and g2(cmd, slashed(segs), fl)) or g3_bash(cmd, segs, cwd, fl)
    hit = hit or g3_bash(cmd, segs, cwd, fl, False, True)           # the quote-aware reading of the redirections comes after every older reading, so a denial keeps its reason
    if hit or not any(sg.endswith(">") for sg, _ in segs):      # a segment that ends in `>` is where the splitter cut a `>|`
        return hit, segs, deep
    try:
        return g3_bash(cmd, expand(cmd, fl=fl, clobber=True, **kw), cwd, fl, False, True), segs, deep      # and the reading with `>|` whole
    except TooComplex:
        return TOO_COMPLEX, segs, deep


def g3_gaps(cmd, segs, deep, cwd, fl=HOST):
    """The readings of the leaf posix_gaps that are not a pass over the same commands: targets that cannot be expanded or that are globs (`_gap_hit`), and, when the command names a settings file anywhere, a shell string nested deeper than the pass follows or a shell that reads its
    script from its input (the script is not in the command text)."""
    hit = g3_bash(cmd, segs, cwd, fl, False, False, True)
    if hit or not _NAMES_ANY.search(nt_fold(cmd) if fl == "nt" else cmd):       # not NAMES_*: its `[^\s..]*` in front is quadratic on a long word
        return hit
    if deep:
        return "G3", "a shell string is nested too deep to be read, and the command names a Claude Code settings file"
    if _stdin_shell(segs, fl):
        return "G3", "a shell reads a script that is not in the command, and the command names a Claude Code settings file"
    return None


def _input_chars(inp):
    """The characters of the strings of a Write, Edit, MultiEdit or NotebookEdit input that the guard reads: the path, the content, and each old and new string."""
    edits = inp.get("edits")
    parts = [inp.get(k) for k in ("file_path", "path", "notebook_path", "content", "new_source", "old_string", "new_string")]
    for e in edits if isinstance(edits, list) else []:
        if isinstance(e, dict):
            parts += [e.get("old_string"), e.get("new_string")]
    return sum(len(p) for p in parts if isinstance(p, str))


def decide(event, fl=HOST):
    """(group, why) when the event is to be denied, else None. fl is the flavour of the paths and program names: "posix" or "nt" (the OS this runs on, by default)."""
    tool, inp, cwd = event.get("tool_name"), event.get("tool_input") or {}, event.get("cwd") or ""
    if tool == "Bash":
        cmd = inp.get("command") or ""
        if isinstance(cmd, str) and "\0" in cmd:
            return "G?", "the command holds a NUL character, which a shell cannot receive"
        if isinstance(cmd, str) and len(cmd) > MAX_CHARS:
            return "G?", "the command is too long to be checked (more than %d characters)" % MAX_CHARS
        hit, _, _ = _bash_pass(cmd, cwd, fl, False)
        if hit:
            return hit
        hit, segs, deep = _bash_pass(cmd, cwd, fl, True)           # the readings of the leaf posix_gaps come after every older reading, so a denial keeps its reason
        return hit or g3_gaps(cmd, segs, deep, cwd, fl)
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        hit = g3_edit(inp, cwd, fl)
        if not hit and _input_chars(inp) > MAX_CHARS:
            hit = "G?", "the input is too long to be checked (more than %d characters)" % MAX_CHARS
        return hit or g4_script(inp, cwd, fl)
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
            with open(log, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(dict(tool=tool, what=what, decision="deny" if hit else "allow", group=hit[0] if hit else None)) + "\n")
        except OSError:
            pass
    if not hit:
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": MSG % hit}}


FIXTURES = os.path.join(HERE, "fixtures", "guard_lists")   # copied from __reports__/wave-06/author-w06-5 (the research record keeps the originals)
FIXTURE_COUNTS = {"attacks": 50, "ordinary": 28, "mention": 6, "evasions": 13}   # a missing file or a different count fails the selftest: it must never pass on empty lists
WINDOWS_COUNT = 106   # windows_paths.json: each case carries the cwd and the expected decision under both flavours ("allow" or the group); the same file is read by the Rust tests and by check_guard_equal.py
POSIX_GAPS_COUNT = 110   # posix_gaps.json: the same layout; the shell strings, targets, NULs and sizes that leaf posix_gaps closed or denies, and the ordinary forms next to them that stay allowed
REDIRECTS_COUNT = 110   # redirects.json: the same layout; the forms of a Bash redirection onto a settings file that are denied, and the ones that must stay allowed


def selftest():
    import tempfile
    T = tempfile.mkdtemp()
    ok = True
    missing = []

    def load(n):
        p = os.path.join(FIXTURES, "e3_%s.json" % n)
        try:
            cases = json.loads(open(p, encoding="utf-8").read().replace("{T}", json.dumps(T)[1:-1]))      # {T} is replaced in JSON text: a Windows T (D:\\a\\..) pasted raw makes invalid escapes
        except (OSError, ValueError):
            missing.append(n)
            return []
        if len(cases) != FIXTURE_COUNTS[n]:
            missing.append("%s (%d cases, %d pinned)" % (n, len(cases), FIXTURE_COUNTS[n]))
        return cases

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
    holes = json.load(open(os.path.join(HERE, "guard_selftest_holes.json"), encoding="utf-8"))        # w08-c10: the forms that hid a flag after a substitution or behind an option of a wrapper, and controls
    for c in holes:
        check("hole-form %s (%s)" % (c["id"], "deny" if c["deny"] else "allow"), bool(decide(dict(tool_name="Bash", tool_input={"command": c["command"]}, cwd=T))) == c["deny"])
    def both_flavours(name, count):
        """The cases of a list that carries the cwd and the expected decision under both flavours; a missing file or a different count fails the selftest."""
        try:
            cases = json.loads(open(os.path.join(FIXTURES, name + ".json"), encoding="utf-8").read())
        except (OSError, ValueError):
            cases = []
        if len(cases) != count:
            missing.append("%s (%d cases, %d pinned)" % (name, len(cases), count))
        for c in cases:       # both flavours run on every host: the posix column is what Unix decides, the nt column what Windows decides
            e = dict(tool_name=c["tool"], tool_input={"command": c["command"]} if c["tool"] == "Bash" else c["input"], cwd=c["cwd"])
            for fl in ("posix", "nt"):
                hit = decide(e, fl)
                check("%s %s under %s (want %s)" % (name, c["id"], fl, c[fl]), (hit[0] if hit else "allow") == c[fl])
        return cases
    windows = both_flavours("windows_paths", WINDOWS_COUNT)
    redirects = both_flavours("redirects", REDIRECTS_COUNT)
    posix_gaps = both_flavours("posix_gaps", POSIX_GAPS_COUNT)
    for tool, key, body in (("Bash", "command", "echo a"), ("Write", "content", "a"), ("Edit", "new_string", "a"), ("NotebookEdit", "new_source", "a")):       # the cap: one character over is denied G?, the cap itself is read (the lists keep to small commands)
        for n, want in ((MAX_CHARS, False), (MAX_CHARS + 1, True)):
            pad = body * (n // len(body))
            h = decide(dict(tool_name=tool, tool_input={key: pad + "a" * (n - len(pad))}, cwd=T))
            check("size %s %d (want %s)" % (tool, n, "G?" if want else "allow"), bool(h) == want and (not h or h[0] == "G?"))
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
    for n in sorted(set(missing)):
        check("fixture %s present with its pinned count" % n, False)
    print("selftest %s: attacks %d denied, ordinary %d allowed, windows_paths %d, redirects %d and posix_gaps %d x 2 flavours; not-gated: evasions caught %s, mention-only denied %s" % (
        "ok" if ok else "FAILED", len(load("attacks")), len(load("ordinary")), len(windows), len(redirects), len(posix_gaps), ev_pass, mention_denied))
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
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    ans = run(sys.stdin.read(), os.environ.get("MURMURATION_GUARD_LOG"))
    if ans:
        sys.stdout.write(json.dumps(ans))


if __name__ == "__main__":
    main()
