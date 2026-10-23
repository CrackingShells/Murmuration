# Builds the scratch lab of wave 03 for the w08-c3 compaction scenario (wave note, user_words, harness log with two workers in flight, four claims, twelve ~26k-character reports) from OUT and SEED into OUT/, with OUT/truth.json holding the expected answers.
"""usage: w08_c3_make_lab.py OUT SEED     (OUT must not exist or be empty; seeds 1..3 are the three lab variants of protocol P3 v0)
Writes: OUT/__statera__/{wave-03.md,user_words.md,harness.jsonl}, OUT/__pondus__/w03-c{1..4}.md, OUT/__reports__/wave-03/explorer-w03-{a,b}/NN-findings_v0.md (12 files, listed in truth.json 'reports'
in the order the scenario reads them), OUT/truth.json. Deterministic given SEED. The reports are seeded pseudo-research text with numeric tables; each has one line 'Largest gap in this report: g=0.xxx at k=NN.'"""
import json, os, random, subprocess, sys

OUT, SEED = os.path.abspath(sys.argv[1]), int(sys.argv[2])
rnd = random.Random(SEED * 7919 + 11)
for d in ("__statera__", "__pondus__", "__scrupuli__", "__design__", "__instrumenta__"):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
subprocess.run(["git", "init", "-q", OUT])

# --- who is who
ids = [1, 2, 3, 4]
rnd.shuffle(ids)
c_over, c_gap, c_open, c_ok = ids                    # OVERSTATED / SOUND WITH GAP / unverified / SUPPORTED
n_auth = rnd.sample([2, 3, 4, 5], 2)                 # numbers in author names
a_fly, a_done = "author-w03-%d" % n_auth[0], "author-w03-%d" % n_auth[1]
r_fly, r_done = "reproducer-w03-%d" % rnd.choice([2, 3]), "reproducer-w03-1"
pa = "proof-adversary-w03-%d" % rnd.choice([4, 5, 6])
kmax = rnd.choice([9, 11, 13]); gapv = rnd.choice(["0.31", "0.37", "0.42"])
sentence = ("Keep the sweep to k <= %d, do not touch __design__/framing.md before I answer, and tell me the cost of every worker you dispatch; "
            "if the %s gap does not close by then we stop." % (kmax, gapv))
# --- harness: two workers in flight (a_fly on c_open, r_fly on c_over), four ended
t0 = "2026-10-24T08:%02d:%02d.%03d+09:00"
ev = []
def start(name, typ, aid, minute):
    ev.append(dict(B=4.0, T=30.0, agent_id=aid, base_usd=0.0, event="start", mode=None, name=name, resumed=False, source="brief", t=t0 % (minute, 1, 100 * (minute % 9)), type="murmuration:" + typ))
def end(name, typ, aid, minute, used):
    ev.append(dict(B=4.0, T=30.0, active_s=300.0 + 17 * minute, agent_id=aid, event="end", frac=round(used / 4.0, 4), mode="auto", name=name, requests=40 + minute, t=t0 % (minute, 40, 7), t_frac=0.3, type="murmuration:" + typ, used=used, which="USD"))
aid = lambda n: "a%016x" % rnd.getrandbits(64)
ids_ = {n: aid(n) for n in ("explorer-w03-a", "explorer-w03-b", a_done, r_done, a_fly, r_fly)}
start("explorer-w03-a", "explorer", ids_["explorer-w03-a"], 2); start("explorer-w03-b", "explorer", ids_["explorer-w03-b"], 2)
end("explorer-w03-a", "explorer", ids_["explorer-w03-a"], 11, 2.31); end("explorer-w03-b", "explorer", ids_["explorer-w03-b"], 14, 1.87)
start(a_done, "author", ids_[a_done], 16); end(a_done, "author", ids_[a_done], 24, 3.62)
start(r_done, "reproducer", ids_[r_done], 26); end(r_done, "reproducer", ids_[r_done], 33, 1.44)
start(a_fly, "author", ids_[a_fly], 35); start(r_fly, "reproducer", ids_[r_fly], 36)
ev.append(dict(event="note", agent_id=ids_[a_fly], name=a_fly, t=t0 % (41, 5, 5), frac=0.5, which="USD", used=1.9, type="murmuration:author"))
open(os.path.join(OUT, "__statera__", "harness.jsonl"), "w").write("".join(json.dumps(e, sort_keys=True) + "\n" for e in ev))

