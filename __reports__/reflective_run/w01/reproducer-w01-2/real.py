import glob,sys,collections
sys.path.insert(0,'.')
import indep
D=sys.argv[1]
fs=sorted(glob.glob(D+"/*.jsonl"))
tn=tt=0; allfinal=0; empty=0
for f in fs:
    r=indep.reqs(f)
    if not r: empty+=1; continue
    n=sum(1 for u,s in r.values() if s is None)
    tn+=n; tt+=len(r); allfinal+= (n==0)
print(len(fs),"files",empty,"empty","requests",tt,"null-last",tn,"files all-final",allfinal)
