# Computes, for each n<=N (default 14) over all binary words of length n, M(n)=max D(w), compares with sum_k min(2^k,n-k+1), and checks the maximiser set equals {w: all 2^k0 k0-words present and the n-k0 windows of length k0+1 distinct}; prints one line per n and exits nonzero on mismatch.
import sys, itertools
N = int(sys.argv[1]) if len(sys.argv) > 1 else 14
bad = 0
for n in range(1, N+1):
    k0 = max(k for k in range(0, n+1) if 2**k <= n-k+1)
    formula = sum(min(2**k, n-k+1) for k in range(1, n+1))
    best, maxs, cond = -1, set(), set()
    for t in itertools.product('01', repeat=n):
        w = ''.join(t)
        D = sum(len({w[i:i+k] for i in range(n-k+1)}) for k in range(1, n+1))
        if D > best: best, maxs = D, set()
        if D == best: maxs.add(w)
        a = len({w[i:i+k0] for i in range(n-k0+1)}) == 2**k0
        b = len({w[i:i+k0+1] for i in range(n-k0)}) == n-k0
        if a and b: cond.add(w)
    ok = best == formula and maxs == cond and len(maxs) > 0
    bad += not ok
    print(n, k0, best, formula, len(maxs), 'OK' if ok else 'FAIL')
sys.exit(1 if bad else 0)
