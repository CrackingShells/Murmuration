//! `murmuration budget`: the port of `scripts/budget.py` (notes at 50, 75, 87.5, 93.75 and 100+ percent, the 150 percent block, dispatch records, raises).
//!
//! Same stdout, same exit code (0), same lines in `__statera__/harness.jsonl`, same state files. An event or a file whose shape the port does not model returns
//! `Stop::Delegate` before anything is written; the caller then runs the Python script.

use crate::hook::{self, getd, harness_dir, log_line, now, opt_text, path_text, round, sum, truthy_text, Num, Rec, Stop, J, R};
use crate::json::{self, Value};
use crate::text::{self, text, Text};
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::path::PathBuf;

const SCHEDULE: [f64; 4] = [0.5, 0.75, 0.875, 0.9375];
const OVER_AT: f64 = 1.0;
const HARD_AT: f64 = 1.5;
const HALT_AFTER: i64 = 3;
const PENDING_TTL: f64 = 600.0;
const FLOOR_USD: f64 = 0.30;
const FLOOR_MIN: f64 = 3.0;
const CHARS_PER_TOKEN: f64 = 1.3;
const BASIS: &str = "input and cache exact; output = max(recorded, content chars / 1.3)";
const OVER_SENTENCE: &str = "If one or two more steps finish the result, finish it. Otherwise hand back now: what you have, what is missing, and what more budget would buy.";
const LONG_HAIKU: [f64; 5] = [0.50, 2.50, 0.05, 0.625, 1.0];
const MAX_INPUT_DEPTH: usize = 40;

fn row(name: &str) -> Option<[f64; 5]> {
    match name {
        "claude-opus-5-5" => Some([4.0, 20.0, 0.20, 5.0, 8.0]),
        "claude-sonnet-5-5" => Some([2.0, 10.0, 0.10, 2.5, 4.0]),
        "claude-fable-5-1" => Some([10.0, 50.0, 0.25, 12.5, 20.0]),
        "claude-haiku-5-5" => Some([0.10, 0.50, 0.01, 0.125, 0.20]),
        _ => None,
    }
}

fn default_usd(role: &str) -> f64 {
    match role {
        "explorer" | "author" => 3.0,
        _ => 2.0,
    }
}

fn default_min(role: &str) -> f64 {
    match role {
        "explorer" | "author" => 20.0,
        _ => 15.0,
    }
}

/// The event's fields, each checked for the type the platform sends.
struct Ev {
    cwd: Option<Text>,
    kind: Option<String>,
    tool_name: Option<String>,
    agent_id: Option<Text>,
    agent_type: Option<Text>,
    tool_input: Option<Value>,
    tool_use_id: Option<Text>,
    transcript_path: Option<Text>,
    agent_transcript_path: Option<Text>,
    mode: Option<Text>,
    handback_in_batch: R<bool>,
}

fn small(t: Option<&Text>) -> R<Option<String>> {
    t.map(|t| path_text(t)).transpose()
}

fn event(v: &Value) -> R<Ev> {
    let tool_calls = match v.get("tool_calls") {
        Some(Value::Arr(items)) => Ok(items.iter().any(|c| matches!(c.get("tool_name"), Some(Value::Str(t)) if text::eq(t, "SubagentHandback")))),
        Some(x @ (Value::Int(_) | Value::Float(_) | Value::Bool(_))) if x.truthy() => Err(Stop::Silent),
        _ => Ok(false),
    };
    let tool_input = match v.get("tool_input") {
        None | Some(Value::Null) => None,
        Some(o @ Value::Obj(_)) => Some(o.clone()),
        Some(_) => return Err(Stop::Delegate),
    };
    Ok(Ev {
        cwd: opt_text(v.get("cwd"))?.cloned(),
        kind: small(opt_text(v.get("hook_event_name"))?)?,
        tool_name: small(opt_text(v.get("tool_name"))?)?,
        agent_id: truthy_text(v.get("agent_id"))?.cloned(),
        agent_type: opt_text(v.get("agent_type"))?.cloned(),
        tool_input,
        tool_use_id: opt_text(v.get("tool_use_id"))?.cloned(),
        transcript_path: opt_text(v.get("transcript_path"))?.cloned(),
        agent_transcript_path: opt_text(v.get("agent_transcript_path"))?.cloned(),
        mode: opt_text(v.get("permission_mode"))?.cloned(),
        handback_in_batch: tool_calls,
    })
}

// ---- the brief's lines ----

/// `^<prefix>(\d+(?:\.\d+)?)[ \t]*$` (multiline), first matching line: its number.
fn line_figure(t: &[u32], prefix: &str) -> R<Option<f64>> {
    let pre = text(prefix);
    for line in t.split(|&c| c == 10) {
        if !line.starts_with(&pre) {
            continue;
        }
        let rest = &line[pre.len()..];
        let mut i = 0;
        let digits = |i: &mut usize| {
            let s = *i;
            while *i < rest.len() && text::is_digit(rest[*i]) {
                *i += 1;
            }
            *i - s
        };
        if digits(&mut i) == 0 {
            continue;
        }
        if i < rest.len() && rest[i] == 46 {
            let save = i;
            i += 1;
            if digits(&mut i) == 0 {
                i = save;
            }
        }
        if !rest[i..].iter().all(|&c| c == 32 || c == 9) {
            continue;
        }
        let num = &rest[..i];
        if num.iter().any(|&c| c >= 128) {
            return Err(Stop::Delegate);
        }
        let s: String = num.iter().filter_map(|&c| char::from_u32(c)).collect();
        let x: f64 = s.parse().map_err(|_| Stop::Delegate)?;
        if !x.is_finite() {
            return Err(Stop::Delegate);
        }
        return Ok(Some(x));
    }
    Ok(None)
}

