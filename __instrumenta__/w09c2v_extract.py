# Cuts PI main-thread transcripts (.jsonl, read only) into wake turns led by a peer hand-back and writes one JSON line per turn (sender, role, body head, tool calls, assistant text, opened-artifact flags by my own rule R2) to <outdir>/wakes.jsonl; prints raw-open counts by wave and sender role, and the ESCALATE-by-reproducer table; usage: python3 -I w09c2v_extract.py <outdir> <files.txt with label=path lines>
# Written independently of w09d_turns.py (not imported). Rules, stated before counting:
#  R1 wake: a user record with origin.kind=="peer" and origin.body starting "[Subagent hand-back]", plus every later record up to the next user record that is not only tool_result blocks. Counted only if the turn holds >=1 assistant record. Role = origin.name with an optional "murmuration:" prefix, first word explorer/author/reproducer, else other.
#  R2 raw open of the returning worker's artifact: in the turn, an assistant tool_use that is Read (file_path) or a Bash command whose first word (after cd/&&/;/|) is one of cat head tail sed nl less grep egrep rg jq awk wc ls diff stat python3 (git, lab_status, colgrep excluded, redirect targets excluded) and that names a path P where either
#     (i) P contains the sender's agent name (e.g. author-w05-2), or
#     (ii) P's basename (>=6 chars, has an extension) occurs in the hand-back body, or
#     (iii) P is __pondus__/<id>.md and <id> (wNN-cK) occurs in the first 600 chars of the hand-back body.
#   "strict" = Read or cat/head/tail/sed/nl/less only (no grep/jq/awk/python3/ls/wc/stat/diff).
import json, sys, re, os, collections

VIEW = {'cat','head','tail','sed','nl','less'}
QUERY = {'grep','egrep','rg','jq','awk','wc','ls','diff','stat','python3','python','find','du'}
PATH_RE = re.compile(r'(?:/|\.\.?/|__[a-z]+__/|~/)[^\s"\'`;|&<>()]*|[A-Za-z0-9_\-]+\.(?:md|py|tsv|json|jsonl|txt|csv|sh)\b')

def role_of(name):
    n = (name or '').replace('murmuration:', '')
    for r in ('explorer', 'author', 'reproducer'):
        if n.startswith(r): return r
    return 'other'

def segs(cmd):
    # v1 (after the first run mis-split awk programs and read heredoc bodies as commands): drop heredoc bodies, split on ; & | newline only outside quotes
    cmd = re.sub(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\b", "", cmd, flags=re.S)
    out = []; cur = []; q = None
    for ch in cmd:
        if q:
            cur.append(ch)
            if ch == q: q = None
        elif ch in "'\"":
            q = ch; cur.append(ch)
        elif ch in ';&|\n':
            out.append(''.join(cur)); cur = []
        else: cur.append(ch)
    out.append(''.join(cur))
    return [x.strip() for x in out if x.strip()]

def opened_paths(tu):
    """yield (path, kind) pairs for view/query reads in a tool_use; kind in view|query"""
    nm = tu['name']; inp = tu['input']
    out = []
    if nm == 'Read':
        out.append((inp.get('file_path', ''), 'view'))
    elif nm == 'Bash':
        cmd = inp.get('command', '')
        for s in segs(cmd):
            w = s.split()
            if not w: continue
            first = w[0]
            while first in ('cd', 'export') and False: pass
            if first in VIEW or first in QUERY:
                kind = 'view' if first in VIEW else 'query'
                # drop redirect targets
                s2 = re.sub(r'\d?>>?\s*\S+', '', s)
                for p in PATH_RE.findall(s2):
                    out.append((p, kind))
    return out

def analyse(lab, path):
    L = []
    for l in open(path):
        try: L.append(json.loads(l))
        except Exception: pass
    wakes = []
    i = 0; n = len(L)
    while i < n:
        d = L[i]; o = d.get('origin')
        if d.get('type') == 'user' and isinstance(o, dict) and o.get('kind') == 'peer' and (o.get('body') or '').startswith('[Subagent hand-back]'):
            body = o['body']; sender = o.get('name') or ''
            j = i + 1; recs = []
            while j < n:
                e = L[j]
                if e.get('type') == 'user':
                    c = e['message']['content']
                    if isinstance(c, list) and c and all(b.get('type') == 'tool_result' for b in c):
                        j += 1; continue
                    break
                if e.get('type') == 'assistant': recs.append(e)
                j += 1
            tus = []; texts = []
            for e in recs:
                for b in e['message'].get('content', []):
                    if b.get('type') == 'tool_use': tus.append(b)
                    elif b.get('type') == 'text' and b['text'].strip(): texts.append(b['text'])
            wakes.append(dict(lab=lab, idx=i, ts=d.get('timestamp'), sender=sender, role=role_of(sender), body=body,
                              n_asst=len(recs), tus=[{'name': t['name'], 'input': t['input']} for t in tus], texts=texts, end=j))
            i = j
        else:
            i += 1
    return wakes

def code(w):
    body = w['body']; sender = w['sender']
    body_files = set(re.findall(r'[A-Za-z0-9_\-]+\.(?:md|py|tsv|json|jsonl|txt|csv|sh)\b', body))
    ids = set(re.findall(r'w\d\d-c\d+', body[:600]))
    hits = []
    for t in w['tus']:
        for p, kind in opened_paths(t):
            base = os.path.basename(p.rstrip('/'))
            why = None
            if sender and sender in p and not sender.startswith('murmuration:'): why = 'i'
            elif len(base) >= 6 and '.' in base and base in body_files: why = 'ii'
            else:
                m = re.search(r'__pondus__/(w\d\d-c\d+)\.md', p)
                if m and m.group(1) in ids: why = 'iii'
            if why: hits.append((p, kind, why, t['name']))
    w['hits'] = hits
    w['open'] = bool(hits)
    w['open_strict'] = any(k == 'view' for _, k, _, _ in hits)

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    allw = []
    for line in open(sys.argv[2]):
        if '=' not in line: continue
        lab, p = line.strip().split('=', 1)
        ws = analyse(lab, p)
        for w in ws: code(w)
        allw += ws
    with open(os.path.join(out, 'wakes.jsonl'), 'w') as f:
        for w in allw: f.write(json.dumps(w) + '\n')
    wake = [w for w in allw if w['n_asst'] >= 1]
    print('hand-back wakes total', len(allw), 'with >=1 assistant record', len(wake))
    by = collections.defaultdict(lambda: [0, 0, 0])
    for w in wake:
        wv = w['lab']
        for key in ((wv, w['role']), (wv, 'ALL')):
            by[key][0] += 1; by[key][1] += w['open']; by[key][2] += w['open_strict']
    for k in sorted(by): print(k, 'open %d/%d strict %d' % (by[k][1], by[k][0], by[k][2]))
    tot = collections.defaultdict(lambda: [0, 0, 0])
    for w in wake:
        if w['lab'] in ('w5', 'w6', 'w7', 'w8'):
            for key in (w['role'], 'ALL'):
                tot[key][0] += 1; tot[key][1] += w['open']; tot[key][2] += w['open_strict']
    print('WAVES 5-8')
    for k in sorted(tot): print(k, 'open %d/%d strict %d' % (tot[k][1], tot[k][0], tot[k][2]))
