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
const WRAP: &[&str] = &["env", "command", "nohup", "exec", "time", "sudo", "nice", "ionice", "stdbuf", "xargs", "timeout", "gtimeout", "setsid", "caffeinate", "busybox"];
const KEYWORDS: &[&str] = &["if", "then", "else", "elif", "do", "while", "until", "!", "{", "}", "fi", "done"];
const SHELLS: &[&str] = &["sh", "bash", "zsh", "dash", "ksh", "ash", "mksh", "yash", "posh", "rbash", "fish", "csh", "tcsh"];
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

/// `_split`: one pass of the splitter; the segments (stripped, non-empty) and the quote left open at the end. With `clobber` the `|` of a `>|` is not a cut (the reading of `>|` as one operator).
fn split_pass(cmd: &[u32], quotes: bool, clobber: bool) -> (Vec<Text>, Option<u32>) {
    let (sq, dq, bs, bt, amp, gt) = (cp('\''), cp('"'), cp('\\'), cp('`'), cp('&'), cp('>'));
    let mut segs: Vec<Text> = Vec::new();
    let mut cur = Text::new();
    let mut q: Option<u32> = None;
    let mut after_gt = false; // the previous character was a plain `>` (not escaped, not quoted)
    let mut i = 0;
    while let Some(c) = at(cmd, i) {
        let prev_gt = std::mem::take(&mut after_gt);
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
        } else if clobber && c == cp('|') && prev_gt {
            cur.push(c);
        } else if [cp('\n'), cp(';'), cp('|'), cp('('), cp(')'), bt].contains(&c)
            || (c == amp && !((i > 0 && at(cmd, i - 1) == Some(gt)) || at(cmd, i + 1) == Some(gt)))
        {
            segs.push(std::mem::take(&mut cur));
        } else {
            cur.push(c);
            after_gt = c == gt;
        }
        i += 1;
    }
    segs.push(cur);
    let segs = segs.iter().map(|s| strip(s).to_vec()).filter(|s| !s.is_empty()).collect();
    (segs, q)
}

/// `split_segments`; `clobber` as in `split_pass` (`expand` passes it on).
fn split_segments(cmd: &[u32], clobber: bool) -> Vec<Text> {
    let (segs, q) = split_pass(cmd, true, clobber);
    if q.is_some() { split_pass(cmd, false, clobber).0 } else { segs }
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

const WORK: usize = 2_000_000;
/// `TEXT_COST`: what each text that `mask` reads costs besides its length.
const TEXT_COST: usize = 400;

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

/// `_SQUASH`: the characters of the inside of a substitution that `mask` turns to `,` when it keeps the inside (`\s;&|<>()'"` + backtick + `\$*?[`).
fn squash_char(c: u32) -> bool {
    is_space(c) || ";&|<>()'\"`\\$*?[".chars().any(|x| cp(x) == c)
}

/// `_mask`: the text with every outermost matched substitution replaced by one word, and the insides that were replaced. `keep` (the second pass, leaf posix_gaps): the word is else `SUBST_` and the inside with blanks, operators, quotes and glob characters turned to `,`,
/// so that a target `$(echo .claude/settings.json)` still shows the name; `claude` only when the inside does not name a settings file as well.
fn mask(s: &[u32], work: &mut usize, os: Os, keep: bool) -> Result<(Text, Vec<Text>), TooComplex> {
    *work += TEXT_COST;
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
        if keep {
            if names_claude(&inner, os) && !names_span(&inner, os) {
                out.extend(text("claude"));
            } else {
                out.extend(text("SUBST_"));
                out.extend(inner.iter().map(|&c| if squash_char(c) { cp(',') } else { c }));
            }
        } else {
            out.extend(text(if names_claude(&inner, os) { "claude" } else { "SUBST" }));
        }
        inners.push(inner);
        prev = en;
    }
    out.extend_from_slice(slice(s, prev, s.len()));
    Ok((out, inners))
}

/// `substitution_texts`: the texts to split in addition to `cmd`; empty when `cmd` has no substitution.
fn substitution_texts(cmd: &[u32], work: &mut usize, os: Os, keep: bool) -> Result<Vec<Text>, TooComplex> {
    if !contains(cmd, "$(") && !has_char(cmd, '`') && !contains(cmd, "<(") && !contains(cmd, ">(") {
        return Ok(Vec::new());
    }
    let mut texts: Vec<Text> = Vec::new();
    let mut queue: std::collections::VecDeque<Text> = std::collections::VecDeque::new();
    queue.push_back(cmd.to_vec());
    while let Some(t) = queue.pop_front() {
        let (m, inners) = mask(&t, work, os, keep)?;
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

/// The options of `expand` that the second pass of leaf posix_gaps changes: `clobber` (`>|` is one operator, see `split_pass`), `ansi` (also read the words of a command whose text holds `$'` or `$"` as bash removes the quotes, and keep the text of a substitution in
/// its word) and `limit` (the depth to which shell strings are followed).
#[derive(Clone, Copy)]
struct Mode {
    clobber: bool,
    ansi: bool,
    limit: usize,
}

/// The first pass: the reading of before the leaf posix_gaps.
const FIRST: Mode = Mode { clobber: false, ansi: false, limit: 3 };

/// `expand`: every simple command of `cmd`: those of the plain splitter first, in order, then those of the command and of each substitution inside it with the substitutions replaced by one word;
/// descends into `sh -c '...'`, `eval '...'` and `env -S '...'` strings to depth `mode.limit` (3 in the first pass); when a string lies deeper, `deep` is set. `decide` makes the `>|` reading in addition to the plain one, never instead of it.
fn expand(cmd: &[u32], depth: usize, work: &mut usize, os: Os, mode: Mode, deep: &mut bool) -> Result<Vec<Seg>, TooComplex> {
    let mut out: Vec<Seg> = Vec::new();
    let mut segs = split_segments(cmd, mode.clobber);
    for t in substitution_texts(cmd, work, os, mode.ansi)? {
        segs.extend(split_segments(&t, mode.clobber));
    }
    for seg in segs {
        let toks0 = words(&seg);
        let mut variants: Vec<Vec<Text>> = vec![toks0.clone()];
        if mode.ansi && (contains(&seg, "$'") || contains(&seg, "$\"")) {
            let more = ansi_words(&seg);
            if more != toks0 {
                variants.push(more);
            }
        }
        for toks in variants {
            out.push((seg.clone(), toks.clone()));
            let sc = scan(&toks, os);
            let k = sc.k;
            let mut subs: Vec<Text> = Vec::new();
            for st in &sc.strings {
                let mut parts: Vec<Text> = vec![st.clone()];
                parts.extend_from_slice(slice_toks(&toks, k));
                subs.push(join_with(&parts, ' '));
            }
            if k < toks.len() {
                let prog_text = prog_name(toks.get(k).map_or(&[][..], |x| x), os);
                let prog = prog_text.as_slice();
                let rest = slice_toks(&toks, k + 1);
                if in_set(prog, SHELLS) || (mode.ansi && var_word(toks.get(k).map_or(&[][..], |x| x))) {
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
                            subs.push(arg.clone());
                        }
                    }
                } else if eq(prog, "eval") {
                    subs.push(join_with(rest, ' '));
                }
                if mode.ansi {
                    // second pass: the string as the shell gets it from a double-quoted word, where `\$` and a backslash before a backtick are only escapes of the word
                    let more: Vec<Text> = subs.iter().map(|st| dq_unescape(st)).filter(|u| !subs.contains(u)).collect();
                    subs.extend(more);
                }
            }
            if depth < mode.limit {
                for st in subs {
                    out.extend(expand(&st, depth + 1, work, os, mode, deep)?);
                }
            } else if !subs.is_empty() {
                *deep = true;
            }
        }
    }
    Ok(out)
}

