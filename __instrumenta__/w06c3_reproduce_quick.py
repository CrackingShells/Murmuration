# w06-c3 reproduction: runs the author's w06c3_run_all.py (quick or full subset) unchanged except that its output root S is moved to the reproducer's directory; inputs: S path, optional --quick; outputs: run directories under S/runs[_quick]
import os, sys
S = sys.argv[1]; rest = [a for a in sys.argv[2:]]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "w06c3_run_all.py")).read()
src = src.replace('S = "/private/tmp/murmuration-w06/author-w06-3"', 'S = %r' % S)
assert S in src
os.makedirs(S + "/work", exist_ok=True)
sys.argv = [os.path.abspath(__file__)] + rest
exec(compile(src, "run_all_moved", "exec"), {"__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "w06c3_run_all.py"), "__name__": "__main__"})
