"""For each research prompt in explorer-w01-d/prompts.csv, find the PI output the human reacted to:
the last assistant text blocks (main thread) and the last wrap_up recap/ask before the prompt.
Read-only on transcripts. usage: python3 -I extract_prev.py > prev_pi.json
Why Python: JSONL transcripts, a few thousand records; exact timestamp joins."""
import json, csv, os, re
from datetime import datetime
P = os.path.expanduser('~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/')
FILES = {'G': P + '566fa912-7009-421a-9d79-11145e2b8db9.jsonl', 'D': P + '82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl'}
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'explorer-w01-d', 'prompts.csv')
def ts(s): return datetime.fromisoformat(s.replace('Z', '+00:00'))
outs = {}
for k, f in FILES.items():
    L = []
    for i, l in enumerate(open(f)):
        d = json.loads(l)
        if d.get('type') != 'assistant' or d.get('isSidechain'): continue
        for b in d['message']['content']:
            if b.get('type') == 'text' and b['text'].strip():
                L.append((d['timestamp'], i + 1, 'text', b['text']))
            if b.get('type') == 'tool_use' and b['name'] == 'mcp__ccd_turn__wrap_up':
                inp = b['input']
                L.append((d['timestamp'], i + 1, 'wrap_up', json.dumps(inp, ensure_ascii=False)))
    outs[k] = L
res = []
for r in csv.DictReader(open(D)):
    if r['cls'] in ('STOP',) and r['human_text'].startswith('[Request'): continue
    L = outs[r['session']]
    before = [x for x in L if x[0] < r['ts_utc']]
    t = [x for x in before if x[2] == 'text'][-3:]
    w = [x for x in before if x[2] == 'wrap_up'][-1:]
    res.append(dict(uuid=r['uuid'][:8], session=r['session'], ts=r['ts_utc'], cls=r['cls'], who=r['who'], human=r['human_text'],
                    prev_text=[dict(ts=x[0], line=x[1], text=x[3]) for x in t],
                    prev_wrap=[dict(ts=x[0], line=x[1], text=x[3]) for x in w]))
json.dump(res, open('prev_pi.json', 'w'), ensure_ascii=False, indent=1)
print(len(res))
