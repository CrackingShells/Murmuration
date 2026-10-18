# Briefs

A brief is everything a cold agent needs and nothing it does not. Point to files instead of pasting
them.

## Every brief contains

1. **Read first:** the paths the agent must read (always `__design__/framing.md`; the claim file
   for a verifier; the relevant raw artifacts).
2. **The question,** in one or two sentences, quoting the user's words when they apply.
3. **What to return:** the deliverable paths, and the labels the agent may use.
4. **Rules:** the project's tool and compute limits; no downloads unless allowed; commit only your
   own files; never stop processes by name pattern.
5. **The closing request:** "End with your puzzles in `__scrupuli__/wave-NN-<your name>.md`: what
   did not add up, with pointers to raw artifacts. No length limit." Ask what puzzled the agent,
   not only what it found.

## By role

| Role | Add to the brief |
|:--|:--|
| explorer | The direction, deliberately loose; a turn limit (`maxTurns`) suited to a cheap probe; "if you leave the brief, say where and why in your first line" |
| author | The claim id; the hunch to harden; proof or experiment; the verifier's name |
| reproducer / proof-adversary | The claim id; the author's name; "produce your own result before reading the author's explanations" |

## Pairs

Dispatch the author and its verifier with explicit names (for example `author-w03-2` and
`verifier-w03-2`) and give each the other's name. They talk with `SendMessage` directly and resume
each other as needed. The verifier ends the conversation with a verdict or an escalation; read the
claim file, not only their final messages, before acting on an escalation.

## Models

The PI runs on the strongest model. Every other role runs on the agent file's default model; a
stronger model for one dispatch is a deliberate exception, stated in the wave note.
