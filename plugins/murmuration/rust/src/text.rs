//! Python-`str` semantics over code points: the text type, the character classes of `re`, the path helpers of `posixpath` that the guard uses, and the reading of Windows paths (`nt_*`).
//!
//! A `Text` is a vector of code points, not of Rust `char`, because a Python `str` read from JSON can hold a lone surrogate, which a `char` cannot.

use crate::platform::Os;
use crate::tables::{DIGIT, SPACE, WORD};

/// A Python `str`: code points in `0..=0x10FFFF`, surrogates allowed.
pub(crate) type Text = Vec<u32>;

/// A failure that the Python guard would have raised as an exception; its name goes into the deny message.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub(crate) enum Fault {
    /// `AttributeError`: `.get` on a value that is not an object.
    Attribute,
    /// `TypeError`: an operation on the wrong type.
    Type,
    /// `KeyError`: indexing an object with an integer.
    Key,
    /// `ValueError`: a NUL in a path, or an integer of more than 4300 digits.
    Value,
    /// `RecursionError`: JSON nested deeper than the interpreter allows.
    Recursion,
    /// `JSONDecodeError`: the event is not JSON.
    JsonDecode,
    /// `UnicodeEncodeError`: a lone surrogate in a path that is opened.
    UnicodeEncode,
    /// A value type the port does not model (a float, array or object where a string is expected); the Python guard may allow it, the port denies.
    Unsupported,
}

impl Fault {
    /// The name Python gives the exception.
    #[must_use]
    pub(crate) const fn name(self) -> &'static str {
        match self {
            Self::Attribute => "AttributeError",
            Self::Type => "TypeError",
            Self::Key => "KeyError",
            Self::Value => "ValueError",
            Self::Recursion => "RecursionError",
            Self::JsonDecode => "JSONDecodeError",
            Self::UnicodeEncode => "UnicodeEncodeError",
            Self::Unsupported => "UnsupportedType",
        }
    }
}

/// The event's working directory: a string, or a truthy non-string that makes `os.path.join` raise `TypeError`.
#[derive(Debug, Clone)]
#[non_exhaustive]
pub(crate) enum Cwd {
    /// A string (possibly empty).
    Str(Text),
    /// A truthy value that is not a string.
    Bad,
}

/// The code points of a Rust string.
#[must_use]
pub(crate) fn text(s: &str) -> Text {
    s.chars().map(u32::from).collect()
}

/// A Rust string from code points; a surrogate becomes U+FFFD (only for file names and diagnostics).
#[must_use]
pub(crate) fn string(t: &[u32]) -> String {
    t.iter().map(|&c| char::from_u32(c).unwrap_or('\u{FFFD}')).collect()
}

/// The code point of an ASCII or other scalar character.
#[must_use]
pub(crate) const fn cp(c: char) -> u32 {
    c as u32 // CAST: char → u32, lossless widening
}

fn in_ranges(table: &[(u32, u32)], c: u32) -> bool {
    let i = table.partition_point(|&(_, hi)| hi < c);
    table.get(i).is_some_and(|&(lo, _)| lo <= c)
}

/// Python's `str.isspace()` for one code point (`\s`).
#[must_use]
pub(crate) fn is_space(c: u32) -> bool {
    in_ranges(SPACE, c)
}

/// The `\w` of `re` for one code point.
#[must_use]
pub(crate) fn is_word(c: u32) -> bool {
    in_ranges(WORD, c)
}

/// The `\d` of `re` for one code point.
#[must_use]
pub(crate) fn is_digit(c: u32) -> bool {
    in_ranges(DIGIT, c)
}

/// `t[a:b]` with Python's clamping.
#[must_use]
pub(crate) fn slice(t: &[u32], a: usize, b: usize) -> &[u32] {
    let b = b.min(t.len());
    let a = a.min(b);
    // INDEX: both ends are clamped to the length just above
    &t[a..b]
}

/// `t[i]` or `None` when out of range.
#[must_use]
pub(crate) fn at(t: &[u32], i: usize) -> Option<u32> {
    t.get(i).copied()
}

/// `t == s`.
#[must_use]
pub(crate) fn eq(t: &[u32], s: &str) -> bool {
    t.len() == s.chars().count() && starts_at(t, 0, s)
}

/// `t.startswith(s, i)`.
#[must_use]
pub(crate) fn starts_at(t: &[u32], i: usize, s: &str) -> bool {
    for (k, ch) in (i..).zip(s.chars()) {
        if at(t, k) != Some(cp(ch)) {
            return false;
        }
    }
    true
}

/// `t.startswith(s)`.
#[must_use]
pub(crate) fn starts(t: &[u32], s: &str) -> bool {
    starts_at(t, 0, s)
}

/// `s in t` for a substring.
#[must_use]
pub(crate) fn contains(t: &[u32], s: &str) -> bool {
    find_from(t, 0, s).is_some()
}

