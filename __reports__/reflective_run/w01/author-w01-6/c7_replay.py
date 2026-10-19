"""w01-c7 replay: the 19 asks and the 6 S-class prompts against the user's words available at the moment of each ask.

usage (full, seconds, no tokens):  python3 -I c7_replay.py > c7_summary.txt     (writes c7_asks_replay.csv, c7_s_prompts.csv)
quick:                              python3 -I c7_replay.py --quick               (first 6 asks only)
Inputs (read only): ../explorer-w01-d/prompts.csv, ../explorer-w01-d/asks.csv

Columns computed by code are MEASURED: outcome (default / declined / typed from the verbatim_click field), latency,
away (latency >= 120 min), prompts between the settling prompt and the ask, keyword overlap.
Columns typed below by hand (HAND dict) are CONJECTURE: verdict, settling prompt, reason. One rater (author-w01-6).
Why Python: small CSV joins and set arithmetic; nothing here needs a CAS.
"""
import csv, os, re, sys
from datetime import datetime

H = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(H, '..', 'explorer-w01-d')
prompts = list(csv.DictReader(open(os.path.join(D, 'prompts.csv'))))
sys.path.insert(0, H)
from fulltext import load
_full = load(prompts)                       # prompts.csv caps human_text near 420 chars: use the transcripts' full text (revision after reproducer-w01-7 Q1)
_cut = 0
for p in prompts:
    t = _full.get(p['uuid'])
    if t and len(t) > len(p['human_text']) + 5: _cut += 1
    if t: p['human_text'] = t
print('prompts whose csv text was shorter than the transcript text:', _cut, 'of', len(prompts))
asks = list(csv.DictReader(open(os.path.join(D, 'asks.csv'))))
genuine = sorted([p for p in prompts if p['channel'] in ('A', 'B')], key=lambda p: p['ts_utc'])
byid = {p['uuid'][:8]: p for p in prompts}

# HAND (CONJECTURE): index -> (answer prompt, verdict, settling prompt or '', reason)
# verdicts: REMOVE = the PI would not have asked; SHORTEN = ask stays but the round trip or idle time shrinks;
#           AT_RISK = looks removable by the habit but the human's answer carried something only the human knew,
#                     or the action is outside the project; KEEP = the human's to decide, habit changes nothing
HAND = {
 0: ('a019d827', 'KEEP', '', 'naming is taste. Near miss for keyword search: option "Try Greek" overlaps the 04:10 words "Greek root or Latin", which asked for a process, not a choice'),
 1: ('b32ab3d7', 'REMOVE', '', 'repo-local reversible git config: not the human\'s to decide (by "ask only what only the human decides"); no settling prompt found'),
 2: ('bf53476b', 'AT_RISK', '', 'REVISED (reproducer-w01-7 Q3; was REMOVE): the PI had already looked on disk (HF cache) before asking; the LM Studio folder was knowledge only the human had, and the default (download) was declined; a PI that took the default would have started a 2.5 GB download the human then redirected'),
 3: ('442c488c', 'KEEP', '', 'REVISED (reproducer-w01-7 Q5; was SHORTEN): publication ambition is the human\'s; nothing shows the PI would have read the prior art unasked (it had already verified the counsel\'s citations; the human\'s move was a specific skill call)'),
 4: ('d446c3be', 'KEEP', '', 'evidence bar for proposing externally; human declined the default'),
 5: ('6ffdb47e', 'KEEP', '', 'REVISED (reproducer-w01-7 Q4; was AT_RISK): a write into the human\'s own scheduler is covered by the first paragraph of the proposed text (schedules wait for a yes), so under the diff it is still asked; AT_RISK would apply only to the habit without that paragraph. explorer-w01-d classed it R'),
 6: ('dd1a26b0', 'KEEP', '', 'writes estimates of the human\'s own time'),
 7: ('e88c56b1', 'KEEP', '', 'design gate; human declined the default (Build it)'),
 8: ('33a2540f', 'KEEP', '', 'design gate; human declined the default; first "More revisions", not predictable from earlier words'),
 9: ('ae452525', 'KEEP', '', 'naming set; default accepted'),
 10: ('5b683d15', 'SHORTEN', '33a2540f', 'same gate type declined twice before (v1 "More revisions", first "Revise design first"); an open "what to change, or say go" replaces click then question'),
 11: ('85f8ec42', 'SHORTEN', '5b683d15', 'same as above, third decline in a row'),
 12: ('ef016b13', 'KEEP', '', 'repository name; default accepted'),
 13: ('f70fd73b', 'SHORTEN', '69ca9e2b', 'REVISED (reproducer-w01-7 Q2; was REMOVE): the ask bundles creating the repo (authorised by 08:48 "make this MAS a first-class repo") with opening the roadmap from v4, a gate the human declined at v1, v2, v3. Accepted this time, but a hindsight removal; shortened into an open "anything to change in v4 first, else I create the repo and open the roadmap"'),
 14: ('4b6b6b36', 'AT_RISK', '', 'typed answer added a constraint only the human knew (other sessions are running in this repo; use the worktree tools); starting by default would have ignored it'),
 15: ('201e1cdd', 'KEEP', '', 'only the human could log in (blocked: true)'),
 16: ('038a7abe', 'SHORTEN', '85f8ec42', 'fourth gate of the same type after three declines'),
 17: ('c93476cc', 'REMOVE', '3b472151', '15:35 "once we have v1, I plan to run the agent system on itself"; default accepted; found only by reading, not by keyword'),
 18: ('c3d595a8', 'KEEP', '', 'GUI or terminal is the human\'s environment'),
}

