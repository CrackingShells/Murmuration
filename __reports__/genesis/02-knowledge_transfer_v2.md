# Imbrication study, process — Knowledge Transfer (v2)

Date: 2026-10-18 · Replaces §3 (triggers) and §4 (doubt) of
[01-knowledge_transfer_v1.md](01-knowledge_transfer_v1.md). §1 (PI agent), §2 (tools) and §5
(perseverance) of v1 stand.

## The correction

v1 answered "the PI did not reassess on its own" with **rules**: pre-registered kill criteria,
intent checks, a red-team agent on the framing. The PI rejected this. In open research nothing
can be pre-registered in a way that decides anything, and the reason to hand research to a model
is to delegate **judgement**: reacting to weak signals, noticing what does not add up. A rule
for deciding is the opposite of that. v1 repeated the failure it was diagnosing: it treated the
PI role as a verification pipeline.

## What actually went wrong: the signals were there, and judgement did not act on them

| Signal (and where it appeared) | What it was saying | What the PI did |
|:--|:--|:--|
| The user's first message: "a combinatorics problem", "bounds of the numbers that can be expressed", "generative sequences", "a whole generative space", and calling the idea "dumb or naive" | The object was the point; compression was the motivation | Framed regimes and hypotheses around compression; the user had to redirect |
| Atlas: Champernowne, a *normal* sequence, completes later than random | Completeness and randomness are different axes; "complete" is not "typical" | Relayed it as a curiosity |
| Laws: Bernoulli(θ) has h = 1 for every θ | The generative-space theory as built is **blind to frequencies**, so it cannot speak to compression; the missing object is a frequency-weighted generative space, the bridge to the user's application | Written into the notebook as a caveat ("set vs measure") instead of opening a direction |
| Trellis: a trained map barely beats a random one at large ω | The value lies in the overlap structure (the imbrication), not in the map's contents, which is back to the user's combinatorics | Logged as a number |
| Atlas: m-sequence ≡ de Bruijn word for parse statistics though c differs | Completeness order is not the quantity that governs composition | Logged as a number |
| The user's remark that ρ depends on G | The user saw optimizing G as a field | Turned into a provenance table, then closed by theorems that cover only part of it (v1 §5) |

The one signal the PI did chase, the count 2, 6, 20, 58, … being independent of n and ω, gave
the study's best combinatorial result. Following a signal paid off; the others were not
followed.

## Root cause: the delegation design starved judgement of raw material

Weak signals live in raw outputs: figures, odd table rows, an agent's side remark. The PI
designed the team to send back **word-capped summaries with labels**, read one figure, and read
reports only in sections. That minimized context and made verification cheap, and it filtered
out the material that judgement works on. Agents decided what counted as "surprising", and the
PI mostly checked what they surfaced instead of looking for itself.

## What to change: attention, not procedure

These are not decision rules; they change what the PI sees and how it spends attention:

- **Look at the primary material yourself.** Figures, a sample of rows, the agent's dead ends,
  not only the headline. Spend PI context there and save it on verification, which the
  reproducer and adversary already do well.
- **Ask agents what puzzled them**, not only what they found, and give the answer room (no word
  cap on that part).
- **Let the next wave come from what is most interesting or most off**, said in plain words in the
  decision note ("this doesn't add up because…"), rather than from the plan's next node.
- **Hold the user's own words close.** Re-read the original request at each re-plan as a
  researcher would re-read a colleague's question, not as a checklist.
- **Configuration consequence.** The `research-pi` agent (v1 §1) should describe the role as
  judgement and taste: name the PI's job as noticing, and keep procedure in the skills that the
  team members use. The verifiers keep their rules, because verification *is* mechanical.

## Open question

Where is the boundary between a PI using its context on raw material and drowning in it? This
study erred on the starved side. One wave with full raw returns would show where it starts to
cost more than it yields.
