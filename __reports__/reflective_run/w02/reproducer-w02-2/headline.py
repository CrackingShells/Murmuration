import importlib.util, json, os, sys, tempfile, glob, collections
D="/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/__reports__/reflective_run/w02/reproducer-w02-2/"
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
new=load("new","/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/scripts/user_words.py")
old=load("old",D+"head_user_words.py")
os.environ.pop("CLAUDE_PROJECT_DIR",None)
P="/Users/hacker/.claude/projects/"
files={"566fa912":P+"-Users-hacker-Documents-explore-combinatorics-on-binary/566fa912-7009-421a-9d79-11145e2b8db9.jsonl",
"82e8a947":P+"-Users-hacker-Documents-explore-combinatorics-on-binary/82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl",
"3ccc590f":P+"-Users-hacker-Documents-explore-combinatorics-on-binary/3ccc590f-0187-4f79-b7af-4955944f1374.jsonl",
"2947f9dc":P+"-Users-hacker-Documents-explore-combinatorics-on-binary/2947f9dc-1c3a-452b-97a5-39d4510a1271.jsonl",
"ab96c5ed":P+"-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl"}
def run(mod,prompt):
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(t+"/__statera__")
        mod.handle({"prompt":prompt,"cwd":t})
        p=t+"/__statera__/user_words.md"
        if not os.path.exists(p): return None
        import re
        b=open(p,encoding="utf-8",newline="").read()
        return re.split(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}\n\n",b,flags=re.M)[-1][:-1]
def texts(c):
    if isinstance(c,str): return c
    if isinstance(c,list):
        if any(isinstance(b,dict) and b.get("type")=="tool_result" for b in c): return None
        return "\n".join(b.get("text","") for b in c if isinstance(b,dict) and b.get("type")=="text")
tot=collections.Counter()
for k,f in files.items():
    seen=set(); ev=[]
    for l in open(f):
        try:r=json.loads(l)
        except: continue
        if r.get("isSidechain"): continue
        if r.get("type")=="user" and not r.get("isMeta"):
            t=texts(r.get("message",{}).get("content"))
            if t and r.get("uuid") not in seen: seen.add(r["uuid"]); ev.append(("user",t))
        elif r.get("type")=="attachment" and r["attachment"].get("type")=="queued_command":
            a=r["attachment"]; t=texts(a.get("prompt")) 
            if t and r.get("uuid") not in seen: seen.add(r["uuid"]); ev.append(("queued",t))
    c=collections.Counter()
    for kind,t in ev:
        # typed: not a platform-injected record (hook would not fire / not user words)
        o=run(old,t); n=run(new,t)
        c["events"]+=1
        c["old_store"]+= o is not None
        c["new_store"]+= n is not None
        c["differ"]+= (o!=n)
        c["dropped"]+= (o is not None and n is None)
        c["gained"]+= (o is None and n is not None)
    print(k,dict(c)); tot.update(c)
print("TOTAL",dict(tot))

print("---- listing")
import re
rows=[]
for k,f in files.items():
    seen=set()
    for l in open(f):
        try:r=json.loads(l)
        except: continue
        if r.get("isSidechain"): continue
        t=None;kind=None
        if r.get("type")=="user" and not r.get("isMeta"):
            t=texts(r.get("message",{}).get("content")); kind="user"
        elif r.get("type")=="attachment" and r["attachment"].get("type")=="queued_command":
            t=texts(r["attachment"].get("prompt")); kind="queued"
        if not t or r.get("uuid") in seen: continue
        seen.add(r["uuid"])
        o=run(old,t); n=run(new,t)
        if o is None and n is None: continue
        rows.append((k,kind,o,n,t))
json.dump(rows,open(D+"rows.json","w"))
for k,kind,o,n,t in rows:
    if n is None or o is None or (o!=n):
        pass
import collections
print(collections.Counter((k,kind,(n is None),(o!=n)) for k,kind,o,n,t in rows))
for k,kind,o,n,t in rows:
    if n is None: print("DROPPED",k,kind,repr(t[:100]))
