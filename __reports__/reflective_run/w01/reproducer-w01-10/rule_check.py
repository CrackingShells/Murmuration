"""Own implementation of the claim's rule, run on a real git repo + linked worktree; then the author's patched script is fired as a subprocess on the same cases and compared."""
import os,subprocess,sys,tempfile,json
def mine(cwd,proj):
    h=os.path.abspath(cwd)
    while True:
        if os.path.isdir(os.path.join(h,'__statera__')): return h
        if os.path.exists(os.path.join(h,'.git')) or os.path.dirname(h)==h: break
        h=os.path.dirname(h)
    return proj if proj and os.path.isdir(os.path.join(proj,'__statera__')) else None
author=sys.argv[1]
def sh(*a,cwd=None): subprocess.run(a,cwd=cwd,check=True,capture_output=True)
with tempfile.TemporaryDirectory() as t:
    t=os.path.realpath(t); M=t+'/main'; W=t+'/wt'
    os.makedirs(M); sh('git','init','-q',cwd=M); sh('git','-c','user.name=x','-c','user.email=x@x','commit','-q','--allow-empty','-m','i',cwd=M)
    sh('git','worktree','add','-q','-b','b',W,cwd=M)
    assert os.path.isfile(W+'/.git')
    os.makedirs(M+'/__statera__'); os.makedirs(W+'/sub')
    def run(cwd,proj,tag):
        e=dict(os.environ); e.pop('CLAUDE_PROJECT_DIR',None)
        if proj: e['CLAUDE_PROJECT_DIR']=proj
        before={p:(os.path.getsize(p+'/__statera__/user_words.md') if os.path.exists(p+'/__statera__/user_words.md') else 0) for p in (M,W)}
        subprocess.run([sys.executable,'-I',author],input=json.dumps({'prompt':'hello '+tag,'cwd':cwd}),text=True,env=e,capture_output=True)
        got=[('M' if p==M else 'W') for p in (M,W) if os.path.exists(p+'/__statera__/user_words.md') and os.path.getsize(p+'/__statera__/user_words.md')>before[p]]
        m=mine(cwd,proj); return tag,got,{M:'M',W:'W',None:'-'}[m]
    for r in [run(W,M,'A wt no lab, proj=main (11:04-like before lab)'), run(W+'/sub',M,'B subfolder, no lab')]: print(r)
    os.makedirs(W+'/__statera__')
    for r in [run(W,M,'C wt has lab, proj=main (the 11:04 case)'), run(W+'/sub',M,'D subfolder of wt with lab'), run(M,M,'E shell back in main, proj=main'), run(M,W,'F cwd main, proj=wt (started in wt, shell cd main)'), run(W,W,'G wt both')]: print(r)
