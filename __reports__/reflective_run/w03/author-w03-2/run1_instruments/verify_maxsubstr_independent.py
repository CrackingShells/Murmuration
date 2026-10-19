# Independent check of w01-c1: for each n<=N, brute-force max distinct factors over all binary words, compare with sum min(2^k,n-k+1), and compare the maximiser set with the criterion (all 2^k0 words of length k0 occur, length k0+1 windows distinct). Input: N argv; output: PASS/FAIL lines and maximiser counts.
import sys
N=int(sys.argv[1])
for n in range(1,N+1):
    k0=max(k for k in range(0,n+2) if 2**k+k-1<=n)
    S=sum(min(2**k,n-k+1) for k in range(1,n+1))
    best=0;mx=set();crit=set()
    for x in range(2**n):
        w=format(x,'0%db'%n)
        d=set(w[i:j] for i in range(n) for j in range(i+1,n+1))
        D=len(d)
        if D>best: best=D;mx=set()
        if D==best: mx.add(w)
        if k0==0: a=True
        else: a=len({w[i:i+k0] for i in range(n-k0+1)})==2**k0
        b=len({w[i:i+k0+1] for i in range(n-k0)})==n-k0
        if a and b: crit.add(w)
    print(n,best,S,best==S,mx==crit,len(mx))
