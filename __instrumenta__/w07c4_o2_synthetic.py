"""Prices a synthetic transcript holding a fast-mode message and web-search messages under two copies of lab_status.py, from the two script paths and a scratch folder to the priced rows on stdout (o2 of protocol P4); exit 1 when B does not price them as message_usd intends or A does.

usage: w07c4_o2_synthetic.py A.py B.py SCRATCH
The session has no cost-state, so the list-price path is used. Messages (model claude-opus-5-5, USD 20 per million output tokens, 4 per million input):
  m1  plain: 1,000,000 output tokens                                        -> 20.00
  m2  fast:  1,000,000 output tokens, usage.speed "fast"                    -> 40.00 (factor 2)
  m3  three web searches, 0 tokens                                          ->  0.03 (USD 0.01 each)
  m4  streamed over three records of one message id: output 10, 500000, 1000000; `speed` "fast" only on the middle record;
      web_search_requests 0, 1, 2                                           -> 40.00 + 0.02 (the maximum of each field is kept)
  m5  `speed` "standard", server_tool_use with web_search_requests 0       -> 4.00 for 1,000,000 input tokens
Expected total 104.05 for B. Also: B's cache round trip (second run from the cache) prices the same; a cache file of version 1 is ignored by B.
"""
import importlib.util
import json
import os
import re
import shutil
import sys

OPUS = "claude-opus-5-5"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rec(mid, usage, sid="s1", ts="2026-10-22T10:00:00Z", stop="end_turn"):
    return json.dumps({"type": "assistant", "sessionId": sid, "timestamp": ts, "cwd": ROOT, "requestId": "r" + mid,
                       "message": {"id": mid, "model": OPUS, "stop_reason": stop, "usage": usage}}) + "\n"


def main(a_path, b_path, scratch):
    global ROOT
    shutil.rmtree(scratch, ignore_errors=True)
    ROOT = os.path.realpath(os.path.join(scratch, "proj"))
    os.makedirs(ROOT)
    cfg = os.path.join(scratch, "cfg")
    folder = os.path.join(cfg, "projects", re.sub(r"[^A-Za-z0-9]", "-", ROOT))
    os.makedirs(folder)
    u = lambda **k: dict({"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}, **k)
    lines = [rec("m1", u(output_tokens=1000000)),
             rec("m2", u(output_tokens=1000000, speed="fast")),
             rec("m3", u(server_tool_use={"web_search_requests": 3})),
             rec("m4", u(output_tokens=10, server_tool_use={"web_search_requests": 0}), stop=None),
             rec("m4", u(output_tokens=500000, speed="fast", server_tool_use={"web_search_requests": 1}), stop=None),
             rec("m4", u(output_tokens=1000000, speed="standard", server_tool_use={"web_search_requests": 2})),
             rec("m5", u(input_tokens=1000000, speed="standard", server_tool_use={"web_search_requests": 0}))]
    with open(os.path.join(folder, "s1.jsonl"), "w") as fh:
        fh.write(json.dumps({"type": "user", "sessionId": "s1", "cwd": ROOT, "timestamp": "2026-10-22T09:59:00Z"}) + "\n" + "".join(lines))
    expected = 20.0 + 40.0 + 0.03 + (40.0 + 0.02) + 4.0
    A, B = load(a_path, "A"), load(b_path, "B")
    results = {}
    for name, mod in (("A", A), ("B", B)):
        mod.config_dir = lambda: cfg
        os.environ["LAB_STATUS_CACHE"] = "off"
        text = "\n".join(mod.report_spend(ROOT))
        row = [l for l in text.splitlines() if "opus-5-5" in l]
        results[name] = float(row[0].split()[-2]) if row else None
        print("%s: %s" % (name, row))
    # B through its cache, twice, and over a version-1 cache
    cache = os.path.join(scratch, "cache.json")
    os.environ["LAB_STATUS_CACHE"] = cache
    first = [l for l in B.report_spend(ROOT) if "opus-5-5" in l]
    second = [l for l in B.report_spend(ROOT) if "opus-5-5" in l]
    stored = json.load(open(cache))
    old = dict(stored, v=1)
    json.dump(old, open(cache, "w"))
    loaded_old = B.Cache(cache)
    print("B via cache, first run %s; second run (from the cache) %s; same: %s; cache version %s" % (first, second, first == second, stored["v"]))
    print("B ignores a cache file of version 1: %s" % (loaded_old.files == {}))
    ok = results["B"] is not None and abs(results["B"] - expected) < 0.006 and first == second and loaded_old.files == {}
    # A without them: the same transcript priced with the fields dropped by merge_usage
    expected_a = 20.0 + 20.0 + 0.0 + 20.0 + 4.0
    ok = ok and results["A"] is not None and abs(results["A"] - expected_a) < 0.006
    print("expected B %.2f, got %s; expected A %.2f, got %s; message_usd direct: fast %.2f, 3 searches %.2f" % (
        expected, results["B"], expected_a, results["A"],
        B.message_usd(OPUS, u(output_tokens=1000000, speed="fast")), B.message_usd(OPUS, u(server_tool_use={"web_search_requests": 3}))))
    print("o2:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