/// The figure a brief sets and whether it set it.
fn figure(brief: &[u32], prefix: &str, default: f64) -> R<(f64, bool)> {
    match line_figure(brief, prefix)? {
        Some(x) if x > 0.0 => {
            if x < 1e-6 {
                return Err(Stop::Delegate);
            }
            Ok((x, true))
        }
        _ => Ok((default, false)),
    }
}

fn budget_for(role: &str, brief: &[u32]) -> R<(f64, bool)> {
    figure(brief, "Budget: USD ", default_usd(role))
}

fn time_for(role: &str, brief: &[u32]) -> R<(f64, bool)> {
    figure(brief, "Time: min ", default_min(role))
}

// ---- the transcript ----

struct Raise {
    x: Option<f64>,
    t: Option<f64>,
    ts: Option<f64>,
    n: usize,
    usd_at: Num,
}

struct Seen {
    brief: Text,
    usd: Num,
    usd_recorded: Num,
    requests: i64,
    unpriced: i64,
    raises: Vec<Raise>,
}

#[derive(Default)]
struct Req {
    model: Option<Text>,
    fast: bool,
    blocks: HashSet<Text>,
    inp: i128,
    out: i128,
    cr: i128,
    cw: i128,
    cw5: i128,
    cw1: i128,
}

fn price_row(model: &Option<Text>) -> R<String> {
    let s = match model {
        None => String::new(),
        Some(t) => {
            if t.iter().any(|&c| c >= 128) {
                return Err(Stop::Delegate);
            }
            text::string(t)
        }
    };
    if row(&s).is_some() {
        return Ok(s);
    }
    let (core, tail) = s.strip_suffix('\n').map_or((s.as_str(), ""), |c| (c, "\n"));
    let b = core.as_bytes();
    if b.len() >= 9 && b[b.len() - 9] == b'-' && b[b.len() - 8..].iter().all(u8::is_ascii_digit) {
        return Ok(format!("{}{tail}", &core[..core.len() - 9]));
    }
    Ok(s)
}

fn usd_of(model: &Option<Text>, r: &Req, out: i128) -> R<f64> {
    let name = price_row(model)?;
    let starts_haiku = model.as_ref().is_some_and(|m| text::starts(m, "claude-haiku-5-5"));
    let p = match row(&name) {
        None => row("claude-opus-5-5").unwrap_or([0.0; 5]),
        Some(p) if starts_haiku && r.inp + r.cr + r.cw > 100_000 => {
            let _ = p;
            LONG_HAIKU
        }
        Some(p) => p,
    };
    let cw5 = r.cw5 + 0.max(r.cw - r.cw5 - r.cw1);
    let usd = ((r.inp as f64) * p[0] + (out as f64) * p[1] + (r.cr as f64) * p[2] + (cw5 as f64) * p[3] + (r.cw1 as f64) * p[4]) / 1e6;
    Ok(usd * if r.fast { 2.0 } else { 1.0 })
}

fn depth_ok(v: &Value, d: usize) -> bool {
    match v {
        Value::Arr(a) => d < MAX_INPUT_DEPTH && a.iter().all(|x| depth_ok(x, d + 1)),
        Value::Obj(o) => d < MAX_INPUT_DEPTH && o.iter().all(|(_, x)| depth_ok(x, d + 1)),
        _ => true,
    }
}

/// `handback.dumps(v, sort_keys=True)`.
fn dump_sorted(v: &Value, out: &mut String) {
    match v {
        Value::Arr(a) => {
            out.push('[');
            for (i, x) in a.iter().enumerate() {
                if i > 0 {
                    out.push_str(", ");
                }
                dump_sorted(x, out);
            }
            out.push(']');
        }
        Value::Obj(o) => {
            let mut items: Vec<&(Text, Value)> = o.iter().collect();
            items.sort_by(|a, b| a.0.cmp(&b.0));
            out.push('{');
            for (i, (k, x)) in items.into_iter().enumerate() {
                if i > 0 {
                    out.push_str(", ");
                }
                json::dump_str(k, out);
                out.push_str(": ");
                dump_sorted(x, out);
            }
            out.push('}');
        }
        other => json::dump(other, out),
    }
}

fn block_text(b: &Value) -> R<Text> {
    if let Some(input) = b.get("input") {
        if !depth_ok(input, 0) {
            return Err(Stop::Delegate);
        }
        let mut s = String::new();
        dump_sorted(input, &mut s);
        return Ok(text(&s));
    }
    for key in ["text", "thinking"] {
        match b.get(key) {
            Some(Value::Str(t)) if !t.is_empty() => return Ok(t.clone()),
            Some(x) if x.truthy() => return Err(Stop::Delegate),
            _ => {}
        }
    }
    Ok(Vec::new())
}

fn plain_text(content: Option<&Value>) -> R<Option<Text>> {
    match content {
        Some(Value::Str(t)) => Ok(Some(t.clone())),
        Some(Value::Arr(items)) => {
            let blocks: Vec<&Value> = items.iter().filter(|b| matches!(b, Value::Obj(_))).collect();
            if blocks.iter().any(|b| matches!(b.get("type"), Some(Value::Str(t)) if text::eq(t, "tool_result"))) {
                return Ok(None);
            }
            let mut parts: Vec<Text> = Vec::new();
            for b in blocks.iter().filter(|b| matches!(b.get("type"), Some(Value::Str(t)) if text::eq(t, "text"))) {
                match b.get("text") {
                    None => parts.push(Vec::new()),
                    Some(Value::Str(t)) => parts.push(t.clone()),
                    Some(_) => return Err(Stop::Silent),
                }
            }
            Ok(Some(text::join_with(&parts, '\n')))
        }
        Some(x @ (Value::Int(_) | Value::Float(_) | Value::Bool(_))) if x.truthy() => Err(Stop::Silent),
        _ => Ok(Some(Vec::new())),
    }
}

