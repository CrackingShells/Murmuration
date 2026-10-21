#!/usr/bin/env python3
"""Draw a wave Gantt chart (PNG) and print per-lane time shares from the per-lane interval TSVs of wave_timeline_pi.py plus the headless-cell TSV of wave_headless_cells.py.

Usage: wave_gantt.py INTERVAL_DIR CELLS.tsv OUT.png
Colours: model turn, tool call < 45 s, tool call >= 45 s (wait), not running (idle); lane 'headless' shows claude -p cells of author-w04-2.
"""
import sys,glob,os,csv,datetime as dt,collections
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d0=dt.datetime(2026,10,20)
def mins(s):
    h,m,x=s.split(':'); return int(h)*60+int(m)+float(x)/60-9*60-27   # minutes after 09:27
lanes=[]; order=['PI']+sorted([os.path.basename(f)[:-4] for f in glob.glob(sys.argv[1]+'/*.tsv') if not f.endswith('/PI.tsv')],key=lambda n:(n.split('-w')[0]!='author',n))
def first(n):
    r=list(csv.DictReader(open(f'{sys.argv[1]}/{n}.tsv'),delimiter='\t')); return mins(r[0]['start_jst'])
order=['PI']+sorted([n for n in order if n!='PI'],key=first)
fig,ax=plt.subplots(figsize=(15,9)); col={'model':'#d95f02','tool_s':'#7570b3','tool_l':'#1b9e77','idle':'#eeeeee'}
share={}
for y,n in enumerate(order):
    tot=collections.Counter()
    for r in csv.DictReader(open(f'{sys.argv[1]}/{n}.tsv'),delimiter='\t'):
        a,b=mins(r['start_jst']),mins(r['end_jst']); s=float(r['secs']); c=r['class']
        k='tool_l' if c=='tool' and s>=45 else 'tool_s' if c=='tool' else c
        if n=='PI' and k=='idle': k='idle_pi'
        tot[k]+=s
        ax.barh(y,b-a,left=a,color=('#cfe8f3' if k=='idle_pi' else col[k]),edgecolor='none',height=0.7)
    share[n]=tot
# headless lane
y=len(order)
for r in csv.DictReader(open(sys.argv[2]),delimiter='\t'):
    if r['author']!='author-w04-2': continue
    a,b=mins(r['start_jst']),mins(r['end_jst']); ax.barh(y,b-a,left=a,height=0.25,color='#1f78b4',edgecolor='white',linewidth=0.3)
ax.set_yticks(list(range(len(order)+1))); ax.set_yticklabels(order+['headless cells (author-w04-2)'])
ax.invert_yaxis(); ticks=list(range(0,90,10)); ax.set_xticks(ticks); ax.set_xticklabels([f'{9+(27+t)//60:02d}:{(27+t)%60:02d}' for t in ticks]); ax.set_xlabel('JST, 2026-10-20')
import matplotlib.patches as mp
ax.legend(handles=[mp.Patch(color=col['model'],label='model turn'),mp.Patch(color=col['tool_s'],label='tool call < 45 s'),mp.Patch(color=col['tool_l'],label='tool call >= 45 s (wait loops, runs)'),mp.Patch(color='#cfe8f3',label='PI idle (waiting for a notification)'),mp.Patch(color='#1f78b4',label='headless claude -p cell')],loc='upper center',bbox_to_anchor=(0.5,-0.07),ncol=5)
ax.set_title('Wave 4 timeline: PI and 15 worker runs (lane = one agent, resumes shown as separate bars)')
plt.tight_layout(); plt.savefig(sys.argv[3],dpi=110)
print('lane\tmodel_s\ttool_short_s\ttool_long_s\tidle_s')
for n in order:
    t=share[n]; print(f"{n}\t{t['model']:.0f}\t{t['tool_s']:.0f}\t{t['tool_l']:.0f}\t{t['idle']+t['idle_pi']:.0f}")
