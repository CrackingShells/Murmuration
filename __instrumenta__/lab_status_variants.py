"""Builds three variants of scripts/lab_status.py in a scratch folder (v1 one git call, v2 = v1 + bytes-level line filter, v3 = v2 + per-file parse cache) from the plugin's own file; writes <out>/v{1,2,3}/lab_status.py.

usage: lab_status_variants.py <repo root> <out dir>. Each variant is a text patch of the original (asserted to apply exactly once); the original file is never touched. v3's cache is a JSON file named by $LAB_STATUS_CACHE (default <out>/cache.json), keyed by path with (size, mtime_ns).
"""
import os, sys
root, out = sys.argv[1], sys.argv[2]
src = open(os.path.join(root, "scripts", "lab_status.py")).read()
def sub(s, a, b):
    assert s.count(a) == 1, a[:50]
    return s.replace(a, b)
v1 = sub(src, 'def git_worktrees(root):\n    """Paths of the git worktrees of root\'s repository, the main checkout first (needs git; else empty)."""\n    try:',
         '_GW = {}\n\n\ndef git_worktrees(root):\n    """Paths of the git worktrees of root\'s repository, the main checkout first (needs git; else empty)."""\n    if root in _GW:\n        return _GW[root]\n    _GW[root] = _git_worktrees(root)\n    return _GW[root]\n\n\ndef _git_worktrees(root):\n    try:')
v2 = sub(v1, 'with open(path, encoding="utf-8", errors="replace") as fh:\n            for line in fh:\n                if \'"assistant"\' not in line and \'"cost-state"\' not in line and \'"agent-setting"\' not in line:',
         'with open(path, "rb") as fh:\n            for line in fh:\n                if b\'"assistant"\' not in line and b\'"cost-state"\' not in line and b\'"agent-setting"\' not in line:')
v2 = sub(v2, "                try:\n                    rec = json.loads(line)\n                except ValueError:\n                    continue\n                if not isinstance(rec, dict):",
         "                try:\n                    rec = json.loads(line.decode(\"utf-8\", \"replace\"))\n                except ValueError:\n                    continue\n                if not isinstance(rec, dict):")
v3 = sub(v2, "def read_transcript(path, warnings):", "def read_transcript_uncached(path, warnings):")
v3 = sub(v3, "def agent_label(path):", '''_CACHE = None
_CACHE_FILE = os.environ.get("LAB_STATUS_CACHE") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache.json")


def read_transcript(path, warnings):
    global _CACHE
    if _CACHE is None:
        try:
            with open(_CACHE_FILE) as fh:
                _CACHE = json.load(fh)
        except (OSError, ValueError):
            _CACHE = {}
        import atexit
        atexit.register(_save_cache)
    try:
        st = os.stat(path)
        key = [st.st_size, st.st_mtime_ns]
    except OSError:
        return read_transcript_uncached(path, warnings)
    hit = _CACHE.get(path)
    if hit and hit[0] == key:
        return hit[1], hit[2], hit[3]
    res = read_transcript_uncached(path, warnings)
    _CACHE[path] = [key, res[0], res[1], res[2]]
    return res


def _save_cache():
    try:
        tmp = _CACHE_FILE + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(_CACHE, fh)
        os.replace(tmp, _CACHE_FILE)
    except OSError:
        pass


def agent_label(path):''')
for name, text in (("v1", v1), ("v2", v2), ("v3", v3)):
    os.makedirs(os.path.join(out, name), exist_ok=True)
    open(os.path.join(out, name, "lab_status.py"), "w").write(text)
print("wrote", out)
