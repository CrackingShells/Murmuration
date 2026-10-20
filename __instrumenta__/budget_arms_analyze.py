#!/usr/bin/env python3
"""Computes the E1/E2 metrics (denies, fraction at first and final hand-back, report present and in shape, items done and correct, cost, stop reason) of headless explorer cells from their run folders, into a TSV and one JSON per cell.
usage: budget_arms_analyze.py <scratch> <budget.py dir> <out dir> <cell:arm> [<cell:arm> ...]   (arm is a label: A, B, C, ...)
Inputs: <scratch>/runs/<cell>/{meta.json, ground.json, lab/} and the worker transcript in ~/.claude/projects/*; fractions are ESTIMATES (budget.py's price table, output = max(recorded, chars/1.3)). Stdlib only."""
import glob, json, os, re, sys
SELFTEST = sys.argv[1:2] == ["--selftest"]
if not SELFTEST:
    scratch, bdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
    sys.path.insert(0, bdir)
    import budget  # noqa: E402  (the plugin's own price table and output estimate: the same figures its hook uses)
HEADS = ["## Result", "## Table", "## Worst-fitting case", "## Not covered", "## Steering questions", "## Pointers"]


def worker_transcript(cell):
    lab = os.path.join(scratch, "runs", cell, "lab")
    key = re.sub(r"[^A-Za-z0-9-]", "-", lab)
    cands = glob.glob(os.path.expanduser("~/.claude/projects/%s/*/subagents/agent-*.jsonl" % key))
    return sorted(cands, key=os.path.getsize)[-1] if cands else None


def passes(path, B):
    """Per request in order: cumulative USD at its end; the requests that hold a SubagentHandback call; the text of each such call."""
    order, reqs, handbacks = [], {}, []
    for line in open(path, encoding="utf-8", errors="replace"):
        rec = json.loads(line)
        msg = rec.get("message") or {}
        if rec.get("type") != "assistant" or not isinstance(msg.get("usage"), dict):
            continue
        use = msg["usage"]; cc = use.get("cache_creation") if isinstance(use.get("cache_creation"), dict) else {}
        key = rec.get("requestId") or msg.get("id") or rec.get("uuid")
        got = dict(in_=use.get("input_tokens"), out=use.get("output_tokens"), cr=use.get("cache_read_input_tokens"), cw=use.get("cache_creation_input_tokens"),
                   cw5=cc.get("ephemeral_5m_input_tokens"), cw1=cc.get("ephemeral_1h_input_tokens"))
        got = {k.rstrip("_"): int(v or 0) for k, v in got.items()}
        if key not in reqs:
            reqs[key] = dict(model=msg.get("model"), fast=False, blocks=set(), **{k: 0 for k in got}); order.append(key)
        r = reqs[key]
        for k, v in got.items():
            r[k] = max(r[k], v)
        r["fast"] = r["fast"] or use.get("speed") == "fast"
        r["model"] = r["model"] if r["model"] and r["model"] != "<synthetic>" else msg.get("model")
        for b in msg.get("content") or []:
            if isinstance(b, dict):
                r["blocks"].add(budget.block_text(b))
                if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                    handbacks.append((key, str((b.get("input") or {}).get("message") or "")))
    cum, at = 0.0, {}
    for key in order:
        r = reqs[key]
        r["out"] = max(r["out"], int(sum(len(b) for b in r["blocks"]) / budget.CHARS_PER_TOKEN))
        cum += budget.usd_of(r["model"], r); at[key] = cum
    return cum / B, [(at[k] / B, t) for k, t in handbacks], len(order)


def parse_items(text, ground):
    """{file: (station ok, year ok, founder ok)} for rows (lines) that name a file and carry data; the first row per file counts."""
    got = {}
    for ln in text.splitlines():
        m = re.search(r"\bf(\d{3})\b", ln)
        if not m or "f%s" % m.group(1) not in ground or "f%s" % m.group(1) in got:
            continue
        g = ground["f" + m.group(1)]; body = ln[m.end():]
        if "total" in g:   # sums task: a row carries the total population (digits, commas allowed) and the lowest-elevation station
            flat = re.sub(r"(?<=\d)[,_ ](?=\d{3}\b)", "", ln[m.end():])
            if not re.search(r"\d{4,}", flat):
                continue
            got["f" + m.group(1)] = (g["lowest"] in ln, bool(re.search(r"(?<!\d)%d(?!\d)" % g["total"], flat)), True)
            continue
        if not re.search(r"\d{4}", body):
            continue
        got["f" + m.group(1)] = (g["station"] in ln, str(g["year"]) in ln, g["founder"] in ln)
    return got


