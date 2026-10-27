//! The permission guard: a line-for-line port of `scripts/permission_guard.py` (`decide` and `run`), over code points, with the regular expressions written out by hand.
//!
//! The Python file is the reference. Every function below names the Python function it ports; the `os` argument is its `fl` (the flavour of paths and program names). The patterns of `re` that Python evaluates with backtracking are
//! evaluated here by the equivalent deterministic scan; the comments say why the two agree.

use crate::json::{self, Value};
use crate::platform::{self, Os};
use crate::shlex;
use crate::text::{
    at, basename, contains, cp, dirname, display_name, eq, expanduser, expanduser_for, find_from, has_char, is_digit, is_space, is_word, isabs, join, join_with,
    nt_fold, nt_join, nt_resolve, nt_root, nt_str, nt_walk, normpath, prog_name, prog_name_with, slice, split_on, split_ws, starts, starts_at, strip, string, text, Cwd, Fault, Text,
};

const INERT: &[&str] = &["grep", "egrep", "fgrep", "rg", "jq", "wc", "head", "tail", "cat", "ls", "diff", "sort", "uniq", "cut", "tr", "nl", "less"];
const GIT_INERT: &[&str] = &["log", "grep", "show", "diff", "status", "blame", "shortlog"];
const WRAP: &[&str] = &["env", "command", "nohup", "exec", "time", "sudo", "nice", "ionice", "stdbuf", "xargs", "timeout", "gtimeout", "setsid", "caffeinate"];
const KEYWORDS: &[&str] = &["if", "then", "else", "elif", "do", "while", "until", "!", "{", "}", "fi", "done"];
const SHELLS: &[&str] = &["sh", "bash", "zsh", "dash", "ksh"];
const SCRIPT_EXT: &[&str] = &[".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".mjs", ".ipynb"];

type Res<T> = Result<T, Fault>;
type Seg = (Text, Vec<Text>);

/// A denial: the rule group and why.
pub(crate) struct Hit {
    group: &'static str,
    why: Text,
}

fn in_set(t: &[u32], set: &[&str]) -> bool {
    set.iter().any(|s| eq(t, s))
}

fn cat(parts: &[&[u32]]) -> Text {
    parts.iter().flat_map(|p| p.iter().copied()).collect()
}

fn hit(group: &'static str, why: Text) -> Option<Hit> {
    Some(Hit { group, why })
}

fn quote_chars(c: u32) -> bool {
    c == cp('\'') || c == cp('"')
}

// ---------------------------------------------------------------------------------------------------------------------------------------------------------
// splitting: `_split`, `split_segments`, `words`, `program`, `flag_value`, `expand`

/// `_split`: one pass of the splitter; the segments (stripped, non-empty) and the quote left open at the end.
fn split_pass(cmd: &[u32], quotes: bool) -> (Vec<Text>, Option<u32>) {
    let (sq, dq, bs, bt, amp, gt) = (cp('\''), cp('"'), cp('\\'), cp('`'), cp('&'), cp('>'));
    let mut segs: Vec<Text> = Vec::new();
    let mut cur = Text::new();
    let mut q: Option<u32> = None;
    let mut i = 0;
    while let Some(c) = at(cmd, i) {
        if q == Some(sq) {
            cur.push(c);
            if c == sq {
                q = None;
            }
        } else if c == bs && i + 1 < cmd.len() {
            cur.push(c);
            cur.extend(at(cmd, i + 1));
            i += 1;
        } else if q == Some(dq) {
            if c == dq {
                q = None;
                cur.push(c);
            } else if c == bt || starts_at(cmd, i, "$(") {
                segs.push(std::mem::take(&mut cur));
                if c != bt {
                    i += 1;
                }
            } else {
                cur.push(c);
            }
        } else if quotes && quote_chars(c) {
            q = Some(c);
            cur.push(c);
        } else if [cp('\n'), cp(';'), cp('|'), cp('('), cp(')'), bt].contains(&c)
            || (c == amp && !((i > 0 && at(cmd, i - 1) == Some(gt)) || at(cmd, i + 1) == Some(gt)))
        {
            segs.push(std::mem::take(&mut cur));
        } else {
            cur.push(c);
        }
        i += 1;
    }
    segs.push(cur);
    let segs = segs.iter().map(|s| strip(s).to_vec()).filter(|s| !s.is_empty()).collect();
    (segs, q)
}

/// `split_segments`.
fn split_segments(cmd: &[u32]) -> Vec<Text> {
    let (segs, q) = split_pass(cmd, true);
    if q.is_some() { split_pass(cmd, false).0 } else { segs }
}

/// `words`.
fn words(seg: &[u32]) -> Vec<Text> {
    shlex::split(seg).unwrap_or_else(|()| split_ws(seg))
}

/// `ASSIGN.match(t)`: `^[A-Za-z_][A-Za-z0-9_]*=`.
fn is_assign(t: &[u32]) -> bool {
    let ident = |c: u32, first: bool| char::from_u32(c).is_some_and(|ch| ch.is_ascii_alphabetic() || ch == '_' || (!first && ch.is_ascii_digit()));
    if !at(t, 0).is_some_and(|c| ident(c, true)) {
        return false;
    }
    let end = t.iter().skip(1).position(|&c| !ident(c, false)).map_or(t.len(), |k| k + 1);
    at(t, end) == Some(cp('='))
}

/// `re.fullmatch(r"[\d.]+[smhd]?", t)`.
fn is_duration(t: &[u32]) -> bool {
    let body = |c: u32| is_digit(c) || c == cp('.');
    let n = t.len();
    if n == 0 {
        return false;
    }
    let all = t.iter().all(|&c| body(c));
    let last_unit = n >= 2 && [cp('s'), cp('m'), cp('h'), cp('d')].contains(&t[n - 1]) && slice(t, 0, n - 1).iter().all(|&c| body(c)); // INDEX: n >= 2 checked in the same expression
    all || last_unit
}

/// `VALUE_OPTS`: per wrapper, the short option letters and the long option names that take their value from the next word.
const VALUE_OPTS: &[(&str, &str, &[&str])] = &[
    ("env", "uCSPa", &["--unset", "--chdir", "--split-string", "--argv0"]),
    ("exec", "a", &[]),
    ("timeout", "ks", &["--kill-after", "--signal"]),
    ("gtimeout", "ks", &["--kill-after", "--signal"]),
    ("nice", "n", &["--adjustment"]),
    ("ionice", "cnpPu", &["--class", "--classdata", "--pid", "--pgid", "--uid"]),
    ("stdbuf", "ioe", &["--input", "--output", "--error"]),
    ("xargs", "nILPsdaERS", &["--max-args", "--max-lines", "--max-procs", "--max-chars", "--delimiter", "--arg-file", "--eof"]),
    ("caffeinate", "tw", &[]),
    (
        "sudo",
        "ugCDhprtTUR",
        &["--user", "--group", "--close-from", "--chdir", "--host", "--prompt", "--role", "--type", "--command-timeout", "--other-user", "--chroot"],
    ),
    ("time", "fo", &["--format", "--output"]),
];

/// `name.startswith(t)` for a literal `name`.
fn name_starts_with(name: &str, t: &[u32]) -> bool {
    let n = text(name);
    n.len() >= t.len() && slice(&n, 0, t.len()) == t
}

/// `_value_option`: the option word `t` of wrapper `w` takes its value from the next word.
fn value_option(w: &[u32], t: &[u32]) -> bool {
    let (shorts, longs) = VALUE_OPTS.iter().find(|(n, _, _)| eq(w, n)).map_or(("", &[][..]), |(_, s, l)| (*s, *l));
    if starts(t, "--") {
        return !has_char(t, '=') && t.len() > 2 && longs.iter().any(|name| name_starts_with(name, t));
    }
    for k in 1..t.len() {
        if at(t, k).is_some_and(|ch| shorts.chars().any(|sc| cp(sc) == ch)) {
            return k == t.len() - 1;
        }
    }
    false
}

/// `_env_string`: the string of `env -S` / `--split-string` in the option word `t` (`toks[i]` is the word after it).
fn env_string(t: &[u32], toks: &[Text], i: usize) -> Option<Text> {
    if starts(t, "--") {
        let eq_at = t.iter().position(|&c| c == cp('='));
        let name = slice(t, 0, eq_at.unwrap_or(t.len()));
        if name.len() > 2 && name_starts_with("--split-string", name) {
            return match eq_at {
                Some(e) => Some(slice(t, e + 1, t.len()).to_vec()),
                None => toks.get(i).cloned(),
            };
        }
        return None;
    }
    for k in 1..t.len() {
        let Some(ch) = at(t, k) else {
            continue;
        };
        if "uCSPa".chars().any(|sc| cp(sc) == ch) {
            if ch != cp('S') {
                return None;
            }
            return if k + 1 < t.len() { Some(slice(t, k + 1, t.len()).to_vec()) } else { toks.get(i).cloned() };
        }
    }
    None
}

/// What `_scan` finds: the program word's index, the assignments before it, the strings of `env -S`, and whether a wrapper option's value was skipped.
struct Scan {
    k: usize,
    assigns: Vec<Text>,
    strings: Vec<Text>,
    skipped: bool,
}

/// `_scan`.
fn scan(toks: &[Text], os: Os) -> Scan {
    let mut i = 0;
    let mut sc = Scan { k: 0, assigns: Vec::new(), strings: Vec::new(), skipped: false };
    while let Some(t) = toks.get(i) {
        if in_set(t, KEYWORDS) {
            i += 1;
        } else if is_assign(t) {
            sc.assigns.push(t.clone());
            i += 1;
        } else if in_set(&prog_name(t, os), WRAP) {
            let w_text = prog_name(t, os);
            let w = w_text.as_slice();
            let timed = eq(w, "timeout") || eq(w, "gtimeout") || eq(w, "nice");
            i += 1;
            while let Some(o) = toks.get(i) {
                if !(starts(o, "-") || is_assign(o) || (timed && is_duration(o))) {
                    break;
                }
                if is_assign(o) {
                    sc.assigns.push(o.clone());
                }
                i += 1;
                if eq(w, "env") && starts(o, "-") {
                    if let Some(st) = env_string(o, toks, i) {
                        sc.strings.push(st);
                    }
                }
                if starts(o, "-") && value_option(w, o) {
                    if let Some(v) = toks.get(i) {
                        // a value is never taken for the program, but `claude` is never taken for a value
                        if !eq(&prog_name(v, os), "claude") {
                            i += 1;
                            sc.skipped = true;
                        }
                    }
                }
            }
        } else {
            sc.k = i;
            return sc;
        }
    }
    sc.k = toks.len();
    sc
}

/// `program`: the index of the program word and the assignments before it.
fn program(toks: &[Text], os: Os) -> (usize, Vec<Text>) {
    let sc = scan(toks, os);
    (sc.k, sc.assigns)
}

/// `flag_value`: the values given to `--flag`, separate or with `=`.
fn flag_value(toks: &[Text], flag: &str) -> Vec<Text> {
    let mut out = Vec::new();
    for (k, t) in toks.iter().enumerate() {
        if eq(t, flag) {
            out.push(toks.get(k + 1).cloned().unwrap_or_default());
        } else if starts(t, flag) && at(t, flag.chars().count()) == Some(cp('=')) {
            out.push(slice(t, flag.chars().count() + 1, t.len()).to_vec());
        }
    }
    out
}

/// `TooComplex`: more characters scanned while masking substitutions than `WORK` allows (a text scanned once costs its length; each nesting level scans its inside again).
struct TooComplex;

const WORK: usize = 10_000_000;

/// A span of a matched substitution: start, end, inside start, inside end.
type Span = (usize, usize, usize, usize);

/// `_heredoc`: at `<<` (not `<<<`): the delimiter, whether tabs are stripped, and the index after the delimiter word.
fn heredoc_op(s: &[u32], i: usize) -> Option<(Text, bool, usize)> {
    let n = s.len();
    let mut j = i + 2;
    let mut strip = false;
    if at(s, j) == Some(cp('-')) {
        strip = true;
        j += 1;
    }
    while at(s, j).is_some_and(|c| c == cp(' ') || c == cp('\t')) {
        j += 1;
    }
    let first = at(s, j)?;
    if first == cp('\'') || first == cp('"') {
        let k = (j + 1..n).find(|&k| at(s, k) == Some(first))?;
        return Some((slice(s, j + 1, k).to_vec(), strip, k + 1));
    }
    if first == cp('\\') {
        j += 1;
    }
    let mut k = j;
    while at(s, k).is_some_and(|c| !" \t\n;&|<>()`".chars().any(|x| cp(x) == c)) {
        k += 1;
    }
    if k > j { Some((slice(s, j, k).to_vec(), strip, k)) } else { None }
}

/// `_skip_bodies`: `s[i]` is a newline: the index just after the last delimiter line (or the end).
fn skip_bodies(s: &[u32], i: usize, pend: &[(Text, bool)]) -> usize {
    let n = s.len();
    let mut pos = i + 1;
    for (delim, strip) in pend {
        loop {
            let e = (pos..n).find(|&k| at(s, k) == Some(cp('\n'))).unwrap_or(n);
            let mut line = slice(s, pos, e);
            if *strip {
                let t = line.iter().position(|&c| c != cp('\t')).unwrap_or(line.len());
                line = slice(line, t, line.len());
            }
            pos = (e + 1).min(n);
            if line == delim.as_slice() || e == n {
                break;
            }
        }
    }
    pos
}

/// `_spans`: one pass with a stack of what is open; the matched substitutions, and whether a quote was still open at the end.
fn spans(s: &[u32], quotes: bool, work: &mut usize) -> Result<(Vec<Span>, bool), TooComplex> {
    *work += s.len();
    if *work > WORK {
        return Err(TooComplex);
    }
    // frame kinds: b'S' single quote, b'D' double quote, b'B' backtick, b'P' parenthesis; the flag is true for a substitution
    let mut stack: Vec<(u8, usize, bool)> = Vec::new();
    let mut out: Vec<Span> = Vec::new();
    let mut pend: Vec<(Text, bool)> = Vec::new();
    let mut nsub = 0usize;
    let mut i = 0;
    while let Some(c) = at(s, i) {
        let top = stack.last().map(|f| f.0);
        if top == Some(b'S') {
            if c == cp('\'') {
                stack.pop();
            }
        } else if c == cp('\\') {
            i += 1;
        } else if top == Some(b'B') {
            if c == cp('`') {
                if let Some(f) = stack.pop() {
                    out.push((f.1, i + 1, f.1 + 1, i));
                }
            }
        } else if top == Some(b'D') {
            if c == cp('"') {
                stack.pop();
            } else if starts_at(s, i, "$(") {
                stack.push((b'P', i, true));
                nsub += 1;
                i += 1;
            } else if c == cp('`') {
                stack.push((b'B', i, false));
            }
        } else if quotes && (c == cp('\'') || c == cp('"')) {
            stack.push((if c == cp('\'') { b'S' } else { b'D' }, i, false));
        } else if c == cp('`') {
            stack.push((b'B', i, false));
        } else if nsub > 0 && c == cp('<') && starts_at(s, i, "<<") && !starts_at(s, i, "<<<") && heredoc_op(s, i).is_some() {
            if let Some((d, strip, j)) = heredoc_op(s, i) {
                pend.push((d, strip));
                i = j - 1;
            }
        } else if nsub > 0 && c == cp('\n') && !pend.is_empty() {
            i = skip_bodies(s, i, &pend) - 1;
            pend.clear();
        } else if (c == cp('$') || c == cp('<') || c == cp('>')) && at(s, i + 1) == Some(cp('(')) {
            stack.push((b'P', i, true));
            nsub += 1;
            i += 1;
        } else if c == cp('(') {
            stack.push((b'P', i, false));
        } else if c == cp(')') {
            if let Some(f) = stack.pop() {
                if f.2 {
                    nsub -= 1;
                    out.push((f.1, i + 1, f.1 + 2, i));
                }
            }
        }
        i += 1;
    }
    Ok((out, stack.iter().any(|f| f.0 == b'S' || f.0 == b'D')))
}

/// `_mask`: the text with every outermost matched substitution replaced by one word, and the insides that were replaced.
fn mask(s: &[u32], work: &mut usize, os: Os) -> Result<(Text, Vec<Text>), TooComplex> {
    let (mut sp, open_quote) = spans(s, true, work)?;
    if open_quote {
        sp = spans(s, false, work)?.0;
    }
    sp.sort_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)));
    let mut out: Text = Text::new();
    let mut inners: Vec<Text> = Vec::new();
    let mut prev = 0;
    for (st, en, a, b) in sp {
        if st < prev {
            continue;
        }
        let inner = slice(s, a, b).to_vec();
        out.extend_from_slice(slice(s, prev, st));
        out.extend(text(if names_claude(&inner, os) { "claude" } else { "SUBST" }));
        inners.push(inner);
        prev = en;
    }
    out.extend_from_slice(slice(s, prev, s.len()));
    Ok((out, inners))
}

