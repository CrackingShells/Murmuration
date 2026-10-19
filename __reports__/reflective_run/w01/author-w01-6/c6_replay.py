"""w01-c6 replay: would a human-facing close-message contract have pre-empted any of the 55 research prompts?

usage (full, seconds, no tokens): python3 -I extract_prev.py && python3 -I c6_replay.py > c6_summary.txt   (writes c6_replay.csv)
quick:                            python3 -I c6_replay.py --quick     (only the prompts that react to a PI statement, no transcript pass)
Inputs (read only): ../explorer-w01-d/prompts.csv, prev_pi.json (made by extract_prev.py from the two genesis/design transcripts)

MEASURED: counts of prompts, quote-replies, regex features of the PI message a prompt reacts to, words per message,
          output tokens per displayed word. CONJECTURE: every entry of HAND (one rater: author-w01-6).
Contract elements (E1..E5): E1 open with the user's question in their words; E2 each hypothesis: verdict, label, scope
(what it closes, one thing outside) in one quotable sentence; E3 cost against the budget, in its unit, plus minutes;
E4 what needs the human, with the default; E5 terms glossed on first use.
Pre-emption scale: Y = a contract element is exactly what the human asked for and the reacted-to message lacked it;
P = the element would have made the gap visible, but the human supplied the insight; N = outside what a format can do.
"""
import csv, json, os, re, sys, statistics as st
H = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(H, '..', 'explorer-w01-d')
rows = [r for r in csv.DictReader(open(os.path.join(D, 'prompts.csv'))) if r['channel'] in ('A', 'B') and r['phase'] != 'G-C']
assert len(rows) == 55, len(rows)
sys.path.insert(0, H)
from fulltext import load                       # prompts.csv caps human_text near 420 chars; use the full transcript text (after reproducer-w01-6 Q4)
_full = load(rows)
for _r in rows:
    if _r['uuid'] in _full: _r['human_text'] = _full[_r['uuid']]

