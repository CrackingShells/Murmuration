# Draws a seeded random sample of N hand-back wakes of waves 5-8 from my wakes.jsonl (argv[1]) and prints a short blind extraction (sender, body head, PI tool calls trimmed, PI text head) with no automatic code; also writes the sample ids to <dir>/sample_ids.txt; usage: python3 -I w09c2v_sample.py <wakes.jsonl> <seed> <N>
import json,sys,random,re,os
W=[json.loads(l) for l in open(sys.argv[1])]
pool=[w for w in W if w['lab'] in ('w5','w6','w7','w8')]
random.seed(int(sys.argv[2]))
S=random.sample(pool,int(sys.argv[3]))
open(os.path.join(os.path.dirname(sys.argv[1]),'sample_ids.txt'),'w').write('\n'.join('%s %d'%(w['lab'],w['idx']) for w in S)+'\n')
for k,w in enumerate(S,1):
    b=re.sub(r'^\[Subagent hand-back\].*?The report follows:\s*','',w['body'],flags=re.S)
    b=re.sub(r'\[harness: subagent output matched.*?\]\s*','',b,flags=re.S)
    print('#### S%02d sender=%s'%(k,w['sender']))
    print('BODY:',b[:260].replace('\n',' '))
    for t in w['tus']:
        i=t['input']
        s=i.get('command') or i.get('file_path') or i.get('query') or json.dumps(i)
        if t['name']=='SendMessage': s='to='+str(i.get('to'))
        if t['name']=='Agent': s='name='+str(i.get('name'))
        print('  TU',t['name'],s[:230].replace('\n',' ; '))
    for x in w['texts'][:2]: print('  TXT',x[:200].replace('\n',' '))