STOP = set('the and for that this with from have will your you are not but what which should them then when about into each does their they than more also only such after before first make made over under same most just like need needs there here'.split())
def terms(s): return {w for w in re.findall(r'[a-zA-Z]{4,}', s.lower()) if w not in STOP}
def ts(s): return datetime.fromisoformat(s.replace('Z', '+00:00'))
def minutes(a, b): return (ts(b) - ts(a)).total_seconds() / 60

quick = '--quick' in sys.argv
rows = []
for i, a in enumerate(asks):
    if quick and i >= 6: break
    ans, verdict, settle, why = HAND[i]
    options = [o.strip() for o in a['options'].split('|')]
    p = byid[ans]
    vc = p['verbatim_click']
    if vc.startswith('yes:'):
        lab = vc[4:].strip().lower()
        idx = next((k for k, o in enumerate(options) if o.lower().startswith(lab[:12]) or lab.startswith(o.lower()[:12])), None)
        outcome = 'default' if idx == 0 else ('declined' if idx else 'typed')
    else:
        outcome = 'typed'
    lat = float(a['latency_to_next_human_prompt_min'])
    at = a['wrap_up_ts_utc']
    prior = [q for q in genuine if q['ts_utc'] < at]
    A = terms(a['ask'] + ' ' + a['options'])
    scored = sorted(((len(A & terms(q['human_text'])) / max(1, len(A)), q['uuid'][:8]) for q in prior), reverse=True)
    best = scored[0] if scored else (0, '')
    sscore = next((s for s, u in scored if u == settle[:8]), '') if settle else ''
    # tie-aware rank: 1 + number of prompts with a strictly higher overlap; ties = other prompts with the same overlap
    srank = (1 + sum(1 for s, _ in scored if s > sscore)) if settle else ''
    sties = (sum(1 for s, _ in scored if s == sscore) - 1) if settle else ''
    between = minutes_between = ''
    if settle:
        sp = byid[settle]
        between = sum(1 for q in genuine if sp['ts_utc'] < q['ts_utc'] < at)
        minutes_between = round(minutes(sp['ts_utc'], at), 1)
    rows.append(dict(i=i, ask_ts=at[:19], ask=a['ask'], options=a['options'], d_class=a['judgement_class'], answer=ans, outcome=outcome,
                     latency_min=lat, away=lat >= 120, verdict=verdict, settling=settle, prompts_between=between, minutes_between=minutes_between,
                     top_overlap=round(best[0], 2), top_uuid=best[1], settle_overlap=sscore if sscore == '' else round(sscore, 2), settle_rank=srank, settle_ties=sties, why=why))

w = csv.DictWriter(open(os.path.join(H, 'c7_asks_replay.csv' if not quick else 'c7_asks_replay_quick.csv'), 'w', newline=''), fieldnames=list(rows[0].keys()))
w.writeheader(); w.writerows(rows)

