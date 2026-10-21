"""Re-derives m1-m5, the strict template shape and the budget_usd attachment count per run of the w04-c8 E1b cells from their raw folders (harness.jsonl, transcripts under ~/.claude/projects, report file, hand-back log, ground.json, meta.json), independently of budget_arms_analyze.py, as a table on stdout.
usage: python3 -I w04c8_rederive_e1b.py <runs dir> <cell> [<cell> ...]
m1 denies = deny lines in the lab's harness.jsonl; m2 fractions = own repricing of the worker transcript (list prices of claude-sonnet-5-5: 2/10/0.10/2.5/4.0 USD per Mtok in/out/cache-read/cache-write5m/cache-write1h; output = max(recorded, chars/1.3)) at the first and at the last SubagentHandback call, over B = 0.30, next to the hook's own `end` frac; m3 report at __reports__/wave-04/<name>/00-findings_v0.md, strict shape = front matter keys of the template plus its six `## ` headings; items = table or pipe rows naming fNNN, correct = station, year and founder all in the line vs ground.json, looked for in the report and in the hand-back text; m5 = usd of meta.json; budget_usd = count of attachments of type budget_usd in the transcripts. Stdlib only."""
import glob, json, os, re, sys
runs = sys.argv[1]
P = dict(i=2.0, o=10.0, cr=0.10, cw5=2.5, cw1=4.0)
HEADS = ["## Result", "## Table", "## Worst-fitting case", "## Not covered", "## Steering questions", "## Pointers"]
KEYS = ["type:", "wave:", "author:", "date:", "version:", "decision-required:"]
def items(text, gt):
    got = {}
    for line in text.splitlines():
        m = re.match(r"\W*(f\d{3})(?:\.txt)?\W", line)
        if m and m.group(1) in gt and re.search(r"\b\d{4}\b", line):
            got[m.group(1)] = line
    ok = sum(1 for k, line in got.items() if gt[k]["station"] in line and str(gt[k]["year"]) in line and gt[k]["founder"] in line)
    return len(got), ok
print("cell\tdenies\tfirst\tfinal\thook_end\tover\treport\tshape_strict\theads6\tfront_keys\trep_items\trep_ok\thb_items\tbudget_usd_att\tusd")
for cell in sys.argv[2:]:
    d = os.path.join(runs, cell)
    meta = json.load(open(d + "/meta.json")); gt = json.load(open(d + "/ground.json")); B = float(meta["B"])
    log = [json.loads(l) for l in open(d + "/lab/__statera__/harness.jsonl")]
    nden = sum(r["event"] == "deny" for r in log)
    end = [r["frac"] for r in log if r["event"] == "end"]
    tr = glob.glob(os.path.expanduser("~/.claude/projects/*-runs-%s-lab/*/subagents/agent-*.jsonl" % cell))
    assert len(tr) == 1, tr
    reqs = {}; order = []; hb_idx = []; chars = {}; att = 0
    for k, l in enumerate(open(tr[0])):
        r = json.loads(l)
        if r.get("type") == "attachment" and r["attachment"].get("type") == "budget_usd": att += 1
        if r.get("type") != "assistant": continue
        m = r["message"]; rid = m["id"]
        if rid not in reqs: order.append(rid); chars[rid] = 0
        reqs[rid] = m["usage"]
        for c in m.get("content", []):
            if c.get("type") == "text": chars[rid] += len(c["text"])
            elif c.get("type") == "tool_use":
                chars[rid] += len(json.dumps(c["input"]))
                if c["name"].endswith("SubagentHandback"): hb_idx.append(len(order))  # requests up to and including this one
    cum = []; tot = 0.0
    for rid in order:
        u = reqs[rid]; cc = u.get("cache_creation") or {}
        cw1 = cc.get("ephemeral_1h_input_tokens", 0); cw5 = cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) - cw1)
        out = max(u.get("output_tokens", 0), chars[rid] / 1.3)
        tot += (u["input_tokens"] * P["i"] + out * P["o"] + u["cache_read_input_tokens"] * P["cr"] + cw5 * P["cw5"] + cw1 * P["cw1"]) / 1e6
        cum.append(tot)
    first = cum[hb_idx[0] - 1] / B if hb_idx else None; last = cum[hb_idx[-1] - 1] / B if hb_idx else None
    rep = glob.glob(d + "/lab/__reports__/wave-04/*/00-findings_v0.md")
    t = open(rep[0]).read() if rep else ""
    h6 = sum(h in t for h in HEADS); fk = sum(("\n" + k) in t.split("\n---")[0] if t.startswith("---") else False for k in KEYS)
    strict = bool(t.startswith("---")) and h6 == 6 and fk == 6
    ri, ro = items(t, gt) if t else (0, 0)
    hbf = glob.glob(d + "/lab/__statera__/handbacks/*.md")
    hb = open(hbf[0]).read() if hbf else ""
    hi, _ = items(hb, gt)
    print("\t".join(str(x) for x in [cell, nden, None if first is None else round(first, 3), None if last is None else round(last, 3), end[-1] if end else None,
          None if first is None else round(last - first, 3), bool(t), strict, h6, fk, ri, ro, hi, att, round(meta["usd"], 3)]), flush=True)
    print("   handback calls (request index):", hb_idx, "of", len(order), "requests; own total/B", round(tot / B, 3))