# HAND: uuid8 -> (trouble, preempt, element, why).  trouble: LEG legibility, SCO scope, INS human insight or fact, DIR direction/new idea,
# GATE approval or choice, OPS instruction, admin, stop or unblock
HAND = {
 '721d5438': ('OPS', 'N', '', 'initial brief'),
 '29aad9e7': ('OPS', 'N', '', 'git instruction (c7 matter)'),
 '6ee68017': ('OPS', 'N', '', 'plan-shape instruction before any report'),
 '29e87874': ('INS', 'N', '', 'read the framing file and added a dependency of rho on G: domain insight'),
 '24b8031f': ('DIR', 'N', '', 'redirect to enumerate G'),
 '8af30fe6': ('SCO', 'P', 'E2', 'PI said completeness only goes downward; true for single reads (the PI\'s own later admission, KT v1). A scope clause "for single reads, not for concatenations" would have shown the gap; the 5+3 counterexample is the human\'s'),
 'fa7c006d': ('INS', 'N', '', 'naming taste; PI already said "provisional, you have the final say"'),
 'a019d827': ('GATE', 'N', '', 'button'),
 '63f8fb70': ('DIR', 'N', '', 'stop: open problems are edge cases'),
 '9cd91bd9': ('LEG', 'P', 'E1', 'PI headline "Applications: the version that works is QTIP" took an example (LLM weights) for the goal. Opening with the question in the human\'s words ("possible applications") sets the PI\'s reading beside it; the correction might still be needed'),
 '835df5bd': ('DIR', 'N', '', 'new question: in-between versions'),
 'b9d09057': ('GATE', 'N', '', 'go-ahead'),
 '38205ded': ('INS', 'N', '', 'tool knowledge only the human held'),
 'b32ab3d7': ('GATE', 'N', '', 'button'),
 'd10ebf86': ('LEG', 'P', 'E1+E2', 'REVISED after reproducer-w01-6 Q1 (was Y): the human reacted to the findings FILE, which no line of c6-contract.diff regulates. The contract would help only if the chat message announcing a report carried its verdicts, so he need not open the file. The PI answer 1 min later (hypothesis table with Confirmed/Refuted/Not tested) drew no further format complaint'),
 '83e43ba0': ('SCO', 'P', 'E2', 'PI sentence extrapolated from one model family; a scope line "one pair: gemma-2-2b / -it" shows the single family; the PI had flagged "prediction, not measurement" which is part of the contract already'),
 '98cbb48b': ('DIR', 'N', '', 'human tracks uptake of own idea'),
 'bf53476b': ('OPS', 'N', '', 'c7 matter'),
 'fb06ac93': ('DIR', 'N', '', 'next idea after a modest result'),
 '7920d665': ('GATE', 'N', '', 'c7 matter'),
 '939bea68': ('LEG', 'P', 'E5', '"I don\'t understand": explanation used "internal bases", "rotation", "coordinates". Gloss-on-first-use targets exactly that; the PI\'s explanation was also thin on mechanism, which a format does not fix'),
 '3959fc84': ('SCO', 'N', 'E2', 'REVISED after reproducer-w01-6 Q3 (was P): the complaint is that the PI did not try the untried direction; a scope sentence only helps if the PI already knows what to name as outside, and a rule in context failed once (S-w01-explorer-w01-d-1)'),
 '9d8a4417': ('DIR', 'N', '', 'next experiments'),
 '87c07414': ('DIR', 'N', '', 'publication idea'),
 '442c488c': ('OPS', 'N', '', 'c7 matter'),
 'd446c3be': ('GATE', 'N', '', 'button'),
 'c16c48f6': ('DIR', 'N', '', 'stop and resume elsewhere'),
 '3168e671': ('DIR', 'N', '', 'fork for KT report'),
 '8b8533e8': ('INS', 'N', '', 'validator was fixed upstream (stale install); design questions'),
 '87831bbf': ('INS', 'N', '', 'about how a PI should think, not about format'),
 'b3822de3': ('DIR', 'N', '', 'endorsement and reframing'),
 '4efb86a5': ('GATE', 'N', '', 'go-ahead'),
 'e88c56b1': ('GATE', 'N', '', 'button, hold (c7 matter)'),
 'f5966b4c': ('DIR', 'N', '', 'design review comments'),
 '33a2540f': ('GATE', 'N', '', 'button, hold (c7 matter)'),
 '623236e7': ('DIR', 'N', '', 'design review comments'),
 'ae452525': ('GATE', 'N', '', 'button'),
 '5b683d15': ('GATE', 'N', '', 'button, hold'),
 '05f44db5': ('DIR', 'N', '', 'new idea: entropy as hooks'),
 '742ac0ec': ('DIR', 'N', '', 'more hooks'),
 '85f8ec42': ('GATE', 'N', '', 'button, hold'),
 '69ca9e2b': ('DIR', 'N', '', 'all agents Sonnet; first-class repo'),
 'ef016b13': ('GATE', 'N', '', 'button'),
 'f70fd73b': ('GATE', 'N', '', 'button'),
 '4b6b6b36': ('OPS', 'N', '', 'constraint only the human knew (c7 matter)'),
 '201e1cdd': ('OPS', 'N', '', 'login'),
 '038a7abe': ('GATE', 'N', '', 'button, hold'),
 'ad3ad733': ('DIR', 'N', '', 'ask for a new review'),
 '3b472151': ('INS', 'N', '', 'hooks overbuilt; estimates optimistic: a judgement the format does not touch (the cost estimates would carry ESTIMATE and a source, which does not stop the disagreement)'),
 'f5e5a66e': ('OPS', 'N', '', 'no meta-discourse rule'),
 '9b8f9ecb': ('OPS', 'N', '', 'c7 matter'),
 '038667af': ('INS', 'N', '', 'MCP servers per agent'),
 'c93476cc': ('GATE', 'N', '', 'button (c7 matter)'),
 'c3d595a8': ('OPS', 'N', '', 'GUI preference'),
 '355d9ea5': ('DIR', 'N', '', 'unneeded warning from the PI; brief for this run'),
}
assert set(HAND) == {r['uuid'][:8] for r in rows}, set(HAND) ^ {r['uuid'][:8] for r in rows}

from collections import Counter
print('research prompts', len(rows))
print('pre-emption (CONJECTURE)', dict(Counter(v[1] for v in HAND.values())))
print('by trouble x pre-emption', dict(Counter((v[0], v[1]) for v in HAND.values())))
cls = {r['uuid'][:8]: r['cls'] for r in rows}
print('by explorer-w01-d class x pre-emption', dict(Counter((cls[u], v[1]) for u, v in HAND.items())))
print('Y or P prompts:', [u for u, v in HAND.items() if v[1] in ('Y', 'P')])
print('contract element behind them:', dict(Counter(v[2] for v in HAND.values() if v[1] in ('Y', 'P'))))

