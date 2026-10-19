import sys,glob,os; sys.path.insert(0,"/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w01/reproducer-w01-5")
from my_check import analyse
P=os.path.expanduser('~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/')
rows=[]
for sid in ['566fa912','82e8a947']:
    for f in glob.glob(P+sid+'*/subagents/agent-*.jsonl'):
        n,res=analyse(f)
        for r in res: rows.append((round(r['gap'],1),os.path.basename(f)[6:15],r['ctx'],round(r['cw']/r['ctx'],3),r['turns_before']))
for r in sorted(rows): print(r)