/// `substitution_texts`: the texts to split in addition to `cmd`; empty when `cmd` has no substitution.
fn substitution_texts(cmd: &[u32], work: &mut usize, os: Os) -> Result<Vec<Text>, TooComplex> {
    if !contains(cmd, "$(") && !has_char(cmd, '`') && !contains(cmd, "<(") && !contains(cmd, ">(") {
        return Ok(Vec::new());
    }
    let mut texts: Vec<Text> = Vec::new();
    let mut queue: std::collections::VecDeque<Text> = std::collections::VecDeque::new();
    queue.push_back(cmd.to_vec());
    while let Some(t) = queue.pop_front() {
        let (m, inners) = mask(&t, work, os)?;
        texts.push(m);
        queue.extend(inners);
    }
    let same = texts.len() == 1 && texts.first().is_some_and(|t| t.as_slice() == cmd);
    Ok(if same { Vec::new() } else { texts })
}

/// `_shell_script`: the index in `toks` of the word a shell reads as the string of `-c`, or None. Options come first: a word of `-` and letters with a `c` among them sets -c (`-lc`, `-ec`, `-c`); a letter `o` or `O` in such a word,
/// and `--rcfile`, `--init-file`, take the next word as their value; `--` or `-` ends the options; any other word is the first non-option, which is the string when -c was set.
fn shell_script(toks: &[Text]) -> Option<usize> {
    let mut c = false;
    let mut pend = 0usize;
    for (i, t) in toks.iter().enumerate() {
        if pend > 0 {
            pend -= 1;
        } else if eq(t, "--") || eq(t, "-") {
            return if c && i + 1 < toks.len() { Some(i + 1) } else { None };
        } else if t.len() > 1 && (starts(t, "-") || starts(t, "+")) && t.iter().skip(1).all(|&ch| char::from_u32(ch).is_some_and(|x| x.is_ascii_alphabetic())) {
            pend = t.iter().filter(|&&ch| ch == cp('o') || ch == cp('O')).count();
            c = c || (starts(t, "-") && has_char(t, 'c'));
        } else if eq(t, "--rcfile") || eq(t, "--init-file") {
            pend = 1;
        } else if t.len() > 1 && (starts(t, "-") || starts(t, "+")) {
            // another option
        } else {
            return if c { Some(i) } else { None };
        }
    }
    None
}

