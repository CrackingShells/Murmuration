// w07d_rs: parses Claude Code transcripts (the fields scripts/lab_status.py's parse_transcript keeps) from a file list, on N rayon threads, to a canonical dump (one line per message, sorted) and phase timings on stderr.
// usage: w07d_rs --files LIST [--threads N] [--dump OUT] [--reps K] [--nofilter] [--item]
//   LIST: one transcript path per line. --dump: canonical text identical to __instrumenta__/w07d_parsers.py canonical(); without it only a checksum is printed.
//   --reps K: repeat the whole parse K times in-process (the page cache is warm) and print each wall time. --nofilter: skip the substring prefilter (every line goes to serde). --item: one rayon task per file (with_max_len(1)) instead of rayon's recursive halving.
use memchr::memmem;
use rayon::prelude::*;
use serde::Deserialize;
use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Instant;

#[derive(Deserialize, Default)]
struct CacheCreation {
    ephemeral_1h_input_tokens: Option<u64>,
    ephemeral_5m_input_tokens: Option<u64>,
}
#[derive(Deserialize, Default)]
struct Usage {
    input_tokens: Option<u64>,
    output_tokens: Option<u64>,
    cache_read_input_tokens: Option<u64>,
    cache_creation_input_tokens: Option<u64>,
    cache_creation: Option<CacheCreation>,
}
#[derive(Deserialize, Default)]
struct Msg {
    id: Option<String>,
    model: Option<String>,
    stop_reason: Option<serde_json::Value>,
    usage: Option<Usage>,
}
#[derive(Deserialize, Default)]
struct Rec {
    #[serde(rename = "type")]
    kind: Option<String>,
    message: Option<Msg>,
    timestamp: Option<String>,
    #[serde(rename = "sessionId")]
    session_id: Option<String>,
    #[serde(rename = "requestId")]
    request_id: Option<String>,
    uuid: Option<String>,
    #[serde(rename = "totalCostUSD")]
    total_cost: Option<serde_json::Number>,
    #[serde(rename = "agentSetting")]
    agent_setting: Option<String>,
}

#[derive(Clone, Default)]
struct Out {
    model: String,
    i: u64,
    o: u64,
    cr: u64,
    cw: u64,
    c1: u64,
    c5: u64,
    ts: Option<String>,
    sid: Option<String>,
    fin: bool,
}

fn truthy_str(s: &Option<String>) -> Option<&str> {
    match s {
        Some(x) if !x.is_empty() => Some(x.as_str()),
        _ => None,
    }
}

struct FileRes {
    path: String,
    msgs: Vec<(String, Out)>,
    cost: Option<String>,
    setting: Option<String>,
    lines: u64,
    passed: u64,
}

static NS_READ: AtomicU64 = AtomicU64::new(0);
static NS_SCAN: AtomicU64 = AtomicU64::new(0);
static NS_PARSE: AtomicU64 = AtomicU64::new(0);

fn parse_file(path: &str, filter: bool) -> FileRes {
    let t0 = Instant::now();
    let buf = std::fs::read(path).unwrap_or_default();
    NS_READ.fetch_add(t0.elapsed().as_nanos() as u64, Ordering::Relaxed);
    let f1 = memmem::Finder::new(b"\"assistant\"");
    let f2 = memmem::Finder::new(b"\"cost-state\"");
    let f3 = memmem::Finder::new(b"\"agent-setting\"");
    let mut idx: HashMap<String, usize> = HashMap::new();
    let mut msgs: Vec<(String, Out)> = Vec::new();
    let mut cost = None;
    let mut setting: Option<String> = None;
    let (mut lines, mut passed) = (0u64, 0u64);
    let mut start = 0usize;
    let mut scan_ns = 0u64;
    let mut parse_ns = 0u64;
    while start < buf.len() {
        let t = Instant::now();
        let end = memchr::memchr(b'\n', &buf[start..]).map(|p| start + p).unwrap_or(buf.len());
        let line = &buf[start..end];
        start = end + 1;
        lines += 1;
        let keep = !filter || f1.find(line).is_some() || f2.find(line).is_some() || f3.find(line).is_some();
        scan_ns += t.elapsed().as_nanos() as u64;
        if !keep {
            continue;
        }
        passed += 1;
        let t = Instant::now();
        let rec: Rec = match serde_json::from_slice(line) {
            Ok(r) => r,
            Err(_) => continue,
        };
        parse_ns += t.elapsed().as_nanos() as u64;
        match rec.kind.as_deref() {
            Some("cost-state") if rec.total_cost.is_some() => {
                cost = rec.total_cost.as_ref().map(|n| n.to_string());
            }
            Some("agent-setting") => {
                if setting.is_none() {
                    if let Some(s) = truthy_str(&rec.agent_setting) {
                        setting = Some(s.to_string());
                    }
                }
            }
            Some("assistant") => {
                let m = match &rec.message { Some(m) => m, None => continue };
                let u = match &m.usage { Some(u) => u, None => continue };
                if m.model.as_deref() == Some("<synthetic>") {
                    continue;
                }
                let key = truthy_str(&m.id).or(truthy_str(&rec.request_id)).or(truthy_str(&rec.uuid)).map(|s| format!("s:{}", s)).unwrap_or_else(|| format!("n:{}", msgs.len()));
                let slot = match idx.get(&key) {
                    Some(&i) => i,
                    None => {
                        msgs.push((key.clone(), Out { model: m.model.clone().filter(|x| !x.is_empty()).unwrap_or_else(|| "unknown".into()), ts: rec.timestamp.clone().filter(|x| !x.is_empty()), sid: rec.session_id.clone(), ..Default::default() }));
                        idx.insert(key, msgs.len() - 1);
                        msgs.len() - 1
                    }
                };
                let o = &mut msgs[slot].1;
                o.i = o.i.max(u.input_tokens.unwrap_or(0));
                o.o = o.o.max(u.output_tokens.unwrap_or(0));
                o.cr = o.cr.max(u.cache_read_input_tokens.unwrap_or(0));
                o.cw = o.cw.max(u.cache_creation_input_tokens.unwrap_or(0));
                if let Some(cc) = &u.cache_creation {
                    o.c1 = cc.ephemeral_1h_input_tokens.unwrap_or(0);
                    o.c5 = cc.ephemeral_5m_input_tokens.unwrap_or(0);
                }
                o.fin = match &m.stop_reason {
                    None | Some(serde_json::Value::Null) => false,
                    Some(serde_json::Value::String(s)) => !s.is_empty(),
                    Some(_) => true,
                };
            }
            _ => {}
        }
    }
    NS_SCAN.fetch_add(scan_ns, Ordering::Relaxed);
    NS_PARSE.fetch_add(parse_ns, Ordering::Relaxed);
    FileRes { path: path.to_string(), msgs, cost, setting, lines, passed }
}