fn or_obj(v: Option<&Value>) -> R<Option<&Value>> {
    match v {
        None => Ok(None),
        Some(x) if !x.truthy() => Ok(None),
        Some(x @ Value::Obj(_)) => Ok(Some(x)),
        Some(_) => Err(Stop::Silent),
    }
}

fn int_of(v: Option<&Value>) -> R<i128> {
    match v {
        None | Some(Value::Null) => Ok(0),
        Some(Value::Bool(b)) => Ok(i128::from(*b)),
        Some(Value::Int(s)) => s.parse::<i64>().map(i128::from).map_err(|_| Stop::Delegate),
        Some(_) => Err(Stop::Delegate),
    }
}

fn has_str(v: Option<&Value>, s: &str) -> bool {
    matches!(v, Some(Value::Str(t)) if text::eq(t, s))
}

/// Reads a subagent transcript once. `Ok(None)` where Python returns `None` (unreadable file, a line that is not JSON).
fn scan(path: &str) -> R<Option<Seen>> {
    let Ok(bytes) = std::fs::read(path) else {
        return Ok(None);
    };
    let mut content = String::from_utf8_lossy(&bytes).into_owned();
    if content.contains('\r') {
        content = content.replace("\r\n", "\n").replace('\r', "\n");
    }
    let mut reqs: Vec<Req> = Vec::new();
    let mut index: HashMap<Option<Text>, usize> = HashMap::new();
    let mut brief: Option<Text> = None;
    let mut raises: Vec<Raise> = Vec::new();
    macro_rules! parse {
        ($line:expr) => {
            match json::loads($line) {
                Ok(v) => v,
                Err(text::Fault::Recursion) => return Err(Stop::Silent),
                Err(_) => return Ok(None),
            }
        };
    }
    for line in content.split_inclusive('\n') {
        if brief.is_none() && line.contains("\"user\"") {
            let rec = parse!(line);
            if has_str(getd(&rec, "type")?, "user") {
                let msg = or_obj(rec.get("message"))?;
                brief = Some(plain_text(msg.and_then(|m| m.get("content")))?.unwrap_or_default());
            }
        } else if line.contains("\"origin\"") {
            let rec = parse!(line);
            let att = or_obj(getd(&rec, "attachment")?)?;
            let (txt, origin): (Option<Text>, Option<&Value>) = if has_str(getd(&rec, "type")?, "user") {
                let msg = or_obj(rec.get("message"))?;
                (plain_text(msg.and_then(|m| m.get("content")))?, rec.get("origin"))
            } else if has_str(att.and_then(|a| a.get("type")), "queued_command") {
                let a = att.unwrap_or(&Value::Null);
                (if let Some(Value::Str(t)) = a.get("prompt") { Some(t.clone()) } else { None }, a.get("origin"))
            } else {
                (None, None)
            };
            if let Some(txt) = txt.filter(|t| !t.is_empty()) {
                let o = or_obj(origin)?;
                if has_str(o.and_then(|o| o.get("kind")), "coordinator") {
                    let usd = line_figure(&txt, "Budget: USD ")?;
                    let mins = line_figure(&txt, "Time: min ")?;
                    if usd.is_some_and(|x| x > 0.0) || mins.is_some_and(|x| x > 0.0) {
                        let ts = match rec.get("timestamp") {
                            None | Some(Value::Null) => None,
                            Some(Value::Str(t)) => hook::parse_iso(&path_text(t)?)?.map(|us| us as f64 / 1e6),
                            Some(_) => return Err(Stop::Delegate),
                        };
                        raises.push(Raise { x: usd.filter(|&x| x > 0.0), t: mins.filter(|&x| x > 0.0), ts, n: reqs.len(), usd_at: Num::I0 });
                    }
                }
            }
        }
        if !line.contains("\"usage\"") {
            continue;
        }
        let rec = parse!(line);
        let msg = or_obj(getd(&rec, "message")?)?;
        let usev = msg.and_then(|m| m.get("usage"));
        if !has_str(rec.get("type"), "assistant") {
            continue;
        }
        let Some(Value::Obj(_)) = usev else { continue };
        let usev = usev.unwrap_or(&Value::Null);
        let cc = match usev.get("cache_creation") {
            Some(c @ Value::Obj(_)) => Some(c),
            _ => None,
        };
        let (inp, out, cr, cw) = (int_of(usev.get("input_tokens"))?, int_of(usev.get("output_tokens"))?, int_of(usev.get("cache_read_input_tokens"))?, int_of(usev.get("cache_creation_input_tokens"))?);
        let cw5 = int_of(cc.and_then(|c| c.get("ephemeral_5m_input_tokens")))?;
        let cw1 = int_of(cc.and_then(|c| c.get("ephemeral_1h_input_tokens")))?;
        let mut key: Option<Text> = None;
        for cand in [rec.get("requestId"), msg.and_then(|m| m.get("id")), rec.get("uuid")] {
            match cand {
                None | Some(Value::Null) => key = None,
                Some(Value::Str(t)) => {
                    key = Some(t.clone());
                    if !t.is_empty() {
                        break;
                    }
                }
                Some(_) => return Err(Stop::Delegate),
            }
        }
        let model = opt_text(msg.and_then(|m| m.get("model")))?.cloned();
        let idx = *index.entry(key).or_insert_with(|| {
            reqs.push(Req { model: model.clone(), ..Req::default() });
            reqs.len() - 1
        });
        let old = &mut reqs[idx];
        old.inp = old.inp.max(inp);
        old.out = old.out.max(out);
        old.cr = old.cr.max(cr);
        old.cw = old.cw.max(cw);
        old.cw5 = old.cw5.max(cw5);
        old.cw1 = old.cw1.max(cw1);
        match msg.and_then(|m| m.get("content")) {
            Some(Value::Arr(items)) => {
                for b in items.iter().filter(|b| matches!(b, Value::Obj(_))) {
                    let t = block_text(b)?;
                    old.blocks.insert(t);
                }
            }
            Some(x @ (Value::Int(_) | Value::Float(_) | Value::Bool(_))) if x.truthy() => return Err(Stop::Silent),
            _ => {}
        }
        old.fast = old.fast || has_str(usev.get("speed"), "fast");
        let keep = old.model.as_ref().is_some_and(|m| !m.is_empty() && !text::eq(m, "<synthetic>"));
        if !keep {
            old.model = model;
        }
    }
    let mut costs = Vec::with_capacity(reqs.len());
    let mut recorded = Vec::with_capacity(reqs.len());
    for r in &reqs {
        let chars: usize = r.blocks.iter().map(Vec::len).sum();
        let est = (chars as f64 / CHARS_PER_TOKEN) as i128;
        costs.push(usd_of(&r.model, r, r.out.max(est))?);
        recorded.push(usd_of(&r.model, r, r.out)?);
    }
    let mut live = 0;
    let mut unpriced = 0;
    for r in &reqs {
        let synthetic = r.model.as_ref().is_some_and(|m| text::eq(m, "<synthetic>"));
        if !synthetic || r.inp + r.out + r.cr + r.cw != 0 {
            live += 1;
            if row(&price_row(&r.model)?).is_none() {
                unpriced += 1;
            }
        }
    }
    for r in &mut raises {
        r.usd_at = sum(&costs[..r.n]);
    }
    Ok(Some(Seen { brief: brief.unwrap_or_default(), usd: sum(&costs), usd_recorded: sum(&recorded), requests: live, unpriced, raises }))
}

