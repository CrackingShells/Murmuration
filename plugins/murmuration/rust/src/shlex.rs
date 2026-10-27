//! Python's `shlex.split(s, posix=True)` (comments off), as a state machine over code points.

use crate::text::{cp, Text};

enum State {
    Blank,
    Word,
    Single,
    Double,
    Escape,
}

/// Splits `s` as `shlex.split` does.
///
/// # Errors
/// Returns `Err(())` where Python raises `ValueError` (an open quote or a trailing backslash).
pub(crate) fn split(s: &[u32]) -> Result<Vec<Text>, ()> {
    let mut out: Vec<Text> = Vec::new();
    let mut token = Text::new();
    let mut state = State::Blank;
    // the state to return to after an escape: `true` means the word state, otherwise the quote that was open
    let mut escaped_in_quote: Option<u32> = None;
    let blank = |c: u32| c == cp(' ') || c == cp('\t') || c == cp('\r') || c == cp('\n');
    let backslash = cp('\\');
    let squote = cp('\'');
    let dquote = cp('"');
    let emit = |token: &mut Text, out: &mut Vec<Text>| out.push(std::mem::take(token));
    for &c in s {
        match state {
            State::Blank => {
                if blank(c) {
                    continue;
                } else if c == backslash {
                    escaped_in_quote = None;
                    state = State::Escape;
                } else if c == squote {
                    state = State::Single;
                } else if c == dquote {
                    state = State::Double;
                } else {
                    token.push(c);
                    state = State::Word;
                }
            }
            State::Word => {
                if blank(c) {
                    emit(&mut token, &mut out);
                    state = State::Blank;
                } else if c == squote {
                    state = State::Single;
                } else if c == dquote {
                    state = State::Double;
                } else if c == backslash {
                    escaped_in_quote = None;
                    state = State::Escape;
                } else {
                    token.push(c);
                }
            }
            State::Single => {
                if c == squote {
                    state = State::Word;
                } else {
                    token.push(c);
                }
            }
            State::Double => {
                if c == dquote {
                    state = State::Word;
                } else if c == backslash {
                    escaped_in_quote = Some(dquote);
                    state = State::Escape;
                } else {
                    token.push(c);
                }
            }
            State::Escape => {
                // inside double quotes only the quote itself or the backslash may be escaped; otherwise the backslash stays
                if let Some(q) = escaped_in_quote {
                    if c != backslash && c != q {
                        token.push(backslash);
                    }
                    token.push(c);
                    state = State::Double;
                } else {
                    token.push(c);
                    state = State::Word;
                }
            }
        }
    }
    match state {
        State::Blank => {}
        State::Word => emit(&mut token, &mut out),
        State::Single | State::Double | State::Escape => return Err(()),
    }
    Ok(out)
}
