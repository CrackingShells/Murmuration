import json, os, sys, importlib.util, tempfile, collections
HERE = os.path.dirname(os.path.abspath(__file__))
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
sys.path.insert(0, os.path.join(HERE, 'scratch', 'scripts_orig'))
old = load('uw_old', os.path.join(HERE, 'scratch', 'scripts_orig', 'user_words.py'))
sys.path.insert(0, os.path.join(HERE, 'scratch', 'repo', 'scripts'))
new = load('uw_new', os.path.join(HERE, 'scratch', 'repo', 'scripts', 'user_words.py'))
P = os.path.expanduser('~/.claude/projects/')
FILES = {
 '566fa912': P+'-Users-hacker-Documents-explore-combinatorics-on-binary/566fa912-7009-421a-9d79-11145e2b8db9.jsonl',
 '82e8a947': P+'-Users-hacker-Documents-explore-combinatorics-on-binary/82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl',
 '3ccc590f': P+'-Users-hacker-Documents-explore-combinatorics-on-binary/3ccc590f-0187-4f79-b7af-4955944f1374.jsonl',
 '2947f9dc': P+'-Users-hacker-Documents-explore-combinatorics-on-binary/2947f9dc-1c3a-452b-97a5-39d4510a1271.jsonl',
 'ab96c5ed': P+'-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl',
}
def text_of(c):
    if isinstance(c, str): return c
    parts = [b.get('text','') for b in c if b.get('type') == 'text']
    return '\n'.join(parts)
def events(path, dedupe_seen):
    for ln, l in enumerate(open(path), 1):
        d = json.loads(l)
        t = d.get('type')
        if t == 'user' and not d.get('isSidechain') and not d.get('isMeta'):
            c = d['message']['content']
            if isinstance(c, list) and any(b.get('type') == 'tool_result' for b in c): continue
            if not isinstance(c, str) and not any(b.get('type')=='text' for b in c): continue
            key = ('u', d.get('uuid'))
            kind = 'typed' if (d.get('origin') or {}).get('kind') == 'human' else 'other'
            yield ln, kind, 'user', key, text_of(c)
        elif t == 'attachment' and d['attachment'].get('type') == 'queued_command':
            a = d['attachment']
            p = a.get('prompt')
            if isinstance(p, list): p = text_of(p)
            if not isinstance(p, str): continue
            key = ('q', a.get('delivery_id') or a.get('source_uuid'))
            kind = 'typed' if (a.get('origin') or {}).get('kind') == 'human' else 'other'
            yield ln, kind, 'queued', key, p
def run(handle_mod, label, ev):
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, '__statera__'))
        os.environ.pop('CLAUDE_PROJECT_DIR', None)
        f = os.path.join(tmp, '__statera__', 'user_words.md')
        r = handle_mod.handle({'prompt': ev, 'cwd': tmp})
        if not r: return None
        s = open(f, encoding='utf-8').read()
        return s.split('\n', 5)[-1] if False else s[s.index('\n## ')+len('\n## YYYY-MM-DD HH:MM\n\n'):]
if __name__ == '__main__':
    dedupe = '--nodedupe' not in sys.argv
    seen = set(); tot = collections.Counter(); rows = []
    for sid, path in FILES.items():
        c = collections.Counter()
        for ln, kind, src, key, prompt in events(path, seen):
            if dedupe:
                if key in seen: c['dup']+=1; continue
                seen.add(key)
            a = run(old, 'old', prompt); b = run(new, 'new', prompt)
            c[(kind,'fired')] += 1
            c[(kind,'old_stores')] += a is not None
            c[(kind,'new_stores')] += b is not None
            c[(kind,'differ')] += (a != b)
            if kind == 'typed' and a is not None and b is None: c['TYPED_DROPPED'] += 1; print('DROPPED', sid, ln, repr(prompt[:150]))
            if kind=='typed' and a is not None and b is not None and a != b:
                # check new is a suffix-ish: removed only platform text
                if b.strip() not in a: c['typed_new_not_substring_of_old'] += 1; print('NOTSUB', sid, ln, repr(a[:100]), repr(b[:100]))
            rows.append((sid, ln, kind, src, len(a or ''), len(b or '')))
            if a is not None: c[(kind,'chars_old')] += len(a)
            if b is not None: c[(kind,'chars_new')] += len(b)
        print(sid, dict(c)); tot.update(c)
    print('TOTAL', {k: v for k, v in sorted(tot.items(), key=str)})