// ---- state ----

#[derive(Clone)]
struct St {
    role: Text,
    b: f64,
    t: f64,
    base: Num,
    base_recorded: Option<Num>,
    acc: f64,
    run_start: f64,
    run_open: bool,
    last_seen: f64,
    k: i64,
    raises_done: i64,
    stops: i64,
    ceil_req: i64,
    brief_read: bool,
    warned: bool,
}

const KEYS: [&str; 15] = ["role", "B", "T", "base", "base_recorded", "acc", "run_start", "run_open", "last_seen", "k", "raises_done", "stops", "ceil_req", "brief_read", "warned"];

fn dump_state(st: &St) -> String {
    let mut o = String::from("{");
    let mut first = true;
    let mut put = |k: &str, v: J| {
        if !first {
            o.push_str(", ");
        }
        first = false;
        json::dump_str(&text(k), &mut o);
        o.push_str(": ");
        hook::dump_j(&v, &mut o);
    };
    put("role", J::T(st.role.clone()));
    put("B", J::F(st.b));
    put("T", J::F(st.t));
    put("base", J::N(st.base));
    if let Some(x) = st.base_recorded {
        put("base_recorded", J::N(x));
    }
    put("acc", J::F(st.acc));
    put("run_start", J::F(st.run_start));
    put("run_open", J::B(st.run_open));
    put("last_seen", J::F(st.last_seen));
    put("k", J::I(st.k));
    put("raises_done", J::I(st.raises_done));
    put("stops", J::I(st.stops));
    put("ceil_req", J::I(st.ceil_req));
    put("brief_read", J::B(st.brief_read));
    put("warned", J::B(st.warned));
    o.push('}');
    o
}

fn num_of(v: &Value) -> R<Num> {
    match v {
        Value::Float(x) => Ok(Num::F(*x)),
        Value::Int(s) if s == "0" => Ok(Num::I0),
        _ => Err(Stop::Delegate),
    }
}

fn float_of(v: &Value) -> R<f64> {
    match v {
        Value::Float(x) if x.is_finite() => Ok(*x),
        _ => Err(Stop::Delegate),
    }
}

fn int64(v: &Value) -> R<i64> {
    match v {
        Value::Int(s) => s.parse().map_err(|_| Stop::Delegate),
        _ => Err(Stop::Delegate),
    }
}

fn bool_of(v: &Value) -> R<bool> {
    match v {
        Value::Bool(b) => Ok(*b),
        _ => Err(Stop::Delegate),
    }
}

fn parse_state(v: &Value) -> R<St> {
    let Value::Obj(items) = v else {
        return Err(Stop::Silent);
    };
    let names: Vec<String> = items.iter().map(|(k, _)| text::string(k)).collect();
    let with: Vec<String> = KEYS.iter().map(ToString::to_string).collect();
    let without: Vec<String> = KEYS.iter().filter(|k| **k != "base_recorded").map(ToString::to_string).collect();
    if names != with && names != without {
        return Err(Stop::Delegate);
    }
    let g = |k: &str| v.get(k).ok_or(Stop::Delegate);
    let st = St {
        role: match g("role")? {
            Value::Str(t) => t.clone(),
            _ => return Err(Stop::Delegate),
        },
        b: float_of(g("B")?)?,
        t: float_of(g("T")?)?,
        base: num_of(g("base")?)?,
        base_recorded: v.get("base_recorded").map(num_of).transpose()?,
        acc: float_of(g("acc")?)?,
        run_start: float_of(g("run_start")?)?,
        run_open: bool_of(g("run_open")?)?,
        last_seen: float_of(g("last_seen")?)?,
        k: int64(g("k")?)?,
        raises_done: int64(g("raises_done")?)?,
        stops: int64(g("stops")?)?,
        ceil_req: int64(g("ceil_req")?)?,
        brief_read: bool_of(g("brief_read")?)?,
        warned: bool_of(g("warned")?)?,
    };
    if st.b < 1e-6 && st.b != 0.0 || st.t < 1e-6 && st.t != 0.0 || st.b < 0.0 || st.t < 0.0 {
        return Err(Stop::Delegate);
    }
    Ok(st)
}

fn state_file(root: &str, aid: &str) -> R<PathBuf> {
    Ok(harness_dir(root)?.join(format!("{aid}.json")))
}

