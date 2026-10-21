#!/usr/bin/env python3
"""Recomputes, independently of w07c1_table.py, per cell request 0 tokens, deferred-name counts, skill-listing size, distinct model requests, Reads and the final answer, from each cell's stdout.jsonl session id and the transcript ~/.claude/projects/*/<session>.jsonl; input: runs dir; output: stdout table."""
import json,glob,os,sys
runs=sys.argv[1]
def cells():
    return sorted(os.listdir(runs))
out={}
for c in cells():
    so=os.path.join(runs,c,'stdout.jsonl')
    if not os.path.exists(so): continue
    sid=None; final=None; init_tools=None
    for l in open(so):
        d=json.loads(l)
        sid=d.get('session_id',sid)
        if d.get('type')=='result': final=d.get('result')
        if d.get('type')=='system' and d.get('subtype')=='init': init_tools=d.get('tools')
    tp=glob.glob(os.path.expanduser('~/.claude/projects/*/%s.jsonl'%sid))
    if not tp: print(c,'NO TRANSCRIPT',sid); continue
    recs=[json.loads(l) for l in open(tp[0])]
    first=None; rids=set(); reads=[]; dn=0; names=set(); sl=None; slc=0; stop=False
    for r in recs:
        a=r.get('attachment')
        if a:
            if a.get('type')=='deferred_tools_delta' and first is None:
                names|=set(a.get('addedNames',[]))
            if a.get('type')=='skill_listing': sl=a.get('skillCount'); slc=len(a.get('content',''))
        if r.get('type')=='assistant':
            m=r['message']
            if first is None and m.get('usage'): first=m['usage']
            rids.add(m.get('id'))
            for b in m.get('content',[]):
                if b.get('type')=='tool_use' and b['name']=='Read': reads.append(b['input'].get('file_path'))
    u=first
    req0=u['input_tokens']+u['cache_creation_input_tokens']+u['cache_read_input_tokens']
    out[c]=(req0,len(names),sl,slc,len(rids),reads,(final or '')[:70].replace('\n',' '),len(init_tools or []))
    print(c,req0,'names',len(names),'listing',sl,slc,'reqs',len(rids),'ntools',len(init_tools or []),'|',(final or '')[:70].replace('\n',' '))
    for p in reads: print('    Read',p.replace('/private/tmp/murmuration-w07/author-w07-1/runs/',''), 'EXISTS' if os.path.exists(p) else 'MISSING')