from collections import Counter
print('asks replayed', len(rows))
print('verdicts (CONJECTURE)', dict(Counter(r['verdict'] for r in rows)))
print('outcomes (MEASURED)  ', dict(Counter(r['outcome'] for r in rows)))
print('verdict x outcome    ', dict(Counter((r['verdict'], r['outcome']) for r in rows)))
print('explorer-w01-d class vs my verdict', dict(Counter((r['d_class'], r['verdict']) for r in rows)))
for v in ('REMOVE', 'SHORTEN', 'AT_RISK', 'KEEP'):
    sel = [r for r in rows if r['verdict'] == v]
    pres = sum(r['latency_min'] for r in sel if not r['away'])
    away = sum(r['latency_min'] for r in sel if r['away'])
    print(f'{v:8s} n={len(sel):2d}  idle-minutes human present={pres:6.1f}  human away={away:6.1f}')
print()
print('keyword search as the finder (MEASURED): settling prompt rank among all prior prompts, by word overlap with the ask')
for r in rows:
    if r['settling']:
        print(f"  ask {r['i']:2d} settle {r['settling']} rank {r['settle_rank']} (+{r['settle_ties']} tied) of {sum(1 for q in genuine if q['ts_utc'] < r['ask_ts'])}  overlap {r['settle_overlap']}  best {r['top_uuid']} {r['top_overlap']}  prompts between {r['prompts_between']}  minutes between {r['minutes_between']}")
print('keyword search false-positive pressure (MEASURED): highest overlap with ANY prior prompt for asks the habit must not suppress (KEEP/AT_RISK)')
for r in rows:
    if r['verdict'] in ('KEEP', 'AT_RISK'):
        print(f"  ask {r['i']:2d} {r['verdict']:7s} best overlap {r['top_overlap']} with {r['top_uuid']}   {r['ask'][:60]}")

# the six S-class prompts (explorer-w01-d classes.csv who == S)
S = {
 'bf53476b': ('N', 'REVISED (was Y): the PI had already searched the disk; the LM Studio location was the human\'s knowledge; the habit does not find it'),
 '442c488c': ('N', 'REVISED (was cond): nothing shows the PI would have read the prior art unasked; the human\'s move was a specific skill call'),
 '9b8f9ecb': ('cond', 'a rule stated once goes into the framing; needs the 03:22 "use writing-history, commit as you go" rule to have been written and the plan overview to be checked against it'),
 '29aad9e7': ('N', 'first statement of the rule; nothing earlier to find. A `git status` at session start would find "not initialised" but that is not the asking habit'),
 '6ee68017': ('N', 'first statement; the shipped waves.md already says "plan only the current wave"; not an asking matter'),
 '7920d665': ('cond', 'answers a second plain-text ask about the same download; under the habit the PI would take the default (a download into data/raw is reversible); conditional because ask 2 itself is now AT_RISK'),
}
print()
print('S-class prompts (CONJECTURE verdicts)')
sw = csv.writer(open(os.path.join(H, 'c7_s_prompts.csv'), 'w', newline=''))
sw.writerow(['uuid8', 'ts', 'chars', 'habit_removes', 'why'])
for u, (v, why) in S.items():
    p = byid[u]; print(f"  {u} {p['ts_utc'][5:16]} {len(p['human_text']):4d} chars  {v:4s} {why}")
    sw.writerow([u, p['ts_utc'], len(p['human_text']), v, why])
research = [p for p in prompts if p['channel'] in ('A', 'B') and p['phase'] != 'G-C']
assert len(research) == 55
ids = {p['uuid'][:8] for p in research}
removed = ({r['answer'] for r in rows if r['verdict'] == 'REMOVE'} | {u for u, (v, _) in S.items() if v == 'Y'}) & ids
cond = {u for u, (v, _) in S.items() if v == 'cond'} & ids
short = ({r['answer'] for r in rows if r['verdict'] == 'SHORTEN'} - removed - cond) & ids
risk = {r['answer'] for r in rows if r['verdict'] == 'AT_RISK'} & ids   # ask 5's answer (6ffdb47e) is scheduler bookkeeping, outside the 55
print('(asks 5 and 6 are answered by scheduler-bookkeeping prompts of phase G-C, outside the 55)')
print()
print(f'research prompts {len(research)}; habit would remove {len(removed)} ({sorted(removed)}), plausibly {len(cond)} more ({sorted(cond)}); shorten {len(short)}; at risk {len(risk)}')
print(f'removed share {len(removed)}/{len(research)} = {len(removed)/len(research):.1%}; with conditional {len(removed|cond)}/{len(research)} = {len(removed|cond)/len(research):.1%}')
chars = sum(len(p['human_text']) for p in research); words = sum(len(p['human_text'].split()) for p in research)
print(f'reading the whole user-words file at the end of the genesis+design sessions: {len(research)} prompts, {chars} chars, {words} words')
