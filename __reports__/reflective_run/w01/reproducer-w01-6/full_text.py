import csv,json,glob,re
P='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
rows=[r for r in csv.DictReader(open('../explorer-w01-d/prompts.csv')) if r['channel'] in('A','B') and r['phase']!='G-C']
byuuid={}
for s in ['566fa912','82e8a947']:
    for l in open(glob.glob(P+s+'*.jsonl')[0]):
        d=json.loads(l)
        if d.get('type')=='user' and d.get('uuid'): byuuid[d['uuid']]=d
def txt(d):
    c=d['message']['content']
    if isinstance(c,str): return c
    return '\n'.join(b.get('text','') for b in c if isinstance(b,dict) and b.get('type')=='text')
miss=0; full={}
for r in rows:
    d=byuuid.get(r['uuid'])
    if d is None: miss+=1; full[r['uuid'][:8]]=r['human_text']; continue
    t=re.sub(r'<system-reminder>.*?</system-reminder>','',txt(d),flags=re.S).strip()
    full[r['uuid'][:8]]=t
print('missing in transcripts',miss)
json.dump(full,open('full_text.json','w'))
lab=r'\b(measured|conjecture|estimate|unsupported|overstated|supported|cited|theorem|checked|verdict|verified|label|claim|puzzle|wave)\b'
for u,t in full.items():
    h=re.findall(lab,t.lower())
    if h: print('label-ish',u,set(h))
for u,t in full.items():
    h=re.findall(r'\b(cost|budget|usd|tokens?|minutes?|hours?|dollars?)\b|\$',t.lower())
    if h: print('cost-ish',u,set(h))
starts=[u for u,t in full.items() if t.lstrip().startswith('>')]
print(len(starts))
