import sys,glob,os,json; sys.path.insert(0,"/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-5")
from my_check import load,D
for f in sorted(glob.glob(D+'/subagents/agent-*.jsonl')):
    recs=load(f)
    if not recs: continue
    first=recs[0]['message']['content']
    first=first if isinstance(first,str) else json.dumps(first)
    if 'explorer-w01' not in first[:60]: continue
    name=first[first.find('explorer-w01'):][:12]
    turn=0; seen=set(); tu={}; out=[]
    for r in recs:
        if r['type']=='assistant':
            i=r['message']['id']
            if i not in seen: seen.add(i); turn=len(seen)
            for b in r['message']['content']:
                if b['type']=='tool_use': tu[b['id']]=(turn,b['name'],b['input'])
        elif r['type']=='user' and isinstance(r['message']['content'],list):
            for b in r['message']['content']:
                if b.get('type')=='tool_result' and b['tool_use_id'] in tu:
                    t,n,inp=tu[b['tool_use_id']]
                    txt=json.dumps(b.get('content'))
                    path=inp.get('file_path','') if n in('Write','Edit') else (inp.get('command','')[:0])
                    cmd=inp.get('command','') if n=='Bash' else ''
                    if n=='Write' or ('cat >' in cmd and 'scrupuli' in cmd) or ('scrupuli' in cmd and '>>' in cmd):
                        refused='Subagents should return' in txt
                        out.append((t,n,os.path.basename(path) if path else 'bash:'+cmd[:40].replace('\n',' '),'REFUSED' if refused else 'ok'))
    print(name,len(seen),out)
