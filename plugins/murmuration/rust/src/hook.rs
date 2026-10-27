//! What `budget` and `handback` share: the stop signals, Python-compatible number and time formatting, the lab's files (log, state folder), the agent's name, SHA-256.
//!
//! An event the port does not model resolves to `Stop::Delegate`: the caller runs the Python script on the same stdin before any file was written.

use crate::json::{self, Value};
use crate::text::{self, text, Text};
use std::io::Write as _;
use std::path::{Path, PathBuf};

/// Why the port stops.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum Stop {
    /// The shape is not modeled: hand the event to the Python script.
    Delegate,
    /// Python would have raised an exception that its `main` swallows: exit 0, say nothing.
    Silent,
}

pub(crate) type R<T> = Result<T, Stop>;

impl From<std::io::Error> for Stop {
    fn from(_: std::io::Error) -> Self {
        Self::Silent
    }
}

/// A Python number that is either the int `0` (what `sum([])` gives) or a float.
#[derive(Debug, Clone, Copy)]
pub(crate) enum Num {
    /// the int 0
    I0,
    /// a float
    F(f64),
}

impl Num {
    pub(crate) fn f(self) -> f64 {
        match self {
            Self::I0 => 0.0,
            Self::F(x) => x,
        }
    }

    /// `self - other` with Python's int/float typing.
    pub(crate) fn sub(self, other: Self) -> Self {
        match (self, other) {
            (Self::I0, Self::I0) => Self::I0,
            _ => Self::F(self.f() - other.f()),
        }
    }

    /// `round(self, nd)`.
    pub(crate) fn round(self, nd: usize) -> Self {
        match self {
            Self::I0 => Self::I0,
            Self::F(x) => Self::F(round(x, nd)),
        }
    }
}

/// `round(x, nd)` of a float: the correctly rounded decimal, read back.
pub(crate) fn round(x: f64, nd: usize) -> f64 {
    if !x.is_finite() {
        return x;
    }
    format!("{x:.nd$}").parse().unwrap_or(x)
}

/// `sum(xs)` of Python 3.12 over floats (Neumaier compensated); the int 0 when empty.
pub(crate) fn sum(xs: &[f64]) -> Num {
    if xs.is_empty() {
        return Num::I0;
    }
    let (mut s, mut c) = (0.0f64, 0.0f64);
    for &x in xs {
        let t = s + x;
        if s.abs() >= x.abs() {
            c += (s - t) + x;
        } else {
            c += (x - t) + s;
        }
        s = t;
    }
    if c != 0.0 && c.is_finite() {
        s += c;
    }
    Num::F(s)
}

/// `"%g" % x` (six significant digits).
pub(crate) fn fmt_g(x: f64) -> String {
    if x == 0.0 {
        return String::from(if x.is_sign_negative() { "-0" } else { "0" });
    }
    let sci = format!("{x:.5e}");
    let (mant, exp) = sci.split_once('e').unwrap_or((&sci, "0"));
    let exp: i32 = exp.parse().unwrap_or(0);
    if !(-4..6).contains(&exp) {
        let mut m = mant.to_string();
        if m.contains('.') {
            m = m.trim_end_matches('0').trim_end_matches('.').to_string();
        }
        return format!("{m}e{}{:02}", if exp < 0 { '-' } else { '+' }, exp.abs());
    }
    let dec = usize::try_from(5 - exp).unwrap_or(0);
    let mut s = format!("{x:.dec$}");
    if s.contains('.') {
        s = s.trim_end_matches('0').trim_end_matches('.').to_string();
    }
    s
}

// ---- time ----

/// The clock: the system's, or (test builds only) the `MURMURATION_NOW` of the environment, the same value Python's `time.time` is set to by the replay wrapper.
pub(crate) fn now() -> f64 {
    #[cfg(feature = "testclock")]
    if let Some(v) = std::env::var("MURMURATION_NOW").ok().and_then(|v| v.parse::<f64>().ok()) {
        return v;
    }
    std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map_or(0.0, |d| d.as_secs_f64())
}