/// `_VAR_WORD.fullmatch(t)`: `t` is one variable, `$NAME` or `${NAME}`.
fn var_word(t: &[u32]) -> bool {
    if at(t, 0) != Some(cp('$')) {
        return false;
    }
    let body = slice(t, 1, t.len());
    let word = |b: &[u32]| !b.is_empty() && b.iter().all(|&c| is_word(c));
    if at(body, 0) == Some(cp('{')) && at(body, body.len().wrapping_sub(1)) == Some(cp('}')) && body.len() >= 2 {
        return word(slice(body, 1, body.len() - 1));
    }
    word(body)
}

/// `_SHELL_VAR.fullmatch(t)`: the word is a variable that names a shell (`$SHELL`, `${SHELL}`, `$0`, `$BASH`, ...).
fn shell_var(t: &[u32]) -> bool {
    if at(t, 0) != Some(cp('$')) {
        return false;
    }
    let body = slice(t, 1, t.len());
    let named = |b: &[u32]| ["0", "SHELL", "BASH", "ZSH", "SH", "DASH", "KSH"].iter().any(|n| eq(b, n));
    if at(body, 0) == Some(cp('{')) && body.len() >= 2 && at(body, body.len() - 1) == Some(cp('}')) {
        return named(slice(body, 1, body.len() - 1));
    }
    named(body)
}