/// `c in t` for one character.
#[must_use]
pub(crate) fn has_char(t: &[u32], c: char) -> bool {
    t.contains(&cp(c))
}

/// `t.find(s, from)`.
#[must_use]
pub(crate) fn find_from(t: &[u32], from: usize, s: &str) -> Option<usize> {
    let n = s.chars().count();
    (from..=t.len().saturating_sub(n)).find(|&i| i + n <= t.len() && starts_at(t, i, s))
}

/// `t.strip()`.
#[must_use]
pub(crate) fn strip(t: &[u32]) -> &[u32] {
    let a = t.iter().position(|&c| !is_space(c)).unwrap_or(t.len());
    let b = t.iter().rposition(|&c| !is_space(c)).map_or(a, |p| p + 1);
    slice(t, a, b)
}

/// `t.split()`: the runs between whitespace.
#[must_use]
pub(crate) fn split_ws(t: &[u32]) -> Vec<Text> {
    t.split(|&c| is_space(c)).filter(|w| !w.is_empty()).map(<[u32]>::to_vec).collect()
}

/// `t.split(sep)` for a one-character separator.
#[must_use]
pub(crate) fn split_on(t: &[u32], sep: char) -> Vec<Text> {
    t.split(|&c| c == cp(sep)).map(<[u32]>::to_vec).collect()
}

/// `s.join(parts)` for a one-character separator.
#[must_use]
pub(crate) fn join_with(parts: &[Text], sep: char) -> Text {
    let mut out = Text::new();
    for (i, p) in parts.iter().enumerate() {
        if i > 0 {
            out.push(cp(sep));
        }
        out.extend_from_slice(p);
    }
    out
}

/// `os.path.isabs`.
#[must_use]
pub(crate) fn isabs(p: &[u32]) -> bool {
    at(p, 0) == Some(cp('/'))
}

/// `os.path.basename`.
#[must_use]
pub(crate) fn basename(p: &[u32]) -> &[u32] {
    let i = p.iter().rposition(|&c| c == cp('/')).map_or(0, |k| k + 1);
    slice(p, i, p.len())
}

/// `os.path.dirname`.
#[must_use]
pub(crate) fn dirname(p: &[u32]) -> &[u32] {
    let i = p.iter().rposition(|&c| c == cp('/')).map_or(0, |k| k + 1);
    let head = slice(p, 0, i);
    if !head.is_empty() && !head.iter().all(|&c| c == cp('/')) {
        let end = head.iter().rposition(|&c| c != cp('/')).map_or(0, |k| k + 1);
        return slice(head, 0, end);
    }
    head
}

/// `os.path.normpath`.
#[must_use]
pub(crate) fn normpath(p: &[u32]) -> Text {
    if p.is_empty() {
        return text(".");
    }
    let slash = cp('/');
    let mut initial = usize::from(at(p, 0) == Some(slash));
    if initial == 1 && at(p, 1) == Some(slash) && at(p, 2) != Some(slash) {
        initial = 2;
    }
    let mut out: Vec<Text> = Vec::new();
    for comp in p.split(|&c| c == slash) {
        if comp.is_empty() || eq(comp, ".") {
            continue;
        }
        let dotdot = eq(comp, "..");
        let last_dotdot = out.last().is_some_and(|l| eq(l, ".."));
        if !dotdot || (initial == 0 && out.is_empty()) || last_dotdot {
            out.push(comp.to_vec());
        } else if !out.is_empty() {
            out.pop();
        }
    }
    let mut path = join_with(&out, '/');
    if initial > 0 {
        let mut head = vec![slash; initial];
        head.extend(path);
        path = head;
    }
    if path.is_empty() { text(".") } else { path }
}

/// `os.path.join(cwd, p)` for a possibly invalid `cwd`.
///
/// # Errors
/// Returns [`Fault::Type`] when `cwd` is a truthy non-string.
pub(crate) fn join(cwd: &Cwd, p: &[u32]) -> Result<Text, Fault> {
    let Cwd::Str(a) = cwd else {
        return Err(Fault::Type);
    };
    if isabs(p) {
        return Ok(p.to_vec());
    }
    let mut out = a.clone();
    if !out.is_empty() && at(&out, out.len() - 1) != Some(cp('/')) {
        out.push(cp('/'));
    }
    out.extend_from_slice(p);
    Ok(out)
}