def selftest():
    """The item check can fail: a wrong year, a wrong founder, a row with no data and a repeated row are not counted as correct."""
    g = {"f001": dict(station="Fenford", year=1900, founder="Ada Pell"), "f002": dict(station="Moorwick", year=1850, founder="Bram Holt"), "f003": dict(station="Tarnhaven", year=1810, founder="Cora Maro")}
    text = "| f001 | Fenford | 1900 | Ada Pell |\n| f002 | Moorwick | 1851 | Bram Holt |\n| f003 | Tarnhaven |\n| f001 | Fenford | 1900 | Ada Pell |\n"
    got = parse_items(text, g)
    assert got == {"f001": (True, True, True), "f002": (True, False, True)}, got
    assert sum(1 for v in got.values() if all(v)) == 1
    h = {"f001": dict(total=12345, lowest="Fenford")}
    assert parse_items("| f001 | 12,345 | Fenford |", h) == {"f001": (True, True, True)}
    assert parse_items("| f001 | 12,346 | Fenford |", h) == {"f001": (True, False, True)}
    assert parse_items("| f001 | 12345 | Moorwick |", h) == {"f001": (False, True, True)}
    assert parse_items("| f001 | 123 | Fenford |", h) == {}
    print("PASS budget_arms_analyze")


if SELFTEST:
    selftest()
    sys.exit(0)
os.makedirs(out, exist_ok=True)
rows = []
for spec in sys.argv[4:]:
    cell, arm = spec.split(":")
    base = os.path.join(scratch, "runs", cell); lab = os.path.join(base, "lab")
    meta = json.load(open(os.path.join(base, "meta.json"))); ground = json.load(open(os.path.join(base, "ground.json")))
    B = float(meta["B"]); name = meta["name"]
    log = [json.loads(l) for l in open(os.path.join(lab, "__statera__", "harness.jsonl"))] if os.path.exists(os.path.join(lab, "__statera__", "harness.jsonl")) else []
    mine = [r for r in log if r.get("name") == name or r.get("event") in ("start",)]
    tp = worker_transcript(cell)
    fin, hbs, nreq = passes(tp, B) if tp else (None, [], 0)
    rep = os.path.join(lab, "__reports__", "wave-04", name, "00-findings_v0.md")
    rtext = open(rep).read() if os.path.exists(rep) else ""
    hdir = glob.glob(os.path.join(lab, "__statera__", "handbacks", "*%s*.md" % name))
    htext = "".join(open(f, errors="replace").read() for f in hdir)
    final_hb = hbs[-1][1] if hbs else ""
    it_r, it_h = parse_items(rtext, ground), parse_items(final_hb, ground)
    items = dict(it_h); items.update(it_r)   # the report counts first; the hand-back adds what the report lacks
    first_hb_text = hbs[0][1] if hbs else ""
    cap_att = sum(1 for l in open(tp, errors="replace") if '"type": "budget_usd"' in l or '"type":"budget_usd"' in l) if tp else None   # platform spend attachments (appear with --max-budget-usd)
    ctx = sum(1 for l in open(tp, errors="replace") if '"hook_additional_context"' in l) if tp else None   # notes the worker was shown (the start note included)
    row = dict(cell=cell, arm=arm, seed=meta["seed"], B=B, usd_total=meta["usd"], usd_sonnet=(meta.get("model_usd") or {}).get("claude-sonnet-5-5"), wall_s=meta["wall_s"],
               denies=sum(1 for r in log if r.get("event") == "deny"), notes=sum(1 for r in log if r.get("event") == "note"), notes_over=sum(1 for r in log if r.get("event") == "note" and r.get("over")),
               stops=sum(1 for r in log if r.get("event") in ("stop", "halt")), handback_calls=len(hbs),
               frac_first=round(hbs[0][0], 3) if hbs else None, frac_final=round(hbs[-1][0], 3) if hbs else None, frac_end=round(fin, 3) if fin is not None else None,
               overshoot=round(hbs[-1][0] - hbs[0][0], 3) if hbs else None, requests=nreq,
               report_present=bool(rtext), report_shape=all(h in rtext for h in HEADS) and rtext.startswith("---"), report_bytes=len(rtext),
               items_report=len(it_r), items_handback=len(it_h), items_done=len(items), items_correct=sum(1 for v in items.values() if all(v)), n_files=meta["files"],
               deliverable_lost=(len(hbs) == 0 or len(items) == 0), ctx_attachments=ctx, platform_budget_attachments=cap_att, cap=meta.get("cap", "1.5 (before the driver recorded it)"), stopped_short=len(items) < meta["files"],
               n4_budget_reason_for_stopping=len(items) < meta["files"] and bool(re.search(r"budget|USD|spent|limit|\bnote\b|\d+%", first_hb_text, re.I)), first_hb_chars=len(first_hb_text))
    row["items_per_usd"] = round(row["items_done"] / meta["usd"], 1) if meta["usd"] else None
    row["unused"] = round(max(0.0, 1 - row["frac_first"]), 3) if row["frac_first"] is not None else None
    json.dump(dict(row, first_handback=first_hb_text, final_handback=final_hb, harness=mine), open(os.path.join(out, "cell_%s.json" % cell), "w"), indent=1)
    rows.append(row)
cols = list(rows[0].keys())
with open(os.path.join(out, "table_%s.tsv" % "_".join(c.split(":")[0] for c in sys.argv[4:])[:60]), "w") as fh:
    fh.write("\t".join(cols) + "\n" + "\n".join("\t".join(str(r[c]) for c in cols) for r in rows) + "\n")
for r in rows:
    print(json.dumps(r))
