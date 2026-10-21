"""Runs lab_status.py --selftest on the original and on hand-made mutants of its Cache, from a script path and a scratch dir to one PASS/FAIL line per mutant on stdout.

usage: w05c5_repro_mutants.py LAB_STATUS.py SCRATCH
Own mutants (not the author's list); a mutant that still passes is a hole in the selftest.
"""
import os, subprocess, sys
src, scr = sys.argv[1:3]
os.makedirs(scr, exist_ok=True)
code = open(src).read()
M = {
 "size-only":      ("hit[:2] == stamp", "hit[0] == stamp[0]"),
 "mtime-only":     ("hit[:2] == stamp", "hit[1] == stamp[1]"),
 "ignore-version": ('data.get("v") == CACHE_VERSION and ', ''),
 "non-atomic":     ("os.replace(tmp, self.path)", "open(self.path, 'w').write(open(tmp).read()); os.unlink(tmp)"),
 "cache-warned":   ("if len(warnings) == before:", "if True:"),
 "no-R_OK":        (" and os.access(path, os.R_OK)", ""),
 "keep-unseen":    ('"files": self.seen}', '"files": self.files}'),
 "ids-as-text":    ("[list(msgs.items()), cost_state, setting]", "[[[str(k), v] for k, v in msgs.items()], cost_state, setting]"),
 "stat-after-parse": ("        stamp = [st.st_size, st.st_mtime_ns]\n        hit =", "        hit ="),
 "no-gitignore":   ('fh.write("*\\n")', 'fh.write("")'),
 "always-write":   ("if not (self.dirty or len(self.seen) != len(self.files)):\n            return", "pass"),
 "no-makedirs":    ("os.makedirs(os.path.dirname(self.path), exist_ok=True)", "pass"),
 "tmp-no-pid":     ('"%s.%d.tmp" % (self.path, os.getpid())', '"%s.tmp" % self.path'),
 "ignore-all":     ("hit[:2] == stamp", "True"),
}
def selftest(path):
    p = subprocess.run([sys.executable, path, "--selftest"], capture_output=True, text=True, cwd=scr)
    return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1:] 
print("original:", selftest(src))
for name, (a, b) in M.items():
    if code.count(a) != 1:
        print("%-16s PATTERN COUNT %d" % (name, code.count(a))); continue
    m = code.replace(a, b)
    if name == "stat-after-parse":   # stamp taken after the parse instead of before
        m = m.replace("        msgs, cost_state, setting = parse_transcript(path, warnings)\n        if len(warnings) == before:",
                      "        msgs, cost_state, setting = parse_transcript(path, warnings)\n        st = os.stat(path); stamp = [st.st_size, st.st_mtime_ns]\n        if len(warnings) == before:")
        m = m.replace("        hit = self.files.get(path)", "        st = os.stat(path); stamp = [st.st_size, st.st_mtime_ns]\n        hit = self.files.get(path)", 1)
    mp = os.path.join(scr, "mutant_%s.py" % name)
    open(mp, "w").write(m)
    rc, tail = selftest(mp)
    print("%-16s %s  %s" % (name, "KILLED (selftest fails)" if rc else "SURVIVES (selftest passes)", tail))
