# reproducer-w02-1: does grouping by message.id vs requestId give a different file-level mark, over all subagent files?
import json, glob, os
files = glob.glob(os.path.expanduser('~/.claude/projects/*/*/subagents/**/agent-*.jsonl'), recursive=True)
diff = 0; noreq = 0
for f in files:
    a, b = {}, {}
    for l in open(f, errors='replace'):
        if '"assistant"' not in l: continue
        try: d = json.loads(l)
        except ValueError: continue
        m = d.get('message')
        if d.get('type') != 'assistant' or not isinstance(m, dict) or not isinstance(m.get('usage'), dict) or m.get('model') == '<synthetic>': continue
        if not d.get('requestId'): noreq += 1
        a[m.get('id')] = bool(m.get('stop_reason')); b[d.get('requestId') or m.get('id')] = bool(m.get('stop_reason'))
    if any(not v for v in a.values()) != any(not v for v in b.values()): diff += 1; print('differs', f)
print('files', len(files), 'file-level differences', diff, 'records without requestId', noreq)
