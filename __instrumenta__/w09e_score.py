# Scores w09e_run.py cells (stream.jsonl, debug.log, meta.json) into one tsv row per run on stdout: compaction numbers, requests and tool calls after the boundary, tokens re-read, spend re-priced at Opus 5.5 list, the six answers' scored items; prints no transcript text unless --show.
"""usage: w09e_score.py RUNS_DIR NAME [NAME ...] [--show]      (RUNS_DIR = S/runs)
Prices per million tokens, Opus 5.5 list (scripts/lab_status.py PRICES): input 4, output 20, cache read 0.20, cache write 5 min 5, 1 h 8. The compaction request's usage is the forked agent's `totalUsage` in debug.log
(the stream's own cost line does not show it separately). Re-read tokens (ESTIMATE): characters of every tool result after the compact boundary / 3.6; also the growth of the request context between the first
request after the boundary and the last (MEASURED from usage), which is what the re-reads add to every later request.
Scoring of the answers (truth from the lab at the cut, w09e truth in this file): Q1 the three names each with its claim id or task; Q2 the user's sentence verbatim (whitespace and quotes ignored);
Q3 both labels `unverified MEASURED`; Q4 w08-c2 does not land / no verifier AND w08-c1 decided at the verifier's verdict; Q5 the number 9 and w05-c1, w07-c7 (and not w06-c3); Q6 `bfbcc96` and line 5; Q7 (explorer-w08-d's hand-back) 7 sessions, 1,123 requests, costliest read 33k characters at USD 0.80; Q8 (explorer-w08-b's) right file in the top 10 for 15 and 17 of 23 questions.
Regex scoring is a first pass; the runs' answers are read by hand and the table notes disagreements (--show prints the final answers)."""
import json, os, re, sys, glob

PR = dict(i=4.0, o=20.0, r=0.20, w5=5.0, w1=8.0)
SENT = ("You can proceed with wave 8 following the results of wave 7 and all other puzzles. The overarching goal is to progressively optimize murmuration by using it yourself. "
        "You are Murmuration and you optimize murmuration. Budget is 150USD; it is currently midnight, you have 6 hours. Use them.")
norm = lambda t: re.sub(r"\s+", " ", re.sub(r"[`*‘’“”\"']", "", t)).strip().lower()


def usd(u):
    cc = u.get("cache_creation") or {}
    w1 = cc.get("ephemeral_1h_input_tokens", u.get("cache_creation_input_tokens", 0) if not cc else 0)
    w5 = cc.get("ephemeral_5m_input_tokens", 0)
    return (u.get("input_tokens", 0) * PR["i"] + u.get("output_tokens", 0) * PR["o"] + u.get("cache_read_input_tokens", 0) * PR["r"] + w5 * PR["w5"] + w1 * PR["w1"]) / 1e6


def sections(text):
    marks = list(re.finditer(r"(?m)^\s*(?:[#>*\-\s]*)\(?([1-8])[\).:]\s|^\s*\*\*\(?([1-8])[\).:]", text))
    out = {}
    for n, m in enumerate(marks):
        k = int(m.group(1) or m.group(2))
        if k not in out:
            out[k] = text[m.end():marks[n + 1].start()] if n + 1 < len(marks) else text[m.end():]
    return out