/// `expand`: every simple command of `cmd`: those of the plain splitter first, in order, then those of the command and of each substitution inside it with the substitutions replaced by one word;
/// descends into `sh -c '...'`, `eval '...'` and `env -S '...'` strings to depth 3.
fn expand(cmd: &[u32], depth: usize, work: &mut usize, os: Os) -> Result<Vec<Seg>, TooComplex> {
    let mut out: Vec<Seg> = Vec::new();
    let mut segs = split_segments(cmd);
    for t in substitution_texts(cmd, work, os)? {
        segs.extend(split_segments(&t));
    }
    for seg in segs {
        let toks = words(&seg);
        out.push((seg, toks.clone()));
        let sc = scan(&toks, os);
        let k = sc.k;
        if depth < 3 {
            for st in &sc.strings {
                let mut parts: Vec<Text> = vec![st.clone()];
                parts.extend_from_slice(slice_toks(&toks, k));
                out.extend(expand(&join_with(&parts, ' '), depth + 1, work, os)?);
            }
        }
        if depth < 3 && k < toks.len() {
            let prog_text = prog_name(&toks[k], os); // INDEX: k < toks.len() checked on the line above
            let prog = prog_text.as_slice();
            let rest = slice_toks(&toks, k + 1);
            if in_set(prog, SHELLS) {
                let mut js: Vec<usize> = Vec::new();
                if let Some(j) = rest.iter().position(|t| eq(t, "-c")) {
                    js.push(j + 1); // the word after the first `-c`, as before
                }
                if let Some(j) = shell_script(rest) {
                    if !js.contains(&j) {
                        js.push(j); // the string of `-c` as the shell reads its options (`-lc`, `-c -x`, ...)
                    }
                }
                for j in js {
                    if let Some(arg) = rest.get(j) {
                        out.extend(expand(arg, depth + 1, work, os)?);
                    }
                }
            } else if eq(prog, "eval") {
                out.extend(expand(&join_with(rest, ' '), depth + 1, work, os)?);
            }
        }
    }
    Ok(out)
}

/// `inert`: a read-only search that may carry the words without being an attack.
fn inert(toks: &[Text], os: Os) -> bool {
    let sc = scan(toks, os);
    // a wrapper option's value was skipped: the program may be one the old reading took for `inert`, so it counts as not inert
    if sc.skipped {
        return false;
    }
    let Some(first) = toks.get(sc.k) else {
        return false;
    };
    let prog_text = prog_name_with(first, os, &[".exe"]); // only `grep.exe` is the grep; a `grep.cmd` or `ls.bat` can run anything
    let prog = prog_text.as_slice();
    let rest = slice_toks(toks, sc.k + 1);
    if in_set(prog, INERT) {
        return !rest.iter().any(|t| eq(t, "--pre") || starts(t, "--pre="));
    }
    if eq(prog, "git") {
        let sub = rest.iter().find(|t| !starts(t, "-"));
        return sub.is_some_and(|s| in_set(s, GIT_INERT)) && !rest.iter().any(|t| eq(t, "-c")) && !rest.iter().any(|t| starts(t, "--exec"));
    }
    false
}

fn slice_toks(toks: &[Text], a: usize) -> &[Text] {
    let a = a.min(toks.len());
    // INDEX: a is clamped to the length just above
    &toks[a..]
}

// ---------------------------------------------------------------------------------------------------------------------------------------------------------
// the regular expressions, by hand

