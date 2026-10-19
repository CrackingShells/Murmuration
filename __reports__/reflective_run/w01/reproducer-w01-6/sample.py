import csv, random
rows=[r for r in csv.DictReader(open('../explorer-w01-d/prompts.csv')) if r['channel'] in ('A','B') and r['phase']!='G-C']
print(len(rows))
forced=['8af30fe6','9cd91bd9','d10ebf86','83e43ba0','939bea68','3959fc84']
rest=[r['uuid'][:8] for r in rows if r['uuid'][:8] not in forced]
random.seed(6)
s=random.sample(rest,8)
print(s)
open('sample.txt','w').write('\n'.join(forced+s))