def score(text):
    sec = sections(text); s = lambda k: sec.get(k, text)
    s1 = s(1)
    def pair(n, pat):
        i = s1.find(n); return i >= 0 and re.search(pat, s1[i:i + 260], re.I) is not None
    q1 = pair("author-w08-3", r"w08-c3|compaction") and pair("explorer-w08-g", r"request|merge|batch|worker") and pair("reproducer-w08-1", r"w08-c1|verif")
    q2 = norm(SENT) in norm(s(2))
    s3 = s(3); q3 = len(re.findall(r"unverified", s3, re.I)) >= 1 and "w08-c1" in s3 and "w08-c2" in s3 and not re.search(r"\bSUPPORTED\b|\bOVERSTATED\b", s3)
    s4 = s(4); q4 = bool(re.search(r"(not land|does not land|won.t land|no verifier|not .{0,30}verif|without a verifier)", s4, re.I)) and bool(re.search(r"reproducer|verdict", s4, re.I))
    s5 = s(5); q5 = bool(re.search(r"\b9\b|\bnine\b", s5, re.I)) and "w05-c1" in s5 and "w07-c7" in s5 and "w06-c3" not in s5
    s6 = s(6); q6 = "bfbcc96" in s6 and bool(re.search(r"line\s*5\b|:5\b|\b5\b", s6))
    s7 = s(7); q7 = bool(re.search(r"\b7\b|seven", s7, re.I)) and "1,123" in s7.replace(" ", "") and bool(re.search(r"0\.80", s7)) and bool(re.search(r"33\s*k|33,\d{3}", s7))
    s8 = s(8); q8 = bool(re.search(r"\b15\b", s8)) and bool(re.search(r"\b17\b", s8)) and "23" in s8
    return dict(q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6, q7=q7, q8=q8, sectioned=all(k in sec for k in range(1, 9)))


def one(RD, name, show=False):
    D = os.path.join(RD, name); m = json.load(open(os.path.join(D, "meta.json")))
    reqs, results, boundary, text, calls, order = {}, [], None, "", [], []
    pending = {}
    for l in open(os.path.join(D, "stream.jsonl")):
        try: d = json.loads(l)
        except ValueError: continue
        t = d.get("type")
        if t == "system" and d.get("subtype") == "compact_boundary": boundary = len(order); bmeta = d["compact_metadata"]
        elif t == "assistant":
            mm = d["message"]; mid = mm["id"]
            if mid not in reqs: reqs[mid] = mm["usage"]; order.append(mid)
            for b in mm["content"]:
                if b.get("type") == "tool_use": pending[b["id"]] = (len(order), b["name"], json.dumps(b["input"])[:160])
        elif t == "user" and isinstance(d["message"].get("content"), list):
            for b in d["message"]["content"]:
                if b.get("type") == "tool_result":
                    c = b["content"]; c = c if isinstance(c, str) else json.dumps(c)
                    k, nm, inp = pending.get(b.get("tool_use_id"), (0, "?", ""))
                    results.append((k, nm, inp, len(c), c[:100]))
        elif t == "result": text = d.get("result", "")
    fa = None
    for l in open(os.path.join(D, "debug.log"), errors="replace"):
        mm = re.search(r"Forked agent \[reactive-compact\] finished.*totalUsage: input=(\d+) output=(\d+) cacheRead=(\d+) cacheCreate=(\d+)", l)
        if mm: fa = dict(input_tokens=int(mm.group(1)), output_tokens=int(mm.group(2)), cache_read_input_tokens=int(mm.group(3)), cache_creation_input_tokens=int(mm.group(4)))
    ctx = lambda u: u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
    post = [reqs[i] for i in order]
    first, last = ctx(post[0]), ctx(post[-1])
    rr = [r for r in results if r[1] not in ("Skill",)]
    chars = sum(r[3] for r in rr)
    comp_usd = usd(fa) if fa else 0.0
    post_usd = sum(usd(u) for u in post)
    sc = score(text)
    row = dict(run=name, arm=m["arm"], boundary=bmeta["pre_tokens"], post_tokens=bmeta["post_tokens"], comp_s=round(bmeta["duration_ms"] / 1000, 1), comp_input=fa and fa["input_tokens"], comp_out=fa and fa["output_tokens"],
               comp_usd=round(comp_usd, 3), requests=len(post), first_ctx=first, last_ctx=last, tool_calls=len(rr), reread_chars=chars, reread_tok_est=round(chars / 3.6), growth=last - first,
               after_usd=round(post_usd, 3), total_usd=round(comp_usd + post_usd, 3), cost_reported=m.get("cost_reported"), **{k: int(v) for k, v in sc.items()})
    if show:
        print("=====", name); print(text)
        for r in rr: print("  call", r[0], r[1], r[2][:110].replace("\n", " "), "->", r[3], "chars")
    return row


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--show"]
    rows = [one(a[0], n, "--show" in sys.argv) for n in a[1:]]
    cols = list(rows[0])
    print("\t".join(cols))
    for r in rows: print("\t".join(str(r[c]) for c in cols))
