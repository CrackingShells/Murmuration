"""Re-run the word checks of w01-c6 on the FULL human text (prompts.csv truncates 19 of the 55 prompts at 428 chars).
usage: python3 -I full_text_check.py > full_text_check.txt     (seconds, 0 tokens, read-only on the two transcripts)
Full text = the human's own text blocks of the record whose uuid starts with the prompt's uuid8 (user record, or queued_command attachment),
with leading <system-reminder> blocks dropped.
"""
import csv, json, os, re
H = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in csv.DictReader(open(os.path.join(H, '..', 'explorer-w01-d', 'prompts.csv'))) if r['channel'] in ('A', 'B') and r['phase'] != 'G-C']
P = os.path.expanduser('~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/')
full = {}
want = {r['uuid'] for r in rows}
def strings(x):
    if isinstance(x, str): yield x
    elif isinstance(x, list):
        for y in x: yield from strings(y)
    elif isinstance(x, dict):
        if x.get('type') == 'text' and 'text' in x: yield x['text']
        else:
            for k in ('prompt', 'content', 'text', 'message'):
                if k in x: yield from strings(x[k])
for f in ('566fa912-7009-421a-9d79-11145e2b8db9.jsonl', '82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl'):
    for l in open(P + f):
        d = json.loads(l)
        u = d.get('uuid')
        if u in want and u not in full:
            body = d.get('message') if d.get('type') == 'user' else d.get('attachment')
            t = [s for s in strings(body) if not s.lstrip().startswith('<system-reminder>')]
            full[u] = '\n'.join(t)
miss = want - set(full)
trunc = [r['uuid'][:8] for r in rows if len(full.get(r['uuid'], '')) > len(r['human_text']) + 5]
print('prompts', len(rows), 'full text found', len(full), 'missing', len(miss), 'longer than the csv text', len(trunc))
def hits(p, flags=re.I): return [(r['uuid'][:8], sorted({m.lower() for m in re.findall(p, full.get(r['uuid'], ''), flags)})) for r in rows if re.search(p, full.get(r['uuid'], ''), flags)]
print('label or verdict words:', hits(r'\b(measured|conjecture|theorem|checked|estimate|cited|supported|overstated|unsupported)\b'))
print('cost unit words (usd, tokens, hours, minutes, budget, cost):', hits(r'\b(usd|tokens?|hours?|minutes?|budget|cost)\b'))
print('lab vocabulary (claim, puzzle, wave, hypothes, verdict):', hits(r'\b(claim|puzzle|wave|scrupul|pondus|statera|verdict|hypothes)'))
print('quote-replies start with ">":', len([r for r in rows if full.get(r['uuid'], '').lstrip().startswith('>')]), '; contain a quoted line:', len([r for r in rows if re.search(r'(^|\n|/ )> ', full.get(r['uuid'], ''))]))
