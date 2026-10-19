"""Timeline of human prompts per session, coloured by who (judgement label), marker by class. usage: python3 -I timeline.py prompts.csv timeline.png"""
import csv,sys
from datetime import datetime
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=[r for r in csv.DictReader(open(sys.argv[1])) if r['channel'] in('A','B')]
def t(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
col={'J':'#1b6ca8','M':'#7f7f7f','S':'#d95f02','W':'#b3b3b3'}
lab={'J':'J  human judgement','M':'M  mixed','S':'S  system could do','W':'W  only because the agent waited'}
mk={'ND':'o','CE':'X','AP':'s','MM':'^','RC':'D','STOP':'P','UT':'v','ADMIN':'.'}
# compress overnight: segments separated by gaps >120 min are laid out with a fixed 20 min visual gap
fig,axs=plt.subplots(2,1,figsize=(11,5.2))
for ax,(s,title) in zip(axs,[('G','Genesis session 566fa912 (study 03:21-06:02 UTC, follow-on to 09:38, scheduler 15:10-00:34)'),('D','Design session 82e8a947 (after the fork at 06:07 UTC)')]):
    rows=[r for r in R if r['session']==s]
    if s=='D': rows=[r for r in rows if r['ts_utc']>='2026-10-18T06:02']
    x=0;prev=None;xs=[];breaks=[]
    for r in rows:
        tt=t(r['ts_utc'])
        if prev is not None:
            g=(tt-prev).total_seconds()/60
            if g>120: x+=25;breaks.append(x-12)
            else: x+=g
        prev=tt;xs.append(x)
    for xx,r in zip(xs,rows):
        ax.scatter(xx,{'J':3,'M':2,'S':1,'W':0}[r['who']],c=col[r['who']],marker=mk[r['cls']],s=60,edgecolors='k',linewidths=0.4,zorder=3)
    for b in breaks: ax.axvline(b,color='k',ls=':',lw=0.8); ax.text(b,3.6,'human away',fontsize=7,ha='center')
    ax.set_yticks([3,2,1,0]);ax.set_yticklabels([lab[k] for k in 'JMSW'],fontsize=7)
    ax.set_title(title,fontsize=8,loc='left');ax.set_xlabel('minutes (breaks >120 min compressed)',fontsize=7);ax.tick_params(labelsize=7);ax.set_ylim(-0.7,4)
    ax.grid(axis='x',lw=0.3)
h=[plt.Line2D([],[],marker=m,ls='',color='w',markerfacecolor='#999',markeredgecolor='k',label=k) for k,m in mk.items() if k!='ADMIN']
fig.legend(handles=h,loc='lower center',ncol=7,fontsize=7,title='class: ND new direction, CE correction, AP approval/choice, MM micro-management, RC review comment, STOP, UT unblock',title_fontsize=7)
plt.tight_layout(rect=(0,0.1,1,1));plt.savefig(sys.argv[2],dpi=130)
