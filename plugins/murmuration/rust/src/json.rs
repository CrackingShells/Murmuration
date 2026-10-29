//! A JSON reader and writer with the behaviour of Python's `json.loads` and `json.dumps` (default arguments) where the hooks can see it.
//!
//! Differences from strict JSON that Python has and this reader copies: `NaN`, `Infinity` and `-Infinity` are numbers, a lone surrogate escape is kept,
//! a duplicate key keeps its last value, an integer of more than 4300 digits raises `ValueError`, and nesting of 9998 containers raises `RecursionError`.

use crate::text::{cp, text, Fault, Text};

/// Containers that may be open at once; Python 3.12's C scanner raises `RecursionError` at this depth.
const MAX_DEPTH: usize = 9998;
/// Digits of an integer literal that Python 3.12 converts before it raises `ValueError`.
const MAX_INT_DIGITS: usize = 4300;

/// A parsed JSON value.
#[derive(Debug, Clone)]
#[non_exhaustive]
pub(crate) enum Value {
    /// `null`
    Null,
    /// `true` or `false`
    Bool(bool),
    /// An integer literal: its decimal text (without a leading `-` on zero) and whether it is zero.
    Int(String),
    /// A number with a fraction or an exponent, or `NaN`, `Infinity`.
    Float(f64),
    /// A string.
    Str(Text),
    /// An array.
    Arr(Vec<Value>),
    /// An object, in first-insertion order of its keys, each key holding its last value.
    Obj(Vec<(Text, Value)>),
}

impl Value {
    /// Python truthiness.
    #[must_use]
    pub(crate) fn truthy(&self) -> bool {
        match self {
            Self::Null => false,
            Self::Bool(b) => *b,
            Self::Int(s) => s != "0",
            Self::Float(f) => *f != 0.0,
            Self::Str(s) => !s.is_empty(),
            Self::Arr(a) => !a.is_empty(),
            Self::Obj(o) => !o.is_empty(),
        }
    }

    /// `dict.get(key)` on an object; `None` when the key is absent or the value is not an object.
    #[must_use]
    pub(crate) fn get(&self, key: &str) -> Option<&Self> {
        let Self::Obj(o) = self else {
            return None;
        };
        let k = text(key);
        o.iter().find(|(name, _)| *name == k).map(|(_, v)| v)
    }
}

struct Reader {
    s: Vec<char>,
    i: usize,
}

impl Reader {
    fn peek(&self) -> Option<char> {
        self.s.get(self.i).copied()
    }

    fn ws(&mut self) {
        while matches!(self.peek(), Some(' ' | '\t' | '\n' | '\r')) {
            self.i += 1;
        }
    }

    fn lit(&mut self, word: &str) -> bool {
        let n = word.chars().count();
        let ok = self.s.get(self.i..self.i + n).is_some_and(|w| w.iter().copied().eq(word.chars()));
        if ok {
            self.i += n;
        }
        ok
    }

    fn hex4(&mut self) -> Result<u32, Fault> {
        let mut v = 0u32;
        for _ in 0..4 {
            let d = self.peek().and_then(|c| c.to_digit(16)).ok_or(Fault::JsonDecode)?;
            v = v * 16 + d;
            self.i += 1;
        }
        Ok(v)
    }

    fn string(&mut self) -> Result<Text, Fault> {
        // the opening quote is already consumed
        let mut out = Text::new();
        loop {
            let c = self.peek().ok_or(Fault::JsonDecode)?;
            self.i += 1;
            match c {
                '"' => return Ok(out),
                '\\' => {
                    let e = self.peek().ok_or(Fault::JsonDecode)?;
                    self.i += 1;
                    match e {
                        '"' | '\\' | '/' => out.push(cp(e)),
                        'b' => out.push(8),
                        'f' => out.push(12),
                        'n' => out.push(10),
                        'r' => out.push(13),
                        't' => out.push(9),
                        'u' => {
                            let hi = self.hex4()?;
                            if (0xD800..=0xDBFF).contains(&hi) && self.peek() == Some('\\') && self.s.get(self.i + 1) == Some(&'u') {
                                let save = self.i;
                                self.i += 2;
                                let lo = self.hex4()?;
                                if (0xDC00..=0xDFFF).contains(&lo) {
                                    out.push(0x10000 + ((hi - 0xD800) << 10) + (lo - 0xDC00));
                                } else {
                                    self.i = save;
                                    out.push(hi);
                                }
                            } else {
                                out.push(hi);
                            }
                        }
                        _ => return Err(Fault::JsonDecode),
                    }
                }
                c if u32::from(c) < 0x20 => return Err(Fault::JsonDecode),
                c => out.push(cp(c)),
            }
        }
    }

