#!/usr/bin/env python3
"""Compute, from a wave's harness.jsonl, the end time and span of each author-to-verifier chain and the wave length under 'wave = pre + longest chain + close'; prints a table.

Usage: wave_chain_ends.py HARNESS.jsonl PRE_END_HHMMSS WAVE_END_HHMMSS CHAIN1=a,b,c CHAIN2=...   (names are agent names; chain end = latest 'end' event among them)
"""
import json,sys,datetime as dt
def tt(s): return dt.datetime.fromisoformat(s)
ev=[json.loads(l) for l in open(sys.argv[1])]
def hms(s): h,m,x=s[:2],s[2:4],s[4:]; return int(h)*3600+int(m)*60+int(x)
def sec(t): return t.hour*3600+t.minute*60+t.second
first=min(sec(tt(e['t'])) for e in ev if e['event']=='start')
pre_end=hms(sys.argv[2]); wave_end=hms(sys.argv[3])
print('first dispatch', dt.timedelta(seconds=first))
res=[]
for arg in sys.argv[4:]:
    n,names=arg.split('='); names=names.split(',')
    e=max(sec(tt(x['t'])) for x in ev if x['event']=='end' and x['name'] in names)
    res.append((n,e)); print(f'{n}\tend {dt.timedelta(seconds=e)}\tspan_min {(e-first)/60:.1f}')
res.sort(key=lambda r:-r[1])
close=wave_end-res[0][1]
print(f'pre (to first dispatch, from wave start {dt.timedelta(seconds=pre_end)}): {(first-pre_end)/60:.1f} min; close after last verdict: {close/60:.1f} min; wave end {dt.timedelta(seconds=wave_end)}')
print(f'second chain {res[1][0]} ends {dt.timedelta(seconds=res[1][1])}: removing the critical chain entirely saves at most {(res[0][1]-res[1][1])/60:.1f} min if close time is unchanged')
