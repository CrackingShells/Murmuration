# Computes, from the six PI transcripts (label=path lines in argv[1]) and my wakes.jsonl (argv[2]), (b) PI path-rows of reads in waves 5-8 (Read tool, view and query commands by my parser) and their repeats by basename, by normalised path and by identical call text, and (e) raw-open (my rule R2) with and without the platform banner over waves 1-8 hand-backs with Fisher exact p; also lists my hand-back wakes of waves 5-8 by (label, ts, sender) to <dir>/wakes58.txt for a diff against another cut; usage: python3 -I w09c2v_rereads_banner.py <files.txt> <wakes.jsonl>
import json,sys,os,re,collections
from math import comb
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from w09c2v_extract import opened_paths
files=[l.strip().split('=',1) for l in open(sys.argv[1]) if '=' in l]
def norm(p):
    p=re.sub(r'^/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/[^/]+/','',p)
    p=re.sub(r'^/Users/hacker/Documents/src/CrackingShells/Murmuration/(\.claude/worktrees/[^/]+/)?','',p)
    return p
rows=[]
for lab,p in files:
    if lab not in('w5','w6','w7','w8'): continue
    seen_b=set();seen_n=set();seen_call={}
    for l in open(p):
        if '"tool_use"' not in l: continue
        d=json.loads(l)
        if d.get('type')!='assistant': continue
        for b in d['message'].get('content',[]):
            if b.get('type')!='tool_use': continue
            ops=opened_paths({'name':b['name'],'input':b['input']})
            ops=[(q,k) for q,k in ops if ('/' in q or '.' in q) and len(q)>4][:3]
            callkey=re.sub(r'\s+',' ',(b['input'].get('command') or b['input'].get('file_path') or '')).strip()[:int(os.environ.get('KEYLEN','100000'))]+json.dumps([b['input'].get('offset'),b['input'].get('limit')])
            for q,k in ops:
                bn=os.path.basename(q.rstrip('/')); n=norm(q)
                rows.append((lab,bn in seen_b,n in seen_n,(bn in seen_b) and (bn,callkey) in seen_call))
                seen_b.add(bn);seen_n.add(n);seen_call[(bn,callkey)]=1
print('(b) my read path-rows, waves 5-8: %d; repeat by basename %d (%.0f%%); by normalised path %d (%.0f%%); of the basename repeats, call text identical to an earlier row of that basename %d'%(len(rows),sum(r[1] for r in rows),100*sum(r[1] for r in rows)/len(rows),sum(r[2] for r in rows),100*sum(r[2] for r in rows)/len(rows),sum(r[3] for r in rows)))
for lab in('w5','w6','w7','w8'):
    rr=[r for r in rows if r[0]==lab]; print('   ',lab,len(rr),sum(r[1] for r in rr),sum(r[2] for r in rr))
W=[json.loads(l) for l in open(sys.argv[2])]
def fisher(a,n1,b,n2):
    N=n1+n2;K=a+b;tot=comb(N,K);p0=comb(n1,a)*comb(n2,b)/tot
    return sum(comb(n1,x)*comb(n2,K-x)/tot for x in range(max(0,K-n2),min(n1,K)+1) if comb(n1,x)*comb(n2,K-x)/tot<=p0*(1+1e-9))
B='[harness: subagent output matched'
bw=[w for w in W if B in w['body'][:1200]]; nb=[w for w in W if B not in w['body'][:1200]]
anywhere=[w for w in W if B in w['body'] and B not in w['body'][:1200]]
print('(e) my hand-backs waves 1-8:',len(W),'banner in first 1200 chars',len(bw),'banner later in body',len(anywhere))
for key in ('open','open_strict'):
    a=sum(w[key] for w in bw);b=sum(w[key] for w in nb)
    print('   ',key,'banner %d/%d (%.0f%%) none %d/%d (%.0f%%) Fisher p=%.2f'%(a,len(bw),100*a/len(bw),b,len(nb),100*b/len(nb),fisher(a,len(bw),b,len(nb))))
bys=collections.defaultdict(lambda:[0,0,0,0])
for w in W:
    k=bys[w['role']]; i=0 if B in w['body'][:1200] else 2; k[i]+=1; k[i+1]+=w['open']
for r,k in sorted(bys.items()): print('    role',r,'banner %d/%d none %d/%d'%(k[1],k[0],k[3],k[2]))
with open(os.path.join(os.path.dirname(sys.argv[2]),'wakes58.txt'),'w') as f:
    for w in W:
        if w['lab'] in('w5','w6','w7','w8'): f.write('%s\t%s\t%s\n'%(w['lab'],w['ts'],w['sender']))