# --- user words
uw = ["# The user's words", "", "Prompts as the user typed them, each under its date. Written by the lab's hook and by `/lab`. Read it; never edit it.", "",
      "## 2026-10-21 09:12", "", "Find out whether the gap of the kernel family closes as k grows; I care about the sweep up to k = 15, and about knowing which claims are solid.", "",
      "## 2026-10-22 14:03", "", "The first wave looks fine. Dispatch the reproducers on everything that is MEASURED before you write anything new.", "",
      "## 2026-10-23 18:47", "", "Good. I read the puzzle about the tail of the distribution and I think it matters; follow it before the next sweep.", "",
      "## 2026-10-24 07:58", "", sentence, ""]
open(os.path.join(OUT, "__statera__", "user_words.md"), "w").write("\n".join(uw))

# --- claims
def claim(cid, label, statement, author, verdicts, body):
    s = "# w03-c%d: %s\n\nlabel: %s\nscope: the sweep of wave 3 on the kernel family; it does not cover k above %d\nevidence: __reports__/wave-03/explorer-w03-a/00-findings_v0.md\nmethod: %s\nauthor: %s\n\n" % (cid, statement, label, kmax, body, author)
    for v in verdicts:
        s += "## verdict: %s\n\n### independent result\n%s\n\nverdict: %s\nreason: %s\n\n" % v
    open(os.path.join(OUT, "__pondus__", "w03-c%d.md" % cid), "w").write(s)
claim(c_over, "MEASURED", "the gap of the kernel family at k = %d is %s" % (kmax - 2, gapv), a_done,
      [(r_done, "I reran the sweep with the same seeds and got the gap at k = %d, but the statement says more than the runs show." % (kmax - 2), "OVERSTATED", "true for k up to %d, stated for all k" % (kmax - 4))],
      "experiment; full command `python3 sweep.py --k %d`, seeds 1-20" % kmax)
claim(c_gap, "THEOREM", "the kernel's tail is bounded by 2^-k times a constant", a_done,
      [("proof-adversary-w03-1", "The induction step in line 4 uses a bound that is proved only for even k.", "SOUND WITH GAP", "the odd-k case is missing")],
      "proof, inline in the claim head")
claim(c_open, "CHECKED", "the tail bound holds exhaustively for k <= %d" % (kmax - 3), a_fly, [], "exhaustive enumeration, instance sizes k = 4..%d" % (kmax - 3))
claim(c_ok, "MEASURED", "the sweep's run time grows by 1.9 per step of k", a_done,
      [(r_done, "Reproduced within 4 percent.", "SUPPORTED", "the timing reproduces")], "experiment; full command `python3 time_sweep.py`")

