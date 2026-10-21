# w06-c9: builds the five `_json` masks A-E of reproducer-w06-6 as plugin trees from a build tree (a copy with lines prepended to scripts/run_hook.py, so that `_json` is missing, empty, half there or broken in the hook process); inputs: SRC plugin root, OUT folder (new); output: OUT/mask{A..E}
"""A: sys.modules['_json'] = None (no module). B: an empty module. C: only make_scanner. D: only encode_basestring_ascii. E: encode_basestring_ascii and a make_scanner that raises TypeError.
The prefixes are those of /private/tmp/murmuration-w06/reproducer-w06-6/maskA..E (diffed against the run_hook.py of 056312d). Each tree is also given a fresh scripts/__pycache__-free copy."""
import os, shutil, sys

src, out = sys.argv[1:3]
PRE = {
    "A": "import sys\nsys.modules['_json'] = None\n",
    "B": "import sys, types\nsys.modules['_json'] = types.ModuleType('_json')\n",
    "C": "import sys, types\nimport _json as _r\nm = types.ModuleType('_json'); m.make_scanner = _r.make_scanner\nsys.modules['_json'] = m\n",
    "D": "import sys, types\nimport _json as _r\nm = types.ModuleType('_json'); m.encode_basestring_ascii = _r.encode_basestring_ascii\nsys.modules['_json'] = m\n",
    "E": ("import sys, types\nimport _json as _r\nm = types.ModuleType('_json'); m.encode_basestring_ascii = _r.encode_basestring_ascii\n"
          "def bad(ctx): raise TypeError('signature changed')\nm.make_scanner = bad\nsys.modules['_json'] = m\n"),
}
os.makedirs(out)
for k, pre in PRE.items():
    dst = os.path.join(out, "mask" + k)
    shutil.copytree(src, dst, symlinks=True, ignore=shutil.ignore_patterns("__pycache__"))
    path = os.path.join(dst, "scripts", "run_hook.py")
    body = open(path).read()   # read before the file is opened for writing
    open(path, "w").write(pre + body)
    print(dst)
