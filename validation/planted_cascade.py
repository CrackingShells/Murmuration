#!/usr/bin/env python3
"""Experiment B: does "whose words the verdict reuses" separate a primed verifier from an independent one?

Python fits because the work is deterministic text arithmetic (substring coverage, lzma code
lengths, first-occurrence offsets) on a few kilobytes, with only the standard library.

Functions
  byte_reuse(text, source, min_len)   share of text's bytes covered by substrings >= min_len bytes found in source
  lzma_redundancy(text, ctx)          1 - (C(ctx+text) - C(ctx)) / C(text), raw lzma, preset 9
  term_first_use(events, terms)       per term and speaker: first event index and byte offset
  load_transcript(path)               events from a Claude Code subagent .jsonl
Usage
  python3 validation/planted_cascade.py --selftest
  python3 validation/planted_cascade.py --run [--genesis PATH] [--out validation/runs]

Measures are instruments for attention, not decision rules (see __reports__/genesis/08).
"""
import argparse
import json
import lzma
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GENESIS = "/Users/hacker/Documents/explore/combinatorics_on_binary"
AUTHOR_REPORT = "__reports__/strided_trellis/00-findings_v0.md"
# controls: the null set (other workers' v0 reports on unrelated topics) and two texts neither run saw
NULL_REPORTS = ["literature/00-findings_v0.md", "foundations/00-findings_v0.md", "generative_atlas/00-findings_v0.md",
                "generative_laws/00-findings_v0.md", "superstring_g/00-findings_v0.md", "naming/00-findings_v0.md"]
REVISED_AUTHOR = "__reports__/strided_trellis/01-findings_v1.md"
REPRODUCTION = "__reports__/reproduction/00-findings_v0.md"
CLAIM = ('Bitwise-majority training of a binary table is a fixed point from a random start (identical to the '
         'random table in 46 of 51 runs; the 5 exceptions are all at ω ≤ 8), so no "trained binary" curve is reported.')

# Chosen by me after both final verdicts had been read, NOT pre-registered; the report says so.
TERMS = {
    "claim_framing": ["fixed point", "bitwise", "majority", "identical", "exceptions", "46 of 51", "random start"],
    "report_only_framing": ["held-out", "side information", "repetition code", "decorrelat", "Lloyd", "regime C"],
    "own_method": ["strictly", "tolerance", "exact", "1e-3", "40 of 51", "11 "],
}


# ---------------------------------------------------------------- measures
def byte_reuse(text, source, min_len=12):
    """Fraction of the bytes of `text` covered by maximal substrings of length >= min_len found in `source`.

    Greedy left to right: at each position take the longest match in source; if it is at least
    min_len bytes, those bytes count as reused and the scan jumps past them; otherwise advance one byte.
    Deterministic, case-sensitive, byte-level (so multi-byte characters count as several bytes).
    """
    t, s = text.encode("utf-8"), source.encode("utf-8")
    if not t:
        return 0.0
    covered, i = 0, 0
    while i < len(t):
        lo, hi = 0, len(t) - i  # longest L with t[i:i+L] in s; monotone in L, so bisect
        if hi < min_len or t[i:i + min_len] not in s:
            i += 1
            continue
        lo = min_len
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if t[i:i + mid] in s:
                lo = mid
            else:
                hi = mid - 1
        covered += lo
        i += lo
    return covered / len(t)


