#!/usr/bin/env python3
"""Recomputes n1-n5, the budget_usd attachment count and the hook-log fraction at the first hand-back call, per run, from raw run folders (harness.jsonl, worker transcript, report or hand-back text, ground.json), without importing the author's analyser; prints one TSV to stdout.
usage: w04c3_verify_runs.py <scratch> <cell> [<cell> ...]   (scratch = /private/tmp/murmuration-w04/author-w04-2)
Inputs: <scratch>/runs/<cell>/{meta.json,ground.json,lab/__statera__/harness.jsonl,lab/__reports__,lab/__statera__/handbacks} and ~/.claude/projects/*runs-<cell>-lab/*/subagents/agent-*.jsonl. Stdlib only."""
import glob, json, os, re, sys
scratch = sys.argv[1]
def worker(cell):
    c = glob.glob(os.path.expanduser("~/.claude/projects/*runs-%s-lab/*/subagents/agent-*.jsonl" % cell))
    return sorted(c, key=os.path.getsize)[-1] if c else None
print("\t".join("cell n_req budget_att att_total_remaining hb_req_index frac_first_hooklog frac_end_log log_last_frac n_hb_calls items_ok items_wrong n_files usd ipu n1_ge_0.9 unused".split()))
for cell in sys.argv[2:]:
    R = os.path.join(scratch, "runs", cell)
    meta = json.load(open(R + "/meta.json")); ground = json.load(open(R + "/ground.json"))
    logs = [json.loads(l) for l in open(R + "/lab/__statera__/harness.jsonl")]
    reqs, order, hb, att, first_att = {}, [], [], 0, None
    for l in open(worker(cell)):
        d = json.loads(l)
        if d.get("type") == "attachment" and d["attachment"].get("type") == "budget_usd":
            att += 1; first_att = first_att or d["attachment"]
        if d.get("type") != "assistant": continue
        key = d.get("requestId") or d["message"].get("id")
        if key not in reqs: reqs[key] = len(order) + 1; order.append(key)
        for b in d["message"].get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                hb.append((reqs[key], str((b.get("input") or {}).get("message") or "")))
    n = len(order)
    fr = [(x.get("requests"), x.get("frac")) for x in logs if x.get("frac") is not None]
    ends = [x for x in logs if x.get("event") == "end"]
    hbi = hb[0][0] if hb else None
    ff = None
    if hbi is not None:
        after = [f for r, f in fr if r is not None and r >= hbi]
        ff = after[0] if after else None
    # items: report table (N=90) else hand-back text; first row per file
    text = ""
    for p in glob.glob(R + "/lab/__reports__/wave-04/*/*.md"): text += open(p, errors="replace").read() + "\n"
    if meta.get("brief") != "report": text = "\n".join(t for _, t in hb[:1]) if hb else ""
    ok = wrong = 0; seen = set()
    for ln in text.splitlines():
        m = re.search(r"\bf(\d{3})\b", ln)
        if not m or "f" + m.group(1) not in ground or m.group(1) in seen: continue
        g = ground["f" + m.group(1)]
        if str(g["year"]) in ln and g["founder"] in ln and g["station"] in ln:
            seen.add(m.group(1)); ok += 1
        elif re.search(r"\b1[0-9]{3}\b", ln):
            seen.add(m.group(1)); wrong += 1
    usd = meta["usd"]; B = float(meta["B"])
    n1 = ff
    print("\t".join(str(x) for x in [cell, n, att, (first_att or {}).get("total"), hbi, ff, ends[0]["frac"] if ends else None, fr[-1][1] if fr else None, len(hb), ok, wrong, meta["files"], round(usd, 3), round(ok / usd, 1), (n1 >= 0.9) if n1 is not None else None, round(max(0, 1 - n1), 3) if n1 is not None else None]))