/// Whether the code point `tc` matches the ASCII letter or character `ch` under `(?i)` in a `str` pattern (the folds `i`, `k`, `s` have extra members).
fn ci_eq(ch: char, tc: u32) -> bool {
    if tc == cp(ch) {
        return true;
    }
    if !ch.is_ascii_alphabetic() {
        return false;
    }
    let lower = ch.to_ascii_lowercase();
    if tc == cp(lower) || tc == cp(lower.to_ascii_uppercase()) {
        return true;
    }
    match lower {
        'i' => tc == 0x130 || tc == 0x131,
        'k' => tc == 0x212A,
        's' => tc == 0x17F,
        _ => false,
    }
}

/// A case-insensitive literal at `p`; the end index when it matches.
fn lit_ci(t: &[u32], p: usize, lit: &str) -> Option<usize> {
    let mut k = p;
    for ch in lit.chars() {
        if !at(t, k).is_some_and(|tc| ci_eq(ch, tc)) {
            return None;
        }
        k += 1;
    }
    Some(k)
}

/// The match of `BYPASS` that starts at `p`, as an end index.
fn bypass_at(t: &[u32], p: usize) -> Option<usize> {
    if let Some(e) = lit_ci(t, p, "bypassPermissions") {
        return Some(e);
    }
    for head in ["--permission-mode", "defaultMode"] {
        if let Some(e) = lit_ci(t, p, head) {
            let mut j = e;
            while at(t, j).is_some_and(|c| !is_word(c)) {
                j += 1;
            }
            if j > e {
                if let Some(end) = lit_ci(t, j, "bypass") {
                    return Some(end);
                }
            }
        }
    }
    if let Some(e) = lit_ci(t, p, "dangerously-skip") {
        return Some(e);
    }
    if let Some(e) = lit_ci(t, p, "--") {
        if let Some(e2) = lit_ci(t, e, "allow-").and_then(|a| lit_ci(t, a, "dangerously")) {
            return Some(e2);
        }
        if let Some(e2) = lit_ci(t, e, "dangerously") {
            return Some(e2);
        }
    }
    lit_ci(t, p, "skipDangerousModePermissionPrompt")
}

/// `BYPASS.search(t)` from index `from`: the leftmost match as (start, end).
fn bypass_search_from(t: &[u32], from: usize) -> Option<(usize, usize)> {
    (from..t.len()).find_map(|p| bypass_at(t, p).map(|e| (p, e)))
}

fn bypass_search(t: &[u32]) -> Option<Text> {
    bypass_search_from(t, 0).map(|(a, b)| slice(t, a, b).to_vec())
}

/// `NAMES_CLAUDE.search(cmd)` (Windows: `NAMES_CLAUDE_NT`): `claude` not glued to a word, dot or dash, or `claude_agent_sdk`. On Windows the name is case-insensitive, may carry one of `.exe .cmd .bat .com .ps1`,
/// and a backslash after it also glues it to a folder name.
fn names_claude(cmd: &[u32], os: Os) -> bool {
    if contains(cmd, "claude_agent_sdk") {
        return true;
    }
    let bad_before = |c: u32| is_word(c) || c == cp('.') || c == cp('-');
    if os == Os::Windows {
        let bad_after = |c: u32| bad_before(c) || c == cp('/') || c == cp('\\');
        return (0..cmd.len()).any(|i| {
            let Some(e) = lit_ci(cmd, i, "claude") else {
                return false;
            };
            if i > 0 && at(cmd, i - 1).is_some_and(bad_before) {
                return false;
            }
            // the optional extension is tried first and, when what follows it is glued, dropped (the regex backtracks)
            let clear = |end: usize| !at(cmd, end).is_some_and(bad_after);
            [".exe", ".cmd", ".bat", ".com", ".ps1"].iter().any(|x| lit_ci(cmd, e, x).is_some_and(clear)) || clear(e)
        });
    }
    let bad_after = |c: u32| bad_before(c) || c == cp('/');
    (0..cmd.len()).any(|i| {
        starts_at(cmd, i, "claude") && !(i > 0 && at(cmd, i - 1).is_some_and(bad_before)) && !at(cmd, i + 6).is_some_and(bad_after)
    })
}

fn boundary(t: &[u32], i: usize) -> bool {
    let before = i > 0 && at(t, i - 1).is_some_and(is_word);
    let after = at(t, i).is_some_and(is_word);
    before != after
}

/// `INTERP.search(cmd)` (Windows: `INTERP_NT`, case-insensitive): `\b(?:python[\d.]*|node|ruby|perl|php|osascript|deno|bun)\b`.
fn interp_search(cmd: &[u32], os: Os) -> bool {
    let lit = |i: usize, w: &str| -> Option<usize> {
        if os == Os::Windows { lit_ci(cmd, i, w) } else { starts_at(cmd, i, w).then(|| i + w.chars().count()) }
    };
    (0..cmd.len()).any(|i| {
        if !boundary(cmd, i) {
            return false;
        }
        if let Some(from) = lit(i, "python") {
            let mut e = from;
            while at(cmd, e).is_some_and(|c| is_digit(c) || c == cp('.')) {
                e += 1;
            }
            // greedy with backtracking: the longest run first, then shorter ones
            if (from..=e).rev().any(|end| boundary(cmd, end)) {
                return true;
            }
        }
        ["node", "ruby", "perl", "php", "osascript", "deno", "bun"].iter().any(|w| lit(i, w).is_some_and(|end| boundary(cmd, end)))
    })
}

fn skip_space(t: &[u32], mut j: usize) -> usize {
    while at(t, j).is_some_and(is_space) {
        j += 1;
    }
    j
}

fn is_wax(c: u32) -> bool {
    c == cp('w') || c == cp('a') || c == cp('x')
}

/// `WRITEISH.search(cmd)`.
fn writeish(cmd: &[u32]) -> bool {
    (0..cmd.len()).any(|i| {
        let word_start = !(i > 0 && at(cmd, i - 1).is_some_and(is_word));
        // `\bwrite`, `writeFile`
        if (word_start && starts_at(cmd, i, "write")) || starts_at(cmd, i, "writeFile") || starts_at(cmd, i, ".dump(")
        {
            return true;
        }
        // `mode\s*=\s*['"][wax]`
        if starts_at(cmd, i, "mode") {
            let j = skip_space(cmd, i + 4);
            if at(cmd, j) == Some(cp('=')) {
                let j = skip_space(cmd, j + 1);
                if at(cmd, j).is_some_and(quote_chars) && at(cmd, j + 1).is_some_and(is_wax) {
                    return true;
                }
            }
        }
        // `,\s*['"][wax]\+?b?['"]`
        if at(cmd, i) == Some(cp(',')) {
            let j = skip_space(cmd, i + 1);
            if at(cmd, j).is_some_and(quote_chars) && at(cmd, j + 1).is_some_and(is_wax) {
                let mut k = j + 2;
                if at(cmd, k) == Some(cp('+')) {
                    k += 1;
                }
                if at(cmd, k) == Some(cp('b')) {
                    k += 1;
                }
                if at(cmd, k).is_some_and(quote_chars) {
                    return true;
                }
            }
        }
        // `\bopen\s*\([^)]*['"][wax]`
        if word_start && starts_at(cmd, i, "open") {
            let j = skip_space(cmd, i + 4);
            if at(cmd, j) == Some(cp('(')) {
                let mut k = j + 1;
                while let Some(c) = at(cmd, k) {
                    if c == cp(')') {
                        break;
                    }
                    if quote_chars(c) && at(cmd, k + 1).is_some_and(is_wax) {
                        return true;
                    }
                    k += 1;
                }
            }
        }
        false
    })
}

