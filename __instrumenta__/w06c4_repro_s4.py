# w06-c4 verifier: counts lines of the lab scripts of two plugin exports (argv: OLD_ROOT NEW_ROOT), whole file and without the body of every function whose name contains 'selftest' (ast, def line through end_lineno), blank and comment lines counted/not counted; output: a table on stdout
import ast, sys
def count(path):
    src = open(path).read(); lines = src.splitlines()
    skip = set()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and "selftest" in n.name:
            skip.update(range(n.lineno - len(n.decorator_list), n.end_lineno + 1))
    whole = len(lines)
    prod = [l for i, l in enumerate(lines, 1) if i not in skip]
    code = [l for l in prod if l.strip() and not l.strip().startswith("#")]
    return whole, len(prod), len(code)
old, new = sys.argv[1:3]
def tot(root, names):
    r = [0, 0, 0]
    for n in names:
        try: c = count(f"{root}/scripts/{n}.py")
        except FileNotFoundError: continue
        print(f"  {root.split('/')[-1]:4} {n:12} whole {c[0]:5} prod {c[1]:5} prod-nonblank-noncomment {c[2]:5}")
        r = [a + b for a, b in zip(r, c)]
    return r
o = tot(old, ["budget", "handback"])
n = tot(new, ["budget", "handback", "hook_server", "outage"])
print("main", o, "build (4 files)", n, "delta", [b - a for a, b in zip(o, n)])
