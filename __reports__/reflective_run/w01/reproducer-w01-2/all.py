import os,collections,sys
sys.path.insert(0,'.')
import indep
c=collections.Counter(); bad=[]
for name in sorted(os.listdir(indep.R)):
    try: r=indep.cell(name)
    except Exception as e: c["err"]+=1; continue
    ex=r["diff"]["output_tokens"]==0; det=r["nullsub"]==0 and r["nsubreq"]>0
    ic=any(r["diff"][k] for k in("input_tokens","cache_read_input_tokens","cache_creation_input_tokens"))
    grp=("auto" if r["pm"]=="auto" else "plan" if r["pm"]=="plan" else "other")
    c[(r["bin"],grp,"exact" if ex else "inexact")]+=1
    c["agree" if ex==det else "DISAGREE"]+=1
    c["ic_inexact"]+=ic
    if grp=="other" and not ex: bad.append((name,r["mode"],r["think"],r["length"],r["diff"]["output_tokens"]))
for k,v in sorted(c.items(),key=str): print(k,v)
for b in bad: print(b)
