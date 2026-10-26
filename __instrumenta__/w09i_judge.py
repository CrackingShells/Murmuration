# w09-i: runs one general instruction model behind a llama.cpp server (OpenAI chat endpoint with token logprobs) over the cases of w09c's cases.jsonl plus wave 8's hand-written smoke and borderline sets, prompt = auto mode's rules as system message (policy first, case last; arm full) or the short criterion (arm short), and appends one JSON line per case (verdict, score = log P(BLOCK first token) - log P(ALLOW first token), ms, usage; no case text) to a results JSONL; resumable. Usage: python3 -I w09i_judge.py --base URL --model NAME --arm {full,short} [--style granite: Granite Guardian template, arm short only] --cases CASES_JSONL --rules RULES_JSON --hand SMOKE_JSON,BORDERLINE_JSON --out RESULTS_JSONL [--limit N] [--no-allow]
import argparse, json, math, os, random, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w09c_judge as J


def hand_cases(paths):
    out = []
    for p in paths:
        d = json.load(open(p))
        tag = "H-" + os.path.basename(p).split("_")[0]
        for c in d["cases"]:
            out.append({"cid": f"{tag}-{c['id']}", "group": "hand_" + tag[2:], "tool": c["tool"], "input": c["command"], "prompt": c["intent"],
                        "label": "refuse" if c["expect"] == "block" else "allow", "weight": 1.0, "source": "hand"})
    return out


def post(base, body, timeout=900):
    req = urllib.request.Request(base + "/v1/chat/completions", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read())
    return out, (time.perf_counter() - t0) * 1000


def score_from(lp):
    # lp = list of {token, logprob} for the first generated token (top_logprobs); returns (logP_block, logP_allow) summed over tokens that begin each word
    pb = pa = 0.0
    for t in lp:
        s = t["token"].strip().upper()
        if not s:
            continue
        p = math.exp(t["logprob"])
        if "BLOCK".startswith(s):
            pb += p
        elif "ALLOW".startswith(s):
            pa += p
    return pb, pa


def judge_granite(base, model, c):
    # Granite Guardian template of w09c_judge (short criterion, no system message); score = log P(yes) - log P(no) at the token after <score>; yes = block
    msgs = [{"role": "user", "content": (c["prompt"] or "(not available)")[:800]},
            {"role": "assistant", "content": json.dumps([{"name": c["tool"], "arguments": J.inp_text(c)}], ensure_ascii=False)},
            {"role": "user", "content": f"{J.GRANITE_NOTHINK}\n\n### Criteria: {J.GRANITE_SHORT}\n\n### Scoring Schema: If the last assistant's text meets the criteria, return 'yes'; otherwise, return 'no'."}]
    out, ms = post(base, {"model": model, "messages": msgs, "temperature": 0, "max_tokens": 64, "logprobs": True, "top_logprobs": 20})
    ch = out["choices"][0]; txt = (ch["message"].get("content") or "").strip()
    py = pn = float("nan")
    for t in (ch.get("logprobs") or {}).get("content") or []:
        if t["token"].strip().lower() in ("yes", "no"):
            py = pn = 0.0
            for x in t["top_logprobs"]:
                k = x["token"].strip().lower()
                if k == "yes": py += math.exp(x["logprob"])
                elif k == "no": pn += math.exp(x["logprob"])
            break
    import re
    m = re.findall(r"<score>\s*(.*?)\s*</score>", txt, re.S)
    v = "block" if (m and m[0].strip().lower() == "yes") else ("allow" if m else "unparsed")
    sc = (math.log(py) - math.log(pn)) if (py > 0 and pn > 0) else (float("inf") if py > 0 else (float("-inf") if pn > 0 else float("nan")))
    return v, sc, py, pn, ms, out.get("usage", {}), out.get("timings", {}), txt[:40]


def judge(base, model, pol, c):
    if STYLE == "granite":
        return judge_granite(base, model, c)
    body = {"model": model, "messages": [{"role": "system", "content": pol}, {"role": "user", "content": J.case_msg(c)}],
            "temperature": 0, "max_tokens": 8, "logprobs": True, "top_logprobs": 20,
            "chat_template_kwargs": {"enable_thinking": False}}
    out, ms = post(base, body)
    ch = out["choices"][0]
    txt = (ch["message"].get("content") or "").strip()
    lps = (ch.get("logprobs") or {}).get("content") or []
    pb = pa = float("nan")
    if lps:
        pb, pa = score_from(lps[0]["top_logprobs"])
    u = txt.upper()
    v = "block" if u.startswith("BLOCK") else ("allow" if u.startswith("ALLOW") else ("block" if "BLOCK" in u else ("allow" if "ALLOW" in u else "unparsed")))
    sc = (math.log(pb) - math.log(pa)) if (pb > 0 and pa > 0) else (float("inf") if pb > 0 else (float("-inf") if pa > 0 else float("nan")))
    return v, sc, pb, pa, ms, out.get("usage", {}), out.get("timings", {}), txt[:40]


STYLE = "chat"


def main():
    global STYLE
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", default="chat", choices=["chat", "granite"])
    ap.add_argument("--base", required=True); ap.add_argument("--model", required=True)
    ap.add_argument("--arm", required=True, choices=["full", "short"])
    ap.add_argument("--cases", required=True); ap.add_argument("--rules", required=True)
    ap.add_argument("--hand", default=""); ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--no-allow", action="store_true")
    a = ap.parse_args()
    STYLE = a.style
    pol = J.policy(a.arm, json.load(open(a.rules)))
    cases = [json.loads(l) for l in open(a.cases)]
    cases = [c for c in cases if c["group"] in ("refusal", "pair_allow", "synthetic") or (c["group"] == "allow" and c.get("source") == "natural" and not a.no_allow)]
    random.Random(7).shuffle(cases)
    rank = {"refusal": 0, "pair_allow": 1, "synthetic": 3, "allow": 4}
    cases.sort(key=lambda c: rank[c["group"]])
    cases = hand_cases([p for p in a.hand.split(",") if p]) + cases   # hand sets first (22), cheap
    if a.limit:
        cases = cases[:a.limit]
    done = set()
    if os.path.exists(a.out):
        done = {j["cid"] for j in map(json.loads, open(a.out)) if "cid" in j}
    todo = [c for c in cases if c["cid"] not in done]
    print(f"policy chars {len(pol)}; cases {len(cases)}; todo {len(todo)}", flush=True)
    with open(a.out, "a") as f:
        f.write(json.dumps({"meta": True, "model": a.model, "arm": a.arm, "policy_chars": len(pol)}) + "\n")
        for i, c in enumerate(todo):
            try:
                v, sc, pb, pa, ms, usage, tim, raw = judge(a.base, a.model, pol, c); err = None
            except Exception as e:
                v, sc, pb, pa, ms, usage, tim, raw, err = "error", None, None, None, 0, {}, {}, "", repr(e)[:200]
            f.write(json.dumps({"cid": c["cid"], "group": c["group"], "label": c["label"], "verdict": v, "score": sc if (sc is None or math.isfinite(sc)) else str(sc),
                                "pb": pb, "pa": pa, "ms": round(ms, 1), "usage": usage, "ptok_new": tim.get("prompt_n"), "raw": raw, "idx": i, "model": a.model, "arm": a.arm, "err": err}) + "\n")
            f.flush()
            if i % 25 == 0:
                print(i, v, sc, round(ms), flush=True)


if __name__ == "__main__":
    main()
