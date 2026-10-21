"""Runs lab_status.py --selftest on hand-made mutants of the E8 changes (the author's list, w05-c5), from a lab_status.py path to one KILLED/SURVIVES line per mutant on stdout.

usage: w05c5_author_mutants.py LAB_STATUS.py   (a mutant is a text substitution asserted to apply once; the original is never written)
Why a file: the eight mutants of the first claim were run from a heredoc and not kept; this list holds them (with the 'rename' one stated as it was: a rename to another name, not an os.rename in place of os.replace, which is atomic too), and the mutants of the fixes after reproducer-w05-5's questions (shared usage dict, no fallback on a malformed entry).
"""
import os, subprocess, sys, tempfile
src = os.path.abspath(sys.argv[1]); code = open(src).read()
M = {
 "compare time only":    ("hit[:2] == stamp and os.access", "hit[1:2] == stamp[1:2] and os.access"),
 "compare size only":    ("hit[:2] == stamp and os.access", "hit[:1] == stamp[:1] and os.access"),
 "ignore the version":   ('if data.get("v") == CACHE_VERSION and', "if True and"),
 "rename to another name (first claim's 'rename'; not an os.rename in place of os.replace)": ("os.replace(tmp, self.path)", "os.rename(tmp, self.path + 'x')"),
 "os.rename for os.replace (equivalent on POSIX; killed only because the selftest now spies on os.replace)": ("os.replace(tmp, self.path)", "os.rename(tmp, self.path)"),
 "ids as text":          ("list(msgs.items())", "[[str(k), m] for k, m in msgs.items()]"),
 "cache a parse that warned": ("if len(warnings) == before:", "if True:"),
 "drop the readability test": (" and os.access(path, os.R_OK)", ""),
 "drop the entries a warm run used": ("            self.seen[path] = hit\n", ""),
 "share the usage dict (S1)": ("own=(msg[\"sid\"] == sid), usage=dict(msg[\"usage\"]))", "own=(msg[\"sid\"] == sid))"),
 "no fallback on a malformed entry (S4)": ("        except Exception:   # an entry of the cache", "        except ZeroDivisionError:   # an entry of the cache"),
}
tmp = tempfile.mkdtemp()
for name, (a, b) in M.items():
    assert code.count(a) == 1, name
    p = os.path.join(tmp, "lab_status.py"); open(p, "w").write(code.replace(a, b))
    r = subprocess.run([sys.executable, p, "--selftest"], capture_output=True, text=True, cwd=tmp)
    print("%-8s %s" % ("KILLED" if r.returncode else "SURVIVES", name))
