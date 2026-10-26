# Counts, on my wakes.jsonl (argv[1]) for waves 5-8 hand-backs, the raw-open code of the author's classifier (w09d_turns.call_info/obj_class/RAW, sender-name rule included) as shipped and with the "lab_status" substring masked in Bash commands, by sender role; shows how many wakes the substring rule hides; usage: python3 -I w09c2v_labstatus_bug.py <wakes.jsonl>
import json,sys,os,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from w09d_turns import call_info,obj_class,RAW
W=[json.loads(l) for l in open(sys.argv[1])]
def raw(w,mask):
    for t in w['tus']:
        inp=dict(t['input'])
        if mask and t['name']=='Bash': inp['command']=inp.get('command','').replace('lab_status','labstatus')
        c=call_info(t['name'],inp)
        if c['kind'] in('read-whole','read-part','bash-view','bash-query'):
            for p in c['paths']:
                if obj_class(p) in RAW or (w['sender'] and w['sender'] in p): return True
    return False
tot=collections.defaultdict(lambda:[0,0,0]); hid=[]
for w in W:
    if w['lab'] in('w5','w6','w7','w8'):
        a=raw(w,False); b=raw(w,True)
        for k in(w['role'],'ALL'):
            tot[k][0]+=1; tot[k][1]+=a; tot[k][2]+=b
        if b and not a: hid.append((w['lab'],w['sender'],w['ts'][:19]))
for k in sorted(tot): print(k,'n=%d shipped=%d masked=%d'%tuple(tot[k]))
print('hidden by the substring rule:',len(hid)); [print(' ',h) for h in hid]
