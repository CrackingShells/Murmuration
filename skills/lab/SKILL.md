---
name: lab
description: Start a Murmuration research lab in the current project, or add a new question to the lab that is already there. Run it as `/lab <your question>`.
argument-hint: <your question, in your own words>
disable-model-invocation: true
user-invocable: true
---

# /lab

Starts a research lab in the user's current project, or records a new question in the lab that
is already there. The user's words are kept exactly as typed.

The question the user gave:

~~~
$ARGUMENTS
~~~

## 1. Get the question

If the block above is empty, ask the user for their question in their own words, and wait for
the answer. Do not invent one or shorten theirs.

## 2. Run the script

Run it from the project folder (the one that holds, or will hold, `.claude/`), passing the
question on standard input through a quoted heredoc so quotes, `$` and backticks arrive
unchanged. Replace the text between the delimiters with the user's question, character for
character:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lab_init.py" <<'MURMURATION_QUESTION'
<the user's question, verbatim>
MURMURATION_QUESTION
```

The script decides by itself:

- **No `__statera__/` folder: it initializes the lab.** It creates `__statera__/`, `__pondus__/`,
  `__scrupuli__/` and `__design__/`; writes `__design__/framing.md` (a stub from the
  `research-loop` template), `__statera__/user_words.md` (the question, dated) and
  `__statera__/wave-01.md` (the first wave note); and merges into `.claude/settings.json`
  `"agent": "murmuration:research-pi"` and the deny rules `Bash(pkill:*)` and
  `Bash(killall:*)`. It never overwrites an existing file, and it keeps an existing `agent`
  setting that names something else.
- **`__statera__/` exists: it appends the question** to `__statera__/user_words.md` under a
  dated heading and changes nothing else.

If the script exits with an error, show the user the message and stop. Do not recreate its work
by hand, and never edit `__statera__/user_words.md` yourself.

## 3. Tell the user what happened

Report the script's output in a few lines, then:

- **After an initialization:** tell the user to start a new session in this folder (exit, then
  run `claude` there). Project settings are read when a session starts, so only the new session
  opens as the research PI. This session does not become the PI. If the script reported that it
  kept a different `agent` setting, say so and show the line that would open the lab as the PI.
- **After an append:** say the question is recorded. If you are the research PI (your
  instructions say you lead a Murmuration research team), read the new entry in
  `__statera__/user_words.md` and decide whether it changes the current wave. Otherwise a new
  session in this folder will pick it up.

Do not start the research yourself.
