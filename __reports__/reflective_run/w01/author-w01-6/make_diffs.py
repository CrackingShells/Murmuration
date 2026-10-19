"""Build the proposed diffs for w01-c6 and w01-c7 from the files in the worktree, without touching them.
usage: python3 -I make_diffs.py     (seconds, no tokens)  -> c6-contract.diff, c6-optional-lab-status.diff, c7-asking-habit.diff, diff_cost.txt
Each diff is checked with `git apply --check` against the worktree; nothing is applied.
"""
import os, subprocess, difflib, re
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '..', '..', '..', '..'))
def rd(p): return open(os.path.join(ROOT, p)).read()

def sub(text, old, new):
    assert text.count(old) == 1, (old[:50], text.count(old))
    return text.replace(old, new)

CHANGES = {}   # diff name -> {path: new text}

# ---------- c6 main: how the PI speaks to the person at a close ----------
waves = rd('skills/research-loop/references/waves.md')
waves = sub(waves, "4. End the note with the line `closed: YYYY-MM-DD`",
"""4. Tell the user, in chat, and put the same text under `## For the user` in the note before it closes
   (a run without a chat reader leaves only the note). Open with their question in their own words.
   Then one sentence per claim that stands alone when quoted: what it establishes, its label, what it
   closes and one thing it leaves outside. Then the cost against the budget, in the budget's own unit,
   and the minutes the wave took. Then what needs them, each with the default you will take. Say what a
   term means the first time you use it.
5. End the note with the line `closed: YYYY-MM-DD`""")
waves = sub(waves, "Show the user the open puzzles and what budget remains, and ask where the remaining effort should\ngo.",
"Show the user the open puzzles and what budget remains, in the same order as a wave close, and ask\nwhere the remaining effort should go.")
wave_t = rd('skills/research-loop/templates/wave.md')
wave_t = sub(wave_t, "## Notes\n", "## For the user (at close)\n\n<The close message sent in chat: their question in their words; one sentence per claim with label and\nscope; cost and minutes; what needs them, with the default. Written before `closed:`.>\n\n## Notes\n")
pi = rd('agents/research-pi.md')
pi = sub(pi, "and you do not report as done what has not yet\nhappened.\n",
"and you do not report as done what has not yet\nhappened. You write to the person as to a colleague who reads one sentence at a time and quotes it\nback.\n")
CHANGES['c6-contract.diff'] = {'skills/research-loop/references/waves.md': waves, 'skills/research-loop/templates/wave.md': wave_t, 'agents/research-pi.md': pi}

# ---------- c6 optional: /lab-status in the same order ----------
ls = rd('skills/lab-status/SKILL.md')
ls = sub(ls, "Show the output to the user as it is. Then add at most a few lines of your own: how many puzzles\nare open and which, which claims need a decision, and anything printed on a `!` line.",
"""Show the output to the user as it is. Then add four lines, in this order: **Doing** (who is working);
**Found** (each claim as one sentence with its state and the `scope:` of its head); **Cost** (the
Spend totals against the budget, in the budget's unit); **Needs you** (open decisions, each with its
default, and anything printed on a `!` line).""")
CHANGES['c6-optional-lab-status.diff'] = {'skills/lab-status/SKILL.md': ls}

# ---------- c7: an asking habit ----------
wd = rd('skills/research-loop/references/working_defaults.md')
wd = wd.rstrip('\n') + """

## Asking the user

The rule above (hard to reverse, or visible outside the project: wait for a yes) also covers what the
person owns beyond the project: their other sessions, accounts and schedules. For every other
question:

- First read the last entries of `__statera__/user_words.md` and the rules in the framing, and look at
  what you can reach on the machine. Ask only what only the person can decide or do.
- Ask in the middle of the work, not at its end: say which default you are taking, and carry on with
  what does not depend on the answer.
- When the person says how they want the work done, add it in their words to "Rules for the team" in
  `__design__/framing.md` before you continue.
"""
CHANGES['c7-asking-habit.diff'] = {'skills/research-loop/references/working_defaults.md': wd}

out = []
for name, files in CHANGES.items():
    d = ''
    for path, new in files.items():
        old = rd(path)
        d += ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), 'a/' + path, 'b/' + path))
    open(os.path.join(H, name), 'w').write(d)
    r = subprocess.run(['git', 'apply', '--check', os.path.join(H, name)], cwd=ROOT, capture_output=True, text=True)
    add = [l[1:] for l in d.splitlines() if l.startswith('+') and not l.startswith('+++')]
    rem = [l[1:] for l in d.splitlines() if l.startswith('-') and not l.startswith('---')]
    wa, wr = sum(len(l.split()) for l in add), sum(len(l.split()) for l in rem)
    per = {p: (len(new.split()) - len(rd(p).split())) for p, new in files.items()}
    out.append(f'{name}: git apply --check rc={r.returncode} {r.stderr.strip()[:80]}; words added {wa}, removed {wr}, net {wa - wr}; net per file {per}')
base = {p: len(rd(p).split()) for p in ['agents/research-pi.md', 'skills/research-loop/SKILL.md', 'skills/research-loop/references/waves.md', 'skills/research-loop/references/working_defaults.md', 'skills/research-loop/templates/wave.md', 'skills/lab-status/SKILL.md']}
out.append('words in the touched files today: ' + str(base))
open(os.path.join(H, 'diff_cost.txt'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
