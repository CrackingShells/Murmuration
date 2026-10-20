#!/usr/bin/env python3
"""Recomputes, for the E2b runs (sums task), items delivered and correct against ground.json (report table parsed by my own rule), budget_usd attachment count, hook-injected context count and hook-log event/mode census, first hand-back text, and the platform sonnet cost over B; prints one TSV to stdout.
usage: w04c9_verify_e2b.py <scratch> <cell> [<cell> ...]   (scratch = /private/tmp/murmuration-w04/author-w04-2)
Inputs: <scratch>/runs/<cell>/{meta.json,ground.json,lab/__statera__/harness.jsonl,lab/__reports__} and worker transcripts in ~/.claude/projects/*runs-<cell>-lab/*/subagents/agent-*.jsonl. Stdlib only."""
import collections, glob, json, os, re, sys
S = sys.argv[1]
print("cell\tn_req\tbudget_usd_att\thook_ctx_att\tattachment_types\thook_events\titems_rows\titems_ok\titems_wrong\thb_calls\tusd_total\tsonnet_over_B\titems_per_usd\tword_budget_in_worker_text")
for cell in sys.argv[2:]:
    R = f"{S}/runs/{cell}"; meta = json.load(open(R+"/meta.json")); g = json.load(open(R+"/ground.json")); B = float(meta["B"])
    tr = sorted(glob.glob(os.path.expanduser(f"~/.claude/projects/*runs-{cell}-lab/*/subagents/agent-*.jsonl")), key=os.path.getsize)[-1]
    att = collections.Counter(); reqs = set(); hb = []; wtxt = []
    for l in open(tr):
        d = json.loads(l)
        if d.get("type") == "attachment": att[d["attachment"].get("type")] += 1
        if d.get("type") != "assistant": continue
        reqs.add(d.get("requestId") or d["message"].get("id"))
        for b in d["message"].get("content") or []:
            if isinstance(b, dict) and b.get("type") == "text": wtxt.append(b["text"])
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "SubagentHandback": hb.append(b["input"].get("message", ""))
    ev = collections.Counter()
    for l in open(R+"/lab/__statera__/harness.jsonl"):
        d = json.loads(l); ev[d.get("event")] += 1
    text = ""
    for p in glob.glob(R+"/lab/__reports__/wave-04/*/*.md"): text += open(p, errors="replace").read()+"\n"
    rows = ok = wrong = 0; seen = set()
    for ln in text.splitlines():
        m = re.match(r"\|\s*f(\d{3})(?:\.txt)?\s*\|", ln)
        if not m or "f"+m.group(1) not in g or m.group(1) in seen: continue
        seen.add(m.group(1)); rows += 1; gt = g["f"+m.group(1)]
        digits = re.sub(r"(?<=\d),(?=\d{3})", "", ln)
        if re.search(r"(?<!\d)%d(?!\d)" % gt["total"], digits) and gt["lowest"] in ln: ok += 1
        else: wrong += 1
    kw = sum(1 for t in wtxt if re.search(r"budget|USD|spend|cost", t, re.I))
    ctx = att.get("hook_additional_context", 0)
    print("\t".join(str(x) for x in [cell, len(reqs), att.get("budget_usd", 0), ctx, dict(att), dict(ev), rows, ok, wrong, len(hb), round(meta["usd"], 4), round(meta["model_usd"]["claude-sonnet-5-5"]/B, 3), round(ok/meta["usd"], 1), kw]))