/// The match of `managed-settings[^\s'"),]*|settings(?:\.local)?\.json` at `p`, as an end index (Windows: case-insensitive).
fn settings_literal_at(t: &[u32], p: usize, os: Os) -> Option<usize> {
    let lit = |q: usize, w: &str| -> Option<usize> {
        if os == Os::Windows { lit_ci(t, q, w) } else { starts_at(t, q, w).then(|| q + w.chars().count()) }
    };
    if let Some(mut e) = lit(p, "managed-settings") {
        while at(t, e).is_some_and(|c| !is_space(c) && ![cp('\''), cp('"'), cp(')'), cp(',')].contains(&c)) {
            e += 1;
        }
        return Some(e);
    }
    if let Some(q) = lit(p, "settings") {
        if let Some(end) = lit(q, ".local").and_then(|a| lit(a, ".json")) {
            return Some(end);
        }
        if let Some(end) = lit(q, ".json") {
            return Some(end);
        }
    }
    None
}

/// `re.findall(r"[^\s'\"=,()]*(?:managed-settings[^\s'\"),]*|settings(?:\.local)?\.json)", cmd)`.
///
/// The greedy prefix backtracks from its longest length, so at a start `s` the match uses the largest `p` in the run `[s, e]` where a literal matches.
fn find_names(cmd: &[u32], os: Os) -> Vec<Text> {
    let in_run = |c: u32| !is_space(c) && ![cp('\''), cp('"'), cp('='), cp(','), cp('('), cp(')')].contains(&c);
    let mut out = Vec::new();
    let mut s = 0;
    // the current run: its end and the last literal in it (position, end of the match)
    let mut run: Option<(usize, Option<(usize, usize)>)> = None;
    while s < cmd.len() {
        let (e, found) = match run {
            Some((e, f)) if s <= e => (e, f),
            _ => {
                let mut e = s;
                while at(cmd, e).is_some_and(in_run) {
                    e += 1;
                }
                let f = (s..=e).rev().find_map(|p| settings_literal_at(cmd, p, os).map(|end| (p, end)));
                run = Some((e, f));
                (e, f)
            }
        };
        match found {
            Some((p, end)) if s <= p => {
                out.push(slice(cmd, s, end).to_vec());
                s = end;
            }
            _ => s = e + 1,
        }
    }
    out
}

/// The targets of the redirections of `seg`: `(?:>>?|>\|)\s*(['"]?)([^\s;&|<>'"]+)\1`, group 2 of each match.
fn redirect_targets(seg: &[u32]) -> Vec<Text> {
    let plain = |c: u32| !is_space(c) && ![cp(';'), cp('&'), cp('|'), cp('<'), cp('>'), cp('\''), cp('"')].contains(&c);
    // after the operator: spaces, an optional quote, a run of plain characters, the same quote; the end index and the target
    let tail = |j: usize| -> Option<(usize, Text)> {
        let j = skip_space(seg, j);
        let q = at(seg, j).filter(|&c| quote_chars(c));
        let start = j + usize::from(q.is_some());
        let mut e = start;
        while at(seg, e).is_some_and(plain) {
            e += 1;
        }
        if e == start {
            return None;
        }
        match q {
            Some(qc) if at(seg, e) != Some(qc) => None,
            Some(_) => Some((e + 1, slice(seg, start, e).to_vec())),
            None => Some((e, slice(seg, start, e).to_vec())),
        }
    };
    let mut out = Vec::new();
    let mut i = 0;
    while i < seg.len() {
        let mut hit = None;
        if at(seg, i) == Some(cp('>')) {
            if at(seg, i + 1) == Some(cp('>')) {
                hit = tail(i + 2);
            }
            if hit.is_none() {
                hit = tail(i + 1);
            }
            if hit.is_none() && at(seg, i + 1) == Some(cp('|')) {
                hit = tail(i + 2);
            }
        }
        if let Some((end, target)) = hit {
            out.push(target);
            i = end;
        } else {
            i += 1;
        }
    }
    out
}

// ---------------------------------------------------------------------------------------------------------------------------------------------------------
// the rules

/// `_nt_test`: the settings-file test on the resolved components of a Windows path, names case-folded.
fn nt_test(comps: &[Text]) -> bool {
    let base = comps.last().map_or_else(Text::new, |c| nt_fold(c));
    let parent = if comps.len() > 1 { comps.get(comps.len() - 2).map_or_else(Text::new, |c| nt_fold(c)) } else { Text::new() };
    if starts(&base, "managed-settings") || eq(&parent, "managed-settings.d") {
        return true;
    }
    (eq(&base, "settings.json") || eq(&base, "settings.local.json")) && eq(&parent, ".claude")
}

/// `_nt_protected`.
fn nt_protected(path: &[u32], cwd: &Cwd, mut unknown_dir: bool, keep: bool) -> Res<bool> {
    let p = expanduser_for(path, Os::Windows);
    let r = nt_root(&p);
    if !r.rooted {
        if !r.drive.is_empty() {
            unknown_dir = true; // `C:x`: the working directory of that drive is not known
        }
        if unknown_dir && !has_char(&r.rest, '\\') {
            let comps = nt_walk(Vec::new(), false, &r.rest, keep);
            if comps.last().is_some_and(|c| {
                let f = nt_fold(c);
                eq(&f, "settings.json") || eq(&f, "settings.local.json")
            }) {
                return Ok(true);
            }
        }
    }
    let (_, _, comps) = nt_resolve(cwd, &p, keep)?;
    Ok(nt_test(&comps))
}

/// `protected`: true when `path` names a Claude Code settings file (`keep`: the reading of a Windows name made of dots and spaces that keeps it).
fn protected(path: &[u32], cwd: &Cwd, unknown_dir: bool, os: Os, keep: bool) -> Res<bool> {
    if os == Os::Windows {
        return nt_protected(path, cwd, unknown_dir, keep);
    }
    let mut p = expanduser(path);
    if !isabs(&p) {
        if !has_char(&p, '/') && unknown_dir && (eq(basename(&p), "settings.json") || eq(basename(&p), "settings.local.json")) {
            return Ok(true);
        }
        p = join(cwd, &p)?;
    }
    let p = normpath(&p);
    let base = basename(&p);
    let parent = basename(dirname(&p));
    if starts(base, "managed-settings") || eq(parent, "managed-settings.d") {
        return Ok(true);
    }
    Ok((eq(base, "settings.json") || eq(base, "settings.local.json")) && eq(parent, ".claude"))
}

/// `g1` (v3): the bypass words, only when the command also names `claude` or `claude_agent_sdk`.
fn g1(cmd: &[u32], segs: &[Seg], os: Os) -> Option<Hit> {
    if !names_claude(cmd, os) && !segs.iter().any(|(sg, _)| names_claude(sg, os)) {
        return None;
    }
    let carries = |s: &Text, toks: &Vec<Text>| bypass_search(s).is_some() || bypass_search(&join_with(toks, ' ')).is_some();
    let (seg, _) = segs.iter().find(|(s, toks)| carries(s, toks) && !inert(toks, os))?;
    let m = bypass_search(seg).or_else(|| bypass_search(&join_with(&words(seg), ' ')));
    let what = m.unwrap_or_else(|| text("a bypass flag"));
    hit("G1", cat(&[&text("the command carries `"), &what, &text("`")]))
}

/// `_config_dir`: `t` is a `CLAUDE_CONFIG_DIR=` assignment (Windows: environment names are case-insensitive, so `claude_config_dir=` too).
fn config_dir(t: &[u32], os: Os) -> bool {
    if os == Os::Windows {
        return eq(&nt_fold(slice(t, 0, 18)), "claude_config_dir=");
    }
    starts(t, "CLAUDE_CONFIG_DIR=")
}

