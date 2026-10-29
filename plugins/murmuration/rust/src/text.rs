//! Python-`str` semantics over code points: the text type, the character classes of `re` and the path helpers of `posixpath` that `budget` and `handback` use.
//!
//! A `Text` is a vector of code points, not of Rust `char`, because a Python `str` read from JSON can hold a lone surrogate, which a `char` cannot.

use crate::tables::{DIGIT, SPACE};

/// A Python `str`: code points in `0..=0x10FFFF`, surrogates allowed.
pub(crate) type Text = Vec<u32>;

/// A failure that the Python script would have raised as an exception.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub(crate) enum Fault {
    /// `ValueError`: a NUL in a path, or an integer of more than 4300 digits.
    Value,
    /// `RecursionError`: JSON nested deeper than the interpreter allows.
    Recursion,
    /// `JSONDecodeError`: the event is not JSON.
    JsonDecode,
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

/// `t.strip()`.
#[must_use]
pub(crate) fn strip(t: &[u32]) -> &[u32] {
    let a = t.iter().position(|&c| !is_space(c)).unwrap_or(t.len());
    let b = t.iter().rposition(|&c| !is_space(c)).map_or(a, |p| p + 1);
    slice(t, a, b)
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
    let mut out: Vec<&[u32]> = Vec::new(); // slices of `p`: a path of a thousand components is read once for each command that follows a `cd`
    for comp in p.split(|&c| c == slash) {
        if comp.is_empty() || eq(comp, ".") {
            continue;
        }
        let dotdot = eq(comp, "..");
        let last_dotdot = out.last().is_some_and(|l| eq(l, ".."));
        if !dotdot || (initial == 0 && out.is_empty()) || last_dotdot {
            out.push(comp);
        } else if !out.is_empty() {
            out.pop();
        }
    }
    let mut path = Text::with_capacity(p.len());
    for (i, c) in out.iter().enumerate() {
        if i > 0 {
            path.push(slash);
        }
        path.extend_from_slice(c);
    }
    if initial > 0 {
        let mut head = vec![slash; initial];
        head.extend(path);
        path = head;
    }
    if path.is_empty() { text(".") } else { path }
}
