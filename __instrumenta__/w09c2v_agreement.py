# Computes agreement (count, Cohen's kappa) between my hand codes of the 20 sampled hand-back wakes, my rule R2 coded automatically (wakes.jsonl), and the author's H1 code (turn_table.tsv of w09d_turns.py); also all waves 5-8 hand-back wakes auto-vs-author; usage: python3 -I w09c2v_agreement.py <wakes.jsonl> <sample_ids.txt> <turn_table.tsv> <hand codes: S-numbers coded 1, comma separated>
import json,sys,datetime,collections
W=[json.loads(l) for l in open(sys.argv[1])]
ids=[l.split() for l in open(sys.argv[2])]
rows=[l.rstrip('\n').split('\t') for l in open(sys.argv[3])][1:]
hand1=set(int(x) for x in sys.argv[4].split(','))
def jst(ts):
    t=datetime.datetime.strptime(ts[:19],'%Y-%m-%dT%H:%M:%S')+datetime.timedelta(hours=9); return '%d %s'%(t.day,t.strftime('%H:%M:%S'))
A={}
for r in rows:
    A[(r[0],r[2],r[5])]=r
def kappa(a,b):
    n=len(a); po=sum(x==y for x,y in zip(a,b))/n
    pa=sum(a)/n; pb=sum(b)/n; pe=pa*pb+(1-pa)*(1-pb)
    return po,(po-pe)/(1-pe) if pe<1 else float('nan')
def author_code(w):
    r=A.get((w['lab'],jst(w['ts']),w['sender']))
    if r is None:
        # w7 senders are agent types in transcript; author table 'from' may be name; match by time only
        c=[x for k,x in A.items() if k[0]==w['lab'] and k[1]==jst(w['ts'])]
        r=c[0] if c else None
    return None if r is None else int('H1' in r[10].split(','))
byid={(w['lab'],w['idx']):w for w in W}
hand=[];auto=[];auth=[];miss=0
for k,(lab,idx) in enumerate(ids,1):
    w=byid[(lab,int(idx))]; a=author_code(w)
    if a is None: miss+=1; print('no author row for S%02d'%k,lab,w['ts']); continue
    hand.append(int(k in hand1)); auto.append(int(w['open'])); auth.append(a)
    print('S%02d %s %s hand=%d auto=%d author=%d'%(k,lab,w['sender'],hand[-1],auto[-1],auth[-1]))
print('n',len(hand),'miss',miss)
for nm,x,y in (('hand~author',hand,auth),('hand~myauto',hand,auto),('myauto~author (sample)',auto,auth)):
    po,kp=kappa(x,y); print(nm,'agree %d/%d kappa %.2f'%(sum(p==q for p,q in zip(x,y)),len(x),kp))
a=[];b=[];bad=[]
for w in W:
    if w['lab'] in('w5','w6','w7','w8'):
        c=author_code(w)
        if c is None: continue
        a.append(int(w['open']));b.append(c)
        if int(w['open'])!=c: bad.append((w['lab'],w['sender'],w['ts'],int(w['open']),c))
po,kp=kappa(a,b); print('all w5-8 hand-backs myauto vs author H1: n=%d agree %d kappa %.2f'%(len(a),sum(p==q for p,q in zip(a,b)),kp))
for x in bad: print('  disagree',x)