def _clen(b):
    filt = [{"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME, "dict_size": 1 << 22}]
    return len(lzma.compress(b, format=lzma.FORMAT_RAW, filters=filt))


def lzma_redundancy(text, ctx):
    """1 - new/total, where new = C(ctx+text) - C(ctx) and total = C(text); clipped to [0, 1]."""
    t, c = text.encode("utf-8"), ctx.encode("utf-8")
    total = _clen(t)
    new = _clen(c + t) - _clen(c)
    return max(0.0, min(1.0, 1.0 - new / total))


def term_first_use(events, terms):
    """events: list of (index, speaker, text). Returns {term: {speaker: (index, byte_offset) or None}}.

    Case-insensitive substring search; the byte offset is within that event's text.
    """
    speakers = sorted({sp for _, sp, _ in events})
    out = {}
    for term in terms:
        out[term] = {}
        for sp in speakers:
            hit = None
            for idx, s2, text in events:
                if s2 != sp:
                    continue
                pos = text.lower().find(term.lower())
                if pos >= 0:
                    hit = (idx, len(text[:pos].encode("utf-8")))
                    break
            out[term][sp] = hit
    return out


# ------------------------------------------------------------- transcripts
def _flat(content):
    if isinstance(content, str):
        return content
    parts = []
    for b in content:
        if isinstance(b, dict):
            if b.get("type") == "text":
                parts.append(b["text"])
            elif b.get("type") == "tool_result":
                parts.append(_flat(b.get("content", "")))
    return "\n".join(parts)


def load_transcript(path):
    """Events (index, speaker, text) from a subagent jsonl.

    speaker: 'brief' (the first tool result: the brief file the agent was told to read),
    'tool' (other tool results), 'agent' (assistant text, tool-call inputs, the final hand-back).
    Attachments, system reminders and the harness pointer prompt are skipped.
    """
    events, first_result_seen, n = [], False, 0
    for line in open(path, encoding="utf-8"):
        d = json.loads(line)
        if d.get("type") not in ("user", "assistant"):
            continue
        msg = d.get("message", {})
        content = msg.get("content")
        if d["type"] == "user":
            if isinstance(content, str):
                continue
            for b in content:
                if b.get("type") == "tool_result":
                    txt = _flat(b.get("content", ""))
                    if not first_result_seen:
                        txt = re.sub(r"(?m)^\s*\d+\t", "", txt)  # strip Read's line numbers
                        events.append((n, "brief", txt))
                        first_result_seen = True
                    else:
                        events.append((n, "tool", txt))
                    n += 1
        else:
            for b in content:
                t = b.get("type")
                if t == "text" and b.get("text"):
                    events.append((n, "agent", b["text"]))
                    n += 1
                elif t == "tool_use":
                    inp = b.get("input", {})
                    txt = "\n".join(str(v) for v in inp.values())
                    events.append((n, "agent", txt))
                    n += 1
    return events


def final_message(path):
    for line in open(path, encoding="utf-8"):
        d = json.loads(line)
        if d.get("type") == "assistant":
            for b in d["message"]["content"]:
                if b.get("type") == "tool_use" and b.get("name") == "SubagentHandback":
                    last = b["input"]["message"]
    return last


def render(events):
    out = []
    for idx, sp, text in events:
        out.append(f"### [{idx}] {sp}\n\n```\n{text.rstrip()}\n```\n")
    return "\n".join(out)


# --------------------------------------------------------------------- run
def run(genesis, outdir, agents):
    author = open(os.path.join(genesis, AUTHOR_REPORT), encoding="utf-8").read()
    res = {"min_len_sensitivity": {}, "runs": {}}
    verdicts, briefs, events_by = {}, {}, {}
    for name, path in agents.items():
        ev = load_transcript(path)
        events_by[name] = ev
        briefs[name] = [t for _, sp, t in ev if sp == "brief"][0]
        verdicts[name] = final_message(path)
        with open(os.path.join(outdir, f"{name}_transcript.md"), "w", encoding="utf-8") as f:
            f.write(f"# {name}: events in order (brief = what the agent was handed; agent = its words and commands; tool = outputs)\n\n")
            f.write(render(ev))
        with open(os.path.join(outdir, f"{name}_verdict.txt"), "w", encoding="utf-8") as f:
            f.write(verdicts[name] + "\n")
    scaffold = briefs["run1"]  # run 1's brief = instructions + claim, no report
    for name in agents:
        v = verdicts[name]
        r = {"verdict_bytes": len(v.encode("utf-8"))}
        for L in (8, 12, 20):
            r[f"reuse_author_L{L}"] = round(byte_reuse(v, author, L), 4)
            r[f"reuse_first_message_L{L}"] = round(byte_reuse(v, briefs[name], L), 4)
            r[f"reuse_scaffold_only_L{L}"] = round(byte_reuse(v, scaffold, L), 4)
            r[f"reuse_claim_only_L{L}"] = round(byte_reuse(v, CLAIM, L), 4)
            r[f"reuse_other_verdict_L{L}"] = round(byte_reuse(v, verdicts["run2" if name == "run1" else "run1"], L), 4)
        for L in (12,):
            nulls = [byte_reuse(v, open(os.path.join(genesis, "__reports__", n), encoding="utf-8").read(), L) for n in NULL_REPORTS]
            r["null_reports_mean_L12"] = round(sum(nulls) / len(nulls), 4)
            r["null_reports_max_L12"] = round(max(nulls), 4)
            r["reuse_revised_author_v1_L12"] = round(byte_reuse(v, open(os.path.join(genesis, REVISED_AUTHOR), encoding="utf-8").read(), L), 4)
            r["reuse_reproduction_report_L12"] = round(byte_reuse(v, open(os.path.join(genesis, REPRODUCTION), encoding="utf-8").read(), L), 4)
        r["lzma_redundancy_author"] = round(lzma_redundancy(v, author), 4)
        r["lzma_redundancy_first_message"] = round(lzma_redundancy(v, briefs[name]), 4)
        r["lzma_redundancy_scaffold_only"] = round(lzma_redundancy(v, scaffold), 4)
        agent_ev = [e for e in events_by[name] if e[1] in ("agent", "brief", "tool")]
        allterms = [t for ts in TERMS.values() for t in ts]
        fu = term_first_use(agent_ev, allterms)
        r["first_use"] = {t: fu[t] for t in allterms}
        res["runs"][name] = r
    with open(os.path.join(outdir, "planted_cascade_results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    return res


# ----------------------------------------------------------------- selftest
def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    a = "the trained table is identical to the random table in forty runs of fifty-one"
    check("byte_reuse(identical)=1", byte_reuse(a, a, 12) == 1.0)
    check("byte_reuse(unrelated)=0", byte_reuse("zzzzzzzzzzzzzzzzzzzzzzzz", a, 12) == 0.0)
    half = "the trained table is identical to the random table QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ"
    r = byte_reuse(half, a, 12)
    check("byte_reuse(partial) = 51/85 exactly (got %.4f)" % r, abs(r - 51 / 85) < 1e-12)
    check("byte_reuse ignores matches shorter than min_len", byte_reuse("abcdefghij", "abcdefghij", 12) == 0.0)
    check("byte_reuse counts utf-8 bytes", byte_reuse("ω ≤ 8 ω ≤ 8", "ω ≤ 8 ω ≤ 8", 8) == 1.0)
    check("lzma_redundancy(copy) high", lzma_redundancy(a * 1, a + " ") > 0.5)
    rnd = "".join(chr(97 + (i * 7919 + i * i * 31) % 26) for i in range(300))
    check("lzma_redundancy(self-context) > unrelated", lzma_redundancy(rnd, rnd) > lzma_redundancy(rnd, a))
    ev = [(0, "brief", "claim: fixed point, 46 of 51"), (1, "agent", "I compute the rows"), (2, "agent", "so a Fixed Point it is"), (3, "tool", "no match")]
    fu = term_first_use(ev, ["fixed point", "46 of 51", "absent"])
    check("first use by speaker", fu["fixed point"]["brief"] == (0, 7) and fu["fixed point"]["agent"] == (2, 5) and fu["fixed point"]["tool"] is None)
    check("first use of an absent term is None everywhere", all(v is None for v in fu["absent"].values()))
    check("first use: term only in brief is not credited to the agent", fu["46 of 51"]["agent"] is None)
    print("PASS" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--genesis", default=GENESIS)
    ap.add_argument("--out", default=os.path.join(HERE, "runs"))
    ap.add_argument("--run1")
    ap.add_argument("--run2")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.run:
        print(json.dumps(run(a.genesis, a.out, {"run1": a.run1, "run2": a.run2}), indent=1, ensure_ascii=False))
        return
    ap.print_help()


if __name__ == "__main__":
    main()
