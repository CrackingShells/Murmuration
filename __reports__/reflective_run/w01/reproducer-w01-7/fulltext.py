import csv,json,re,math
from collections import Counter
base='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
P=list(csv.DictReader(open('../explorer-w01-d/prompts.csv')))
A=list(csv.DictReader(open('../explorer-w01-d/asks.csv')))
need={p['uuid']:p for p in P}
full={}
for sid in ['566fa912-7009-421a-9d79-11145e2b8db9','82e8a947-1a0c-441c-bc39-df8e2e5fa743']:
    for l in open(base+sid+'.jsonl'):
        try: r=json.loads(l)
        except: continue
        u=r.get('uuid')
        if u in need and r.get('type')=='user':
            c=r['message']['content']
            if isinstance(c,list): t='\n'.join(b.get('text','') for b in c if b.get('type')=='text')
            else: t=c
            t=re.sub(r'<system-reminder>.*?</system-reminder>','',t,flags=re.S).strip()
            full.setdefault(u,t)
print(len(full),'of',len(need))
gen=sorted([p for p in P if p['channel'] in('A','B')],key=lambda p:p['ts_utc'])
res=[p for p in gen if p['phase']!='G-C']
print('55-set chars full',sum(len(full.get(p['uuid'],p['human_text'])) for p in res), 'words',sum(len(full.get(p['uuid'],p['human_text'])).__class__(0) or len(full.get(p['uuid'],p['human_text']).split()) for p in res))
STOP=set('the and for that this with from have will your you are not but what which should them then when about into each does their they than more also only such after before first make made over under same most just like need needs there here'.split())
def terms(s): return {w for w in re.findall(r'[a-zA-Z]{4,}',s.lower()) if w not in STOP}
for ask,settle in [(13,'69ca9e2b'),(17,'3b472151'),(10,'33a2540f'),(11,'5b683d15'),(16,'85f8ec42')]:
    a=A[ask]; at=a['wrap_up_ts_utc']
    prior=[q for q in gen if q['ts_utc']<at]
    Aset=terms(a['ask']+' '+a['options'])
    sc=[]
    for q in prior:
        t=full.get(q['uuid'],q['human_text'])
        sc.append((len(Aset&terms(t))/max(1,len(Aset)),q['uuid'][:8],sorted(Aset&terms(t))))
    sc.sort(key=lambda x:-x[0])
    # rank with tie = best rank (competition ranking)
    sv=next(s for s,u,_ in sc if u==settle)
    better=sum(1 for s,u,_ in sc if s>sv)
    ties=sum(1 for s,u,_ in sc if s==sv)
    print(ask,settle,'overlap',round(sv,2),'strictly better',better,'ties',ties,'of',len(prior),'shared',next(w for s,u,w in sc if u==settle),'top',sc[0][:2],sc[0][2])
print('--- false-positive pressure on full text')
keep=[0,4,5,6,7,8,9,12,14,15,18]
for i in keep:
    a=A[i]; at=a['wrap_up_ts_utc']
    prior=[q for q in gen if q['ts_utc']<at]
    Aset=terms(a['ask']+' '+a['options'])
    sc=sorted(((len(Aset&terms(full.get(q['uuid'],q['human_text'])))/max(1,len(Aset)),q['uuid'][:8]) for q in prior),reverse=True)
    print(i,round(sc[0][0],2),sc[0][1],a['ask'][:50])
