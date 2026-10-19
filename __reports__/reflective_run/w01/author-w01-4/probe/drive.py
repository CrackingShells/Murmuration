"""Drive one headless claude session turn by turn (stream-json). usage: [DRIVE_LINGER=seconds to keep the session open after the last turn] drive.py <cwd> <settings> <out.jsonl> <msg>..."""
import json,os,subprocess,sys,time
cwd,settings,out=sys.argv[1:4]; msgs=sys.argv[4:]
p=subprocess.Popen(["claude","-p","--input-format","stream-json","--output-format","stream-json","--verbose","--model","haiku",
    "--setting-sources","project","--settings",settings,"--permission-mode","bypassPermissions","--max-budget-usd","0.40"],
    cwd=cwd,stdin=subprocess.PIPE,stdout=open(out,"w"),stderr=subprocess.DEVNULL,text=True)
def results(): return sum(1 for l in open(out) if '"type":"result"' in l.replace(' ',''))
for i,m in enumerate(msgs):
    p.stdin.write(json.dumps({"type":"user","message":{"role":"user","content":[{"type":"text","text":m}]}})+"\n"); p.stdin.flush()
    t=time.time()
    while results()<i+1 and time.time()-t<120: time.sleep(0.5)
time.sleep(float(os.environ.get("DRIVE_LINGER","0")))
p.stdin.close(); p.wait(timeout=60)
