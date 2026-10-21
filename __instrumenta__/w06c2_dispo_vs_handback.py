# Computes, from __statera__/wave-0[1-5].md disposition tables, __scrupuli__ puzzle files and git history, for each disposed puzzle: the commit time it first appeared, the commit time of the claims/items its disposition cites, and the disposition class; writes a TSV to stdout.
import re, subprocess, glob, sys, os
ROOT = os.getcwd()
def git(*a):
    return subprocess.run(["git","-C",ROOT]+list(a),capture_output=True,text=True).stdout
def first_time(path_args, pickaxe=None):
    cmd=["log","--format=%cI","--reverse"]
    if pickaxe: cmd+=["-S"+pickaxe]
    cmd+=["--"]+path_args
    out=git(*cmd).split()
    return out[0] if out else ""
def claim_time(c):
    return first_time(["__pondus__/%s.md"%c])
rows=[]
for w in range(1,6):
    note=open("__statera__/wave-0%d.md"%w).read()
    sec=note.split("## Puzzle dispositions",1)[1].split("\n## ",1)[0]
    closed=re.search(r"closed: (\S+)",note)
    for m in re.finditer(r"^\| (S-w0%d-(\S+)-(\d+)) \| (.*) \|$"%w,sec,re.M):
        pid,agent,n,disp=m.groups()
        f="__scrupuli__/wave-0%d-%s.md"%(w,agent)
        t=first_time([f],"## "+pid) if os.path.exists(f) else ""
        cls="followed" if disp.startswith("followed") else "parked" if disp.startswith("parked") else "other"
        claims=sorted(set(re.findall(r"\bw0\d-c\d+\b",disp)))
        ct=[claim_time(c) for c in claims]
        rows.append((pid,w,cls,t,",".join(claims),",".join(ct),"synth" if "synthesis.md" in disp else "",disp.replace("\t"," ")))
print("\t".join(["pid","wave","cls","puzzle_first_commit","claims","claim_first_commits","synth_item","disposition"]))
for r in rows: print("\t".join(map(str,r)))