/// `g2`: a `claude` child that leaves the user's settings and hooks, and any `CLAUDE_CONFIG_DIR=` assignment.
fn g2(segs: &[Seg], os: Os) -> Option<Hit> {
    for (_, toks) in segs {
        let (k, assigns) = program(toks, os);
        if assigns.iter().chain(toks.iter()).any(|t| config_dir(t, os)) {
            return hit("G2", text("the command sets CLAUDE_CONFIG_DIR, which leaves the user's settings and hooks behind"));
        }
        let Some(first) = toks.get(k) else {
            continue;
        };
        if !eq(&prog_name(first, os), "claude") {
            continue;
        }
        let args = slice_toks(toks, k + 1);
        for v in flag_value(args, "--setting-sources") {
            let ok = split_on(&v, ',').iter().any(|x| eq(strip(x), "user"));
            if !ok {
                return hit("G2", cat(&[&text("the child `claude` is started with `--setting-sources "), &v, &text("`, which leaves out the user's settings")]));
            }
        }
        for f in ["--bare", "--safe-mode"] {
            if args.iter().any(|t| eq(t, f)) {
                return hit("G2", text(&format!("the child `claude` is started with `{f}`, which skips the user's hooks")));
            }
        }
        for v in flag_value(args, "--settings") {
            if contains(&v, "disableAllHooks") {
                return hit("G2", text("the child `claude` is started with settings that disable all hooks"));
            }
        }
    }
    None
}

fn starts_any(t: &[u32], prefixes: &[&str]) -> bool {
    prefixes.iter().any(|p| starts(t, p))
}

fn non_flags(args: &[Text]) -> Vec<Text> {
    args.iter().filter(|t| !starts(t, "-")).cloned().collect()
}

/// `slashed`: the simple commands read with every backslash a slash (a Windows path typed without quotes loses its backslashes when the shell reads the word).
fn slashed(segs: &[Seg]) -> Vec<Seg> {
    segs.iter()
        .map(|(sg, _)| {
            let t: Text = sg.iter().map(|&c| if c == cp('\\') { cp('/') } else { c }).collect();
            let toks = words(&t);
            (t, toks)
        })
        .collect()
}

/// `g3_bash`: a Bash command that writes a Claude Code settings file. On Windows the commands are read twice: as written, then with every backslash a slash.
fn g3_bash(cmd: &[u32], segs: &[Seg], cwd: &Cwd, os: Os) -> Res<Option<Hit>> {
    let first = g3_bash_once(cmd, segs, cwd, os, true, false)?;
    if first.is_some() || os != Os::Windows {
        return Ok(first);
    }
    // Windows: the text as written with the other reading of a dots-and-spaces name, then with every backslash a slash under both readings
    if let Some(h) = g3_bash_once(cmd, segs, cwd, os, true, true)? {
        return Ok(Some(h));
    }
    let sl = slashed(segs);
    if let Some(h) = g3_bash_once(cmd, &sl, cwd, os, false, false)? {
        return Ok(Some(h));
    }
    g3_bash_once(cmd, &sl, cwd, os, false, true)
}

/// `_g3_bash`: one reading; the script check (`script`) is made on the first only.
fn g3_bash_once(cmd: &[u32], segs: &[Seg], cwd: &Cwd, os: Os, script: bool, keep: bool) -> Res<Option<Hit>> {
    let mut unknown = false;
    let mut cur = cwd.clone();
    for (seg, toks) in segs {
        let (k, _) = program(toks, os);
        let prog: Text = toks.get(k).map_or_else(Text::new, |t| prog_name(t, os));
        let prog = prog.as_slice();
        if (eq(prog, "cd") || eq(prog, "pushd")) && k + 1 < toks.len() {
            let t = expanduser_for(toks.get(k + 1).map_or(&[][..], |x| x), os);
            if has_char(&t, '$') || has_char(&t, '`') || eq(&t, "-") {
                unknown = true;
            } else if os == Os::Windows {
                let (d, r, c) = nt_resolve(&cur, &t, keep)?;
                cur = Cwd::Str(nt_str(&d, r, &c));
            } else {
                let base = if isabs(&t) { t } else { join(&cur, &t)? };
                cur = Cwd::Str(normpath(&base));
            }
            continue;
        }
        let mut targets = redirect_targets(seg);
        let args: &[Text] = if k < toks.len() { slice_toks(toks, k + 1) } else { &[] };
        let sed_in_place = (eq(prog, "sed") || eq(prog, "perl") || eq(prog, "awk") || eq(prog, "gawk") || eq(prog, "ruby"))
            && args.iter().any(|t| starts_any(t, &["-i", "--in-place", "-pi", "-ni"]) || eq(t, "inplace"));
        if eq(prog, "tee") || sed_in_place {
            targets.extend(non_flags(args));
        } else if eq(prog, "cp") {
            // only the destination is written: the last plain argument, or the value of -t / --target-directory
            let plain = non_flags(args);
            let mut tdir: Vec<Text> = Vec::new();
            for (j, t) in args.iter().enumerate().take(args.len().saturating_sub(1)) {
                if eq(t, "-t") || eq(t, "--target-directory") {
                    tdir.extend(args.get(j + 1).cloned());
                }
            }
            for t in args {
                if starts(t, "--target-directory=") {
                    tdir.push(slice(t, "--target-directory=".chars().count(), t.len()).to_vec());
                }
            }
            if tdir.is_empty() {
                targets.extend(plain.last().cloned());
            } else {
                targets.extend(tdir);
            }
        } else if ["mv", "install", "ln", "rsync", "rm", "truncate", "unlink", "shred", "chmod", "chown", "touch"].iter().any(|p| eq(prog, p)) {
            targets.extend(non_flags(args));
        } else if eq(prog, "dd") {
            targets.extend(args.iter().filter(|t| starts(t, "of=")).map(|t| slice(t, 3, t.len()).to_vec()));
        }
        for t in targets {
            if protected(&t, &cur, unknown, os, keep)? {
                return Ok(hit("G3", cat(&[&text("the command writes `"), &t, &text("`, a Claude Code settings file")])));
            }
        }
    }
    if !script {
        return Ok(None);
    }
    let nt = os == Os::Windows;
    let first_is_python = segs.iter().any(|(_, ts)| {
        ts.first().is_some_and(|t| {
            let n = prog_name(t, os);
            eq(&n, "python") || eq(&n, "python3") || (nt && (eq(&n, "py") || eq(&n, "pythonw")))
        })
    });
    if interp_search(cmd, os) || first_is_python {
        let names = find_names(cmd, os);
        if !names.is_empty() && writeish(cmd) {
            for n in &names {
                if protected(n, &cur, true, os, keep)? || ((has_char(n, '/') || (nt && has_char(n, '\\'))) && protected(n, cwd, false, os, keep)?) {
                    return Ok(hit("G3", text("a script in the command writes a Claude Code settings file")));
                }
            }
        }
    }
    Ok(None)
}

/// The first truthy of `file_path`, `path`, `notebook_path`, or the empty string.
fn edit_path(inp: &Value) -> Res<Text> {
    for key in ["file_path", "path", "notebook_path"] {
        if let Some(v) = inp.get(key).filter(|v| v.truthy()) {
            return match v {
                Value::Str(s) => Ok(s.clone()),
                _ => Err(Fault::Type),
            };
        }
    }
    Ok(Text::new())
}

/// `g3_edit`: the edit targets a settings file.
fn g3_edit(inp: &Value, cwd: &Cwd, os: Os) -> Res<Option<Hit>> {
    let p = edit_path(inp)?;
    if !p.is_empty() && (protected(&p, cwd, false, os, false)? || (os == Os::Windows && protected(&p, cwd, false, os, true)?)) {
        return Ok(hit("G3", cat(&[&text("the edit targets `"), &p, &text("`, a Claude Code settings file")])));
    }
    Ok(None)
}

/// `str(v or "")` for the values a tool input can hold; floats, arrays and objects are not modelled.
fn py_str(v: Option<&Value>) -> Res<Text> {
    match v {
        None => Ok(Text::new()),
        Some(x) if !x.truthy() => Ok(Text::new()),
        Some(Value::Str(s)) => Ok(s.clone()),
        Some(Value::Bool(_)) => Ok(text("True")),
        Some(Value::Int(s)) => Ok(text(s)),
        Some(_) => Err(Fault::Unsupported),
    }
}

