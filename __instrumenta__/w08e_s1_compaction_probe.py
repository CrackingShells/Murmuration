# Prints the compact_boundary metadata and the summary length (characters, no text) of the PI session s1 (ab96c5ed) from its transcript to stdout: the lab's one real compaction.
import json,sys
f='/Users/hacker/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-'
import glob
f=glob.glob(f+'*.jsonl')[0]
for i,l in enumerate(open(f)):
    if 'api-request-blob' in l[:100]: continue
    d=json.loads(l)
    if d.get('isCompactSummary') or d.get('subtype')=='compact_boundary' or 'compactMetadata' in d:
        c=d.get('message',{}).get('content') if isinstance(d.get('message'),dict) else None
        n=len(c) if isinstance(c,str) else (sum(len(x.get('text','')) for x in c if isinstance(x,dict)) if c else None)
        print(i,d.get('type'),d.get('subtype'),d.get('isCompactSummary'),json.dumps(d.get('compactMetadata')),'chars',n,d.get('timestamp'))
