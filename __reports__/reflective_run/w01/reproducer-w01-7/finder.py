import csv,re,math
from collections import Counter
P=list(csv.DictReader(open('../explorer-w01-d/prompts.csv')))
A=list(csv.DictReader(open('../explorer-w01-d/asks.csv')))
gen=sorted([p for p in P if p['channel'] in('A','B')],key=lambda p:p['ts_utc'])
def toks(s,minlen):
    return re.findall(r'[a-z]{%d,}'%minlen,s.lower())
def rank(askidx,settle,minlen,mode):
    a=A[askidx]; at=a['wrap_up_ts_utc']
    prior=[q for q in gen if q['ts_utc']<at]
    q_=toks(a['ask']+' '+a['options'],minlen)
    docs=[toks(q['human_text'],minlen) for q in prior]
    df=Counter(w for d in docs for w in set(d))
    N=len(docs)
    def vec(t): 
        c=Counter(t); return {w:(1+math.log(n))*(math.log((N+1)/(df.get(w,0)+1))+1 if mode=='tfidf' else 1) for w,n in c.items()}
    qv=vec(q_); sc=[]
    for q,d in zip(prior,docs):
        dv=vec(d); dot=sum(qv[w]*dv[w] for w in qv if w in dv)
        nn=math.sqrt(sum(v*v for v in qv.values()))*math.sqrt(sum(v*v for v in dv.values())) or 1
        sc.append((dot/nn,q['uuid'][:8]))
    sc.sort(reverse=True)
    r=next(i+1 for i,(s,u) in enumerate(sc) if u==settle)
    return r,N,round(dict((u,s) for s,u in sc)[settle],3),sc[0]
for ask,settle in [(13,'69ca9e2b'),(17,'3b472151'),(10,'33a2540f'),(11,'5b683d15'),(16,'85f8ec42')]:
    for minlen in (3,4):
        for mode in ('cos','tfidf'):
            print(ask,settle,'minlen',minlen,mode,rank(ask,settle,minlen,mode))