/// `_hits`: the bypass words and the `--setting-sources` values without `user` that a text carries, in order.
fn hits(t: &[u32]) -> Vec<Text> {
    let mut out = Vec::new();
    let mut from = 0;
    while let Some((a, b)) = bypass_search_from(t, from) {
        out.push(slice(t, a, b).to_vec());
        from = b;
    }
    let flag = "--setting-sources";
    let junk = |c: u32| quote_chars(c) || is_space(c) || [cp('='), cp(','), cp('['), cp(']')].contains(&c);
    let letter = |c: u32| char::from_u32(c).is_some_and(|ch| ch.is_ascii_alphabetic() || ch == ',');
    let mut i = 0;
    while let Some(p) = find_from(t, i, flag) {
        let mut j = p + flag.chars().count();
        while at(t, j).is_some_and(junk) {
            j += 1;
        }
        let g0 = j;
        while at(t, j).is_some_and(letter) {
            j += 1;
        }
        let v = slice(t, g0, j);
        if !v.is_empty() && !split_on(v, ',').iter().any(|x| eq(x, "user")) {
            out.push(cat(&[&text("--setting-sources "), v]));
        }
        i = j;
    }
    out
}

/// The lower-cased path ends in one of the script extensions (only ASCII letters matter for these extensions; K and the dotted I cannot produce one).
fn script_ext(p: &[u32]) -> bool {
    let lowered: Text = p.iter().map(|&c| if (0x41..=0x5A).contains(&c) { c + 32 } else if c == 0x212A { cp('k') } else { c }).collect();
    SCRIPT_EXT.iter().any(|e| lowered.len() >= e.len() && starts_at(&lowered, lowered.len() - e.chars().count(), e))
}

/// The folded file name as Windows resolves it ends in one of the script extensions: `X.PY`, `x.py.`, `x.py::$DATA` are scripts.
fn script_ext_nt(p: &[u32]) -> Res<bool> {
    let (_, _, comps) = nt_resolve(&Cwd::Str(Text::new()), p, false)?;
    Ok(comps.last().is_some_and(|c| {
        let f = nt_fold(c);
        SCRIPT_EXT.iter().any(|e| f.len() >= e.len() && starts_at(&f, f.len() - e.chars().count(), e))
    }))
}

/// Reads the file Python's `open(path, errors="replace")` would read; `Ok(None)` for an `OSError`.
fn read_old(cwd: &Cwd, p: &[u32], os: Os) -> Res<Option<Text>> {
    let full = if os == Os::Windows { nt_join(cwd, &expanduser_for(p, os))? } else { join(cwd, &expanduser(p))? };
    let mut bytes: Vec<u8> = Vec::new();
    for &c in &full {
        if let Some(ch) = char::from_u32(c) {
            let mut b = [0u8; 4];
            bytes.extend_from_slice(ch.encode_utf8(&mut b).as_bytes()); // BORROW: UTF-8 bytes of one character
        } else if (0xDC80..=0xDCFF).contains(&c) {
            bytes.push(u8::try_from(c - 0xDC00).unwrap_or(0)); // surrogateescape: the original byte
        } else {
            return Err(Fault::UnicodeEncode);
        }
    }
    if bytes.contains(&0) {
        return Err(Fault::Value);
    }
    let path = crate::platform::path_from_bytes(bytes);
    Ok(std::fs::read(path).ok().map(|raw| text(&String::from_utf8_lossy(&raw))))
}

/// `g4_script`: Write or Edit of a script file that adds the bypass words or a `--setting-sources` value without `user`.
fn g4_script(inp: &Value, cwd: &Cwd, os: Os) -> Res<Option<Hit>> {
    let p = edit_path(inp)?;
    if !(if os == Os::Windows { script_ext_nt(&p)? } else { script_ext(&p) }) {
        return Ok(None);
    }
    let (new, old);
    if inp.get("new_source").is_some() {
        new = hits(&py_str(inp.get("new_source"))?);
        old = Vec::new();
    } else if inp.get("content").is_some() {
        new = hits(&py_str(inp.get("content"))?);
        old = read_old(cwd, &p, os)?.map_or_else(Vec::new, |t| hits(&t));
    } else {
        let mut edits: Vec<&Value> = vec![inp];
        match inp.get("edits") {
            Some(v) if v.truthy() => match v {
                Value::Arr(a) => edits.extend(a.iter().filter(|e| matches!(e, Value::Obj(_)))),
                Value::Str(_) | Value::Obj(_) => {}
                _ => return Err(Fault::Type),
            },
            _ => {}
        }
        let mut n = Vec::new();
        for e in &edits {
            n.extend(hits(&py_str(e.get("new_string"))?));
        }
        let mut o = Vec::new();
        for e in &edits {
            o.extend(hits(&py_str(e.get("old_string"))?));
        }
        new = n;
        old = o;
    }
    if new.len() > old.len() {
        if let Some(h) = new.get(old.len()) {
            return Ok(hit("G4", cat(&[&text("the edit adds `"), h, &text("` to the script `"), &display_name(&p, os), &text("`")])));
        }
    }
    Ok(None)
}

/// The event's `tool_input` as `event.get("tool_input") or {}`.
fn tool_input(event: &Value) -> Value {
    event.get("tool_input").filter(|v| v.truthy()).cloned().unwrap_or(Value::Obj(Vec::new()))
}

/// The event's working directory as `event.get("cwd") or ""`.
fn event_cwd(event: &Value) -> Cwd {
    match event.get("cwd").filter(|v| v.truthy()) {
        None => Cwd::Str(Text::new()),
        Some(Value::Str(s)) => Cwd::Str(s.clone()),
        Some(_) => Cwd::Bad,
    }
}

/// The Bash command as `inp.get("command") or ""`; a truthy non-string raises in `_split` (`len`) or fails to index.
fn command_text(inp: &Value) -> Res<Text> {
    match inp.get("command").filter(|v| v.truthy()) {
        None => Ok(Text::new()),
        Some(Value::Str(s)) => Ok(s.clone()),
        Some(Value::Obj(_)) => Err(Fault::Key),
        Some(Value::Int(_) | Value::Float(_) | Value::Bool(_)) => Err(Fault::Type),
        Some(_) => Err(Fault::Unsupported),
    }
}

/// `decide`: the denial for an event, or `None`.
fn decide(event: &Value, os: Os) -> Res<Option<Hit>> {
    if !matches!(event, Value::Obj(_)) {
        return Err(Fault::Attribute);
    }
    let inp = tool_input(event);
    let cwd = event_cwd(event);
    let tool = match event.get("tool_name") {
        Some(Value::Str(s)) => string(s),
        _ => String::new(),
    };
    if tool == "Bash" {
        if !matches!(inp, Value::Obj(_)) {
            return Err(Fault::Attribute);
        }
        let cmd = command_text(&inp)?;
        let mut work = 0;
        let Ok(segs) = expand(&cmd, 0, &mut work, os) else {
            return Ok(hit("G?", text("the command has too many command substitutions to be checked")));
        };
        if let Some(h) = g1(&cmd, &segs, os).or_else(|| g2(&segs, os)).or_else(|| if os == Os::Windows { g2(&slashed(&segs), os) } else { None }) {
            return Ok(Some(h));
        }
        return g3_bash(&cmd, &segs, &cwd, os);
    }
    if ["Write", "Edit", "MultiEdit", "NotebookEdit"].contains(&tool.as_str()) {
        // BORROW: explicit .as_str() for the slice-contains lookup
        if !matches!(inp, Value::Obj(_)) {
            return Err(Fault::Attribute);
        }
        if let Some(h) = g3_edit(&inp, &cwd, os)? {
            return Ok(Some(h));
        }
        return g4_script(&inp, &cwd, os);
    }
    Ok(None)
}

