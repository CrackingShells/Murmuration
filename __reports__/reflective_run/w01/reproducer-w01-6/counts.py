import csv,re
rows=[r for r in csv.DictReader(open('../explorer-w01-d/prompts.csv')) if r['channel'] in('A','B') and r['phase']!='G-C']
print(len(rows))
print('start >',sum(r['human_text'].lstrip().startswith('>') for r in rows))
q=lambda r: any(l.lstrip().startswith('>') or l.strip().startswith('/  / >') for l in r['human_text'].split('\n')) or ' / > ' in r['human_text'] or r['human_text'].lstrip().startswith('>')
print('contain', sum(q(r) for r in rows))
ce=[r for r in rows if r['cls']=='CE']
print('CE',len(ce),'start',sum(r['human_text'].lstrip().startswith('>') for r in ce),'contain',sum(q(r) for r in ce))
from collections import Counter
print(Counter(r['cls'] for r in rows))
for r in rows:
    t=r['human_text'].lower()
    hits=[w for w in ['measured','conjecture','estimate','unsupported','overstated','supported','cited','theorem','checked','verdict','label'] if re.search(r'\b'+w+r'\b',t)]
    if hits: print('label-ish',r['uuid'][:8],hits)
    h=[w for w in ['cost','budget','usd','token','tokens','minutes','hours','$','dollar'] if w in t]
    if h: print('cost-ish',r['uuid'][:8],h, r['human_text'][:0])
print(max(len(r['human_text']) for r in rows), sum(len(r['human_text'])<int(r['chars']) for r in rows))