/// `_dq_unescape`: the text with the backslash removed in front of a `$` or a backtick (what bash does in a double-quoted word, and shlex does not).
fn dq_unescape(st: &[u32]) -> Text {
    let mut out: Text = Text::with_capacity(st.len());
    let mut i = 0;
    while i < st.len() {
        let c = at(st, i).unwrap_or(0);
        if c == cp('\\') && at(st, i + 1).is_some_and(|x| x == cp('$') || x == cp('`')) {
            out.push(at(st, i + 1).unwrap_or(0));
            i += 2;
        } else {
            out.push(c);
            i += 1;
        }
    }
    out
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
// the quote-aware reading of the redirections (leaf posix_redirects): `_ANSI_ESC`, `_ansi_c`, `_redirect_word`, `_quote_end`, `_scan_redirects`, `redirect_targets` of the Python file

/// `_ANSI_ESC[d]`: the code point a one-character `$'...'` escape stands for.
fn ansi_simple(d: u32) -> Option<u32> {
    let ch = char::from_u32(d)?;
    Some(match ch {
        'a' => 0x07,
        'b' => 0x08,
        'e' | 'E' => 0x1B,
        'f' => 0x0C,
        'n' => 0x0A,
        'r' => 0x0D,
        't' => 0x09,
        'v' => 0x0B,
        '\\' | '\'' | '"' | '?' => d,
        _ => return None,
    })
}

/// The digit of `radix` (8 or 16, ASCII only) at `s[j]`.
fn digit_at(s: &[u32], j: usize, radix: u32) -> Option<u32> {
    at(s, j).and_then(char::from_u32).and_then(|ch| ch.to_digit(radix))
}

/// `_ansi_c`: `start` is the first character after `$'`; the text the shell makes of the string, the index after its closing quote and whether the quote was closed. An unknown escape keeps its backslash, a value that is not a code point
/// keeps its text, and a NUL ends the text (as it ends a C string).
fn ansi_c(s: &[u32], start: usize) -> (Text, usize, bool) {
    let (sq, bs) = (cp('\''), cp('\\'));
    let n = s.len();
    let (mut out, mut i, mut cut) = (Text::new(), start, false);
    while let Some(c) = at(s, i) {
        if c == sq {
            return (out, i + 1, true);
        }
        let mut piece: Text = vec![c];
        let mut val: Option<u32> = None;
        i += 1;
        if c == bs {
            if let Some(d) = at(s, i) {
                if let Some(e) = ansi_simple(d) {
                    piece = vec![e];
                    i += 1;
                } else if digit_at(s, i, 8).is_some() {
                    let (mut j, mut v) = (i, 0_u32);
                    while j < i + 3 {
                        let Some(g) = digit_at(s, j, 8) else {
                            break;
                        };
                        v = v * 8 + g;
                        j += 1;
                    }
                    val = Some(v & 255);
                    i = j;
                } else if d == cp('x') || d == cp('u') || d == cp('U') {
                    let top = i + 1 + if d == cp('x') { 2 } else if d == cp('u') { 4 } else { 8 };
                    let (mut j, mut v) = (i + 1, 0_u64);
                    while j < top {
                        let Some(g) = digit_at(s, j, 16) else {
                            break;
                        };
                        v = v * 16 + u64::from(g);
                        j += 1;
                    }
                    match u32::try_from(v) {
                        Ok(code) if j > i + 1 && code <= 0x0010_FFFF => {
                            val = Some(code);
                            i = j;
                        }
                        _ => {
                            piece = vec![bs, d];
                            i += 1;
                        }
                    }
                } else if d == cp('c') && i + 1 < n {
                    let x = at(s, i + 1).unwrap_or(0);
                    val = Some(if x == cp('?') { 0x7F } else { x & 0x1F });
                    i += 2;
                } else {
                    piece = vec![bs, d];
                    i += 1;
                }
            }
        }
        if let Some(v) = val {
            if v == 0 {
                cut = true;
            } else {
                piece = vec![v];
            }
        }
        if !cut {
            out.extend(piece);
        }
    }
    (out, n, false)
}

/// The characters that end a redirect target word: a blank, a newline, or one of `;&|<>()`.
const REDIRECT_STOP: &str = " \t\n;&|<>()";

/// `_redirect_word`: the shell word at `s[start..]` with its quotes removed as bash removes them (`'...'`, `"..."` with a backslash before `$`, a backtick, `"` or a backslash only, `$'...'`, `$"..."`, a backslash before any other
/// character); the word, the index after it and whether every quote in it was closed. The word ends at an unquoted character of `stop`. A `$` that remains makes it a word the guard cannot expand; it is passed on as written.
fn redirect_word(s: &[u32], start: usize, stop: &str) -> (Text, usize, bool) {
    let (sq, dq, bs) = (cp('\''), cp('"'), cp('\\'));
    let n = s.len();
    let (mut out, mut i, mut closed) = (Text::new(), start, true);
    while let Some(c) = at(s, i) {
        if stop.chars().any(|b| cp(b) == c) {
            break;
        }
        if c == bs {
            match at(s, i + 1) {
                Some(d) => {
                    if d != cp('\n') {
                        out.push(d);
                    }
                    i += 2;
                }
                None => i += 1,
            }
        } else if c == sq {
            let close = (i + 1..n).find(|&j| at(s, j) == Some(sq));
            out.extend_from_slice(slice(s, i + 1, close.unwrap_or(n)));
            closed = closed && close.is_some();
            i = close.map_or(n, |j| j + 1);
        } else if c == dq || starts_at(s, i, "$\"") {
            i += if c == dq { 1 } else { 2 };
            loop {
                let Some(d) = at(s, i) else {
                    closed = false;
                    break;
                };
                if d == dq {
                    i += 1;
                    break;
                }
                match at(s, i + 1) {
                    Some(e) if d == bs => {
                        if [cp('$'), cp('`'), dq, bs].contains(&e) {
                            out.push(e);
                        } else if e != cp('\n') {
                            out.extend([d, e]);
                        }
                        i += 2;
                    }
                    _ => {
                        out.push(d);
                        i += 1;
                    }
                }
            }
        } else if starts_at(s, i, "$'") {
            let (t, next, ok) = ansi_c(s, i + 2);
            out.extend(t);
            i = next;
            closed = closed && ok;
        } else {
            out.push(c);
            i += 1;
        }
    }
    (out, i, closed)
}

/// `_quote_end`: `s[i]` opens a quote (`'`, `"`, or the `$` of `$'`); the index after its closing quote. A backslash escapes inside `"` and `$'` but not inside `'`.
fn quote_end(s: &[u32], i: usize) -> Option<usize> {
    let (sq, dq, bs) = (cp('\''), cp('"'), cp('\\'));
    let n = s.len();
    if at(s, i) == Some(sq) {
        return (i + 1..n).find(|&j| at(s, j) == Some(sq)).map(|j| j + 1);
    }
    let (q, mut j) = if at(s, i) == Some(dq) { (dq, i + 1) } else { (sq, i + 2) };
    while j < n && at(s, j) != Some(q) {
        j += if at(s, j) == Some(bs) { 2 } else { 1 };
    }
    (j < n).then_some(j + 1)
}

/// `_scan_redirects`: the words that follow each output redirection operator of `seg` that is outside quotes: `>`, `>>`, `>|`, `&>`, `&>>`, `N>`, `N>>`, `N>|` (the operator is `>`, `>>` or `>|`, whatever stands before it), `>&` and a word that is
/// not a number or `-` (`2>&1`, `>&2`, `>&-` are not files), and `<>`; and whether a quote was left open. With `quotes` false a quote character is an ordinary character in the search for operators (the words are still read with their quotes).
fn scan_redirects(seg: &[u32], quotes: bool) -> (Vec<Text>, bool) {
    let (bs, gt, lt, dollar) = (cp('\\'), cp('>'), cp('<'), cp('$'));
    let special = [bs, cp('\''), cp('"'), dollar, lt, gt];
    let n = seg.len();
    let (mut out, mut i, mut open) = (Vec::new(), 0, false);
    while let Some(k) = (i..n).find(|&k| at(seg, k).is_some_and(|x| special.contains(&x))) {
        i = k;
        let c = at(seg, i).unwrap_or(0);
        if c == bs {
            i += 2;
        } else if quote_chars(c) || (c == dollar && starts_at(seg, i, "$'")) {
            if !quotes {
                i += 1;
                continue;
            }
            match quote_end(seg, i) {
                Some(j) => i = j,
                None => {
                    open = true;
                    break;
                }
            }
        } else if (c == lt && at(seg, i + 1) != Some(gt)) || c == dollar {
            i += 1;
        } else {
            let mut j = i + if c == lt { 2 } else { 1 };
            let mut dup = false;
            let nxt = if c == gt { at(seg, j) } else { None };
            if nxt == Some(gt) || nxt == Some(cp('|')) {
                j += 1;
            } else if nxt == Some(cp('&')) {
                j += 1;
                dup = true;
            }
            while at(seg, j).is_some_and(|x| x == cp(' ') || x == cp('\t') || x == cp('\n')) {
                j += 1;
            }
            let (w, end, closed) = redirect_word(seg, j, REDIRECT_STOP);
            open = open || !closed;
            let k = w.iter().take_while(|&&x| char::from_u32(x).is_some_and(|ch| ch.is_ascii_digit())).count();
            let rest = slice(&w, k, w.len());
            let is_fd = dup && (eq(&w, "-") || (k > 0 && (rest.is_empty() || eq(rest, "-"))));
            if !w.is_empty() && !is_fd {
                out.push(w);
            }
            i = end;
        }
    }
    (out, open)
}

/// `redirect_targets` of the Python file: the files the redirections of the simple command `seg` open for writing, as words with their quotes removed. A quote left open makes the scan run again with quotes as ordinary characters, as the splitter does.
fn quoted_redirect_targets(seg: &[u32]) -> Vec<Text> {
    let (mut out, open) = scan_redirects(seg, true);
    if open {
        out.extend(scan_redirects(seg, false).0);
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

// ---------------------------------------------------------------------------------------------------------------------------------------------------------
// the gaps after the redirections (leaf posix_gaps): `ansi_words`, `word_end`, `redirect_spans`, the glob reading, the assignments, the shells that read their input

/// `MAX_CHARS`: the longest Bash command, or Write/Edit input, that is read; a longer one is denied as too long to be checked (a timeout of the guard is a block only on Claude Code 2.1.295 and later).
const MAX_CHARS: usize = 200_000;
/// `NEST`: the depth to which shell strings are followed in the second pass (the first pass follows 3).
const NEST: usize = 8;
const SETTINGS_NAMES: [&str; 2] = ["settings.json", "settings.local.json"];

/// `_ansi_words`: the words of `seg` as bash reads them, quotes removed (`$'..'` and `$".."` too; blanks separate words).
fn ansi_words(seg: &[u32]) -> Vec<Text> {
    let mut out: Vec<Text> = Vec::new();
    let mut i = 0;
    while i < seg.len() {
        if at(seg, i).is_some_and(|c| c == cp(' ') || c == cp('\t') || c == cp('\n')) {
            i += 1;
            continue;
        }
        let (w, next, _) = redirect_word(seg, i, " \t\n");
        out.push(w);
        i = next;
    }
    out
}

/// `_word_end`: the index after the shell word at `s[start..]`, taken whole: a `$( )`, `${ }`, backtick pair or quote is skipped with whatever blanks and operators it holds. One pass with a stack of what is open; an unclosed one runs to the end.
fn word_end(s: &[u32], start: usize) -> usize {
    let (bs, dq, sq, bt, rp, rb) = (cp('\\'), cp('"'), cp('\''), cp('`'), cp(')'), cp('}'));
    let n = s.len();
    let mut i = start;
    let mut stack: Vec<u32> = Vec::new();
    while i < n {
        let c = at(s, i).unwrap_or(0);
        let top = stack.last().copied();
        if c == bs {
            i += 2;
            continue;
        }
        let opens = starts_at(s, i, "$(") || starts_at(s, i, "${");
        let closer = if at(s, i + 1) == Some(cp('(')) { rp } else { rb };
        if top == Some(dq) {
            if c == dq {
                stack.pop();
            } else if c == bt {
                stack.push(bt);
            } else if opens {
                stack.push(closer);
                i += 1;
            }
        } else if top == Some(bt) {
            if c == bt {
                stack.pop();
            }
        } else if c == sq {
            match (i + 1..n).find(|&j| at(s, j) == Some(sq)) {
                Some(j) => i = j,
                None => return n,
            }
        } else if c == dq || c == bt {
            stack.push(c);
        } else if starts_at(s, i, "$'") {
            match quote_end(s, i) {
                Some(j) => i = j.saturating_sub(1),
                None => return n,
            }
        } else if opens {
            stack.push(closer);
            i += 1;
        } else if top == Some(rp) && c == cp('(') {
            stack.push(rp);
        } else if top == Some(c) {
            stack.pop();
        } else if top.is_none() && REDIRECT_STOP.chars().any(|b| cp(b) == c) {
            return i;
        }
        i += 1;
    }
    n
}

/// `_scan_spans`: the text of the whole word (`word_end`) after each output redirection operator that `scan_redirects` finds, quotes and substitutions as written; the scan goes on after the word, so a text is read once.
fn scan_spans(seg: &[u32], quotes: bool) -> (Vec<Text>, bool) {
    let (bs, gt, lt, dollar) = (cp('\\'), cp('>'), cp('<'), cp('$'));
    let special = [bs, cp('\''), cp('"'), dollar, lt, gt];
    let n = seg.len();
    let (mut out, mut i, mut open) = (Vec::new(), 0, false);
    while let Some(k) = (i..n).find(|&k| at(seg, k).is_some_and(|x| special.contains(&x))) {
        i = k;
        let c = at(seg, i).unwrap_or(0);
        if c == bs {
            i += 2;
        } else if quote_chars(c) || (c == dollar && starts_at(seg, i, "$'")) {
            if !quotes {
                i += 1;
                continue;
            }
            match quote_end(seg, i) {
                Some(j) => i = j,
                None => {
                    open = true;
                    break;
                }
            }
        } else if (c == lt && at(seg, i + 1) != Some(gt)) || c == dollar {
            i += 1;
        } else {
            let mut j = i + if c == lt { 2 } else { 1 };
            let mut dup = false;
            let nxt = if c == gt { at(seg, j) } else { None };
            if nxt == Some(gt) || nxt == Some(cp('|')) {
                j += 1;
            } else if nxt == Some(cp('&')) {
                j += 1;
                dup = true;
            }
            while at(seg, j).is_some_and(|x| x == cp(' ') || x == cp('\t') || x == cp('\n')) {
                j += 1;
            }
            let e = word_end(seg, j);
            let w = slice(seg, j, e);
            let k = w.iter().take_while(|&&x| char::from_u32(x).is_some_and(|ch| ch.is_ascii_digit())).count();
            let rest = slice(w, k, w.len());
            let is_fd = dup && (eq(w, "-") || (k > 0 && (rest.is_empty() || eq(rest, "-"))));
            if !w.is_empty() && !is_fd {
                out.push(w.to_vec());
            }
            i = e;
        }
    }
    (out, open)
}

/// `redirect_spans`: the words after the output redirection operators of `seg`, as written; a quote left open makes the scan run again with quotes as ordinary characters.
fn redirect_spans(seg: &[u32]) -> Vec<Text> {
    let (mut out, open) = scan_spans(seg, true);
    if open {
        out.extend(scan_spans(seg, false).0);
    }
    out
}

/// `[A-Za-z0-9_.\-]`: the characters that continue the name of a settings file.
fn name_char(c: u32) -> bool {
    char::from_u32(c).is_some_and(|ch| ch.is_ascii_alphanumeric() || ch == '_' || ch == '.' || ch == '-')
}

/// `settings(?:\.local)?\.json(?![A-Za-z0-9_.\-])` at `p`.
fn settings_file_at(t: &[u32], p: usize) -> bool {
    SETTINGS_NAMES.iter().any(|lit| starts_at(t, p, lit) && !at(t, p + lit.chars().count()).is_some_and(name_char))
}

/// `_names_span` on folded text: `managed-settings`, or `settings.json` / `settings.local.json` not followed by a name character.
fn names_span_text(t: &[u32]) -> bool {
    (0..t.len()).any(|p| starts_at(t, p, "managed-settings") || settings_file_at(t, p))
}

/// `_names_span`: true when the text names a settings file (`settings.json}` and `settings.json"` count, `settings.json.bak` does not); Windows folds first.
fn names_span(t: &[u32], os: Os) -> bool {
    if os == Os::Windows {
        names_span_text(&nt_fold(t))
    } else {
        names_span_text(t)
    }
}

/// `_names_path`: true when the text names a settings file with its folder (`.claude/settings.json`) or is `managed-settings..`: the value of an assignment that makes a later `$F` target a settings file; `settings.json` alone is a piece.
fn names_path(t: &[u32], os: Os) -> bool {
    let folded;
    let t = if os == Os::Windows {
        folded = nt_fold(t);
        folded.as_slice()
    } else {
        t
    };
    let sep = |c: u32| c == cp('/') || c == cp('\\');
    let dot_claude = ".claude".chars().count();
    (0..t.len()).any(|p| {
        if starts_at(t, p, "managed-settings") {
            return true;
        }
        if !starts_at(t, p, ".claude") || !at(t, p + dot_claude).is_some_and(sep) {
            return false;
        }
        let mut q = p + dot_claude;
        while at(t, q).is_some_and(sep) {
            q += 1;
        }
        settings_file_at(t, q)
    })
}

/// `_NAMES_ANY`: the command names a settings file anywhere (`managed-settings`, `settings.json`, `settings.local.json`); Windows folds first.
fn names_any(t: &[u32], os: Os) -> bool {
    let folded;
    let t = if os == Os::Windows {
        folded = nt_fold(t);
        folded.as_slice()
    } else {
        t
    };
    contains(t, "managed-settings") || contains(t, "settings.json") || contains(t, "settings.local.json")
}

/// `_unquoted`: the text without its quote characters and backslashes.
fn unquoted(t: &[u32]) -> Text {
    t.iter().copied().filter(|&c| c != cp('\'') && c != cp('"') && c != cp('\\')).collect()
}

/// `[*?\[]`: a character that makes a word a shell filename pattern.
fn glob_char(c: u32) -> bool {
    c == cp('*') || c == cp('?') || c == cp('[')
}

/// One token of a filename pattern: `*`, `?`, a literal, or a bracket expression (negated, ranges).
enum Gt {
    Star,
    Any,
    Lit(u32),
    Class(bool, Vec<(u32, u32)>),
}

/// `_glob_tokens`: the pattern as shell filename patterns read it: `*` (runs collapse), `?`, a bracket expression `[..]` (with `!` or `^`, ranges; a class name `[:..:]` is any one character, an over-reading; an unclosed `[` is itself), any other character itself.
fn glob_tokens(p: &[u32]) -> Vec<Gt> {
    let n = p.len();
    let mut out: Vec<Gt> = Vec::new();
    let mut i = 0;
    let last = p.iter().rposition(|&x| x == cp(']')); // the last closing bracket: a `[` after it is unclosed without a scan (a run of them would cost its length squared)
    while i < n {
        let c = at(p, i).unwrap_or(0);
        if c == cp('*') {
            if !matches!(out.last(), Some(Gt::Star)) {
                out.push(Gt::Star);
            }
        } else if c == cp('?') {
            out.push(Gt::Any);
        } else if c == cp('[') {
            let mut j = i + 1;
            let neg = at(p, j).is_some_and(|x| x == cp('!') || x == cp('^'));
            if neg {
                j += 1;
            }
            let mut k = if at(p, j) == Some(cp(']')) { j + 1 } else { j };
            k = match last {
                Some(l) if k <= l => k + p.iter().skip(k).position(|&x| x == cp(']')).unwrap_or(n),
                _ => n,
            };
            if k >= n {
                out.push(Gt::Lit(cp('[')));
            } else {
                let body = slice(p, j, k);
                if contains(body, "[:") || contains(body, "[.") || contains(body, "[=") {
                    out.push(Gt::Any);
                } else {
                    let mut rng: Vec<(u32, u32)> = Vec::new();
                    let mut x = 0;
                    while x < body.len() {
                        let lo = at(body, x).unwrap_or(0);
                        if x + 2 < body.len() && at(body, x + 1) == Some(cp('-')) {
                            rng.push((lo, at(body, x + 2).unwrap_or(0)));
                            x += 3;
                        } else {
                            rng.push((lo, lo));
                            x += 1;
                        }
                    }
                    out.push(Gt::Class(neg, rng));
                }
                i = k;
            }
        } else {
            out.push(Gt::Lit(c));
        }
        i += 1;
    }
    out
}

/// `_glob_match`: true when the pattern matches the whole of `s`; with `prefix`, when it matches some text that starts with `s` (what follows `s` is free).
fn glob_match(toks: &[Gt], s: &[u32], prefix: bool) -> bool {
    let n = toks.len();
    let close = |states: &std::collections::BTreeSet<usize>| -> std::collections::BTreeSet<usize> {
        let mut out = states.clone();
        for &t0 in states {
            let mut t = t0;
            while matches!(toks.get(t), Some(Gt::Star)) {
                t += 1;
                out.insert(t);
            }
        }
        out
    };
    let mut cur = close(&std::collections::BTreeSet::from([0usize]));
    for &ch in s {
        let mut nxt: std::collections::BTreeSet<usize> = std::collections::BTreeSet::new();
        for &t in &cur {
            let Some(tok) = toks.get(t) else {
                continue;
            };
            match tok {
                Gt::Star => {
                    nxt.insert(t);
                }
                Gt::Any => {
                    nxt.insert(t + 1);
                }
                Gt::Lit(v) => {
                    if *v == ch {
                        nxt.insert(t + 1);
                    }
                }
                Gt::Class(neg, rng) => {
                    if rng.iter().any(|&(lo, hi)| lo <= ch && ch <= hi) != *neg {
                        nxt.insert(t + 1);
                    }
                }
            }
        }
        cur = close(&nxt);
        if cur.is_empty() {
            return false;
        }
    }
    if prefix {
        !cur.is_empty()
    } else {
        cur.contains(&n)
    }
}

/// `_glob_managed`: true when the pattern could match a name that starts with `managed-settings`. A pattern that starts with `*` counts only when what follows it could start at `managed-settings`, `-settings` or `settings` (so `*.log` and `*.o` do not, `*settings*` does).
fn glob_managed(lt: &[Gt]) -> bool {
    let i = lt.iter().take_while(|t| matches!(t, Gt::Star)).count();
    if i == 0 {
        return glob_match(lt, &text("managed-settings"), true);
    }
    let rest = lt.get(i..).unwrap_or(&[]);
    !rest.is_empty() && ["managed-settings", "-settings", "settings"].iter().any(|s| glob_match(rest, &text(s), true))
}

/// `str.rstrip("/")`.
fn rstrip_slash(t: &[u32]) -> &[u32] {
    let end = t.iter().rposition(|&c| c != cp('/')).map_or(0, |k| k + 1);
    slice(t, 0, end)
}

/// `_glob_protected`: true when the word `w`, read as a shell filename pattern, could match a settings file: its last component could be `managed-settings...`, or its folder component `managed-settings.d`, or its last component `settings.json` / `settings.local.json` in a folder
/// `.claude`. Only the last two components count, as in `protected`. The folder is the working directory's when `w` has no `/`, and any folder when it is unknown (`cd $X` was seen) or holds `$`, a backtick, `)` or `}`; a folder that is `.`, `..` or empty after a pattern is read as any. A folder pattern counts as `managed-settings.d` by the rule of `glob_managed` (`*/x` does not), and where the folder is unknown a last component that starts with `*` does not count.
fn glob_protected(w: &[u32], cwd: &Cwd, unknown_dir: bool, os: Os, keep: bool) -> Res<bool> {
    let nt = os == Os::Windows;
    let mut w = expanduser_for(w, os);
    if nt {
        let sl: Text = w.iter().map(|&c| if c == cp('\\') { cp('/') } else { c }).collect();
        w = nt_fold(&sl);
    }
    if w.iter().all(|&c| c == cp('/')) {
        return Ok(false);
    }
    let w = rstrip_slash(&w);
    let has_sep = has_char(w, '/');
    let (dirpart, last): (&[u32], &[u32]) = match w.iter().rposition(|&c| c == cp('/')) {
        Some(k) => (slice(w, 0, k), slice(w, k + 1, w.len())),
        None => (&[], w),
    };
    let lt = glob_tokens(last);
    if glob_managed(&lt) {
        return Ok(true);
    }
    let named = SETTINGS_NAMES.iter().any(|n| glob_match(&lt, &text(n), false));
    let guess = named && !matches!(lt.first(), Some(Gt::Star)); // where the folder is not known, a name that starts with `*` is no sign
    let dp = rstrip_slash(dirpart);
    let dl = dp.iter().rposition(|&c| c == cp('/')).map_or(dp, |k| slice(dp, k + 1, dp.len()));
    let glob_dir = dirpart.iter().any(|&c| glob_char(c));
    if has_sep && (dl.iter().any(|&c| "$`)}".chars().any(|x| cp(x) == c)) || (glob_dir && (dl.is_empty() || eq(dl, ".") || eq(dl, "..")))) {
        return Ok(guess); // the folder is not known: only the last component decides
    }
    if has_sep && glob_dir {
        let dt = glob_tokens(dl);
        return Ok(glob_managed(&dt) || (named && glob_match(&dt, &text(".claude"), false)));
    }
    if !has_sep && unknown_dir {
        return Ok(guess);
    }
    let rel: Text = if has_sep { cat(&[dirpart, &text("/x")]) } else { text("x") };
    let parent: Text = if nt {
        let relb: Text = rel.iter().map(|&c| if c == cp('/') { cp('\\') } else { c }).collect();
        let (_, _, comps) = nt_resolve(cwd, &relb, keep)?;
        comps.len().checked_sub(2).and_then(|k| comps.get(k)).map_or_else(Text::new, |c| nt_fold(c))
    } else {
        basename(dirname(&normpath(&join(cwd, &rel)?))).to_vec()
    };
    Ok(eq(&parent, "managed-settings.d") || (named && eq(&parent, ".claude")))
}

/// `_DIR_NAMED.search(t)`: the text names a `.claude` folder (at the start or after a separator, and not followed by a name character).
fn dir_named(t: &[u32]) -> bool {
    let name_char = |c: u32| char::from_u32(c).is_some_and(|ch| ch.is_ascii_alphanumeric() || ch == '_' || ch == '.' || ch == '-');
    let dot_claude = ".claude".chars().count();
    (0..t.len()).any(|p| starts_at(t, p, ".claude") && (p == 0 || at(t, p - 1).is_some_and(|c| c == cp('/') || c == cp('\\'))) && !at(t, p + dot_claude).is_some_and(name_char))
}

/// `_assigns`: (file, folder): a simple command assigns a value that names a settings file (`F=..`, in front of a command or after `export`, `declare`, `local`, `readonly`, or `for F in ..`), and one that assigns a value that names a `.claude` folder (`D=~/.claude`).
fn assigns(segs: &[Seg], os: Os) -> (bool, bool) {
    let (mut file, mut folder) = (false, false);
    for (_, toks) in segs {
        let mut vals: Vec<&[u32]> = toks.iter().filter(|t| is_assign(t)).filter_map(|t| t.iter().position(|&c| c == cp('=')).map(|e| slice(t, e + 1, t.len()))).collect();
        if toks.first().is_some_and(|t| eq(t, "for")) {
            if let Some(p) = toks.iter().position(|t| eq(t, "in")) {
                vals.extend(toks.iter().skip(p + 1).map(|t| t.as_slice()));
            }
        }
        for v in vals {
            file = file || names_path(v, os);
            folder = folder || if os == Os::Windows { dir_named(&nt_fold(v)) } else { dir_named(v) };
        }
        if file && folder {
            break;
        }
    }
    (file, folder)
}

/// `_REDIR_TOK.match(t)`: the end of the redirection operator (with its file descriptor) at the start of `t`.
fn redir_tok(t: &[u32]) -> Option<usize> {
    let d = t.iter().take_while(|&&c| is_digit(c)).count();
    ["<<<", "<<-", "<<", "<>", "<&", "<", ">>", ">&", ">|", ">", "&>>", "&>"].iter().find(|op| starts_at(t, d, op)).map(|op| d + op.chars().count())
}

/// `_STDIN_FILES`: the script files that are the input.
const STDIN_FILES: &[&str] = &["/dev/stdin", "/dev/fd/0", "/proc/self/fd/0"];

/// `_reads_stdin`: true when a shell started with these arguments reads its script from its input: `-s` or `-` was given, or no argument is a script file (redirection words and option values do not count), or the script file is the input (`/dev/stdin`, `/dev/fd/0`, `/proc/self/fd/0`).
fn reads_stdin(args: &[Text]) -> bool {
    let (mut s_opt, mut files, mut i) = (false, false, 0usize);
    while let Some(t) = args.get(i) {
        if let Some(e) = redir_tok(t) {
            i += if e < t.len() { 1 } else { 2 };
            continue;
        }
        if eq(t, "-") || STDIN_FILES.iter().any(|f| eq(t, f)) {
            return true;
        }
        if eq(t, "--") {
            if args.get(i + 1).is_some_and(|x| STDIN_FILES.iter().any(|f| eq(x, f))) {
                return true;
            }
            files = files || args.get(i + 1).is_some_and(|x| redir_tok(x).is_none());
            break;
        }
        if t.len() > 1 && (starts(t, "-") || starts(t, "+")) {
            if at(t, 1) != Some(cp('-')) {
                s_opt = s_opt || (starts(t, "-") && has_char(t, 's'));
                if t.iter().skip(1).all(|&c| char::from_u32(c).is_some_and(|ch| ch.is_ascii_alphabetic())) {
                    i += t.iter().filter(|&&c| c == cp('o') || c == cp('O')).count();
                }
            } else if eq(t, "--rcfile") || eq(t, "--init-file") {
                i += 1;
            }
        } else {
            files = true;
        }
        i += 1;
    }
    s_opt || !files
}

/// `_UNKNOWN_STRING.match(t)`: the word starts with a substitution or a variable (`SUBST_`, `$name`, `${`, `$(`, a backtick).
fn unknown_string(t: &[u32]) -> bool {
    starts(t, "SUBST_") || at(t, 0) == Some(cp('`')) || (at(t, 0) == Some(cp('$')) && at(t, 1).is_some_and(|c| is_word(c) || c == cp('{') || c == cp('(')))
}

/// `_stdin_shell`: true when some simple command is a shell (or a variable, `$SHELL`) that runs a script that is not in the command text: with no `-c` string it reads its script from its input (`.. | sh`, `bash -s`, `sh <<EOF`, `sh <<< ..`, `sh<<<..`, `sh < file`, `sh /dev/stdin`) or from a process
/// substitution (`bash <(..)`); with a `-c` string, one that is itself unknown (`sh -c "$(..)"`, `sh -c "$X"`); and `eval` of such a string, `source` and `.` of the input or of a process substitution.
fn stdin_shell(cmd: &[u32], segs: &[Seg], os: Os) -> bool {
    let procsub = contains(cmd, "<("); // a masked substitution is a script only when the command has a process substitution
    segs.iter().any(|(_, toks)| {
        let (k, _) = program(toks, os);
        let Some(t) = toks.get(k) else {
            return false;
        };
        let mut w: &[u32] = t;
        let mut args: Vec<Text> = slice_toks(toks, k + 1).to_vec();
        if let Some(m) = t.iter().skip(1).position(|&c| c == cp('<') || c == cp('>')) {
            // the operator glued to the program: `sh<<<'..'`
            w = slice(t, 0, m + 1);
            args.insert(0, slice(t, m + 1, t.len()).to_vec());
        }
        let name = prog_name(w, os);
        if in_set(&name, SHELLS) || shell_var(w) {
            let dash_c = args.iter().position(|x| eq(x, "-c"));
            let script = shell_script(&args);
            if dash_c.is_some() || script.is_some() {
                let mut js: Vec<usize> = dash_c.map(|j| j + 1).into_iter().collect();
                js.extend(script);
                return js.iter().any(|&j| args.get(j).is_some_and(|a| unknown_string(a)));
            }
            return reads_stdin(&args) || (procsub && args.iter().any(|a| starts(a, "SUBST_")));
        }
        if eq(&name, "eval") {
            return args.first().is_some_and(|a| unknown_string(a));
        }
        if eq(&name, ".") || eq(&name, "source") {
            return args.first().is_some_and(|a| STDIN_FILES.iter().any(|f| eq(a, f)) || (procsub && starts(a, "SUBST_")));
        }
        false
    })
}

/// `_writer_targets`: the words that the program writes or removes, for the writers that G3 knows (`tee`, in-place editors, `cp`, `mv`, ..., `dd of=`).
fn writer_targets(prog: &[u32], args: &[Text]) -> Vec<Text> {
    let mut targets: Vec<Text> = Vec::new();
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
    targets
}

/// What `gap_hit` needs of the walk over the commands: the working directory, whether `cd $X` was seen, whether the command assigns a settings file and a `.claude` folder (`assigns`), the flavour and the dots-and-spaces reading.
#[derive(Clone, Copy)]
struct GapState<'a> {
    cur: &'a Cwd,
    unknown: bool,
    assign: (bool, bool),
    os: Os,
    keep: bool,
}

/// `_gap_hit`: the gap readings of one simple command: each redirect target (as written, whole) and each writer argument that the guard cannot expand is denied when its text names a settings file with its `.claude` folder or is `managed-settings..`, when the command assigns a value that
/// names a settings file, or when the text names `settings.json` and the folder `.claude` is named by an assignment or by the target itself (`$D/settings.json` after `D=~/.claude`, `$(echo .claude)/settings.json`); `$HOME/.vscode/settings.json` is not. Each target that holds a glob character, when it could match a settings file.
fn gap_hit(seg: &[u32], toks: &[Text], k: usize, prog: &[u32], st: &GapState) -> Res<Option<Hit>> {
    let GapState { cur, unknown, assign, os, keep } = *st;
    let args: &[Text] = if k < toks.len() { slice_toks(toks, k + 1) } else { &[] };
    let mut cands: Vec<(Text, bool)> = redirect_spans(seg).into_iter().map(|t| (t, true)).collect();
    cands.extend(writer_targets(prog, args).into_iter().map(|t| (t, false)));
    for (t, raw) in cands {
        let w: Text = if has_char(&t, '$') || has_char(&t, '`') || contains(&t, "SUBST_") {
            let u = unquoted(&t);
            if names_path(&t, os) || names_path(&u, os) {
                return Ok(hit("G3", cat(&[&text("the command writes `"), &t, &text("`, a target the guard cannot expand that names a Claude Code settings file")])));
            }
            if assign.0 {
                return Ok(hit("G3", cat(&[&text("the command writes `"), &t, &text("`, a target the guard cannot expand, and assigns a value that names a Claude Code settings file")])));
            }
            let in_dir = if os == Os::Windows { contains(&nt_fold(&u), ".claude") } else { contains(&u, ".claude") };
            if (names_span(&t, os) || names_span(&u, os)) && (assign.1 || in_dir) {
                return Ok(hit("G3", cat(&[&text("the command writes `"), &t, &text("`, a target the guard cannot expand that names a settings file in a `.claude` folder")])));
            }
            u
        } else if raw {
            redirect_word(&t, 0, REDIRECT_STOP).0
        } else {
            t.clone()
        };
        if w.iter().any(|&c| glob_char(c)) && glob_protected(&w, cur, unknown, os, keep)? {
            return Ok(hit("G3", cat(&[&text("the command writes `"), &t, &text("`, which can match a Claude Code settings file")])));
        }
    }
    Ok(None)
}

/// `g3_bash`: a Bash command that writes a Claude Code settings file. On Windows the commands are read twice: as written, then with every backslash a slash. `redirects` false is the reading of before the leaf posix_redirects; `redirects` true
/// tests only the targets of `quoted_redirect_targets` (and runs no script check), so that a command denied before is denied for the same reason; `gaps` tests only what the leaf posix_gaps adds (`gap_hit`).
fn g3_bash(cmd: &[u32], segs: &[Seg], cwd: &Cwd, os: Os, script: bool, redirects: bool, gaps: bool) -> Res<Option<Hit>> {
    let rd = Reading { script, keep: false, redirects, gaps };
    let first = g3_bash_once(cmd, segs, cwd, os, rd)?;
    if first.is_some() || os != Os::Windows {
        return Ok(first);
    }
    // Windows: the text as written with the other reading of a dots-and-spaces name, then with every backslash a slash under both readings
    if let Some(h) = g3_bash_once(cmd, segs, cwd, os, Reading { keep: true, ..rd })? {
        return Ok(Some(h));
    }
    let sl = slashed(segs);
    if let Some(h) = g3_bash_once(cmd, &sl, cwd, os, Reading { script: false, ..rd })? {
        return Ok(Some(h));
    }
    g3_bash_once(cmd, &sl, cwd, os, Reading { script: false, keep: true, ..rd })
}

/// The switches of one reading of `g3_bash_once`: the script check, the dots-and-spaces reading of a Windows name, and which targets are tested (the older ones, `quoted_redirect_targets`, or `gap_hit`).
#[derive(Clone, Copy)]
struct Reading {
    script: bool,
    keep: bool,
    redirects: bool,
    gaps: bool,
}

/// `_g3_bash`: one reading; the script check (`script`) is made on the first only.
fn g3_bash_once(cmd: &[u32], segs: &[Seg], cwd: &Cwd, os: Os, rd: Reading) -> Res<Option<Hit>> {
    let Reading { script, keep, redirects, gaps } = rd;
    let assign = if gaps { assigns(segs, os) } else { (false, false) };
    let mut unknown = false;
    let mut cur = cwd.clone();
    let mut spent = 0_usize;
    for (seg, toks) in segs {
        spent = spent.saturating_add(cwd_len(&cur)); // every command reads the working directory again
        if spent > CWD_WORK {
            return Ok(too_long_cwd());
        }
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
            if cwd_len(&cur) > CWD_MAX {
                return Ok(too_long_cwd());
            }
            continue;
        }
        if gaps {
            if let Some(h) = gap_hit(seg, toks, k, prog, &GapState { cur: &cur, unknown, assign, os, keep })? {
                return Ok(Some(h));
            }
            continue;
        }
        if redirects {
            for t in quoted_redirect_targets(seg) {
                if protected(&t, &cur, unknown, os, keep)? {
                    return Ok(hit("G3", cat(&[&text("the command writes `"), &t, &text("`, a Claude Code settings file")])));
                }
            }
            continue;
        }
        let mut targets = redirect_targets(seg);
        targets.extend(writer_targets(prog, if k < toks.len() { slice_toks(toks, k + 1) } else { &[] }));
        for t in targets {
            if protected(&t, &cur, unknown, os, keep)? {
                return Ok(hit("G3", cat(&[&text("the command writes `"), &t, &text("`, a Claude Code settings file")])));
            }
        }
    }
    if !script || redirects || gaps {
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

/// `_input_chars`: the characters of the strings of a Write, Edit, MultiEdit or NotebookEdit input that the guard reads: the path, the content, and each old and new string.
fn input_chars(inp: &Value) -> usize {
    let mut total = 0;
    for key in ["file_path", "path", "notebook_path", "content", "new_source", "old_string", "new_string"] {
        if let Some(Value::Str(t)) = inp.get(key) {
            total += t.len();
        }
    }
    if let Some(Value::Arr(edits)) = inp.get("edits") {
        for e in edits {
            for key in ["old_string", "new_string"] {
                if let Some(Value::Str(t)) = e.get(key) {
                    total += t.len();
                }
            }
        }
    }
    total
}

/// `TOO_COMPLEX`: the denial when the splitter has too much to scan.
fn too_complex() -> Option<Hit> {
    hit("G?", text("the command has too many command substitutions to be checked"))
}

/// The length of a directory that is a string, else 0.
fn cwd_len(c: &Cwd) -> usize {
    match c {
        Cwd::Str(t) => t.len(),
        _ => 0,
    }
}

/// `CWD_MAX`: the longest directory the commands are followed into by `cd` and `pushd`.
const CWD_MAX: usize = 1024;

/// `CWD_WORK`: the commands of a chain times the length of their directory, at most.
const CWD_WORK: usize = 4_000_000;

/// `TOO_LONG_CWD`: the denial when a `cd` leads to a path longer than `CWD_MAX`, or the commands times the directory exceed `CWD_WORK`.
fn too_long_cwd() -> Option<Hit> {
    hit("G?", text("the directory of the commands is too long, for as many commands, to be checked"))
}

/// What one pass over a Bash command found: the denial, the simple commands, whether a shell string lay deeper than the pass follows, and the commands with `>|` whole (when a segment ended in `>`).
struct Pass {
    hit: Option<Hit>,
    segs: Vec<Seg>,
    deep: bool,
    alt: Option<Vec<Seg>>,
}

/// `_bash_pass`: the readings of G1 to G3 over the commands of `expand`. `second` is the pass of the leaf posix_gaps (ANSI-C words, strings to depth `NEST`); the first pass is that of before.
fn bash_pass(cmd: &[u32], cwd: &Cwd, os: Os, second: bool) -> Res<Pass> {
    let mode = if second { Mode { clobber: false, ansi: true, limit: NEST } } else { FIRST };
    let mut deep = false;
    let mut work = 0;
    let Ok(segs) = expand(cmd, 0, &mut work, os, mode, &mut deep) else {
        return Ok(Pass { hit: too_complex(), segs: Vec::new(), deep: false, alt: None });
    };
    let mut found = g1(cmd, &segs, os).or_else(|| g2(&segs, os)).or_else(|| if os == Os::Windows { g2(&slashed(&segs), os) } else { None });
    if found.is_none() {
        found = g3_bash(cmd, &segs, cwd, os, true, false, false)?;
    }
    if found.is_none() {
        // the quote-aware reading of the redirections comes after every older reading, so a denial keeps its reason
        found = g3_bash(cmd, &segs, cwd, os, false, true, false)?;
    }
    if found.is_some() || !segs.iter().any(|(sg, _)| sg.last() == Some(&cp('>'))) {
        return Ok(Pass { hit: found, segs, deep, alt: None }); // a segment that ends in `>` is where the splitter cut a `>|`
    }
    let mut work = 0;
    let Ok(alt) = expand(cmd, 0, &mut work, os, Mode { clobber: true, ..mode }, &mut false) else {
        return Ok(Pass { hit: too_complex(), segs, deep, alt: None });
    };
    let found = g3_bash(cmd, &alt, cwd, os, false, true, false)?; // and the reading with `>|` whole
    Ok(Pass { hit: found, segs, deep, alt: Some(alt) })
}

/// `g3_gaps`: the readings of the leaf posix_gaps that are not a pass over the same commands: targets that cannot be expanded or that are globs (`gap_hit`, over the commands with `>|` cut and, when there are some, with it whole), and, when the command names a settings file anywhere, a shell string nested deeper than the pass follows or a shell
/// that reads its script from its input (the script is not in the command text).
fn g3_gaps(cmd: &[u32], pass: &Pass, cwd: &Cwd, os: Os) -> Res<Option<Hit>> {
    if let Some(h) = g3_bash(cmd, &pass.segs, cwd, os, false, false, true)? {
        return Ok(Some(h));
    }
    if let Some(alt) = &pass.alt {
        if let Some(h) = g3_bash(cmd, alt, cwd, os, false, false, true)? {
            return Ok(Some(h));
        }
    }
    if !names_any(cmd, os) {
        return Ok(None);
    }
    if pass.deep {
        return Ok(hit("G3", text("a shell string is nested too deep to be read, and the command names a Claude Code settings file")));
    }
    if stdin_shell(cmd, &pass.segs, os) {
        return Ok(hit("G3", text("a shell reads a script that is not in the command, and the command names a Claude Code settings file")));
    }
    Ok(None)
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
        if cmd.contains(&0) {
            return Ok(hit("G?", text("the command holds a NUL character, which a shell cannot receive")));
        }
        if cmd.len() > MAX_CHARS {
            return Ok(hit("G?", text(&format!("the command is too long to be checked (more than {MAX_CHARS} characters)"))));
        }
        let first = bash_pass(&cmd, &cwd, os, false)?;
        if first.hit.is_some() {
            return Ok(first.hit);
        }
        // the readings of the leaf posix_gaps come after every older reading, so a denial keeps its reason
        let second = bash_pass(&cmd, &cwd, os, true)?;
        if second.hit.is_some() {
            return Ok(second.hit);
        }
        return g3_gaps(&cmd, &second, &cwd, os);
    }
    if ["Write", "Edit", "MultiEdit", "NotebookEdit"].contains(&tool.as_str()) {
        // BORROW: explicit .as_str() for the slice-contains lookup
        if !matches!(inp, Value::Obj(_)) {
            return Err(Fault::Attribute);
        }
        if ["file_path", "path", "notebook_path"].iter().any(|k| matches!(inp.get(k), Some(Value::Str(t)) if t.contains(&0))) {
            return Ok(hit("G?", text("the path holds a NUL character, which a file name cannot hold")));
        }
        if let Some(h) = g3_edit(&inp, &cwd, os)? {
            return Ok(Some(h));
        }
        if input_chars(&inp) > MAX_CHARS {
            return Ok(hit("G?", text(&format!("the input is too long to be checked (more than {MAX_CHARS} characters)"))));
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

    /// The pinned counts of the lists that carry the expected decision under both flavours (`WINDOWS_COUNT`, `REDIRECTS_COUNT` and `POSIX_GAPS_COUNT` of the Python file).
    const WINDOWS_COUNT: usize = 106;
    const REDIRECTS_COUNT: usize = 110;
    const POSIX_GAPS_COUNT: usize = 219;

    /// The cases of the list `name` (`windows_paths`, `redirects`); the file is read here, at test time, from the manifest directory, and is never embedded in the binary.
    fn list_cases(name: &str) -> Vec<Value> {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("..").join("scripts").join("fixtures").join("guard_lists").join(format!("{name}.json"));
        let raw = std::fs::read(&path).unwrap_or_else(|e| panic!("cannot read {}: {e}", path.display()));
        let parsed = json::loads(&String::from_utf8(raw).unwrap_or_else(|_| panic!("{name}.json is UTF-8"))).unwrap_or_else(|_| panic!("{name}.json is JSON"));
        match parsed {
            Value::Arr(cases) => cases,
            _ => panic!("{name}.json is not a list"),
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

    fn check_all(list: &str, count: usize, os: Os, column: &str) {
        let cases = list_cases(list);
        assert_eq!(cases.len(), count, "{list}.json has a pinned count");
        let wrong: Vec<String> = cases
            .iter()
            .filter_map(|c| {
                let (want, got) = (string(&field(c, column)), group_of(c, os));
                (want != got).then(|| format!("{}: want {want}, got {got}", string(&field(c, "id"))))
            })
            .collect();
        assert!(wrong.is_empty(), "{list}: {column} decisions differ from the list: {wrong:?}");
    }

    #[test]
    fn windows_list_under_the_nt_flavour() {
        check_all("windows_paths", WINDOWS_COUNT, Os::Windows, "nt");
    }

    #[test]
    fn windows_list_under_the_posix_flavour() {
        check_all("windows_paths", WINDOWS_COUNT, Os::Unix, "posix");
    }

    #[test]
    fn redirects_list_under_the_nt_flavour() {
        check_all("redirects", REDIRECTS_COUNT, Os::Windows, "nt");
    }

    #[test]
    fn redirects_list_under_the_posix_flavour() {
        check_all("redirects", REDIRECTS_COUNT, Os::Unix, "posix");
    }

    #[test]
    fn posix_gaps_list_under_the_nt_flavour() {
        check_all("posix_gaps", POSIX_GAPS_COUNT, Os::Windows, "nt");
    }

    #[test]
    fn posix_gaps_list_under_the_posix_flavour() {
        check_all("posix_gaps", POSIX_GAPS_COUNT, Os::Unix, "posix");
    }

    #[test]
    fn the_cap_is_the_last_length_that_is_read() {
        // one character over `MAX_CHARS` is denied G?, `MAX_CHARS` itself is read; Bash by its command, the other tools by their text input
        for (tool, key) in [("Bash", "command"), ("Write", "content"), ("Edit", "new_string"), ("NotebookEdit", "new_source")] {
            for (n, want) in [(MAX_CHARS, "allow"), (MAX_CHARS + 1, "G?")] {
                let input = Value::Obj(vec![(text(key), Value::Str(text(&"a".repeat(n))))]);
                let e = Value::Obj(vec![(text("tool_name"), Value::Str(text(tool))), (text("tool_input"), input), (text("cwd"), Value::Str(text("/h/proj")))]);
                let got = match decide(&e, Os::Unix) {
                    Ok(Some(h)) => h.group.to_string(),
                    Ok(None) => "allow".to_string(),
                    Err(f) => format!("fault {}", f.name()),
                };
                assert_eq!(got, want, "{tool} of {n} characters");
            }
        }
    }

    #[test]
    fn a_quoted_target_is_read_as_the_shell_reads_it() {
        let t = |s: &str| quoted_redirect_targets(&text(s)).iter().map(|w| string(w)).collect::<Vec<_>>();
        assert_eq!(t("echo x > \"a b/c\""), ["a b/c"]);
        assert_eq!(t("echo x >| a\\ b"), ["a b"]);
        assert_eq!(t("echo x >$'a\\x20b\\n'"), ["a b\n"]);
        assert_eq!(t("echo x 2>&1 >&2 >&- 1>&2-"), Vec::<String>::new());
        assert_eq!(t("echo x &>>\"p q\" <> r"), ["p q", "r"]);
        assert_eq!(t("echo \"a > b\" 'c > d'"), Vec::<String>::new());
        assert_eq!(t("echo $'a\\x00b' > $'u\\x00v'"), ["u"]);
    }

    #[test]
    fn the_split_keeps_clobber_whole_only_when_asked() {
        let cmd = text("echo x >| f");
        let (mut w, mut w2) = (0, 0);
        let plain: Vec<String> = expand(&cmd, 0, &mut w, Os::Unix, FIRST, &mut false).unwrap_or_default().iter().map(|(sg, _)| string(sg)).collect();
        let whole: Vec<String> = expand(&cmd, 0, &mut w2, Os::Unix, Mode { clobber: true, ..FIRST }, &mut false).unwrap_or_default().iter().map(|(sg, _)| string(sg)).collect();
        assert_eq!(plain, ["echo x >", "f"]);
        assert_eq!(whole, ["echo x >| f"]);
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