/// The answer of `run`: the stdout text (empty to allow) and the line for the optional log.
pub(crate) struct Answer {
    /// What goes to standard output: empty for allow, one JSON object for deny.
    pub(crate) stdout: String,
    /// The line `run` appends to `MURMURATION_GUARD_LOG`, without the newline.
    pub(crate) log_line: String,
}

const MSG_TAIL: &str = ". Skipping or loosening Claude Code's permission layer is the user's decision, not the lab's. \
Do not run it in another form or through a script; tell the user what you wanted and wait for their yes in their own message.";

/// `str(ti.get("command") or ti.get("file_path") or "")[:120]` for the log.
fn what_text(event: &Value) -> Text {
    let ti = tool_input(event);
    let pick = ["command", "file_path"].iter().find_map(|k| ti.get(k).filter(|v| v.truthy()));
    let full = match pick {
        None => Text::new(),
        Some(Value::Str(s)) => s.clone(),
        Some(v) => {
            let mut s = String::new();
            json::dump(v, &mut s);
            text(&s)
        }
    };
    slice(&full, 0, 120).to_vec()
}

/// `run`: the decision for the raw stdin text, in the flavour of the OS this binary was built for. Never fails: any fault becomes a deny.
pub(crate) fn run(raw: &str) -> Answer {
    run_os(raw, platform::host())
}

/// `run` for the paths and program names of `os` (the tests run both on any host).
pub(crate) fn run_os(raw: &str, os: Os) -> Answer {
    let parsed = json::loads(raw);
    let outcome = parsed.as_ref().map_err(|e| *e).and_then(|event| {
        let h = decide(event, os)?;
        if !matches!(tool_input(event), Value::Obj(_)) {
            return Err(Fault::Attribute); // `ti.get` on a non-dict in `run`
        }
        Ok((h, event))
    });
    let (hit, tool_json, what) = match outcome {
        Ok((h, event)) => {
            let mut tj = String::new();
            json::dump(event.get("tool_name").unwrap_or(&Value::Null), &mut tj);
            (h, tj, what_text(event))
        }
        Err(f) => (
            Some(Hit { group: "G?", why: text(&format!("the guard could not read the event ({})", f.name())) }),
            String::from("null"),
            Text::new(),
        ),
    };
    let mut log = String::from("{\"tool\": ");
    log.push_str(&tool_json);
    log.push_str(", \"what\": ");
    json::dump_str(&what, &mut log);
    log.push_str(", \"decision\": ");
    log.push_str(if hit.is_some() { "\"deny\"" } else { "\"allow\"" });
    log.push_str(", \"group\": ");
    match &hit {
        Some(h) => json::dump_str(&text(h.group), &mut log),
        None => log.push_str("null"),
    }
    log.push('}');
    let stdout = hit.map_or_else(String::new, |h| {
        let reason = cat(&[&text("permission_guard ("), &text(h.group), &text("): "), &h.why, &text(MSG_TAIL)]);
        let mut s = String::from("{\"hookSpecificOutput\": {\"hookEventName\": \"PreToolUse\", \"permissionDecision\": \"deny\", \"permissionDecisionReason\": ");
        json::dump_str(&reason, &mut s);
        s.push_str("}}");
        s
    });
    Answer { stdout, log_line: log }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The cases of `windows_paths.json`; the file is read here, at test time, from the manifest directory, and is never embedded in the binary.
    const WINDOWS_COUNT: usize = 106;

    fn windows_cases() -> Vec<Value> {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("..").join("scripts").join("fixtures").join("guard_lists").join("windows_paths.json");
        let raw = std::fs::read(&path).unwrap_or_else(|e| panic!("cannot read {}: {e}", path.display()));
        let parsed = json::loads(&String::from_utf8(raw).expect("windows_paths.json is UTF-8")).expect("windows_paths.json is JSON");
        match parsed {
            Value::Arr(cases) => cases,
            _ => panic!("windows_paths.json is not a list"),
        }
    }

    fn field(c: &Value, key: &str) -> Text {
        match c.get(key) {
            Some(Value::Str(s)) => s.clone(),
            _ => panic!("case without the string `{key}`"),
        }
    }

    fn event(c: &Value) -> Value {
        let tool_input = match c.get("input") {
            Some(v) => v.clone(),
            None => Value::Obj(vec![(text("command"), Value::Str(field(c, "command")))]),
        };
        Value::Obj(vec![(text("tool_name"), Value::Str(field(c, "tool"))), (text("tool_input"), tool_input), (text("cwd"), Value::Str(field(c, "cwd")))])
    }

    fn group_of(c: &Value, os: Os) -> String {
        match decide(&event(c), os) {
            Ok(Some(h)) => h.group.to_string(),
            Ok(None) => "allow".to_string(),
            Err(f) => format!("fault {}", f.name()),
        }
    }

    fn check_all(os: Os, column: &str) {
        let cases = windows_cases();
        assert_eq!(cases.len(), WINDOWS_COUNT, "windows_paths.json has a pinned count");
        let wrong: Vec<String> = cases
            .iter()
            .filter_map(|c| {
                let (want, got) = (string(&field(c, column)), group_of(c, os));
                (want != got).then(|| format!("{}: want {want}, got {got}", string(&field(c, "id"))))
            })
            .collect();
        assert!(wrong.is_empty(), "{column} decisions differ from the list: {wrong:?}");
    }

    #[test]
    fn windows_list_under_the_nt_flavour() {
        check_all(Os::Windows, "nt");
    }

    #[test]
    fn windows_list_under_the_posix_flavour() {
        check_all(Os::Unix, "posix");
    }

    #[test]
    fn run_follows_the_host_flavour() {
        let raw = "{\"tool_name\": \"Write\", \"tool_input\": {\"file_path\": \".claude\\\\settings.json\", \"content\": \"\"}, \"cwd\": \"C:\\\\proj\"}";
        assert_eq!(run(raw).stdout.is_empty(), !cfg!(windows));
        assert!(run_os(raw, Os::Windows).stdout.contains("permission_guard (G3)"));
        assert!(run_os(raw, Os::Unix).stdout.is_empty());
    }

    #[test]
    fn program_names() {
        let n = |s: &str, os: Os| string(&prog_name(&text(s), os));
        assert_eq!(n("C:\\Tools\\CLAUDE.EXE", Os::Windows), "claude");
        assert_eq!(n("C:/x/claude.cmd", Os::Windows), "claude");
        assert_eq!(n("claude.exe.bak", Os::Windows), "claude.exe.bak");
        assert_eq!(n(".exe", Os::Windows), ".exe");
        assert_eq!(n("C:claude.", Os::Windows), "claude");
        assert_eq!(n("C:\\Tools\\CLAUDE.EXE", Os::Unix), "C:\\Tools\\CLAUDE.EXE"); // a backslash is a filename character
        assert_eq!(n("/usr/bin/claude", Os::Unix), "claude");
    }

    #[test]
    fn nt_names_claude_is_case_folded_and_takes_an_extension() {
        let yes = |s: &str| names_claude(&text(s), Os::Windows);
        assert!(yes("CLAUDE -p x"));
        assert!(yes("C:\\a\\claude.cmd -p x"));
        assert!(yes("claude.EXE"));
        assert!(!yes("claude.exe.bak"));
        assert!(!yes("myclaude.exe"));
        assert!(!yes("C:\\claude\\x"));
        assert!(!names_claude(&text("CLAUDE -p x"), Os::Unix));
    }
}
