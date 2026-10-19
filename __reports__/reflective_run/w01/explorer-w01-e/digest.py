"""Prototype: one-screen answer to 'what is the team doing / found / cost / needs me'.
Read-only. Uses only files already in the lab + subagent transcripts. No prices applied.
usage: python3 -I digest.py <lab root> <transcript session folder>  (folder holding subagents/)"""
import json,sys,glob,os,re,importlib.util,datetime as dt
root,sess=sys.argv[1],sys.argv[2]
spec=importlib.util.spec_from_file_location('ls',os.path.join(root,'scripts/lab_status.py'));ls=importlib.util.module_from_spec(spec);spec.loader.exec_module(ls)
now=dt.datetime.fromisoformat(sys.argv[3]) if len(sys.argv)>3 else dt.datetime.now(dt.timezone.utc)
def t(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00'))
print('TEAM')
for m in sorted(glob.glob(sess+'/subagents/*.meta.json')):
    meta=json.load(open(m)); rows=[json.loads(l) for l in open(m.replace('.meta.json','.jsonl'))]
    a=t(rows[0]['timestamp']); b=t(rows[-1]['timestamp'])
    out=sum((r.get('message') or {}).get('usage',{}).get('output_tokens',0) for r in rows if r.get('type')=='assistant')
    name=meta.get('name','?'); rep=glob.glob(f'{root}/__reports__/*/*/{name}/report.md')+glob.glob(f'{root}/__reports__/*/*/*/{name}/report.md')
    idle=(now-b).total_seconds()/60
    state='working' if idle<2 else ('returned' if rep else 'stopped, no report?')
    print(f"  {name:16} {state:20} {int((b-a).total_seconds()//60):3d} min  wrote {out:6,d} tokens  {meta.get('description','')}")
puz=ls.open_puzzles(root) if hasattr(ls,'open_puzzles') else []
print(f"OPEN PUZZLES {len(puz)}   CLAIMS {len(ls.read_claims(root)) if hasattr(ls,'read_claims') else '?'}")
print('NEEDS YOU: (no field for this exists in lab files today; the PI would have to write it)')