# what the human reads and quotes (MEASURED)
q_start = [r['uuid'][:8] for r in rows if r['human_text'].lstrip().startswith('>')]
q_any = [r['uuid'][:8] for r in rows if re.search(r'(^|/ )> ', r['human_text'])]
ce = [r['uuid'][:8] for r in rows if r['cls'] == 'CE']
print(f'quote-replies: start with ">" {len(q_start)}; contain a quoted line {len(q_any)}; of {len(ce)} CE prompts, starting with ">" {len([u for u in ce if u in q_start])}, containing {len([u for u in ce if u in q_any])}')
lab = re.compile(r'\b(measured|conjecture|theorem|checked|estimate|cited|supported|overstated|unsupported)\b', re.I)
print('human prompts that use a plugin label or verdict word:', [(r['uuid'][:8], lab.findall(r['human_text'])) for r in rows if lab.search(r['human_text'])], ' (9cd91bd9 uses "cited" as an ordinary verb)')
filew = re.compile(r'reading the|the reports? is|findings|framing|notebook|slide|report', re.I)
print('prompts that mention a file or report they read:', [r['uuid'][:8] for r in rows if filew.search(r['human_text'])])
lw = re.compile(r'\b(claim|puzzle|wave|scrupul|pondus|statera|verdict|hypothes)', re.I)
print('prompts that mention lab-file vocabulary (claim, puzzle, wave, hypothesis, verdict):', [(r['uuid'][:8], lw.findall(r['human_text'])) for r in rows if lw.search(r['human_text'])])
unit = re.compile(r'\b(usd|tokens?|hours?|minutes?|budget|cost)\b', re.I)
print('prompts that name a cost unit (usd, token, hour, minute, budget, cost):', [(r['uuid'][:8], [m.lower() for m in unit.findall(r['human_text'])]) for r in rows if unit.search(r['human_text'])])

if '--quick' in sys.argv: sys.exit()

# regex features of the PI message each CE/RC prompt reacts to (MEASURED, crude)
prev = {x['uuid']: x for x in json.load(open(os.path.join(H, 'prev_pi.json')))}
norm = lambda s: re.sub(r'[\s’‘“”*`]+', ' ', s).strip().lower()
F = dict(verdict=r'\b(confirmed|refuted|not tested|supported|verdict)\b', label=r'\b(measured|conjecture|theorem|estimate|cited)\b',
         scope=r"\b(only|does not|doesn't|not re-?verified|outside|caveat|limit|prediction|unverified|provisional)\b",
         cost=r'(usd|\$\d|tokens|minutes|hours)', needs=r'(your call|you decide|do you want|would you like|approve|tell me|let me know|if useful|if you)',
         question=r'(your (question|idea|three questions)|you asked|what you)')
print()
print('reacted-to PI message: words and contract-like features (MEASURED, regex)')
wc = []
for u in HAND:
    r = prev.get(u)
    if not r or cls[u] not in ('CE', 'RC'): continue
    # the quoted sentence picks the host message; else the last text block
    t = r['human'].lstrip()
    host = None
    if t.startswith('>') or ' / > ' in t:
        q = norm(t.split('>', 1)[1].split(' / ')[0])[:40]
        host = next((x for x in reversed(r['prev_text']) if q and q in norm(x['text'])), None)
    host = host or (r['prev_text'][-1] if r['prev_text'] else None)
    if not host: continue
    w = len(host['text'].split()); wc.append(w)
    feats = [k for k, p in F.items() if re.search(p, host['text'], re.I)]
    print(f"  {u} {cls[u]} {HAND[u][1]} words {w:4d} features {feats}")
print('median words of the reacted-to messages', st.median(wc), 'n', len(wc))

# output tokens per displayed word for text-only assistant messages of at least 80 words (MEASURED; hidden reasoning could inflate)
P = os.path.expanduser('~/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/')
rat = []
for f in ('566fa912-7009-421a-9d79-11145e2b8db9.jsonl', '82e8a947-1a0c-441c-bc39-df8e2e5fa743.jsonl'):
    by = {}
    for l in open(P + f):
        d = json.loads(l)
        if d.get('type') != 'assistant' or d.get('isSidechain'): continue
        by.setdefault(d['message'].get('id'), []).append((d['message']['content'], d['message'].get('usage', {})))
    for mid, v in by.items():
        if {b.get('type') for c, u in v for b in c} == {'text'}:
            w = sum(len(b['text'].split()) for c, u in v for b in c); o = max(u.get('output_tokens', 0) for c, u in v)
            if w >= 80 and o > 0: rat.append(o / w)
rat.sort()
print(f'output tokens per displayed word, text-only PI messages >= 80 words: n={len(rat)} median {rat[len(rat)//2]:.2f} p10 {rat[len(rat)//10]:.2f} p90 {rat[9*len(rat)//10]:.2f}')
print('model of a close message: 30 words (question) + 40 per claim + 15 (cost) + 30 (needs you); for the 7 claims of this wave:', 30 + 7 * 40 + 15 + 30, 'words')

w = csv.writer(open(os.path.join(H, 'c6_replay.csv'), 'w', newline=''))
w.writerow(['uuid8', 'ts', 'class_d', 'who_d', 'trouble', 'preempt', 'element', 'why'])
for r in rows:
    u = r['uuid'][:8]; w.writerow([u, r['ts_utc'][:19], r['cls'], r['who'], *HAND[u]])
