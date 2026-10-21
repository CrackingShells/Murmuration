# Prints bounded windows of text around each match of a regex in the printable strings of a binary (default: `strings -a -n 8` output cached in a scratch dir); inputs: binary path, regex, before/after sizes, max matches; output: stdout, one escaped window per match with its offset.
import re, subprocess, sys, os, hashlib
def load(binary, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    cache = os.path.join(cache_dir, hashlib.sha1(binary.encode()).hexdigest()[:10] + ".strings")
    if not os.path.exists(cache):
        with open(cache, "wb") as fh:
            subprocess.run(["strings", "-a", "-n", "8", binary], stdout=fh, check=True)
    return open(cache, errors="replace").read()
if __name__ == "__main__":
    binary, pat = sys.argv[1], sys.argv[2]
    before = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    after = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    limit = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    s = load(binary, os.environ.get("W07F_CACHE", "/private/tmp/murmuration-w07/explorer-w07-f"))
    for i, m in enumerate(re.finditer(pat, s)):
        if i >= limit: break
        print("@%d: %s\n" % (m.start(), s[max(0, m.start() - before): m.end() + after].replace("\n", "\\n")))
