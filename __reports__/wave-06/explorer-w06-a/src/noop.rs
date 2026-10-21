use std::io::Read;
use std::time::{SystemTime, UNIX_EPOCH};
fn now() -> f64 { SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs_f64() * 1000.0 }
fn main() {
    let t0 = now();
    let mut s = String::new();
    let _ = std::io::stdin().read_to_string(&mut s);
    let tag = std::env::args().nth(1).unwrap_or_default();
    println!("noop-rs {}", tag);
    if let Ok(log) = std::env::var("W06_LOG") {
        use std::io::Write;
        if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(log) {
            let _ = writeln!(f, "{{\"lang\":\"rs\",\"tag\":\"{}\",\"t0_ms\":{:.3},\"t1_ms\":{:.3},\"pid\":{}}}", tag, t0, now(), std::process::id());
        }
    }
}
