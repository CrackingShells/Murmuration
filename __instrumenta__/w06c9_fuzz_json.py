# w06-c9 verifier: compares handback.loads / handback.dumps of a plugin tree with json.loads / json.dumps on fixed edge cases and random values; inputs: argv[1] = plugin root, optional argv[2] = mask letter (A none-module, B empty-module, C no-encoder, D no-scanner); output: counts and the first mismatches
import json, math, random, sys
root = sys.argv[1]
mask = sys.argv[2] if len(sys.argv) > 2 else ""
if mask:
    import types, _json as r
    if mask == "A":
        sys.modules["_json"] = None
    else:
        m = types.ModuleType("_json")
        if mask == "C": m.make_scanner = r.make_scanner
        if mask == "D": m.encode_basestring_ascii = r.encode_basestring_ascii
        if mask == "E":
            m.encode_basestring_ascii = r.encode_basestring_ascii
            m.make_scanner = lambda ctx: 1 / 0
        sys.modules["_json"] = m
sys.path.insert(0, root + "/scripts")
import handback as H

def outcome(f, x):
    try:
        return ("ok", f(x))
    except RecursionError:
        return ("exc", "RecursionError")
    except Exception as e:
        return ("exc", "ValueError" if isinstance(e, ValueError) else type(e).__name__)

def same(a, b):
    if a[0] != b[0]: return False
    if a[0] == "exc": return a[1] == b[1]
    x, y = a[1], b[1]
    return repr(x) == repr(y)   # repr tells nan, -0.0, 1 versus 1.0, and key order

bad = []
n = 0
ws = ["", " ", "\n", "\t\r\n ", "\f", " ", "﻿", "\x0b"]
atoms = ["null", "true", "false", "NaN", "Infinity", "-Infinity", "-0", "-0.0", "0", "01", "1.", ".5", "1e5", "1E+5", "1e400", "-1e400", "1e-400", "123456789012345678901234567890",
         "9" * 5000, '"a"', '"\\ud800"', '"\\ud83d\\ude00"', '"\\u00e9"', '"é"', '"\x01"', '"\\x"', '"a\nb"', '"\\/"', '"', "{", "}", "[", "]", "[]", "{}", '{"a":1,"a":2}', '{"a":1,}', "[1,]", "[1 2]",
         '{"a" 1}', "{1:2}", "tru", "nul", "+1", "--1", "0x10", "1_0", "[" * 2000 + "]" * 2000, "[" * 100000, '{"k":' * 600 + "1" + "}" * 600, "[NaN]", "[-NaN]", "\x00", "{} {}", "{}x", "x{}", ""]
for a in atoms:
    for pre in ws[:5] + ws[5:]:
        for post in ws:
            t = pre + a + post
            for f_h, f_j in ((H.loads, json.loads),):
                for form in (t, t.encode("utf-8", "surrogatepass")):
                    n += 1
                    ra = outcome(f_h, form)
                    rb = outcome(f_j, form.decode("utf-8", "surrogatepass") if isinstance(form, bytes) else form)   # the old arm read text
                    if not same(ra, rb): bad.append(("loads", t[:60], isinstance(form, bytes), ra, rb))
# encodings json.loads detects for bytes
for enc in ("utf-16", "utf-16-le", "utf-32", "utf-8-sig"):
    for t in ('{"a": 1}', '[1, "é"]'):
        n += 1
        b = t.encode(enc)
        ra, rb = outcome(H.loads, b), outcome(json.loads, b)   # json.loads(bytes) detects UTF-16/32/BOM; the old arm decoded stdin as UTF-8 text first
        if not same(ra, rb):
            rb = outcome(json.loads, b.decode("utf-8", "replace") if enc != "utf-8-sig" else b.decode("utf-8"))
        if not same(ra, rb): bad.append(("loads-bytes-%s" % enc, t, ra, rb))
for b in (b"\xff\xfe{", b"\xc3(", b'{"a": "\xff"}', b"\x80"):
    n += 1
    ra, rb = outcome(H.loads, b), outcome(lambda x: json.loads(x.decode("utf-8")), b)
    if not same(ra, rb): bad.append(("loads-badutf8", b, ra, rb))
rnd = random.Random(660)
def anything(d=0):
    k = rnd.choice(list("ntfixssuul") + (["d", "l"] if d < 4 else []))
    if k == "l": return [anything(d + 1) for _ in range(rnd.randint(0, 4))]
    if k == "d": return {rnd.choice(["a", "b", "ké", "中", "", "z", "😀", "A", "\x7f", "q\"q", "\\"]): anything(d + 1) for _ in range(rnd.randint(0, 4))}
    if k == "i": return rnd.choice([0, -1, 1, 2 ** 63, -2 ** 64, 10 ** 30, rnd.randint(-10 ** 9, 10 ** 9), True, False])
    if k == "x": return rnd.choice([0.0, -0.0, 1.0, 1e16, 1e-5, 1.5e300, 5e-324, 123456789.123456789, math.inf, -math.inf, math.nan, 1e22, 100.0, 0.1])
    if k == "s": return "".join(rnd.choice('ab "\\\n\t/\r\b\f\x00\x1f\x7f') for _ in range(rnd.randint(0, 8)))
    if k == "u": return "".join(chr(rnd.choice([0xe9, 0x4e2d, 0x1f600, 0xd800, 0xdfff, 0x2028, 0x2029, 0xa0, 0xfeff, 0xffff])) for _ in range(rnd.randint(1, 3)))
    return {"n": None, "t": True, "f": False}[k]
for _ in range(20000):
    o = anything()
    for sk in (False, True):
        n += 1
        ra, rb = outcome(lambda x: H.dumps(x, sort_keys=sk), o), outcome(lambda x: json.dumps(x, sort_keys=sk), o)
        if not same(ra, rb): bad.append(("dumps", repr(o)[:80], sk, ra, rb))
    s = json.dumps(o)
    n += 1
    ra, rb = outcome(H.loads, s), outcome(json.loads, s)
    if not same(ra, rb): bad.append(("loads-rt", s[:80], ra, rb))
# types dumps does not claim: report what happens (not counted as a mismatch)
extra = {}
for name, o in (("tuple", (1, 2)), ("int-key", {1: 2}), ("bytes", b"x"), ("set", {1}), ("float-subclass", type("F", (float,), {})(1.5)), ("str-subclass", type("S", (str,), {})("x")), ("int-subclass", type("I", (int,), {"__repr__": lambda s: "I"})(3)),
                ("dict-order-mixed-sort", {"b": 1, 1: 2})):
    extra[name] = (outcome(H.dumps, o), outcome(json.dumps, o))
print("mask=%r cases=%d mismatches=%d" % (mask, n, len(bad)))
import collections
for b in bad[:3]: print("  ", b)
print("  categories:", collections.Counter((b[0], b[1].startswith("\ufeff") if isinstance(b[1], str) else "other") for b in bad))
for k, v in extra.items(): print("  extra", k, "build:", v[0], "json:", v[1], "SAME" if same(*v) else "DIFFERENT")
