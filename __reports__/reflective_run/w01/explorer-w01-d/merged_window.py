"""Merged human-prompt stream across the genesis and design sessions, 06:00-10:10 UTC 2026-10-18. usage: python3 -I merged_window.py prompts.csv"""
import csv,sys,statistics
from datetime import datetime
R=[r for r in csv.DictReader(open(sys.argv[1])) if r['channel'] in('A','B') and '2026-10-18T06:00'<=r['ts_utc']<'2026-10-18T10:10']
t=lambda s: datetime.fromisoformat(s.replace('Z','+00:00'))
R.sort(key=lambda r:r['ts_utc'])
g=[(t(b['ts_utc'])-t(a['ts_utc'])).total_seconds()/60 for a,b in zip(R,R[1:])]
print('prompts',len(R),'G',sum(r['session']=='G' for r in R),'D',sum(r['session']=='D' for r in R),'median gap',round(statistics.median(g),1),'max',round(max(g),1),'alternations',sum(1 for a,b in zip(R,R[1:]) if a['session']!=b['session']),'of',len(g))