/// What `load_state` found: nothing (no file, not JSON, or JSON `null`), a JSON value that is not an object (Python fails when it first indexes it), or a state.
enum Loaded {
    Nothing,
    Bad,
    State(St),
}

fn load_state(root: &str, aid: &str) -> R<Loaded> {
    let path = state_file(root, aid)?;
    let Ok(bytes) = std::fs::read(&path) else {
        return Ok(Loaded::Nothing);
    };
    let Ok(s) = String::from_utf8(bytes) else {
        return Ok(Loaded::Nothing);
    };
    match json::loads(&s) {
        Ok(Value::Null) => Ok(Loaded::Nothing),
        Ok(v @ Value::Obj(_)) => Ok(Loaded::State(parse_state(&v)?)),
        Ok(_) => Ok(Loaded::Bad),
        Err(text::Fault::Recursion) => Err(Stop::Silent),
        Err(_) => Ok(Loaded::Nothing),
    }
}

fn save_state(root: &str, aid: &str, st: &St) -> R<()> {
    let path = state_file(root, aid)?;
    let tmp = PathBuf::from(format!("{}.{}.tmp", path.to_string_lossy(), std::process::id()));
    std::fs::write(&tmp, dump_state(st))?;
    std::fs::rename(&tmp, &path)?;
    Ok(())
}

// ---- the text ----

fn pct(frac: f64) -> i128 {
    let p = (frac * 100.0 + 0.5) as i128;
    if frac < 1.0 {
        p.min(99)
    } else {
        p.max(100)
    }
}

fn line(used: f64, b: f64, minutes: f64, t: f64) -> String {
    format!("Spent {used:.2} of USD {b:.2} ({}%); {minutes:.1} of {} min ({}%)", pct(used / b), hook::fmt_g(t), pct(minutes / t))
}

fn note_text(used: f64, b: f64, minutes: f64, t: f64, frac: f64) -> String {
    line(used, b, minutes, t) + &if frac >= OVER_AT { format!(". {OVER_SENTENCE}") } else { String::new() }
}

fn stop_text(used: f64, b: f64, minutes: f64, t: f64) -> String {
    line(used, b, minutes, t) + ". Hand back now with SubagentHandback: what you have, what is missing, and what more budget would buy; do not start another item."
}

fn halt_text(used: f64, b: f64, minutes: f64, t: f64) -> String {
    line(used, b, minutes, t) + ". The run ends here."
}

fn start_note(b: f64, t: f64, source: &str) -> String {
    let (bs, ts) = (format!("{b:.2}"), hook::fmt_g(t));
    let where_ = match source {
        "brief" => format!("your budget for this run is USD {bs} and {ts} minutes (from your brief)"),
        "default" => format!("your budget for this run is USD {bs} and {ts} minutes (the defaults for your role; a line `Budget: USD <number>` or `Time: min <number>` in your brief replaces them)"),
        _ => format!("your budget for this run is set by the `Budget: USD <number>` and `Time: min <number>` lines of your brief, else it is USD {bs} and {ts} minutes (the defaults for your role)"),
    };
    format!(
        "Budget: {where_}. The harness counts both, as the list price of the tokens you use and the minutes you are active; \
you need not count anything and can work at your usual pace. When the larger of the two reaches 50%, 75%, 87.5% and 93.75%, and at every step from 100%, \
a note comes from the hook that runs you (not from a file or a tool's output), in the form: Spent X of USD Y (Z%); t of T min (W%). \
From 100% you choose: if one or two more steps finish the result, finish it; otherwise hand back what you have, what is missing, and what more budget would buy. \
The principal investigator holds the money and decides whether to resume you with more. \
Before you write a helper script: ToolSearch `select:mcp__plugin_colgrep-mcp_colgrep__search,mcp__plugin_colgrep-mcp_colgrep__find_files`, \
then `search` with `paths: [\"__instrumenta__\"]` and `limit: 5`."
    )
}

fn reply(kind: &str, context: &str) -> String {
    let (mut k, mut c) = (String::new(), String::new());
    json::dump_str(&text(kind), &mut k);
    json::dump_str(&text(context), &mut c);
    format!("{{\"hookSpecificOutput\": {{\"hookEventName\": {k}, \"additionalContext\": {c}}}}}")
}

fn jstr(s: &str) -> String {
    let mut o = String::new();
    json::dump_str(&text(s), &mut o);
    o
}

// ---- figures ----

fn active_s(st: &St, now: f64) -> f64 {
    st.acc + if st.run_open { 0.0f64.max(now - st.run_start) } else { 0.0 }
}

fn active_at(st: &St, ts: Option<f64>, now: f64) -> f64 {
    match ts {
        Some(ts) if st.run_open => st.acc + (0.0f64.max(ts - st.run_start)).min(0.0f64.max(now - st.run_start)),
        _ => active_s(st, now),
    }
}

fn due(frac: f64) -> i64 {
    SCHEDULE.iter().filter(|&&t| frac >= t).count() as i64
}

// ---- the dispatch records ----

fn pending_dir(root: &str) -> R<PathBuf> {
    Ok(harness_dir(root)?.join("pending"))
}

fn base_rec(root_id: &Ev, name: &Text) -> Rec {
    let mut r = Rec::default();
    r.set("agent_id", J::T(root_id.agent_id.clone().unwrap_or_default()));
    r.set("name", J::T(name.clone()));
    r.set("type", root_id.agent_type.clone().map_or(J::Null, J::T));
    r.set("mode", root_id.mode.clone().map_or(J::Null, J::T));
    r
}

