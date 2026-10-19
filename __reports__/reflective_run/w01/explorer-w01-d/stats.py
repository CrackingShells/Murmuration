"""Tables for the report from prompts.csv (MEASURED counts; classes are judgement). usage: python3 -I stats.py prompts.csv"""
import csv,sys,statistics,collections
R=list(csv.DictReader(open(sys.argv[1])))
for r in R:
    for k in('gap_since_prev_human_min','agent_idle_before_min'):
        r[k]=float(r[k]) if r[k] not in('',None) else None
    r['chars']=int(r['chars'])
P=[r for r in R if r['channel'] in('A','B')]
outside=[r for r in P if r['phase']=='G-C']  # scheduler tasks of the human's own, not research
res=[r for r in P if r['phase']!='G-C']
print('records',len(R),'genuine prompts',len(P),'of which scheduler/admin phase G-C',len(outside),'research prompts',len(res))
print('interrupts',sum(r['channel']=='interrupt' for r in R),'slash',sum(r['channel']=='slashcmd' for r in R))
def mat(rows,a,b):
    A=sorted({r[a] for r in rows});B=sorted({r[b] for r in rows})
    print('%-8s'%a+'/'+b,*['%5s'%x for x in B],'  tot')
    for x in A: print('%-12s'%x,*['%5d'%sum(1 for r in rows if r[a]==x and r[b]==y) for y in B],'%5d'%sum(1 for r in rows if r[a]==x))
    print('%-12s'%'tot',*['%5d'%sum(1 for r in rows if r[b]==y) for y in B],'%5d'%len(rows))
print('\n== class x who (research prompts; who: J judgement, S system could, M mixed, W waiting artefact)')
mat(res,'cls','who')
print('\n== phase x who');mat(res,'phase','who')
print('\n== phase x cls');mat(res,'phase','cls')
click=[r for r in res if r['verbatim_click']]
print('\nverbatim clicks',len(click),'of',len(res),'=%.0f%%'%(100*len(click)/len(res)))
print('typed chars: median',statistics.median([r['chars'] for r in res if not r['verbatim_click']]),'max',max(r['chars'] for r in res),'click chars median',statistics.median([r['chars'] for r in click]))
print('state at prompt',collections.Counter(r['state_at_prompt'] for r in res))
# gaps
for ph in ['G-A','G-B','D-A','D-B','D-C']:
    g=[r['gap_since_prev_human_min'] for r in res if r['phase']==ph and r['gap_since_prev_human_min'] is not None]
    t0=min(r['ts_utc'] for r in res if r['phase']==ph);t1=max(r['ts_utc'] for r in res if r['phase']==ph)
    print(ph,'n',sum(1 for r in res if r['phase']==ph),'span',t0[5:16],'->',t1[5:16],'gaps(min):',[round(x) for x in g])
# idle accounting: agent idle before a prompt, only when no subagent was running and idle>=1 min and < 120 (human present)
idle=[r for r in res if r['state_at_prompt']=='idle' and r['agent_idle_before_min'] is not None]
pres=[r for r in idle if r['agent_idle_before_min']<120]
print('\nidle-before-prompt, human present (<120 min): n',len(pres),'sum min',round(sum(r['agent_idle_before_min'] for r in pres)),'median',statistics.median([r['agent_idle_before_min'] for r in pres]))
away=[r for r in idle if r['agent_idle_before_min']>=120]
print('idle >=120 min (human away):',[(r['phase'],round(r['agent_idle_before_min'])) for r in away])
for who in 'JSMW':
    x=[r['agent_idle_before_min'] for r in pres if r['who']==who]
    print(' who',who,'n',len(x),'sum idle min',round(sum(x)))
# W prompts
print('\nW (waiting artefact) rows:',[(r['uuid'][:8],r['verbatim_click']) for r in res if r['who']=='W'])
print('S rows:',[(r['uuid'][:8],r['note'][:50]) for r in res if r['who']=='S'])
# autonomy streaks inside human presence: tool calls + turns between prompts
for ph in ['G-A','D-A']:
    s=[(r['uuid'][:8],r['gap_since_prev_human_min'],r['main_turns_since_prev'],r['tool_calls_since_prev'],r['agent_dispatches_since_prev']) for r in res if r['phase']==ph]
    print(ph,s)
