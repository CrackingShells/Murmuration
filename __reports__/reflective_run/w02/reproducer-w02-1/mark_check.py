# reproducer-w02-1: own check of the "+" marking. Expected: group assistant records by requestId
# (message.id if none), take the last record of each group; marked iff any last record has no stop_reason.
# Actual: the shipped CLI is run on a temp CLAUDE_CONFIG_DIR holding that one file as the only subagent of a stub session.
import json, os, sys, glob, random, subprocess, tempfile, shutil, re
random.seed(20261019)
SCRIPT = sys.argv[1]
files = sorted(glob.glob(os.path.expanduser('~/.claude/projects/*/*/subagents/**/agent-*.jsonl'), recursive=True))
def expected(path):
    last = {}
    sid = None; cwd = None; n = 0
    for l in open(path, errors='replace'):
        try: d = json.loads(l)
        except ValueError: continue
        sid = sid or d.get('sessionId'); cwd = cwd or d.get('cwd')
        m = d.get('message')
        if d.get('type') == 'assistant' and isinstance(m, dict) and isinstance(m.get('usage'), dict) and m.get('model') != '<synthetic>':
            last[d.get('requestId') or m.get('id')] = bool(m.get('stop_reason')); n += 1
    return (any(not v for v in last.values()) if last else None), sid, cwd, n
info = {}
for f in files:
    if 'combinatorics' in f or 'murmuration' in f.lower() or True:
        info[f] = expected(f)
pool = [f for f, v in info.items() if v[0] is not None and v[1] and v[2]]
marked = [f for f in pool if info[f][0]]; unmarked = [f for f in pool if not info[f][0]]
print('subagent files', len(files), 'usable', len(pool), 'expected marked', len(marked), 'unmarked', len(unmarked))
sample = random.sample(marked, 8) + random.sample(unmarked, 8)
bad = 0
for f in sample:
    exp, sid, cwd, n = info[f]
    cfg = tempfile.mkdtemp(dir=os.environ['TMPDIR_R'])
    proj = os.path.join(cfg, 'projects', re.sub(r'[^A-Za-z0-9]', '-', cwd)); os.makedirs(os.path.join(proj, sid, 'subagents'))
    open(os.path.join(proj, sid + '.jsonl'), 'w').write(json.dumps({'type': 'user', 'cwd': cwd, 'sessionId': sid}) + '\n')
    shutil.copy(f, os.path.join(proj, sid, 'subagents', 'agent-x.jsonl'))
    env = dict(os.environ, CLAUDE_CONFIG_DIR=cfg)
    out = subprocess.run([sys.executable, '-I', SCRIPT, '--spend', '--project', cwd], capture_output=True, text=True, env=env).stdout
    rows = [l for l in out.splitlines() if re.search(r'\s\d+\s+\d+\.\d\d\+?\s', l) and 'main thread' not in l and ('sonnet' in l or 'opus' in l or 'haiku' in l or 'fable' in l)]
    act = any('+' in l for l in rows)
    ok = act == exp; bad += (not ok)
    print('%-8s expected=%-5s actual=%-5s msgs=%d %s' % ('OK' if ok else 'MISMATCH', exp, act, n, os.path.basename(f)))
    shutil.rmtree(cfg)
print('mismatches', bad, 'of', len(sample))