fn warn_floor(root: &str, who: &Rec, b: Option<f64>, t: Option<f64>) -> R<()> {
    for (what, value, floor) in [("budget_usd", b, FLOOR_USD), ("time_min", t, FLOOR_MIN)] {
        if let Some(value) = value.filter(|v| *v < floor) {
            let mut r = who.clone();
            r.set("event", J::S("warn".into())).set("what", J::S(what.into())).set("value", J::F(value)).set("floor", J::F(floor)).set(
                "reason",
                J::S("below the floor; the figure is left as the brief gives it".into()),
            );
            log_line(root, &r)?;
        }
    }
    Ok(())
}

fn dispatch(ev: &Ev, root: &str, now: f64) -> R<Option<String>> {
    let tin = ev.tool_input.clone().unwrap_or(Value::Obj(Vec::new()));
    let kind = match truthy_text(tin.get("subagent_type"))? {
        Some(t) => t.clone(),
        None => Vec::new(),
    };
    if !text::starts(&kind, "murmuration:") {
        return Ok(None);
    }
    let role = text::string(&kind[12..]);
    let prompt = truthy_text(tin.get("prompt"))?.cloned().unwrap_or_default();
    let (b, b_set) = budget_for(&role, &prompt)?;
    let (t, t_set) = time_for(&role, &prompt)?;
    let name: Text = match truthy_text(tin.get("name"))? {
        Some(n) => n.clone(),
        None => hook_your_name(&prompt).unwrap_or_else(|| kind.clone()),
    };
    let dir = pending_dir(root)?;
    std::fs::create_dir_all(&dir)?;
    let id: String = match &ev.tool_use_id {
        Some(t) if !t.is_empty() => text::string(t),
        _ => std::process::id().to_string(),
    };
    let id: String = id.chars().filter(|c| c.is_ascii_alphanumeric() || *c == '_' || *c == '-').collect();
    let key = format!("{now:014.3}-{id}");
    let mut body = String::new();
    json::dump(
        &Value::Obj(vec![
            (text("type"), Value::Str(kind.clone())),
            (text("B"), Value::Float(b)),
            (text("T"), Value::Float(t)),
            (text("b_set"), Value::Bool(b_set)),
            (text("t_set"), Value::Bool(t_set)),
            (text("t"), Value::Float(now)),
            (text("name"), Value::Str(name.clone())),
        ]),
        &mut body,
    );
    std::fs::write(dir.join(format!("{key}.json")), body)?;
    let mut who = Rec::default();
    who.set("name", J::T(name)).set("type", J::T(kind));
    warn_floor(root, &who, b_set.then_some(b), t_set.then_some(t))?;
    Ok(None)
}

fn hook_your_name(chars: &[u32]) -> Option<Text> {
    hook::your_name(chars)
}

struct Pending {
    path: PathBuf,
    rec: Value,
}

fn num_val(v: Option<&Value>) -> R<f64> {
    match v {
        Some(Value::Float(x)) => Ok(*x),
        Some(Value::Int(s)) => s.parse::<i64>().map(|i| i as f64).map_err(|_| Stop::Delegate),
        _ => Err(Stop::Delegate),
    }
}

/// The oldest fresh dispatch record of this agent type, removed, and whether other fresh records of the type disagree with it.
fn claim_pending(root: &str, kind: Option<&Text>, now: f64) -> R<(Option<Value>, bool)> {
    let dir = pending_dir(root)?;
    let mut names: Vec<String> = match std::fs::read_dir(&dir) {
        Ok(rd) => rd.filter_map(|e| e.ok()).filter_map(|e| e.file_name().into_string().ok()).filter(|n| n.ends_with(".json") && !n.starts_with('.')).collect(),
        Err(_) => Vec::new(),
    };
    names.sort_by(|a, b| text(a).cmp(&text(b)));
    let mut parsed: Vec<Pending> = Vec::new();
    for n in names {
        let path = dir.join(&n);
        let Ok(bytes) = std::fs::read(&path) else { continue };
        let Ok(s) = String::from_utf8(bytes) else { continue };
        let Ok(rec) = json::loads(&s) else { continue };
        if !matches!(rec, Value::Obj(_)) {
            return Err(Stop::Delegate);
        }
        match rec.get("t") {
            None => {}
            Some(_) => {
                num_val(rec.get("t"))?;
            }
        }
        parsed.push(Pending { path, rec });
    }
    let mut found: Vec<Pending> = Vec::new();
    for p in parsed {
        let t = if p.rec.get("t").is_some() { num_val(p.rec.get("t"))? } else { 0.0 };
        if now - t > PENDING_TTL {
            let _ = std::fs::remove_file(&p.path);
        } else if matches!((p.rec.get("type"), kind), (Some(Value::Str(a)), Some(b)) if a == b) {
            num_val(p.rec.get("B"))?;
            num_val(p.rec.get("T"))?;
            found.push(p);
        }
    }
    for i in 0..found.len() {
        if std::fs::remove_file(&found[i].path).is_err() {
            continue;
        }
        let rec = found[i].rec.clone();
        let (rb, rt) = (num_val(rec.get("B"))?, num_val(rec.get("T"))?);
        let mut mixed = rec.get("ambiguous").is_some_and(Value::truthy);
        for (j, o) in found.iter().enumerate() {
            if j != i && (num_val(o.rec.get("B"))? != rb || num_val(o.rec.get("T"))? != rt) {
                mixed = true;
            }
        }
        if mixed {
            for (j, o) in found.iter().enumerate() {
                if j == i {
                    continue;
                }
                let mut r = o.rec.clone();
                if let Value::Obj(items) = &mut r {
                    match items.iter_mut().find(|(k, _)| text::eq(k, "ambiguous")) {
                        Some(e) => e.1 = Value::Bool(true),
                        None => items.push((text("ambiguous"), Value::Bool(true))),
                    }
                }
                let mut s = String::new();
                json::dump(&r, &mut s);
                let _ = std::fs::write(&o.path, s);
            }
        }
        return Ok((Some(rec), mixed));
    }
    Ok((None, false))
}

// ---- the hook ----

