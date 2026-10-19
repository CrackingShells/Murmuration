# Computes M(n), #maximisers, formula sum_k min(2^k,n-k+1), and the k0-characterisation test, for all binary words of length n=1..N (numpy, exhaustive); prints a table (stdout).
import sys, numpy as np
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
print("n M(n) #max formula M==formula k0 #charset charset==maxset")
for n in range(1, N+1):
    W = np.arange(1 << n, dtype=np.int64)
    D = np.zeros(1 << n, dtype=np.int64)
    fk = {}
    for k in range(1, n+1):
        cols = [((W >> s) & ((1 << k) - 1)) for s in range(n-k+1)]
        A = np.sort(np.stack(cols, 1), axis=1)
        f = 1 + (A[:, 1:] != A[:, :-1]).sum(1)
        fk[k] = f; D += f
    M = D.max(); mx = D == M
    form = sum(min(2**k, n-k+1) for k in range(1, n+1))
    k0 = max(k for k in range(0, n+1) if 2**k <= n-k+1)
    ok = np.ones(1 << n, bool)
    if k0 >= 1: ok &= fk[k0] == 2**k0
    if k0+1 <= n: ok &= fk[k0+1] == n-k0
    print(n, M, int(mx.sum()), form, M == form, k0, int(ok.sum()), bool((ok == mx).all()), flush=True)