/// Whole microseconds since the epoch of a clock reading, rounded to nearest as `datetime.fromtimestamp` does.
pub(crate) fn micros(t: f64) -> i64 {
    let whole = t.floor();
    let frac = ((t - whole) * 1e6).round_ties_even();
    // CAST: epoch seconds of this century fit i64
    (whole as i64) * 1_000_000 + frac as i64
}

fn civil(days: i64) -> (i64, i64, i64) {
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    (yoe + era * 400 + i64::from(m <= 2), m, d)
}

fn days_from_civil(y: i64, m: i64, d: i64) -> i64 {
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let yoe = y.rem_euclid(400);
    let doy = (153 * (if m > 2 { m - 3 } else { m + 9 }) + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146_097 + doe - 719_468
}

/// `datetime.now().astimezone().isoformat(timespec=...)` for the clock reading `t`: `ms` true for milliseconds, false for seconds. Fractions are truncated, as `isoformat` does.
pub(crate) fn iso_local(t: f64, ms: bool) -> String {
    let us = micros(t);
    let secs = us.div_euclid(1_000_000);
    let off = crate::platform::local_offset(secs);
    let loc = secs + off;
    let (y, mo, d) = civil(loc.div_euclid(86_400));
    let sod = loc.rem_euclid(86_400);
    let mut s = format!("{y:04}-{mo:02}-{d:02}T{:02}:{:02}:{:02}", sod / 3600, sod % 3600 / 60, sod % 60);
    if ms {
        s.push_str(&format!(".{:03}", us.rem_euclid(1_000_000) / 1000));
    }
    let a = off.abs();
    s.push(if off < 0 { '-' } else { '+' });
    s.push_str(&format!("{:02}:{:02}", a / 3600, a % 3600 / 60));
    if a % 60 != 0 {
        s.push_str(&format!(":{:02}", a % 60));
    }
    s
}

/// The seconds since the epoch, as microseconds, of an ISO time of the exact forms `iso_local` and the platform write
/// (`YYYY-MM-DDTHH:MM:SS[.f+](Z|+HH:MM)`); `Ok(None)` when it is of that form but not a valid time (Python raises `ValueError`); `Delegate` for any other form.
pub(crate) fn parse_iso(s: &str) -> R<Option<i64>> {
    let b = s.as_bytes();
    let digit = |i: usize| b.get(i).is_some_and(u8::is_ascii_digit);
    let num = |i: usize, n: usize| s.get(i..i + n).and_then(|x| x.parse::<i64>().ok()).unwrap_or(0);
    let shape = b.len() >= 20
        && (0..4).all(digit)
        && b[4] == b'-'
        && (5..7).all(digit)
        && b[7] == b'-'
        && (8..10).all(digit)
        && b[10] == b'T'
        && (11..13).all(digit)
        && b[13] == b':'
        && (14..16).all(digit)
        && b[16] == b':'
        && (17..19).all(digit);
    if !shape {
        return Err(Stop::Delegate);
    }
    let mut i = 19;
    let mut frac = 0i64;
    if b[i] == b'.' {
        let start = i + 1;
        i = start;
        while digit(i) {
            i += 1;
        }
        if i == start {
            return Err(Stop::Delegate);
        }
        let mut d: String = s[start..i].chars().take(6).collect();
        while d.len() < 6 {
            d.push('0');
        }
        frac = d.parse().unwrap_or(0);
    }
    let off = match &s[i..] {
        "Z" => 0,
        tz if tz.len() == 6 && (tz.starts_with('+') || tz.starts_with('-')) && tz.as_bytes()[3] == b':' && tz[1..3].bytes().all(|c| c.is_ascii_digit()) && tz[4..6].bytes().all(|c| c.is_ascii_digit()) => {
            let (h, m) = (num(i + 1, 2), num(i + 4, 2));
            if h > 23 || m > 59 {
                return Ok(None);
            }
            (h * 3600 + m * 60) * if tz.starts_with('-') { -1 } else { 1 }
        }
        _ => return Err(Stop::Delegate),
    };
    let (y, mo, d, hh, mi, ss) = (num(0, 4), num(5, 2), num(8, 2), num(11, 2), num(14, 2), num(17, 2));
    let leap = (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
    let dim = [31, if leap { 29 } else { 28 }, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    if y < 1 || !(1..=12).contains(&mo) || d < 1 || d > dim[usize::try_from(mo - 1).unwrap_or(0)] || hh > 23 || mi > 59 || ss > 59 {
        return Ok(None);
    }
    let secs = days_from_civil(y, mo, d) * 86_400 + hh * 3600 + mi * 60 + ss - off;
    Ok(Some(secs * 1_000_000 + frac))
}

// ---- SHA-256 ----

/// Lowercase hex SHA-256 of `data`.
pub(crate) fn sha256_hex(data: &[u8]) -> String {
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7,
        0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
        0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819,
        0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ];
    let mut h: [u32; 8] = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    let mut msg = data.to_vec();
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&((data.len() as u64) * 8).to_be_bytes());
    for chunk in msg.chunks(64) {
        let mut w = [0u32; 64];
        for (i, c) in chunk.chunks(4).enumerate() {
            w[i] = u32::from_be_bytes([c[0], c[1], c[2], c[3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let mut v = h;
        for i in 0..64 {
            let s1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
            let t1 = v[7].wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(maj);
            v = [t1.wrapping_add(t2), v[0], v[1], v[2], v[3].wrapping_add(t1), v[4], v[5], v[6]];
        }
        for i in 0..8 {
            h[i] = h[i].wrapping_add(v[i]);
        }
    }
    h.iter().map(|x| format!("{x:08x}")).collect()
}

// ---- values and strings ----

/// A value the Python code reads with `event.get(key)` and uses as a string: `Some` for a string, `None` for null or absent, `Delegate` for any other type.
pub(crate) fn opt_text(v: Option<&Value>) -> R<Option<&Text>> {
    match v {
        None | Some(Value::Null) => Ok(None),
        Some(Value::Str(t)) => Ok(Some(t)),
        Some(_) => Err(Stop::Delegate),
    }
}

/// `opt_text`, with the empty string counted as absent (Python truthiness).
pub(crate) fn truthy_text(v: Option<&Value>) -> R<Option<&Text>> {
    Ok(opt_text(v)?.filter(|t| !t.is_empty()))
}

/// A path component from a string: no lone surrogate and no NUL (Python would raise in `open`).
pub(crate) fn path_text(t: &[u32]) -> R<String> {
    if t.iter().any(|&c| (0xD800..0xE000).contains(&c) || c == 0) {
        return Err(Stop::Delegate);
    }
    Ok(text::string(t))
}

/// `dict.get(key)` where Python raises `AttributeError` on a non-dict: `Silent`.
pub(crate) fn getd<'a>(v: &'a Value, key: &str) -> R<Option<&'a Value>> {
    match v {
        Value::Obj(_) => Ok(v.get(key)),
        _ => Err(Stop::Silent),
    }
}

// ---- the lab ----

pub(crate) const STORE: &str = "__statera__";
pub(crate) const LOG: &str = "harness.jsonl";
pub(crate) const HARNESS: &str = ".harness";

fn py_dirname(p: &str) -> String {
    let i = p.rfind('/').map_or(0, |i| i + 1);
    let head = &p[..i];
    if !head.is_empty() && head.chars().any(|c| c != '/') {
        head.trim_end_matches('/').to_string()
    } else {
        head.to_string()
    }
}

fn py_abspath(p: &str) -> R<String> {
    let full = if p.starts_with('/') {
        p.to_string()
    } else {
        let cwd = std::env::current_dir().map_err(|_| Stop::Silent)?;
        format!("{}/{p}", cwd.to_string_lossy().trim_end_matches('/'))
    };
    let t = text::normpath(&text(&full));
    Ok(text::string(&t))
}

/// The nearest folder, from the event's cwd upward and then `CLAUDE_PROJECT_DIR`, that holds a `__statera__/` (`handback.lab_root`).
pub(crate) fn lab_root(cwd: Option<&Text>) -> R<Option<String>> {
    let given = match cwd {
        Some(t) if !t.is_empty() => path_text(t)?,
        _ => String::new(),
    };
    let mut p = py_abspath(&given)?;
    let mut chain = vec![p.clone()];
    for _ in 0..5 {
        p = py_dirname(&p);
        chain.push(p.clone());
    }
    chain.push(std::env::var("CLAUDE_PROJECT_DIR").unwrap_or_default());
    Ok(chain.into_iter().find(|c| !c.is_empty() && Path::new(c).join(STORE).is_dir()))
}

/// A value in a log record.
#[derive(Debug, Clone)]
pub(crate) enum J {
    S(String),
    T(Text),
    Null,
    B(bool),
    I(i64),
    F(f64),
    N(Num),
}

/// A log record: keys in the order set; `set` replaces a key as `dict(..., key=...)` does.
#[derive(Debug, Clone, Default)]
pub(crate) struct Rec(pub Vec<(String, J)>);

impl Rec {
    pub(crate) fn set(&mut self, k: &str, v: J) -> &mut Self {
        if let Some(e) = self.0.iter_mut().find(|(n, _)| n == k) {
            e.1 = v;
        } else {
            self.0.push((k.to_string(), v));
        }
        self
    }

    /// The record as `handback.dumps(record, sort_keys=True)`.
    pub(crate) fn dump_sorted(&self) -> String {
        let mut items: Vec<&(String, J)> = self.0.iter().collect();
        items.sort_by(|a, b| text(&a.0).cmp(&text(&b.0)));
        let mut out = String::from("{");
        for (i, (k, v)) in items.into_iter().enumerate() {
            if i > 0 {
                out.push_str(", ");
            }
            json::dump_str(&text(k), &mut out);
            out.push_str(": ");
            dump_j(v, &mut out);
        }
        out.push('}');
        out
    }
}

pub(crate) fn dump_j(v: &J, out: &mut String) {
    match v {
        J::S(s) => json::dump_str(&text(s), out),
        J::T(t) => json::dump_str(t, out),
        J::Null => out.push_str("null"),
        J::B(b) => out.push_str(if *b { "true" } else { "false" }),
        J::I(i) => out.push_str(&i.to_string()),
        J::F(f) => json::dump(&Value::Float(*f), out),
        J::N(Num::I0) => out.push('0'),
        J::N(Num::F(f)) => json::dump(&Value::Float(*f), out),
    }
}

/// Appends one JSON line (with `t`) to the lab's `harness.jsonl` in one write (`handback.log_line`).
pub(crate) fn log_line(root: &str, record: &Rec) -> R<()> {
    let mut r = record.clone();
    r.set("t", J::S(iso_local(now(), true)));
    let line = format!("{}\n", r.dump_sorted());
    let mut f = std::fs::OpenOptions::new().append(true).create(true).open(Path::new(root).join(STORE).join(LOG))?;
    f.write_all(line.as_bytes())?;
    Ok(())
}

/// The folder of per-agent state files, created with a `.gitignore` that ignores everything in it (`handback.harness_dir`).
pub(crate) fn harness_dir(root: &str) -> R<PathBuf> {
    let path = Path::new(root).join(STORE).join(HARNESS);
    if !path.is_dir() {
        std::fs::create_dir_all(&path)?;
        std::fs::write(path.join(".gitignore"), "*\n")?;
    }
    Ok(path)
}

// ---- the agent's name ----

const ALNUM: &str = "abcdefghijklmnopqrstuvwxyz0123456789";

fn valid_name(name: &Text) -> bool {
    let body: &[u32] = if name.last() == Some(&10) { &name[..name.len() - 1] } else { name };
    let ok = |c: u32| char::from_u32(c).is_some_and(|ch| ALNUM.contains(ch));
    !body.is_empty() && ok(body[0]) && body.iter().all(|&c| ok(c) || c == 45)
}

/// The first 20000 characters of a file as `open(p).read(20000)` gives them (strict UTF-8, read in chunks of 8192 bytes); `None` on any error.
fn read_chars(p: &str) -> Option<Text> {
    use std::io::Read as _;
    let mut f = std::fs::File::open(p).ok()?;
    let mut bytes = Vec::new();
    let mut buf = [0u8; 8192];
    loop {
        let n = f.read(&mut buf).ok()?;
        bytes.extend_from_slice(&buf[..n]);
        let eof = n == 0;
        let valid_len = match std::str::from_utf8(&bytes) {
            Ok(_) => bytes.len(),
            Err(e) if e.error_len().is_none() && !eof => e.valid_up_to(),
            Err(_) => return None,
        };
        let s = std::str::from_utf8(&bytes[..valid_len]).ok()?;
        if eof || s.chars().count() >= 20000 {
            return Some(s.chars().take(20000).map(u32::from).collect());
        }
    }
}

/// `re.search(r"Your name is ([a-z0-9-]+)", chars)`: the first match's group.
pub(crate) fn your_name(chars: &[u32]) -> Option<Text> {
    let key = text("Your name is ");
    let mut i = 0;
    while i + key.len() <= chars.len() {
        if chars[i..i + key.len()] == key[..] {
            let mut j = i + key.len();
            while j < chars.len() && char::from_u32(chars[j]).is_some_and(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-') {
                j += 1;
            }
            if j > i + key.len() {
                return Some(chars[i + key.len()..j].to_vec());
            }
        }
        i += 1;
    }
    None
}

/// `handback.agent_name`: the `.meta.json` name, else the brief's `Your name is`, else `type-id`.
pub(crate) fn agent_name(agent_id: Option<&Text>, agent_type: Option<&Text>, transcript_path: Option<&Text>, agent_transcript_path: Option<&Text>) -> R<Text> {
    let aid: Text = agent_id.filter(|t| !t.is_empty()).cloned().unwrap_or_else(|| text("unknown"));
    let stem: Option<Text> = match (agent_transcript_path.filter(|t| !t.is_empty()), transcript_path.filter(|t| !t.is_empty())) {
        (Some(p), _) => Some(p.clone()),
        (None, Some(tp)) => {
            let mut s: Text = tp[..tp.len().saturating_sub(6)].to_vec();
            if !s.is_empty() && s.last() != Some(&47) {
                s.push(47);
            }
            s.extend(text("subagents/agent-"));
            s.extend(aid.iter());
            s.extend(text(".jsonl"));
            Some(s)
        }
        _ => None,
    };
    if let Some(stem) = &stem {
        if let Ok(stem_s) = path_text(stem) {
            let meta_path = format!("{}.meta.json", text::string(&stem[..stem.len().saturating_sub(6)]));
            let meta = std::fs::read(&meta_path).ok().and_then(|b| String::from_utf8(b).ok()).and_then(|s| json::loads(&s).ok()).and_then(|v| match v.get("name") {
                Some(Value::Str(t)) => Some(t.clone()),
                _ => None,
            });
            if let Some(n) = meta.filter(valid_name) {
                return Ok(n);
            }
            let brief = read_chars(&stem_s).and_then(|chars| your_name(&chars));
            if let Some(n) = brief.filter(valid_name) {
                return Ok(n);
            }
        } else {
            return Err(Stop::Delegate);
        }
    }
    let kind: Text = agent_type.filter(|t| !t.is_empty()).cloned().unwrap_or_else(|| text("agent"));
    if kind.iter().any(|&c| c >= 0x80) {
        return Err(Stop::Delegate);
    }
    let mut out: Text = text::string(&kind).to_lowercase().chars().map(|c| if c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-' { u32::from(c) } else { 45 }).collect();
    out.push(45);
    out.extend(aid.iter().take(8));
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn g_format() {
        assert_eq!(fmt_g(80.0), "80");
        assert_eq!(fmt_g(1.5), "1.5");
        assert_eq!(fmt_g(1e6), "1e+06");
        assert_eq!(fmt_g(0.0001), "0.0001");
        assert_eq!(fmt_g(123456.0), "123456");
        assert_eq!(fmt_g(1234567.0), "1.23457e+06");
    }

    #[test]
    fn sha() {
        assert_eq!(sha256_hex(b"x"), "2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881");
    }
}