/// The hook's stdout (with its newline) or nothing. Writes state and log lines as a side effect.
pub(crate) fn run(v: &Value) -> R<Option<String>> {
    let Value::Obj(_) = v else {
        return Ok(None);
    };
    let ev = event(v)?;
    let now = now();
    let root = hook::lab_root(ev.cwd.as_ref())?;
    if let Some(root) = &root {
        if ev.kind.as_deref() == Some("PreToolUse") && matches!(ev.tool_name.as_deref(), Some("Agent" | "Task")) && ev.agent_id.is_none() {
            return dispatch(&ev, root, now).map(|_| None);
        }
    }
    let role = match (&ev.agent_type, &ev.agent_id) {
        (Some(t), Some(_)) if text::starts(t, "murmuration:") && t.len() > 12 => text::string(&t[12..]),
        _ => return Ok(None),
    };
    let Some(root) = root else {
        return Ok(None);
    };
    let aid = path_text(ev.agent_id.as_ref().unwrap_or(&Vec::new()))?;
    let dir = harness_dir(&root)?;
    let lock = File::create(dir.join(format!("{aid}.lock")))?;
    lock.lock()?;
    let out = handle_locked(&ev, &root, &role, &aid, now);
    drop(lock);
    out.map(|o| o.map(|s| s + "\n"))
}

