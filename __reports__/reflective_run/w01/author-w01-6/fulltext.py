"""Full human text for every prompt of explorer-w01-d/prompts.csv (that file caps human_text near 420 characters).
Import: from fulltext import load; full = load(prompts_rows) -> {uuid: text}. Read-only on the two transcripts."""
import json, os
P = os.path.expanduser('~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/')
def _strings(x):
    if isinstance(x, str): yield x
    elif isinstance(x, list):
        for y in x: yield from _strings(y)
    elif isinstance(x, dict):
        if x.get('type') == 'text' and 'text' in x: yield x['text']
        else:
            for k in ('prompt', 'content', 'text', 'message'):
                if k in x: yield from _strings(x[k])
def load(rows):
    want = {r['uuid'] for r in rows}; full = {}
    for f in ('566fa912-7009-421a-9d79-11145e2b8db9.jsonl', '82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl'):
        for l in open(P + f):
            d = json.loads(l); u = d.get('uuid')
            if u in want and u not in full:
                body = d.get('message') if d.get('type') == 'user' else d.get('attachment')
                full[u] = '\n'.join(s for s in _strings(body) if not s.lstrip().startswith('<system-reminder>'))
    return full