    fn digits(&mut self) -> usize {
        let start = self.i;
        while self.peek().is_some_and(|c| c.is_ascii_digit()) {
            self.i += 1;
        }
        self.i - start
    }

    fn number(&mut self) -> Result<Value, Fault> {
        let start = self.i;
        if self.peek() == Some('-') {
            self.i += 1;
        }
        match self.peek() {
            Some('0') => self.i += 1,
            Some('1'..='9') => {
                self.digits();
            }
            _ => return Err(Fault::JsonDecode),
        }
        let int_end = self.i;
        let mut is_float = false;
        if self.peek() == Some('.') && self.s.get(self.i + 1).is_some_and(char::is_ascii_digit) {
            self.i += 1;
            self.digits();
            is_float = true;
        }
        if matches!(self.peek(), Some('e' | 'E')) {
            let save = self.i;
            self.i += 1;
            if matches!(self.peek(), Some('+' | '-')) {
                self.i += 1;
            }
            if self.digits() == 0 {
                self.i = save;
            } else {
                is_float = true;
            }
        }
        let lit: String = self.s.get(start..self.i).unwrap_or_default().iter().collect();
        if is_float {
            return Ok(Value::Float(lit.parse::<f64>().map_err(|_| Fault::JsonDecode)?));
        }
        let int_text: String = self.s.get(start..int_end).unwrap_or_default().iter().collect();
        if int_text.trim_start_matches('-').len() > MAX_INT_DIGITS {
            return Err(Fault::Value);
        }
        Ok(Value::Int(if int_text == "-0" { String::from("0") } else { int_text }))
    }

    fn value(&mut self, depth: usize) -> Result<Value, Fault> {
        match self.peek().ok_or(Fault::JsonDecode)? {
            '"' => {
                self.i += 1;
                Ok(Value::Str(self.string()?))
            }
            '{' => {
                if depth + 1 >= MAX_DEPTH {
                    return Err(Fault::Recursion);
                }
                self.i += 1;
                self.object(depth + 1)
            }
            '[' => {
                if depth + 1 >= MAX_DEPTH {
                    return Err(Fault::Recursion);
                }
                self.i += 1;
                self.array(depth + 1)
            }
            'n' if self.lit("null") => Ok(Value::Null),
            't' if self.lit("true") => Ok(Value::Bool(true)),
            'f' if self.lit("false") => Ok(Value::Bool(false)),
            'N' if self.lit("NaN") => Ok(Value::Float(f64::NAN)),
            'I' if self.lit("Infinity") => Ok(Value::Float(f64::INFINITY)),
            '-' if self.lit("-Infinity") => Ok(Value::Float(f64::NEG_INFINITY)),
            '-' | '0'..='9' => self.number(),
            _ => Err(Fault::JsonDecode),
        }
    }

    fn array(&mut self, depth: usize) -> Result<Value, Fault> {
        let mut items = Vec::new();
        self.ws();
        if self.peek() == Some(']') {
            self.i += 1;
            return Ok(Value::Arr(items));
        }
        loop {
            self.ws();
            items.push(self.value(depth)?);
            self.ws();
            match self.peek() {
                Some(',') => self.i += 1,
                Some(']') => {
                    self.i += 1;
                    return Ok(Value::Arr(items));
                }
                _ => return Err(Fault::JsonDecode),
            }
        }
    }

    fn object(&mut self, depth: usize) -> Result<Value, Fault> {
        let mut items: Vec<(Text, Value)> = Vec::new();
        self.ws();
        if self.peek() == Some('}') {
            self.i += 1;
            return Ok(Value::Obj(items));
        }
        loop {
            self.ws();
            if self.peek() != Some('"') {
                return Err(Fault::JsonDecode);
            }
            self.i += 1;
            let key = self.string()?;
            self.ws();
            if self.peek() != Some(':') {
                return Err(Fault::JsonDecode);
            }
            self.i += 1;
            self.ws();
            let v = self.value(depth)?;
            if let Some(slot) = items.iter_mut().find(|(k, _)| *k == key) {
                slot.1 = v;
            } else {
                items.push((key, v));
            }
            self.ws();
            match self.peek() {
                Some(',') => self.i += 1,
                Some('}') => {
                    self.i += 1;
                    return Ok(Value::Obj(items));
                }
                _ => return Err(Fault::JsonDecode),
            }
        }
    }
}

