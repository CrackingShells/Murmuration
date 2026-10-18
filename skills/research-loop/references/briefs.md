# Briefs

A brief is everything a cold agent needs and nothing it does not. Point to files instead of pasting
them.

## Every brief contains

1. **Your name:** "Your name is <name>." Use the same string as the Agent tool's `name`.
2. **Read first:** the paths the agent must read (always `__design__/framing.md`; the claim file for
   a verifier; the relevant raw artifacts).
3. **The question,** in one or two sentences, quoting the user's words when they apply.
4. **What to return:** the deliverable paths, and the labels the agent may use.
5. **Rules:** the project's tool and compute limits; no downloads unless allowed; commit only your
   own files; never stop processes by name pattern.
6. **The closing request:** "End with your puzzles in `__scrupuli__/wave-NN-<your name>.md`: what
   did not add up, with pointers to raw artifacts. No length limit." Ask what puzzled the agent,
   not only what it found.

## By role

| Role | Agent type | Add to the brief |
|:--|:--|:--|
| explorer | `murmuration:explorer` | The direction, deliberately loose and small enough for one probe; "if you leave the brief, say where and why in your first line" |
| author | `murmuration:author` | The claim id (`wNN-cK`); the hunch to harden; proof or experiment; the name the verifier will have |
| reproducer | `murmuration:reproducer` | The claim id; the author's name |
| proof-adversary | `murmuration:proof-adversary` | The claim id; the author's name |

Dispatch the author first and the verifier after the claim file exists, as set out in the
research-loop skill ("Author and verifier, in order").

## Models

The PI runs on the strongest model. Every other role runs on its agent file's default model; a
stronger model for one dispatch is a deliberate exception, stated in the wave note.
