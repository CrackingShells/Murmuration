# reproducer-w02-1: own re-derivation. Per (session, model) cell: USD from transcripts (own price table, own dedupe)
# against the session's cost-state modelUsage costUSD. Combinatorics: sum of cost-state totals.
import json, os, glob, random, re, collections
random.seed(7)
P = {"claude-opus-5-5": (4, 20, .2, 5, 8), "claude-sonnet-5-5": (2, 10, .1, 2.5, 4), "claude-fable-5-1": (10, 50, .25, 12.5, 20), "claude-haiku-5-5": (.1, .5, .01, .125, .2)}
def usd(model, u):
    p = P[model]; c = u.get('cache_creation') or {}
    w1 = c.get('ephemeral_1h_input_tokens') or 0; w5 = c.get('ephemeral_5m_input_tokens') or 0
    w = u.get('cache_creation_input_tokens') or 0; w5 += max(0, w - w1 - w5)
    i, o, r = u.get('input_tokens') or 0, u.get('output_tokens') or 0, u.get('cache_read_input_tokens') or 0
    if model == 'claude-haiku-5-5' and i + r + w > 100000: p = (.5, 2.5, .05, .625, 1)
    x = (i*p[0] + o*p[1] + r*p[2] + w5*p[3] + w1*p[4]) / 1e6
    if u.get('speed') == 'fast': x *= 2
    return x + .01 * ((u.get('server_tool_use') or {}).get('web_search_requests') or 0)
def read(path):
    msgs = {}; cs = None
    for l in open(path, errors='replace'):
        if '"assistant"' not in l and '"cost-state"' not in l: continue
        try: d = json.loads(l)
        except ValueError: continue
        if d.get('type') == 'cost-state': cs = d
        elif d.get('type') == 'assistant' and isinstance(d.get('message'), dict) and isinstance(d['message'].get('usage'), dict) and d['message'].get('model') != '<synthetic>':
            m = d['message']; k = m.get('id') or d.get('requestId')
            e = msgs.setdefault(k, {'model': m['model'], 'u': {}, 'sid': d.get('sessionId')})
            for f in ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'):
                e['u'][f] = max(e['u'].get(f, 0), m['usage'].get(f) or 0)
            if isinstance(m['usage'].get('cache_creation'), dict): e['u']['cache_creation'] = m['usage']['cache_creation']
            e['last_final'] = bool(m.get('stop_reason'))
    return msgs, cs
base = os.path.expanduser('~/.claude/projects')
# combinatorics
tot = 0
for f in glob.glob(base + '/-Users-hacker-Documents-explore-combinatorics-on-binary/*.jsonl'):
    tot += read(f)[1]['totalCostUSD']
print('combinatorics sum of cost-state totalCostUSD = %.4f' % tot)
# cells: this lab family, ended sessions
mains = sorted(glob.glob(base + '/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-*/*.jsonl') + glob.glob(base + '/-Users-hacker-Documents-src-CrackingShells-Murmuration*/*.jsonl'))
random.shuffle(mains)
cells = []; seen = set()
for f in mains:
    sid = os.path.basename(f)[:-6]
    msgs, cs = read(f)
    if not cs: continue
    sub = collections.defaultdict(dict)
    for g in glob.glob(f[:-6] + '/subagents/**/agent-*.jsonl', recursive=True):
        for k, m in read(g)[0].items(): sub[k] = m if k not in sub else sub[k]
    own = {}
    for k, m in list(msgs.items()):
        if m['sid'] == sid: own[k] = dict(m, sub=False)
    for k, m in sub.items():
        if m['sid'] == sid and k not in own: own[k] = dict(m, sub=True)
        elif m['sid'] == sid and k in own and not m['last_final']: pass
    by = collections.defaultdict(lambda: [0.0, False])
    for k, m in own.items():
        by[m['model']][0] += usd(m['model'], m['u'])
        by[m['model']][1] |= (m['sub'] and not m['last_final'])
    for model, mu in cs['modelUsage'].items():
        if mu['costUSD'] > .0005 and model in by:
            cells.append((sid[:8], model, by[model][0], mu['costUSD'], by[model][1]))
    if len(cells) >= 60: break
n_ok = n_unm_bad = n_mark = n_mark_above = 0
for sid, model, t, c, lo in cells:
    r = t / c
    if lo:
        n_mark += 1; n_mark_above += (r > 1.0005)
    elif abs(r - 1) <= .0005: n_ok += 1
    else: n_unm_bad += 1; print('unmarked off:', sid, model, '%.4f vs %.4f ratio %.4f' % (t, c, r))
print('sampled cells', len(cells), 'unmarked & within 0.05%%: %d, unmarked off: %d, marked: %d (above cost-state: %d)' % (n_ok, n_unm_bad, n_mark, n_mark_above))
