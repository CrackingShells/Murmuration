# Lab files

One file per writer, append-only in spirit: you add to your own file and never edit another
agent's. Identifiers are short and stable.

| Identifier | Form | Example |
|:--|:--|:--|
| wave | `wave-NN` | `wave-03` |
| claim | `wNN-<agent>-<n>` | `w03-author-2` |
| puzzle | `S-wNN-<agent>-<n>` | `S-w03-explorer-1` |

## `__pondus__/<claim-id>.md`

The author writes the head; each verifier appends one section. Never edit another writer's part.

```markdown
# w03-author-2: <the statement, one sentence>

label: MEASURED
scope: <what this claim covers, one sentence; and one thing it does not>
evidence: code/run_all.py@3f2a1c9, data/derived/results.csv@3f2a1c9
author: author-w03-2

## verdict: verifier-w03-2

independent result: <what the verifier found before reading the author's explanations>
verdict: OVERSTATED
reason: <one or two sentences>
changed_by: <path of the new artifact, only if the verdict changed after the conversation>
```

## `__scrupuli__/wave-NN-<agent>.md`

```markdown
## S-w03-explorer-1
<what did not add up, in plain words>
refs: <paths to the raw artifacts: figure, table rows, log lines>
```

Dispositions are not written here. The PI records them in the wave note when the wave closes.

## `__statera__/wave-NN.md`

Written by the PI from [`../templates/wave.md`](../templates/wave.md); not edited after `closed:`.

## `__statera__/user_words.md`

The user's prompts, appended verbatim with their date by the lab's hook and by `/lab`. Agents
read it and never edit it.

## `__design__/framing.md`

The question, notation and scope, from [`../templates/framing.md`](../templates/framing.md).
Anyone may add a symbol before using it; changing a definition is a PI decision recorded in the
wave note.
