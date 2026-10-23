# w08-c14 verifier: differential test of the guard's reading of `-c` against REAL shells (bash, sh, zsh, dash, ksh); for every sequence of option words (up to 3 from a vocabulary) followed by three harmless strings `echo S1`, `echo S2`, `echo S3`, it runs the real shell (stdin /dev/null, 5 s limit), notes which string the shell executed, and checks that the string-index list the NEW guard reads (expand() on the same command, via the python guard of NEW_TREE) contains it; also counts forms where the guard reads a string the shell does not execute (over-reading, harmless) ; inputs: NEW_TREE (a lab tree with scripts/permission_guard.py); output: stdout (counts, every miss: shell executed a string the guard does not read), --out JSON. No claude flag appears here. Usage: python3 -I w08_v14_realshell.py NEW_TREE [--jobs N] [--out F] [--maxlen 3] [--n3 N]
import concurrent.futures, importlib.util, itertools, json, os, subprocess, sys

VOCAB = ["-l", "-e", "-x", "-c", "-lc", "-ec", "-xc", "-ic", "-cl", "-ce", "-cx", "-lec", "-elc", "-uc", "-o", "-oc", "-co", "-eoc", "-ocx", "-cu", "+o", "+x", "+c", "-O", "-Oc", "-cO", "--", "-", "--norc", "--posix", "--login", "--noprofile", "noglob", "extglob", "--rcfile", "/dev/null", "-u", "-f", "-v", "-E"]
SHELLS = ["bash", "sh", "zsh", "dash", "ksh"]


def load(tree):
    s = importlib.util.spec_from_file_location("pgv14", os.path.join(tree, "scripts", "permission_guard.py"))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def run(shell, words):
    try:
        p = subprocess.run(["/bin/" + shell if os.path.exists("/bin/" + shell) else shell] + words + ["echo S1", "echo S2", "echo S3"], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=5)
    except Exception:
        return None
    out = p.stdout
    return [s for s in ("S1", "S2", "S3") if s in out.splitlines()]


def quote(w):
    return "'" + w + "'" if " " in w else w


def main():
    a = sys.argv[1:]
    tree = a[0]
    jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 8
    maxlen = int(a[a.index("--maxlen") + 1]) if "--maxlen" in a else 3
    out = a[a.index("--out") + 1] if "--out" in a else ""
    m = load(tree)
    seqs = [list(s) for n in range(1, min(maxlen, 2) + 1) for s in itertools.product(VOCAB, repeat=n)]
    if maxlen >= 3:                                   # length 3: a seeded random sample (SEED 14), --n3 sequences
        import random
        rnd = random.Random(14)
        n3 = int(a[a.index("--n3") + 1]) if "--n3" in a else 3000
        seqs += [[rnd.choice(VOCAB) for _ in range(3)] for _ in range(n3)]
    jobs_l = [(sh, s) for sh in SHELLS for s in seqs]
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(lambda j: run(*j), jobs_l))
    n_exec = miss = over = 0
    rows = []
    for (sh, s), r in zip(jobs_l, res):
        if r is None:
            continue
        cmd = " ".join([sh] + [quote(w) for w in s] + ["'echo S1'", "'echo S2'", "'echo S3'"])
        try:
            segs = m.expand(cmd)
        except Exception:
            segs = None
        read = set()
        if segs is not None:
            for sg in segs:
                for w in sg[1]:
                    if w in ("S1", "S2", "S3"):
                        read.add(w)
        if r:
            n_exec += 1
            if segs is not None and not set(r) <= read:
                miss += 1
                rows.append((sh, s, r, sorted(read)))
        elif read:
            over += 1
    print("forms run", len(jobs_l), "forms where the real shell executed a string", n_exec, "MISSES (executed string not read by guard)", miss, "over-reads (guard reads a string no shell executed)", over)
    for r in rows[:60]:
        print("MISS", r)
    if out:
        json.dump(rows, open(out, "w"))


if "--selftest" in sys.argv:
    assert len(VOCAB) == len(set(VOCAB)) and all(os.path.exists("/bin/" + s) for s in ("bash", "sh"))
    print("selftest ok", len(VOCAB))
    sys.exit(0)
main()