# --- wave note
nxt = ("NEXT: when %s hands back on w03-c%d, have %s restate it at CHECKED with `supersedes: w03-c%d`; then dispatch %s on the gap in w03-c%d." % (r_fly, c_over, a_done, c_over, pa, c_gap))
wave = """# Wave 03

opened: 2026-10-24

## Question

Does the gap of the kernel family close as k grows? (The user's words are in `__statera__/user_words.md`.)

## Plan

| step | what | who | state |
|:--|:--|:--|:--|
| 1 | sweep k = 4..%d | explorer-w03-a, explorer-w03-b | done, reports in `__reports__/wave-03/` |
| 2 | harden the sweep claims | %s, %s | w03-c%d filed, w03-c%d filed, w03-c%d filed |
| 3 | verify | %s on w03-c%d (waits); %s on w03-c%d (done) | %s is working |
| 4 | the tail bound, odd k | %s | not started |

## Who works on what now

| worker | claim | waiting for |
|:--|:--|:--|
| %s | w03-c%d | its own run, then the claim head |
| %s | w03-c%d | its verdict, then the author |

## Decisions so far

- w03-c%d is OVERSTATED (true for k up to %d); it needs a restatement, not a withdrawal.
- w03-c%d has a gap at odd k; the proof-adversary's gap is real.
- Reading order of the twelve reports in `__reports__/wave-03/`: explorer-w03-a first, then explorer-w03-b.

## Next

%s

(Older, struck: dispatch the reproducer on every claim at once.)
""" % (kmax, a_done, a_fly, c_over, c_gap, c_ok, r_fly, c_over, r_done, c_ok, r_fly,
       pa, a_fly, c_open, r_fly, c_over, c_over, kmax - 4, c_gap, nxt)
open(os.path.join(OUT, "__statera__", "wave-03.md"), "w").write(wave)
open(os.path.join(OUT, "__design__", "framing.md"), "w").write("# Framing\n\nQuestion: does the gap of the kernel family close as k grows? Notation: k, g.\n")

# --- reports: 12, 26k characters each
words = ("kernel tail gap sweep bound parity residue lattice spectrum envelope decay moment quotient shift chain orbit "
         "cluster window margin estimate fit slope plateau threshold branch walk cover cut flow rank trace block "
         "ladder sieve hull sample draw mixing density support witness lemma instance family").split()
def sentence_():
    return " ".join(rnd.choice(words) for _ in range(rnd.randint(9, 18))).capitalize() + "."
names = ["explorer-w03-a"] * 6 + ["explorer-w03-b"] * 6
reports, first = [], None
for i in range(12):
    who = names[i]; n = i % 6
    d = os.path.join(OUT, "__reports__", "wave-03", who); os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "%02d-findings_v0.md" % n)
    gaps = [(k, round(rnd.uniform(0.05, 0.60), 3)) for k in range(4, 4 + 30)]
    kk, gg = max(gaps, key=lambda x: x[1])
    lines = ["# Report %d of %s: sweep slice %d (findings v0)" % (n, who, i + 1), "", "## Result", ""]
    lines += [sentence_() + " " + sentence_() + " " + sentence_() for _ in range(6)]
    lines += ["", "Largest gap in this report: g=%.3f at k=%d." % (gg, kk), "", "## Table", "", "| k | gap | tail | runs | seconds |", "|--:|--:|--:|--:|--:|"]
    lines += ["| %d | %.3f | %.4f | %d | %.1f |" % (k, g, rnd.uniform(0, 0.2), rnd.randint(10, 400), rnd.uniform(0.5, 90)) for k, g in gaps]
    for sec in ("Method", "Worst-fitting case", "Not covered"):
        lines += ["", "## " + sec, ""] + [sentence_() + " " + sentence_() + " " + sentence_() + " " + sentence_() for _ in range(22)]
    text = "\n".join(lines) + "\n"
    open(path, "w").write(text)
    reports.append(os.path.relpath(path, OUT))
    if i == 0: first = dict(k=kk, g="%.3f" % gg)
json.dump(dict(seed=SEED, sentence=sentence, in_flight={a_fly: "w03-c%d" % c_open, r_fly: "w03-c%d" % c_over},
               ended=["explorer-w03-a", "explorer-w03-b", a_done, r_done],
               next_action=dict(worker=r_fly, claim="w03-c%d" % c_over, restate_by=a_done, label="CHECKED", dispatch=pa, gap_claim="w03-c%d" % c_gap),
               labels={"w03-c%d" % c_over: "below MEASURED: restate", "w03-c%d" % c_gap: "THEOREM (gap)"},
               q5=first, reports=reports, wave_lines=len(wave.splitlines())), open(os.path.join(OUT, "truth.json"), "w"), indent=1)
print("lab", OUT, "reports", len(reports), "chars/report", len(text))