/// `os.path.expanduser` for `~` and `~/...`; `~name` is left alone (the port has no user database).
#[must_use]
pub(crate) fn expanduser(p: &[u32]) -> Text {
    if at(p, 0) != Some(cp('~')) {
        return p.to_vec();
    }
    let i = p.iter().skip(1).position(|&c| c == cp('/')).map_or(p.len(), |k| k + 1);
    if i != 1 {
        return p.to_vec();
    }
    let Some(home) = crate::platform::home_dir() else {
        return p.to_vec();
    };
    let mut home = text(&home);
    while at(&home, home.len().wrapping_sub(1)) == Some(cp('/')) {
        home.pop();
    }
    home.extend_from_slice(slice(p, i, p.len()));
    if home.is_empty() { text("/") } else { home }
}

// ---------------------------------------------------------------------------------------------------------------------------------------------------------
// the reading of a Windows path, one for one with the `_nt_*` functions of `scripts/permission_guard.py` (not `ntpath`; the Python file says why)

/// The names that lose their extension as a program (`.exe`, `.cmd`, `.bat`, `.com`).
const NT_EXE: [&str; 4] = [".exe", ".cmd", ".bat", ".com"];

/// `nt_fold`: the case folding of names: the ASCII letters, and the four characters outside ASCII that fold into it (dotted and dotless I, long S, Kelvin sign).
#[must_use]
pub(crate) fn nt_fold(t: &[u32]) -> Text {
    t.iter()
        .map(|&c| match c {
            0x41..=0x5A => c + 32,
            0x17F => cp('s'),
            0x130 | 0x131 => cp('i'),
            0x212A => cp('k'),
            _ => c,
        })
        .collect()
}

/// `_is_drive`: an ASCII letter and a colon.
fn is_drive(s: &[u32]) -> bool {
    s.len() >= 2 && at(s, 1) == Some(cp(':')) && at(s, 0).is_some_and(|c| char::from_u32(c).is_some_and(|ch| ch.is_ascii_alphabetic()))
}

/// What `_nt_root` finds in a path.
pub(crate) struct NtRoot {
    /// The drive (`C:`) or empty.
    pub(crate) drive: Text,
    /// Whether the path starts at a root (`C:\`, `\`, a UNC `\\server`, or an extended prefix); `C:x` is drive-relative and not rooted.
    pub(crate) rooted: bool,
    /// The text after the drive, with `/` read as `\`.
    pub(crate) rest: Text,
    /// Whether an extended prefix (`\\?\`, `\\.\`, `\??\`, and `UNC\` after it) was cut off.
    pub(crate) ext: bool,
}

/// `_nt_root`.
#[must_use]
pub(crate) fn nt_root(p: &[u32]) -> NtRoot {
    let mut s: Text = p.iter().map(|&c| if c == cp('/') { cp('\\') } else { c }).collect();
    let mut ext = false;
    for pre in ["\\\\?\\", "\\\\.\\", "\\??\\"] {
        if starts(&s, pre) {
            s = slice(&s, pre.chars().count(), s.len()).to_vec();
            ext = true;
            break;
        }
    }
    if ext && eq(&nt_fold(slice(&s, 0, 4)), "unc\\") {
        s = slice(&s, 4, s.len()).to_vec();
    }
    let mut drive = Text::new();
    if is_drive(&s) {
        drive = slice(&s, 0, 2).to_vec();
        s = slice(&s, 2, s.len()).to_vec();
    }
    let rooted = ext || at(&s, 0) == Some(cp('\\'));
    NtRoot { drive, rooted, rest: s, ext }
}

/// `_nt_walk`: the components of `rest` folded onto `stack` as Windows resolves them: an alternate data stream (`:name`) is cut off a component, `.` and empty components vanish,
/// `..` removes the last component (and stays when there is none and the path is not rooted), and trailing dots and spaces are cut off.
#[must_use]
pub(crate) fn nt_walk(mut stack: Vec<Text>, rooted: bool, rest: &[u32]) -> Vec<Text> {
    for comp in rest.split(|&c| c == cp('\\')) {
        let cut = comp.iter().position(|&c| c == cp(':')).unwrap_or(comp.len());
        let comp = slice(comp, 0, cut);
        if eq(comp, ".") {
            continue;
        }
        if eq(comp, "..") {
            if stack.last().is_some_and(|l| !eq(l, "..")) {
                stack.pop();
            } else if !rooted {
                stack.push(text(".."));
            }
            continue;
        }
        let end = comp.iter().rposition(|&c| c != cp(' ') && c != cp('.')).map_or(0, |k| k + 1);
        let comp = slice(comp, 0, end);
        if !comp.is_empty() {
            stack.push(comp.to_vec());
        }
    }
    stack
}

/// A resolved Windows path: drive, whether rooted, components.
pub(crate) type NtPath = (Text, bool, Vec<Text>);