#[allow(clippy::too_many_lines)]
fn handle_locked(ev: &Ev, root: &str, role: &str, aid: &str, now: f64) -> R<Option<String>> {
    let kind = ev.kind.clone().unwrap_or_default();
    let path: Option<Text> = match (&ev.agent_transcript_path, &ev.agent_id, &ev.transcript_path) {
        (Some(p), _, _) if !p.is_empty() => Some(p.clone()),
        (_, Some(id), Some(tp)) if !tp.is_empty() => {
            let mut s: Text = tp[..tp.len().saturating_sub(6)].to_vec();
            if !s.is_empty() && s.last() != Some(&47) {
                s.push(47);
            }
            s.extend(text("subagents/agent-"));
            s.extend(id.iter());
            s.extend(text(".jsonl"));
            Some(s)
        }
        _ => None,
    };
    let seen = match &path {
        Some(p) => {
            let ps = path_text(p)?;
            if std::path::Path::new(&ps).exists() {
                scan(&ps)?
            } else {
                None
            }
        }
        None => None,
    };
    let mut name = hook::agent_name(ev.agent_id.as_ref(), ev.agent_type.as_ref(), ev.transcript_path.as_ref(), ev.agent_transcript_path.as_ref())?;
    let loaded = load_state(root, aid)?;
    let bad = matches!(loaded, Loaded::Bad);
    let mut st = match loaded {
        Loaded::State(s) => Some(s),
        _ => None,
    };
    if kind == "SubagentStart" {
        if bad {
            return Err(Stop::Silent);
        }
        if st.is_none() {
            let (rec, mixed) = claim_pending(root, ev.agent_type.as_ref(), now)?;
            let brief: &[u32] = seen.as_ref().map_or(&[], |s| &s.brief);
            let (mut b, b_set) = budget_for(role, brief)?;
            let (mut t, t_set) = time_for(role, brief)?;
            let mut source = if b_set || t_set { "brief" } else { "default" };
            if let (Some(rec), None) = (&rec, &seen) {
                let flag = |k: &str| match rec.get(k) {
                    Some(Value::Bool(x)) => Ok(*x),
                    _ => Err(Stop::Delegate),
                };
                source = if mixed {
                    "unknown"
                } else if flag("b_set")? || flag("t_set")? {
                    "brief"
                } else {
                    "default"
                };
                if !mixed {
                    b = num_val(rec.get("B"))?;
                    t = num_val(rec.get("T"))?;
                }
            }
            let s0 = St {
                role: text(role),
                b,
                t,
                base: seen.as_ref().map_or(Num::F(0.0), |s| s.usd),
                base_recorded: Some(seen.as_ref().map_or(Num::F(0.0), |s| s.usd_recorded)),
                acc: 0.0,
                run_start: now,
                run_open: true,
                last_seen: now,
                k: 0,
                raises_done: seen.as_ref().map_or(0, |s| s.raises.len() as i64),
                stops: 0,
                ceil_req: -1,
                brief_read: seen.is_some(),
                warned: rec.is_some() || seen.is_some(),
            };
            save_state(root, aid, &s0)?;
            if let Some(Value::Str(n)) = rec.as_ref().and_then(|r| r.get("name")) {
                if !n.is_empty() {
                    name = n.clone();
                }
            }
            let mut r = base_rec(ev, &name);
            r.set("event", J::S("start".into())).set("B", J::F(b)).set("T", J::F(t)).set("source", J::S(source.into()));
            r.set("resumed", J::B(seen.as_ref().is_some_and(|s| s.requests != 0))).set("base_usd", J::N(s0.base.round(6)));
            log_line(root, &r)?;
            return Ok(Some(reply(&kind, &start_note(b, t, source))));
        }
        let mut s = st.take().unwrap_or_else(|| unreachable!());
        if s.run_open {
            s.acc += 0.0f64.max(s.last_seen - s.run_start);
        }
        s.run_start = now;
        s.run_open = true;
        s.last_seen = now;
        save_state(root, aid, &s)?;
        let mut r = base_rec(ev, &name);
        r.set("event", J::S("start".into())).set("B", J::F(s.b)).set("T", J::F(s.t)).set("resumed", J::B(true)).set("active_s", J::F(round(s.acc, 1)));
        log_line(root, &r)?;
        return Ok(None);
    }
    let Some(seen) = seen else {
        return Ok(None);
    };
    if bad {
        return Err(Stop::Silent);
    }
    let mut st = st.unwrap_or(St {
        role: text(role),
        b: 0.0,
        t: 0.0,
        base: Num::F(0.0),
        base_recorded: Some(Num::F(0.0)),
        acc: 0.0,
        run_start: now,
        run_open: true,
        last_seen: now,
        k: 0,
        raises_done: 0,
        stops: 0,
        ceil_req: -1,
        brief_read: false,
        warned: false,
    });
    let base_log = base_rec(ev, &name);
    if !st.warned {
        st.warned = true;
        let b = line_figure(&seen.brief, "Budget: USD ")?.map(|_| budget_for(role, &seen.brief)).transpose()?.map(|x| x.0);
        let t = line_figure(&seen.brief, "Time: min ")?.map(|_| time_for(role, &seen.brief)).transpose()?.map(|x| x.0);
        warn_floor(root, &base_log, b, t)?;
    }
    if !st.run_open && kind != "SubagentStop" {
        st.run_start = now;
        st.run_open = true;
    }
    if !st.brief_read {
        st.b = budget_for(role, &seen.brief)?.0;
        st.t = time_for(role, &seen.brief)?.0;
        st.brief_read = true;
    }
    // apply the raises this state has not seen
    let new_from = usize::try_from(st.raises_done).unwrap_or(0).min(seen.raises.len());
    let changed = new_from < seen.raises.len();
    for r in &seen.raises[new_from..] {
        let used_at = r.usd_at.sub(st.base);
        let mins_at = active_at(&st, r.ts, now) / 60.0;
        let before = (st.b, st.t);
        if let Some(x) = r.x {
            st.b = st.b.max(used_at.f()) + x;
        }
        if let Some(x) = r.t {
            st.t = st.t.max(mins_at) + x;
        }
        let mut rec = base_log.clone();
        rec.set("event", J::S("raise".into())).set("add_usd", r.x.map_or(J::Null, J::F)).set("add_min", r.t.map_or(J::Null, J::F));
        rec.set("B_before", J::F(before.0)).set("T_before", J::F(before.1)).set("B", J::F(round(st.b, 6))).set("T", J::F(round(st.t, 6)));
        rec.set("used_at", J::N(used_at.round(6))).set("minutes_at", J::F(round(mins_at, 4)));
        log_line(root, &rec)?;
    }
    st.raises_done = seen.raises.len() as i64;
    let used = seen.usd.sub(st.base);
    let mins = active_s(&st, now) / 60.0;
    let (usd_frac, t_frac) = (used.f() / st.b, mins / st.t);
    let which = if usd_frac >= t_frac { "USD" } else { "time" };
    let frac = if t_frac > usd_frac { t_frac } else { usd_frac };
    if changed {
        st.k = due(frac);
    }
    let fields = |st: &St, rec: &mut Rec| {
        rec.set("B", J::F(round(st.b, 6))).set("T", J::F(round(st.t, 6))).set("used", J::N(used.round(6)));
        rec.set("used_recorded", J::N(seen.usd_recorded.sub(st.base_recorded.unwrap_or(Num::F(0.0))).round(6)));
        rec.set("frac", J::F(round(usd_frac, 4))).set("t_frac", J::F(round(t_frac, 4))).set("which", J::S(which.into())).set("basis", J::S(BASIS.into()));
        rec.set("requests", J::I(seen.requests)).set("unpriced", J::I(seen.unpriced)).set("active_s", J::F(round(active_s(st, now), 1)));
    };
    // `fields` is read before last_seen changes and before a stop closes the run, as in the Python
    let mut field_rec = Rec::default();
    fields(&st, &mut field_rec);
    st.last_seen = now;
    let with_fields = |mut rec: Rec, extra: &Rec| {
        for (k, v) in &extra.0 {
            rec.set(k, v.clone());
        }
        rec
    };
    if kind == "SubagentStop" {
        if st.run_open {
            st.acc += 0.0f64.max(now - st.run_start);
            st.run_open = false;
        }
        save_state(root, aid, &st)?;
        field_rec.set("active_s", J::F(round(st.acc, 1)));
        let mut rec = base_log.clone();
        rec.set("event", J::S("end".into())).set("k", J::I(st.k)).set("stops", J::I(st.stops));
        log_line(root, &with_fields(rec, &field_rec))?;
        return Ok(None);
    }
    if kind == "PostToolBatch" {
        if ev.handback_in_batch? {
            save_state(root, aid, &st)?;
            return Ok(None);
        }
        if frac >= HARD_AT && st.ceil_req == seen.requests {
            save_state(root, aid, &st)?;
            return Ok(None);
        }
        let n = due(frac);
        if frac < OVER_AT && n <= st.k {
            save_state(root, aid, &st)?;
            return Ok(None);
        }
        st.k = n;
        save_state(root, aid, &st)?;
        let mut rec = base_log.clone();
        rec.set("event", J::S("note".into())).set("over", J::B(frac >= OVER_AT));
        log_line(root, &with_fields(rec, &field_rec))?;
        return Ok(Some(reply(&kind, &note_text(used.f(), st.b, mins, st.t, frac))));
    }
    if kind == "PostToolUse" && ev.tool_name.as_deref() != Some("SubagentHandback") && frac >= HARD_AT && st.ceil_req != seen.requests {
        st.ceil_req = seen.requests;
        let halt = st.stops >= HALT_AFTER;
        st.stops += 1;
        save_state(root, aid, &st)?;
        let mut rec = base_log.clone();
        rec.set("event", J::S(if halt { "halt" } else { "stop" }.into())).set("n", J::I(st.stops));
        log_line(root, &with_fields(rec, &field_rec))?;
        if halt {
            return Ok(Some(format!("{{\"continue\": false, \"stopReason\": {}}}", jstr(&halt_text(used.f(), st.b, mins, st.t)))));
        }
        return Ok(Some(format!("{{\"decision\": \"block\", \"reason\": {}}}", jstr(&stop_text(used.f(), st.b, mins, st.t)))));
    }
    save_state(root, aid, &st)?;
    Ok(None)
}
