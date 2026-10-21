"""Variants of lab_status.parse_transcript (same return value), a canonical dump of their results, and a process-pool wrapper, from a file list to timings and an equality verdict against the original on the same files.

usage: w07d_parsers.py <lab root> <files.txt> check             every variant's canonical dump is compared byte for byte with the original's (and with --rust-dump FILE if given)
       w07d_parsers.py <lab root> <files.txt> time VARIANT [W]  in-process wall time of parsing all files (W fork workers when W is given), 5 repeats, JSON line on stdout
Variants: orig (scripts/lab_status.py as is), bytes (binary read, byte prefilter per line), buf_find (whole file read, bytes.find of the three keys, only the lines around hits are decoded), buf_re (same with one compiled regex).
canonical(): one tab-separated line per (file, message) as w07d_rs --dump writes it, sorted.
"""
import sys, os, re, json, time, glob, multiprocessing as mp
root = os.path.abspath(sys.argv[1]); sys.path.insert(0, os.path.join(root, "scripts"))
import lab_status as L

def _apply(rec, msgs, st):
    """The body of the original loop, unchanged (st = [cost_state, setting])."""
    if not isinstance(rec, dict):
        return
    kind, m = rec.get("type"), rec.get("message")
    if kind == "cost-state" and rec.get("totalCostUSD") is not None:
        st[0] = rec
    elif kind == "agent-setting" and rec.get("agentSetting") and not st[1]:
        st[1] = rec["agentSetting"]
    elif kind == "assistant" and isinstance(m, dict) and isinstance(m.get("usage"), dict) and m.get("model") != "<synthetic>":
        key = m.get("id") or rec.get("requestId") or rec.get("uuid") or len(msgs)
        msg = msgs.setdefault(key, {"model": m.get("model") or "unknown", "usage": {}, "ts": rec.get("timestamp"), "sid": rec.get("sessionId")})
        L.merge_usage(msg["usage"], m["usage"])
        msg["final"] = bool(m.get("stop_reason"))

def _loads(b):
    try:
        return json.loads(b.decode("utf-8", "replace"))
    except ValueError:
        return None

def parse_bytes(path, warnings):
    msgs, st = {}, [None, None]
    try:
        with open(path, "rb") as fh:
            for line in fh:
                if b'"assistant"' not in line and b'"cost-state"' not in line and b'"agent-setting"' not in line:
                    continue
                rec = _loads(line)
                if rec is not None:
                    _apply(rec, msgs, st)
    except OSError as err:
        warnings.append("could not read %s: %s" % (path, err.strerror or err))
    return msgs, st[0], st[1]

KEYS = (b'"assistant"', b'"cost-state"', b'"agent-setting"')

def _spans(buf, hits):
    """Distinct (start, end) of the lines holding the hit offsets, in file order."""
    out, last_end = [], -1
    for p in sorted(hits):
        if p < last_end:
            continue
        s = buf.rfind(b"\n", 0, p) + 1
        e = buf.find(b"\n", p)
        e = len(buf) if e < 0 else e
        out.append((s, e)); last_end = e
    return out

def parse_buf_find(path, warnings):
    msgs, st = {}, [None, None]
    try:
        with open(path, "rb") as fh:
            buf = fh.read()
        hits = []
        for k in KEYS:
            p = buf.find(k)
            while p >= 0:
                hits.append(p); p = buf.find(k, p + 1)
        for s, e in _spans(buf, hits):
            rec = _loads(buf[s:e])
            if rec is not None:
                _apply(rec, msgs, st)
    except OSError as err:
        warnings.append("could not read %s: %s" % (path, err.strerror or err))
    return msgs, st[0], st[1]

RE = re.compile(rb'"(?:assistant|cost-state|agent-setting)"')
def parse_buf_re(path, warnings):
    msgs, st = {}, [None, None]
    try:
        with open(path, "rb") as fh:
            buf = fh.read()
        for s, e in _spans(buf, [m.start() for m in RE.finditer(buf)]):
            rec = _loads(buf[s:e])
            if rec is not None:
                _apply(rec, msgs, st)
    except OSError as err:
        warnings.append("could not read %s: %s" % (path, err.strerror or err))
    return msgs, st[0], st[1]

VARIANTS = {"orig": L.parse_transcript, "bytes": parse_bytes, "buf_find": parse_buf_find, "buf_re": parse_buf_re}

def canonical(path, res):
    msgs, cost, setting = res
    out = ["F\t%s" % path, "S\t%s\t%s" % (path, setting if setting else "-"),
           "C\t%s\t%s" % (path, json.dumps(cost["totalCostUSD"]) if cost else "-")]
    for k, m in msgs.items():
        u = m["usage"]; cc = u.get("cache_creation") if isinstance(u.get("cache_creation"), dict) else {}
        key = ("s:" + k) if isinstance(k, str) else ("n:%d" % k)
        out.append("M\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%d" % (
            path, key, m["model"], int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0), int(u.get("cache_read_input_tokens") or 0),
            int(u.get("cache_creation_input_tokens") or 0), int(cc.get("ephemeral_1h_input_tokens") or 0), int(cc.get("ephemeral_5m_input_tokens") or 0),
            m["ts"] or "-", m["sid"] if m["sid"] is not None else "-", int(bool(m.get("final")))))
    return out

def dump_all(fn, files):
    w = []
    lines = []
    for f in files:
        lines += canonical(f, fn(f, w))
    return "\n".join(sorted(lines)) + "\n"

# ---- process pool: workers fork after import, so lab_status is already loaded in each
_FN = None
def _work(path):
    return path, _FN(path, [])

def parse_many(files, workers, fn):
    global _FN
    _FN = fn
    files = sorted(files, key=lambda f: -os.path.getsize(f))
    if workers <= 1:
        return dict(_work(f) for f in files)
    ctx = mp.get_context("fork")
    with ctx.Pool(workers) as pool:
        return dict(pool.imap_unordered(_work, files, chunksize=1))

def main():
    files = [l for l in open(sys.argv[2]).read().split("\n") if l]
    mode = sys.argv[3]
    if mode == "check":
        ref = None
        for name, fn in VARIANTS.items():
            d = dump_all(fn, files)
            ref = ref or d
            print("%-9s lines %d sha-equal-to-orig %s" % (name, d.count("\n"), d == ref), flush=True)
        for w in (4,):
            res = parse_many(files, w, VARIANTS["buf_find"])
            d = "\n".join(sorted(sum((canonical(f, res[f]) for f in files), []))) + "\n"
            print("buf_find x%d workers equal-to-orig %s" % (w, d == ref))
        if "--rust-dump" in sys.argv:
            rd = open(sys.argv[sys.argv.index("--rust-dump") + 1]).read()
            print("rust dump equal-to-orig %s (%d lines vs %d)" % (rd == ref, rd.count("\n"), ref.count("\n")))
            if rd != ref:
                a, b = ref.split("\n"), rd.split("\n")
                import difflib
                for i, l in enumerate(difflib.unified_diff(a, b, lineterm="", n=0)):
                    if i > 12: break
                    print(l[:200])
        open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[2])), "canonical_orig.txt"), "w").write(ref)
    elif mode == "time":
        fn = VARIANTS[sys.argv[4]]; w = int(sys.argv[5]) if len(sys.argv) > 5 else 1
        ts = []
        for _ in range(5):
            t = time.perf_counter(); parse_many(files, w, fn); ts.append(time.perf_counter() - t)
        print(json.dumps(dict(variant=sys.argv[4], workers=w, walls=[round(x, 4) for x in ts], load1=round(os.getloadavg()[0], 2))))
if __name__ == "__main__":
    main()
