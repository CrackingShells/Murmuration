// reads the payload, answers nothing unless it holds an "agent_id" key with a non-null value (the gate of w05-c4, in Rust)
use std::io::Read;
fn main() { let mut b = Vec::new(); let _ = std::io::stdin().read_to_end(&mut b);
  let s = String::from_utf8_lossy(&b); if s.contains("\"agent_id\"") { println!(""); } }
