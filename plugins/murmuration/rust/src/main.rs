//! `murmuration`: the Murmuration plugin's hook entry points in one binary.
//!
//! ```text
//! murmuration guard      read a PreToolUse event on stdin, deny on stdout or say nothing (the port of scripts/permission_guard.py)
//! murmuration --version
//! ```
//!
//! murmuration budget    the port of scripts/budget.py; murmuration handback    the port of scripts/handback.py.
//! An event the port does not model is handed to the Python script (`$CLAUDE_PLUGIN_ROOT/scripts/run_hook.py`) before anything is written.

#![deny(unsafe_code)]
#![deny(warnings)]

mod budget;
mod guard;
mod handback;
mod hook;
mod json;
mod platform;
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

/// Runs the Python script for an event the port does not model, with the same stdin; its stdout and exit code are ours.
fn delegate(which: &str, raw: &[u8]) -> ExitCode {
    use std::process::{Command, Stdio};
    #[cfg(feature = "testclock")]
    if let Some(p) = std::env::var_os("MURMURATION_DELEGATE_LOG") {
        if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(p) {
            let _ = writeln!(f, "{which}");
        }
    }
    let Some(root) = std::env::var_os("CLAUDE_PLUGIN_ROOT").filter(|r| !r.is_empty()) else {
        return ExitCode::SUCCESS;
    };
    let script = std::path::Path::new(&root).join("scripts").join("run_hook.py");
    let mut cmd = Command::new(platform::python_cmd());
    cmd.arg("-S").arg("-I");
    #[cfg(feature = "testclock")]
    if let Some(shim) = std::env::var_os("MURMURATION_DELEGATE_SHIM") {
        // the replay's fixed clock for the Python side
        cmd.arg(shim).arg(std::path::Path::new(&root).join("scripts")).arg(which);
    } else {
        cmd.arg(&script).arg(which);
    }
    #[cfg(not(feature = "testclock"))]
    cmd.arg(&script).arg(which);
    let Ok(mut child) = cmd.stdin(Stdio::piped()).spawn() else {
        return ExitCode::SUCCESS;
    };
    if let Some(mut stdin) = child.stdin.take() {
        let _ = stdin.write_all(raw);
    }
    match child.wait().ok().and_then(|s| s.code()) {
        Some(0) | None => ExitCode::SUCCESS,
        Some(c) => ExitCode::from(u8::try_from(c).unwrap_or(1)),
    }
}

fn run_hook(which: &'static str) -> ExitCode {
    let mut raw = Vec::new();
    if std::io::stdin().read_to_end(&mut raw).is_err() {
        return ExitCode::SUCCESS;
    }
    let input = raw.clone();
    let worker = std::thread::Builder::new().stack_size(STACK_BYTES).spawn(move || {
        let Ok(s) = String::from_utf8(input) else {
            return Ok(None);
        };
        let s = if s.is_empty() { String::from("{}") } else { s };
        let Ok(event) = json::loads(&s) else {
            return Ok(None);
        };
        if which == "budget" {
            budget::run(&event)
        } else {
            handback::run(&event)
        }
    });
    match worker.map(std::thread::JoinHandle::join) {
        Ok(Ok(Ok(Some(out)))) => {
            let mut o = std::io::stdout().lock();
            let _ = o.write_all(out.as_bytes()).and_then(|()| o.flush());
            ExitCode::SUCCESS
        }
        Ok(Ok(Ok(None) | Err(hook::Stop::Silent))) => ExitCode::SUCCESS,
        Ok(Ok(Err(hook::Stop::Delegate))) | Ok(Err(_)) | Err(_) => delegate(which, &raw),
    }
}

fn main() -> ExitCode {
    let mut args = std::env::args().skip(1);
    match args.next().as_deref() {
        Some("guard") => run_guard(),
        Some("budget") => run_hook("budget"),
        Some("handback") => run_hook("handback"),
        Some("--version" | "-V") => {
            println!("murmuration {}", env!("CARGO_PKG_VERSION"));
            ExitCode::SUCCESS
        }
        _ => {
            eprintln!("usage: murmuration guard | budget | handback | --version");
            ExitCode::from(2)
        }
    }
}
