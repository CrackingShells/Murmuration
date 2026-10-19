import sys; sys.path.insert(0,"/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-5")
import json,glob,os,collections,statistics
from my_check import T,UNTIL,D
P=os.path.expanduser('~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/')
owner={}  # message id -> earliest file
files={}
allf=sorted(glob.glob(P+'566fa912*/subagents/agent-*.jsonl')+glob.glob(P+'82e8a947*/subagents/agent-*.jsonl')+glob.glob(D+'/subagents/agent-*.jsonl'))
rows=[]
first={}
for f in allf:
    ids=collections.OrderedDict(); models=collections.Counter(); ts=None
    for l in open(f):
        try:r=json.loads(l)
        except: continue
        if r.get('timestamp') and T(r['timestamp'])>T(UNTIL): continue
        if r.get('type')=='assistant':
            i=r['message']['id']
            if i not in ids: ids[i]=r['timestamp']; models[r['message'].get('model')]+=1
            first.setdefault(i,(r['timestamp'],f))
    files[f]=(ids,models)
for f,(ids,models) in files.items():
    own=[i for i in ids if first[i][1]==f]
    sess='genesis' if '566fa912' in f else 'design' if '82e8a947' in f else 'this'
    rows.append((sess,os.path.basename(f)[6:15],len(own),len(ids),models.most_common(1)[0][0] if models else None))
for r in rows: print(r)
