# Independent: sessions whose cwd (any record in the first 300 lines) is under a git worktree of the repo family.
import glob, json, os, subprocess, sys
root=sys.argv[1]
def wts(r):
    try: out=subprocess.run(["git","-C",r,"worktree","list","--porcelain"],capture_output=True,text=True,timeout=10).stdout
    except Exception: return []
    return [l[9:] for l in out.splitlines() if l.startswith("worktree ")]
roots={os.path.realpath(root), root}
use_git = "--nogit" not in sys.argv
if use_git: roots |= {os.path.realpath(w) for w in wts(root)} | set(wts(root))
def under(c): return any(c==r or c.startswith(r.rstrip("/")+"/") for r in roots)
H=os.path.expanduser("~/.claude/projects")
found=[]
for f in glob.glob(H+"/*/*.jsonl"):
    cwd=None
    for i,l in enumerate(open(f,errors="replace")):
        if i>300: break
        if '"cwd"' in l:
            try: cwd=json.loads(l).get("cwd")
            except Exception: continue
            if cwd: break
    if cwd and under(cwd): found.append((f,cwd))
wt=os.path.realpath("/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e")
print("roots",sorted(roots)); print("found",len(found),"of which under worktree",sum(1 for f,c in found if c==wt or c.startswith(wt+"/")), "exactly at worktree",sum(1 for f,c in found if c==wt))
