//! Python-`str` semantics over code points: the text type, the character classes of `re`, and the path helpers of `posixpath` that the guard uses.
//!
//! A `Text` is a vector of code points, not of Rust `char`, because a Python `str` read from JSON can hold a lone surrogate, which a `char` cannot.

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
    let home = match std::env::var_os("HOME") {
        Some(h) => h.to_string_lossy().to_string(),
        None => match std::env::home_dir() {
            Some(h) => h.to_string_lossy().to_string(),
            None => return p.to_vec(),
        },
    };
    let mut home = text(&home);
    while at(&home, home.len().wrapping_sub(1)) == Some(cp('/')) {
        home.pop();
    }
    home.extend_from_slice(slice(p, i, p.len()));
    if home.is_empty() { text("/") } else { home }
}
