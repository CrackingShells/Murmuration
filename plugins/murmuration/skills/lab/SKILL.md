---
name: lab
description: Start a Murmuration research lab in the current project, or add a new question to the lab that is already there. Run it as `/lab <your question>`.
argument-hint: <your question, in your own words>
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(python3 *lab_init.py*)
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
  `__scrupuli__/`, `__design__/` and `__instrumenta__/` (helper scripts); writes a `.ignore` (folders colgrep
  and Grep leave out: saved hand-backs, `raw/`, `runs/`, `generated/`; added to a `.ignore` that
  exists, never replacing it); builds the colgrep index once, and says so when `colgrep` is not installed;
  writes `__design__/framing.md` (a stub from the
  `research-loop` template), `__statera__/user_words.md` (the question, dated) and
  `__statera__/wave-01.md` (the first wave note); and merges into `.claude/settings.local.json`
  (personal settings, not shared with the team) the deny rules `Bash(pkill:*)` and
  `Bash(killall:*)`. It never sets the main-thread `agent`: how a session opens as the research PI
  is the user's choice. It never overwrites an existing file and never writes
  `.claude/settings.json`. An `agent` setting that is already in either file, whatever it names, is
  left exactly as it is, and the script says so.
- **`__statera__/` exists: it appends the question** to `__statera__/user_words.md` under a
  dated heading (unless it is already the newest entry). It also restores the deny rules missing
  from `.claude/settings.local.json`, which a fresh clone of the project does not have, and says
  what it restored; it does not set `agent`, and an existing one is left alone. It also creates
  `__instrumenta__/` and the `.ignore` block when they are missing. Nothing else changes.

- **A folder above this one already holds a lab: it creates nothing** and says where that lab is.
  Tell the user to run `/lab` from that folder, or start Claude Code there.

If the script exits with an error, show the user the message and stop. Do not recreate its work
by hand, and never edit `__statera__/user_words.md` yourself.

## 3. Tell the user what happened

Report the script's output in a few lines, then:

- **After an initialization,** tell the user exactly what the script printed under "Next:": how
  to open a session as the research PI, in one of two ways. Either start
  `claude --agent murmuration:research-pi`, or add the line `"agent": "murmuration:research-pi"`
  to `.claude/settings.local.json` and start `claude`. When the plugin is loaded from a folder and
  not installed, the script puts `--plugin-dir <path>` after `claude` in both; when it is
  installed, plain `claude` (the script prints the right one). The lab sets none of this itself,
  and settings are read when a session starts, so only a new session opens as the PI; this
  session does not become the PI. In the new session, the user asks it to begin, for example:
  `Frame my question and plan the first wave.` If the script reported that it kept an `agent`
  setting of the user's, say so. Mention that `.claude/settings.local.json` holds personal
  settings and belongs out of version control.
- **After an append,** say the question is recorded, and what settings the script restored, if
  any (the deny rules; it never sets or restores `agent`). If you are the research PI (your
  instructions say you lead a Murmuration research team), read the new entry in
  `__statera__/user_words.md` and decide whether it changes the current wave. Otherwise a new
  session in this folder will pick it up.

Do not start the research yourself.
