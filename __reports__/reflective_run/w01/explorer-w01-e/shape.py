import json,sys,collections
p=sys.argv[1]
c=collections.Counter()
for l in open(p):
    try:d=json.loads(l)
    except: continue
    c[(d.get('type'),d.get('isSidechain'),d.get('userType'))]+=1
print(c)