/// `json.loads(raw)`.
///
/// # Errors
/// Returns the [`Fault`] Python would raise: `JSONDecodeError` for malformed text, `RecursionError` for deep nesting, `ValueError` for a huge integer.
pub(crate) fn loads(raw: &str) -> Result<Value, Fault> {
    let mut r = Reader { s: raw.chars().collect(), i: 0 };
    r.ws();
    let v = r.value(0)?;
    r.ws();
    if r.i != r.s.len() {
        return Err(Fault::JsonDecode);
    }
    Ok(v)
}

/// Appends a string as `json.dumps` writes it with `ensure_ascii`.
pub(crate) fn dump_str(t: &[u32], out: &mut String) {
    out.push('"');
    for &c in t {
        match c {
            0x22 => out.push_str("\\\""),
            0x5C => out.push_str("\\\\"),
            0x0A => out.push_str("\\n"),
            0x0D => out.push_str("\\r"),
            0x09 => out.push_str("\\t"),
            0x08 => out.push_str("\\b"),
            0x0C => out.push_str("\\f"),
            0x20..=0x7E => out.push(char::from_u32(c).unwrap_or('?')),
            0x10000.. => {
                let v = c - 0x10000;
                out.push_str(&format!("\\u{:04x}\\u{:04x}", 0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF)));
            }
            _ => out.push_str(&format!("\\u{c:04x}")),
        }
    }
    out.push('"');
}

/// Python's `repr` of a finite float, as `json.dumps` writes it.
fn float_repr(f: f64) -> String {
    if f.is_nan() {
        return String::from("NaN");
    }
    if f.is_infinite() {
        return String::from(if f > 0.0 { "Infinity" } else { "-Infinity" });
    }
    let sci = format!("{f:e}");
    let (mant, exp) = sci.split_once('e').unwrap_or((&sci, "0"));
    let exp: i32 = exp.parse().unwrap_or(0);
    let neg = mant.starts_with('-');
    let digits: String = mant.chars().filter(char::is_ascii_digit).collect();
    let sign = if neg { "-" } else { "" };
    if (-4..16).contains(&exp) {
        if exp < 0 {
            let zeros = "0".repeat(usize::try_from(-exp - 1).unwrap_or(0));
            return format!("{sign}0.{zeros}{digits}");
        }
        let int_len = usize::try_from(exp).unwrap_or(0) + 1;
        if digits.len() <= int_len {
            let zeros = "0".repeat(int_len - digits.len());
            return format!("{sign}{digits}{zeros}.0");
        }
        let (a, b) = digits.split_at(int_len);
        return format!("{sign}{a}.{b}");
    }
    let (first, rest) = digits.split_at(1);
    let frac = if rest.is_empty() { String::new() } else { format!(".{rest}") };
    let esign = if exp < 0 { '-' } else { '+' };
    format!("{sign}{first}{frac}e{esign}{:02}", exp.abs())
}

/// Appends a value as `json.dumps` writes it (default separators, `ensure_ascii`).
pub(crate) fn dump(v: &Value, out: &mut String) {
    match v {
        Value::Null => out.push_str("null"),
        Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        Value::Int(s) => out.push_str(s),
        Value::Float(f) => out.push_str(&float_repr(*f)),
        Value::Str(s) => dump_str(s, out),
        Value::Arr(a) => {
            out.push('[');
            for (i, x) in a.iter().enumerate() {
                if i > 0 {
                    out.push_str(", ");
                }
                dump(x, out);
            }
            out.push(']');
        }
        Value::Obj(o) => {
            out.push('{');
            for (i, (k, x)) in o.iter().enumerate() {
                if i > 0 {
                    out.push_str(", ");
                }
                dump_str(k, out);
                out.push_str(": ");
                dump(x, out);
            }
            out.push('}');
        }
    }
}
