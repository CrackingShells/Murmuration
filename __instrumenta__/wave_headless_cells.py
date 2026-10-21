#!/usr/bin/env python3
"""Tabulate the headless claude -p cells of a wave (cell, wall_s, end time from meta.json mtime, derived start) from meta.json files under a run root; prints TSV and per-author max concurrency.

Usage: wave_headless_cells.py RUN_ROOT OUT.tsv   (RUN_ROOT holds <author>/runs/<cell>/meta.json or <author>/<cell>/meta.json)
"""
import json,sys,glob,os,datetime as dt,collections
JST=dt.timezone(dt.timedelta(hours=9))
rows=[]
for f in glob.glob(sys.argv[1]+'/*/**/meta.json',recursive=True):
    try: m=json.load(open(f))
    except Exception: continue
    if 'wall_s' not in m: continue
    a=os.path.relpath(f,sys.argv[1]).split('/')[0]
    end=dt.datetime.fromtimestamp(os.path.getmtime(f),JST); w=float(m['wall_s'])
    rows.append((a,m.get('cell',os.path.basename(os.path.dirname(f))),w,end-dt.timedelta(seconds=w),end,m.get('usd'),m.get('turns')))
rows.sort(key=lambda r:(r[0],r[3]))
with open(sys.argv[2],'w') as o:
    o.write('author\tcell\twall_s\tstart_jst\tend_jst\tturns\n')
    for a,c,w,s,e,u,t in rows: o.write(f'{a}\t{c}\t{w:.0f}\t{s:%H:%M:%S}\t{e:%H:%M:%S}\t{t}\n')
by=collections.defaultdict(list)
for r in rows: by[r[0]].append(r)
for a,rs in by.items():
    ev=sorted([(r[3],1) for r in rs]+[(r[4],-1) for r in rs]); cur=mx=0
    for _,d in ev: cur+=d; mx=max(mx,cur)
    print(f'{a}: {len(rs)} cells, sum wall {sum(r[2] for r in rs):.0f}s, span {min(r[3] for r in rs):%H:%M}-{max(r[4] for r in rs):%H:%M}, max concurrency {mx}')
