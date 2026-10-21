//! `murmuration`: the Murmuration plugin's hook entry points in one binary.
//!
//! ```text
//! murmuration guard      read a PreToolUse event on stdin, deny on stdout or say nothing (the port of scripts/permission_guard.py)
//! murmuration --version
//! ```
//!
//! `budget` and `handback` are the planned next subcommands (SA1); they are not built.

#![forbid(unsafe_code)]
#![deny(warnings)]

mod guard;
mod json;
mod shlex;
mod tables;
mod text;

use std::io::{Read, Write};
use std::process::ExitCode;

/// Stack for the decision thread: JSON nested to the interpreter's limit recurses deeply.
const STACK_BYTES: usize = 256 * 1024 * 1024;

fn deny_internal(what: &str) -> guard::Answer {
    let event = format!("{{\"tool_name\": null, \"tool_input\": \"{what}\"}}");
    guard::run(&event)
}

fn run_guard() -> ExitCode {
    let mut raw = Vec::new();
    if let Err(e) = std::io::stdin().read_to_end(&mut raw) {
        eprintln!("murmuration guard: failed to read stdin: {e}");
        return ExitCode::from(1);
    }
    let Ok(raw) = String::from_utf8(raw) else {
        eprintln!("murmuration guard: stdin is not valid UTF-8 (UnicodeDecodeError)");
        return ExitCode::from(1);
    };
    let worker = std::thread::Builder::new().stack_size(STACK_BYTES).spawn(move || guard::run(&raw));
    let answer = match worker.map(std::thread::JoinHandle::join) {
        Ok(Ok(a)) => a,
        // a panic in the decision: fail closed with a denial the model can read
        Ok(Err(_)) | Err(_) => deny_internal("internal error"),
    };
    if let Some(log) = std::env::var_os("MURMURATION_GUARD_LOG").filter(|p| !p.is_empty()) {
        if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(log) {
            // a failed log write is ignored, as in the Python guard (`except OSError: pass`)
            let _ = writeln!(f, "{}", answer.log_line);
        }
    }
    if !answer.stdout.is_empty() {
        let mut out = std::io::stdout().lock();
        if out.write_all(answer.stdout.as_bytes()).and_then(|()| out.flush()).is_err() {
            return ExitCode::from(1);
        }
    }
    ExitCode::SUCCESS
}

fn main() -> ExitCode {
    let mut args = std::env::args().skip(1);
    match args.next().as_deref() {
        Some("guard") => run_guard(),
        Some("--version" | "-V") => {
            println!("murmuration {}", env!("CARGO_PKG_VERSION"));
            ExitCode::SUCCESS
        }
        _ => {
            eprintln!("usage: murmuration guard | --version");
            ExitCode::from(2)
        }
    }
}