/// `_nt_resolve`: the path `p` seen from the working directory `cwd`.
///
/// # Errors
/// Returns [`Fault::Type`] when `p` is relative and `cwd` is a truthy non-string.
pub(crate) fn nt_resolve(cwd: &Cwd, p: &[u32]) -> Result<NtPath, Fault> {
    let r = nt_root(p);
    if r.rooted {
        return Ok((r.drive, true, nt_walk(Vec::new(), true, &r.rest)));
    }
    let Cwd::Str(c) = cwd else {
        return Err(Fault::Type);
    };
    let cr = nt_root(c);
    let base = nt_walk(Vec::new(), cr.rooted, &cr.rest);
    Ok((cr.drive, cr.rooted, nt_walk(base, cr.rooted, &r.rest)))
}

/// `_nt_str`: a resolved path as text.
#[must_use]
pub(crate) fn nt_str(drive: &[u32], rooted: bool, comps: &[Text]) -> Text {
    let mut out = drive.to_vec();
    if rooted {
        out.push(cp('\\'));
    }
    out.extend(join_with(comps, '\\'));
    out
}

/// `_nt_join`: `os.path.join(a, p)` as Windows reads it, as text (used to open a file; decisions use [`nt_resolve`]).
///
/// # Errors
/// Returns [`Fault::Type`] when `a` is needed and is a truthy non-string.
pub(crate) fn nt_join(a: &Cwd, p: &[u32]) -> Result<Text, Fault> {
    let r = nt_root(p);
    if r.rooted && (!r.drive.is_empty() || r.ext) {
        return Ok(p.to_vec());
    }
    let Cwd::Str(a) = a else {
        return Err(Fault::Type);
    };
    if r.rooted {
        let mut out = nt_root(a).drive;
        out.extend_from_slice(p);
        return Ok(out);
    }
    let p: &[u32] = if r.drive.is_empty() { p } else { &r.rest };
    if a.is_empty() {
        return Ok(p.to_vec());
    }
    let mut out = a.clone();
    if !at(a, a.len() - 1).is_some_and(|c| c == cp('\\') || c == cp('/')) {
        out.push(cp('\\'));
    }
    out.extend_from_slice(p);
    Ok(out)
}

/// `_nt_expanduser`: `~` and `~\...` (or `~/...`) to the home directory (`USERPROFILE`, then `HOME`; neither set: left alone).
#[must_use]
pub(crate) fn nt_expanduser(p: &[u32]) -> Text {
    if at(p, 0) != Some(cp('~')) || at(p, 1).is_some_and(|c| c != cp('\\') && c != cp('/')) {
        return p.to_vec();
    }
    let Some(home) = crate::platform::home_for(Os::Windows) else {
        return p.to_vec();
    };
    let mut home = text(&home);
    while home.last().is_some_and(|&c| c == cp('\\') || c == cp('/')) {
        home.pop();
    }
    home.extend_from_slice(slice(p, 1, p.len()));
    home
}

/// `expanduser(p, fl)`.
#[must_use]
pub(crate) fn expanduser_for(p: &[u32], os: Os) -> Text {
    match os {
        Os::Unix => expanduser(p),
        Os::Windows => nt_expanduser(p),
    }
}

/// `prog_name(t, fl)`: the name of the program word `t`: its basename. On Windows the last component after `\` or `/` (no drive, no `:stream`, no trailing dots or spaces),
/// case-folded, without one of `.exe`, `.cmd`, `.bat`, `.com`.
#[must_use]
pub(crate) fn prog_name(t: &[u32], os: Os) -> Text {
    if os == Os::Unix {
        return basename(t).to_vec();
    }
    let start = t.iter().rposition(|&c| c == cp('/') || c == cp('\\')).map_or(0, |k| k + 1);
    let mut name = slice(t, start, t.len());
    if is_drive(name) {
        name = slice(name, 2, name.len());
    }
    let cut = name.iter().position(|&c| c == cp(':')).unwrap_or(name.len());
    let name = slice(name, 0, cut);
    let end = name.iter().rposition(|&c| c != cp(' ') && c != cp('.')).map_or(0, |k| k + 1);
    let folded = nt_fold(slice(name, 0, end));
    for ext in NT_EXE {
        let n = ext.chars().count();
        if folded.len() > n && starts_at(&folded, folded.len() - n, ext) {
            return slice(&folded, 0, folded.len() - n).to_vec();
        }
    }
    folded
}

/// `display_name(p, fl)`: the basename of `p` as a message shows it (Windows: after the last `\` or `/`, without a drive).
#[must_use]
pub(crate) fn display_name(p: &[u32], os: Os) -> Text {
    if os == Os::Unix {
        return basename(p).to_vec();
    }
    let slashed: Text = p.iter().map(|&c| if c == cp('/') { cp('\\') } else { c }).collect();
    let start = slashed.iter().rposition(|&c| c == cp('\\')).map_or(0, |k| k + 1);
    let name = slice(&slashed, start, slashed.len());
    if !has_char(&slashed, '\\') && is_drive(name) { slice(name, 2, name.len()).to_vec() } else { name.to_vec() }
}