fn dump(results: &[FileRes]) -> String {
    let mut out = Vec::new();
    for r in results {
        out.push(format!("F\t{}", r.path));
        out.push(format!("S\t{}\t{}", r.path, r.setting.as_deref().unwrap_or("-")));
        out.push(format!("C\t{}\t{}", r.path, r.cost.as_deref().unwrap_or("-")));
        for (k, o) in &r.msgs {
            out.push(format!("M\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}", r.path, k, o.model, o.i, o.o, o.cr, o.cw, o.c1, o.c5, o.ts.as_deref().unwrap_or("-"), o.sid.as_deref().unwrap_or("-"), o.fin as u8));
        }
    }
    out.sort();
    out.join("\n") + "\n"
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let get = |k: &str| args.iter().position(|a| a == k).and_then(|i| args.get(i + 1)).cloned();
    let list = get("--files").expect("--files LIST");
    let threads: usize = get("--threads").map(|s| s.parse().unwrap()).unwrap_or(1);
    let reps: usize = get("--reps").map(|s| s.parse().unwrap()).unwrap_or(1);
    let filter = !args.iter().any(|a| a == "--nofilter");
    let mut files: Vec<String> = std::fs::read_to_string(&list).unwrap().lines().filter(|l| !l.is_empty()).map(String::from).collect();
    // largest first: the longest tasks start early
    files.sort_by_key(|f| std::cmp::Reverse(std::fs::metadata(f).map(|m| m.len()).unwrap_or(0)));
    let t_pool = Instant::now();
    let pool = rayon::ThreadPoolBuilder::new().num_threads(threads).build().unwrap();
    eprintln!("pool_build_s {:.6}", t_pool.elapsed().as_secs_f64());
    let mut results = Vec::new();
    for rep in 0..reps {
        NS_READ.store(0, Ordering::Relaxed);
        NS_SCAN.store(0, Ordering::Relaxed);
        NS_PARSE.store(0, Ordering::Relaxed);
        let t = Instant::now();
        results = if args.iter().any(|a| a == "--item") {
            pool.install(|| files.par_iter().with_max_len(1).map(|f| parse_file(f, filter)).collect::<Vec<_>>())
        } else {
            pool.install(|| files.par_iter().map(|f| parse_file(f, filter)).collect::<Vec<_>>())
        };
        let w = t.elapsed().as_secs_f64();
        let nl: u64 = results.iter().map(|r| r.lines).sum();
        let np: u64 = results.iter().map(|r| r.passed).sum();
        eprintln!("rep {} threads {} wall_s {:.4} thread_s read {:.3} scan {:.3} serde {:.3} lines {} passed {}", rep, threads, w, NS_READ.load(Ordering::Relaxed) as f64 / 1e9, NS_SCAN.load(Ordering::Relaxed) as f64 / 1e9, NS_PARSE.load(Ordering::Relaxed) as f64 / 1e9, nl, np);
    }
    results.sort_by(|a, b| a.path.cmp(&b.path));
    if let Some(p) = get("--dump") {
        std::fs::write(p, dump(&results)).unwrap();
    } else {
        let total: u64 = results.iter().flat_map(|r| r.msgs.iter()).map(|(_, o)| o.i + o.o + o.cr + o.cw).sum();
        println!("msgs {} token_sum {}", results.iter().map(|r| r.msgs.len()).sum::<usize>(), total);
    }
}
