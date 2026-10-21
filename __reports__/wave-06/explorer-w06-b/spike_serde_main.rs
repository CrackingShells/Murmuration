use std::io::Read;
fn main() {
    let mut b = String::new();
    let _ = std::io::stdin().read_to_string(&mut b);
    let v: serde_json::Value = serde_json::from_str(&b).unwrap_or(serde_json::Value::Null);
    if v.get("agent_id").and_then(|x| x.as_str()).is_some() { println!("{}", v["hook_event_name"]); }
}
