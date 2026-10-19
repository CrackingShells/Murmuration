import json,re,statistics,sys
base='/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/'
def stats(sid):
    rows=[json.loads(l) for l in open(base+sid+'.jsonl')]
    out=[]
    for i,d in enumerate(rows):
        if d.get('type')!='assistant' or d.get('isSidechain'): continue
        blocks=d['message']['content']
        txt='\n'.join(b.get('text','') for b in blocks if b.get('type')=='text').strip()
        if not txt: continue
        has_tool=any(b.get('type')=='tool_use' for b in blocks)
        w=len(txt.split())
        out.append(dict(line=i,tool=has_tool,words=w,bullets=len(re.findall(r'^\s*[-*] ',txt,flags=re.M)),tables=len(re.findall(r'^\|',txt,flags=re.M)),paths=len(re.findall(r'`[^`]*[/.][a-z]{2,4}`|\.md',txt)),bold=txt.count('**')//2,code=txt.count('```')//2,gloss=0))
    return out
for sid in sys.argv[1:]:
    o=stats(sid)
    fin=[x for x in o if not x['tool']]
    print(sid[:8],'text msgs',len(o),'turn-final',len(fin),'words median',statistics.median([x['words'] for x in fin]),'p90',sorted(x['words'] for x in fin)[int(.9*len(fin))],'max',max(x['words'] for x in fin))
    print('   bullets/msg',round(sum(x['bullets'] for x in fin)/len(fin),1),'table rows/msg',round(sum(x['tables'] for x in fin)/len(fin),2),'paths/msg',round(sum(x['paths'] for x in fin)/len(fin),1),'msgs w/ table',sum(1 for x in fin if x['tables']),'msgs >250 words',sum(1 for x in fin if x['words']>250))
