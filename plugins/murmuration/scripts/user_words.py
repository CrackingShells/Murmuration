#!/usr/bin/env python3
"""Keep the user's own words, verbatim, in a lab project.

Runs as a UserPromptSubmit hook. It reads the hook JSON from stdin and, when the project is an
initialized lab (it has a `__statera__/` folder), appends the prompt to
`__statera__/user_words.md` under a dated heading. The lab is found from the session's first
recorded `cwd` (head of the transcript), else the payload `cwd`, else CLAUDE_PROJECT_DIR; see
`project_root`.

A prompt is the user's own unless it is text the platform injected on someone else's behalf:
a message from another session, a task notification, or an agent message. Those are skipped, and
so are the lab's own slash commands (which record the question themselves) and bare slash
commands such as `/clear` or `/compact`, which carry no words. Platform blocks the app puts in
front of the typed text (`<system-reminder>`, `<artifact-view-context>`, `<side-sessions-event>`)
are cut first, and the app's `<pasted_content>` wrapper is removed around pasted text; what is
left is stored.

The platform also marks who sent a prompt, in the transcript record of that prompt (not in the hook
payload): `origin.kind` is `human` for typed prompts and `!` commands, `peer` for another session's
message, `task-notification` for a finished background task; `promptSource`/`turnOrigin` are
`system`/`scheduled` for the harness's own prompts and `sdk` for the first message of a session started
by another session (or by `claude -p`). The hook finds the record by the payload's `prompt_id` in the
tail of the transcript (polling at most ORIGIN_WAIT seconds: the record reaches the file only after the
UserPromptSubmit hooks have exited, so the hook runs `async` in hooks/hooks.json and the poll blocks nothing) and drops what the record marks as not typed by a person; an `sdk` prompt is kept only when
the record's `entrypoint` is `sdk-cli` (a headless run from a person's own terminal). When there is no
`prompt_id`, no transcript, no record in time, or a record without a known mark, the text rule above
decides, as it did before.

The script never blocks a prompt and always exits 0. Anything unexpected is dropped silently.

Usage:
    user_words.py              read a hook event from stdin
    user_words.py --selftest   check the script on a temporary project
"""
import datetime
import json
import os
import re
import sys
import time

NON_USER_PREFIXES = ("<cross-session-message ", "<task-notification>", "<agent-message from=")
LAB_COMMAND = re.compile(r"^/(?:murmuration:)?lab(?:-status)?(?:\s|$)")
BARE_COMMAND = re.compile(r"^/[A-Za-z][\w:.-]*\s*$")
# Blocks the platform puts before the typed text, cut only at the start of the prompt. The
# `<system-reminder>` form is the exact one seen: `<system-reminder>\n...\n</system-reminder>`.
LEADING_BLOCKS = (
    re.compile(r"\A\s*<system-reminder>\n.*?\n</system-reminder>(?:[ \t]*\n)*", re.S),
    re.compile(r"\A\s*<artifact-view-context\b[^>]*>.*?</artifact-view-context>(?:[ \t]*\n)*", re.S),
    re.compile(r"\A\s*<side-sessions-event>.*?</side-sessions-event>(?:[ \t]*\n)*", re.S),
)
PASTED = re.compile(r'<pasted_content id="([^"]*)">\n?(.*?)\n?</pasted_content id="\1">', re.S)
STORE = "__statera__"
FILE_NAME = "user_words.md"
HEAD_LINES = 200  # how much of a transcript session_cwd() may read
HEAD_BYTES = 1 << 20
ORIGIN_WAIT = 3.0  # seconds the hook may wait for the prompt's record to reach the transcript; the hook runs async, so this blocks nothing
ORIGIN_STEP = 0.025
TAIL_BYTES = (1 << 18, 1 << 22)  # tail windows: 256 KiB, then 4 MiB when the record starts before the first one
DROP_KINDS = ("peer", "task-notification")  # `origin.kind` values: another session, a finished background task
DROP_TURNS = ("peer", "task_notification", "scheduled")  # `turnOrigin` values of harness-sent prompts
HEADER = (
    "# The user's words\n\n"
    "Prompts as the user typed them, each under its date. Written by the lab's hook and by "
    "`/lab`. Read it; never edit it.\n"
)


def is_genuine(prompt):
    """True when the prompt is the user's own text, not platform-injected text."""
    return isinstance(prompt, str) and not prompt.startswith(NON_USER_PREFIXES)


def is_lab_command(prompt):
    """True for the lab's own slash commands (`/lab ...`, `/lab-status`)."""
    return bool(LAB_COMMAND.match(prompt.lstrip()))


def is_bare_command(prompt):
    """True for a slash command with no arguments (`/clear`, `/compact`): not the user's words."""
    return bool(BARE_COMMAND.match(prompt.strip()))


def strip_leading(prompt):
    """The prompt without the platform blocks in front of the typed text. The paste wrapper stays."""
    changed = True
    while changed:
        changed = False
        for block in LEADING_BLOCKS:
            prompt, n = block.subn("", prompt, count=1)
            changed = changed or bool(n)
    return prompt


def unwrap_pasted(text):
    """The text with the paste wrapper removed, one level, and leading blank lines dropped."""
    return re.sub(r"\A\s*\n", "", PASTED.sub(lambda m: m.group(2), text))


def record_mark(record):
    """What a transcript user record says about its sender: True typed by a person, False not, None unknown."""
    origin = record.get("origin")
    kind = origin.get("kind") if isinstance(origin, dict) else None
    if kind == "human":
        return True
    if kind in DROP_KINDS:
        return False
    if isinstance(kind, str):  # a kind this script does not know: leave it to the text rule
        return None
    source, turn = record.get("promptSource"), record.get("turnOrigin")
    if source == "system" or turn in DROP_TURNS:
        return False
    if turn == "human":
        return True
    if source == "sdk" or turn == "sdk":  # the first message of a session started by another session or by `claude -p`
        entry = record.get("entrypoint")
        if entry == "sdk-cli":
            return True
        return False if isinstance(entry, str) else None
    return None


def scan_tail(buf, prompt_id, whole):
    """The marks of the transcript user records with `promptId == prompt_id` in `buf`, the end of a transcript.

    Returns (verdict, cut): verdict is True/False/None as for record_mark (False wins over True when the
    records of one prompt disagree: the platform marked one of them as not typed); cut is True when
    nothing was found and the first line of `buf` was dropped as possibly partial, so a longer window may
    still hold the record (a record starts with its id, and may be longer than the window).
    """
    needle = prompt_id.encode("utf-8", "replace")
    lines = buf.split(b"\n")
    cut = False
    marks = []
    for i, line in enumerate(lines):
        if i == 0 and not whole:
            cut = True  # the window may start inside this line
            continue
        if needle not in line:
            continue
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if not isinstance(record, dict) or record.get("type") != "user" or record.get("promptId") != prompt_id:
            continue
        if "toolUseResult" in record or record.get("sourceToolAssistantUUID"):
            continue
        marks.append(record_mark(record))
    known = [m for m in marks if m is not None]
    return (min(known) if known else None), (cut and not known)


def read_tail(path, size):
    """The last `size` bytes of the file and whether they are the whole file."""
    with open(path, "rb") as fh:
        end = fh.seek(0, os.SEEK_END)
        start = max(0, end - size)
        fh.seek(start)
        return fh.read(end - start), start == 0, end


def human_prompt(event, wait=None):
    """True when the transcript says a person typed the prompt, False when it says another session or
    the harness sent it, None when that is not known (no `prompt_id`, no transcript, record not there in
    `wait` seconds, record without a known mark). Reads only the tail of the transcript."""
    pid, path = event.get("prompt_id"), event.get("transcript_path")
    if not isinstance(pid, str) or not pid or not isinstance(path, str) or not path:
        return None
    deadline = time.monotonic() + (ORIGIN_WAIT if wait is None else wait)
    seen = None
    while True:
        try:
            size = os.stat(path).st_size
            if size != seen:  # nothing new on disk since the last look: do not read again
                seen = size
                for window in TAIL_BYTES:
                    buf, whole, _ = read_tail(path, window)
                    verdict, cut = scan_tail(buf, pid, whole)
                    if verdict is not None:
                        return verdict
                    if not cut:
                        break
        except FileNotFoundError:
            pass  # the first prompt of a session may come before the file exists
        except (OSError, ValueError):
            return None
        if time.monotonic() >= deadline:
            return None
        time.sleep(ORIGIN_STEP)


def session_cwd(transcript_path):
    """The `cwd` of the first record of the session transcript that carries one, or None.

    Reads only the head of the file (at most HEAD_LINES lines and HEAD_BYTES bytes in all, including a single huge line): the first records
    are queue operations without a `cwd`, the next ones carry the directory the session started in.
    """
    if not isinstance(transcript_path, str) or not transcript_path:
        return None
    seen = 0
    try:
        with open(transcript_path, "rb") as fh:
            for _ in range(HEAD_LINES):
                line = fh.readline(HEAD_BYTES - seen + 1)  # bounded read: a huge line cannot cost more than the budget
                seen += len(line)
                if not line or seen > HEAD_BYTES:
                    return None
                if b'"cwd"' in line:
                    try:
                        record = json.loads(line)
                    except ValueError:
                        record = None
                    cwd = record.get("cwd") if isinstance(record, dict) else None
                    if isinstance(cwd, str) and os.path.isabs(cwd):
                        return cwd
    except OSError:
        pass
    return None


def lab_above(start):
    """The nearest directory at or above `start` with a `__statera__/` folder, or None.

    The walk stops at the first directory that has a `.git` entry (a folder, or the file of a linked
    worktree), after testing that directory itself: it never leaves the repository `start` is in.
    """
    here = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(here, STORE)):
            return here
        parent = os.path.dirname(here)
        if os.path.exists(os.path.join(here, ".git")) or parent == here:
            return None
        here = parent


def project_root(event):
    """The lab a hook event belongs to, or None. In this order:

    1. the session's first recorded `cwd` (transcript head), searched upward; the live `cwd` of the
       payload follows the Bash tool's `cd`, the session's first one does not;
    2. the payload `cwd` the same way, only when the transcript has no `cwd` yet (the first prompt of
       a session may come before any record is on disk);
    3. CLAUDE_PROJECT_DIR itself, when it has a lab (the Desktop's value is the main checkout, which
       is wrong in a worktree and right when the session started elsewhere);
    else None: nothing is written.
    """
    event = event if isinstance(event, dict) else {}
    start = session_cwd(event.get("transcript_path"))
    if start is None:
        payload = event.get("cwd")
        start = payload if isinstance(payload, str) and payload else os.getcwd()
    root = lab_above(start)
    if root:
        return root
    fixed = os.environ.get("CLAUDE_PROJECT_DIR")
    if fixed and os.path.isdir(os.path.join(fixed, STORE)):
        return fixed
    return None


def append_words(root, text, when=None):
    """Append `text` verbatim under a dated heading in the project's user_words.md.

    Creates the file with a short header if it does not exist. Returns the file path.
    """
    when = when or datetime.datetime.now()
    folder = os.path.join(root, STORE)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, FILE_NAME)
    entry = "\n## %s\n\n%s\n" % (when.strftime("%Y-%m-%d %H:%M"), text.rstrip("\n"))
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", encoding="utf-8") as fh:
        fh.write((HEADER if new else "") + entry)
    return path


def last_entry(root):
    """The text of the newest entry in the project's user_words.md, or None."""
    try:
        with open(os.path.join(root, STORE, FILE_NAME), encoding="utf-8") as fh:
            blocks = re.split(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}\n", fh.read(), flags=re.M)
    except OSError:
        return None
    return blocks[-1].strip() if len(blocks) > 1 else None


def handle(event):
    """Record the event's prompt if it is genuine and the project is a lab. Returns the path or None."""
    prompt = event.get("prompt")
    if not isinstance(prompt, str):
        return None
    prompt = strip_leading(prompt)  # the command tests below see the paste wrapper, so pasted `/lab ...` is kept
    if not is_genuine(prompt) or not prompt.strip() or is_lab_command(prompt) or is_bare_command(prompt):
        return None
    words = unwrap_pasted(prompt)
    root = project_root(event)
    if not words.strip() or root is None:
        return None
    try:
        typed = human_prompt(event)
    except Exception:  # whatever goes wrong in the lookup, the text rule above has decided
        typed = None
    if typed is False:  # the transcript marks it as another session's or the harness's
        return None
    return append_words(root, words)


def selftest_origin():
    """The origin cases: what the transcript record of the prompt (found by `prompt_id`) decides, and every fallback."""
    import subprocess
    import tempfile
    import threading

    pid = "11111111-2222-3333-4444-555555555555"

    def rec(promptId=pid, text="the words", **fields):
        record = {"type": "user", "promptId": promptId, "message": {"role": "user", "content": text}}
        record.update(fields)
        return record

    def fire(tmp, records, text="the words", extra=None, raw=None, late=None, size=None, late_after=0.1):
        """Run the hook once on a lab in `tmp`; return True when `text` was stored."""
        lab = os.path.join(tmp, "lab")
        os.makedirs(os.path.join(lab, STORE), exist_ok=True)
        tpath = os.path.join(tmp, "t.jsonl")
        with open(tpath, "w", encoding="utf-8") as fh:
            for r in records or []:
                fh.write(json.dumps(r) + "\n")
            fh.write(raw or "")
            if size:
                fh.write(json.dumps({"type": "attachment", "pad": "x" * size}) + "\n")
        event = {"prompt": text, "cwd": lab, "prompt_id": pid, "transcript_path": tpath, "hook_event_name": "UserPromptSubmit"}
        event.update(extra or {})
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        proc = subprocess.Popen([sys.executable, os.path.abspath(__file__)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, env=env, cwd=tmp, encoding="utf-8")
        if late is not None:  # the record reaches the file after the hook has started
            def append():
                time.sleep(late_after)
                with open(tpath, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(late) + "\n")
            threading.Thread(target=append).start()
        out, err = proc.communicate(json.dumps(event))
        assert proc.returncode == 0 and out == "", (proc.returncode, out, err)
        words = os.path.join(lab, STORE, FILE_NAME)
        return os.path.exists(words) and text in open(words, encoding="utf-8").read()

    def run(want, *args, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            assert fire(tmp, *args, **kw) == want, (want, repr((args, kw))[:300])

    human = dict(origin={"kind": "human"}, promptSource="sdk", turnOrigin="human", entrypoint="claude-desktop")
    # who sent it, by the platform's own marker
    run(True, [rec(**human)])
    run(False, [rec(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer", isMeta=True, entrypoint="claude-desktop")])
    run(False, [rec(origin={"kind": "task-notification"}, promptSource="system", entrypoint="claude-desktop")])
    run(False, [rec(promptSource="system", turnOrigin="scheduled", isMeta=True)])
    run(False, [rec(promptSource="sdk", turnOrigin="sdk", entrypoint="claude-desktop")])  # a session started by another session
    run(True, [rec(promptSource="sdk", turnOrigin="sdk", entrypoint="sdk-cli")])  # a person's own `claude -p`
    run(True, [rec(turnOrigin="human")])
    # a mark this script does not know, or none: the text rule decides (it stores plain words)
    run(True, [rec(origin={"kind": "something-new"}, promptSource="sdk", entrypoint="claude-desktop")])
    run(True, [rec()])
    run(True, [rec(promptSource="sdk", turnOrigin="sdk")])  # sdk without an entrypoint
    run(True, [rec(origin="human")])  # origin is not an object
    # the lookup is by prompt_id, in the tail, among other records
    other = rec(promptId="99999999-2222-3333-4444-555555555555", origin={"kind": "peer"}, promptSource="system", turnOrigin="peer")
    run(True, [other])  # another prompt's record says peer; ours is not there: fallback
    run(False, [other, rec(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer"),
                {"type": "attachment", "x": 1}, {"type": "assistant", "message": {}}])
    # a tool result that carries the same promptId and a human mark does not outvote the record of the prompt
    run(False, [rec(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer"), rec(toolUseResult={"x": 1}, **human)])
    run(False, [rec(promptSource="sdk", turnOrigin="sdk", entrypoint="claude-desktop"), rec(sourceToolAssistantUUID="u", **human)])
    # one prompt, several records: an unmarked companion does not hide the marked one, a marked non-human one wins
    run(False, [rec(isMeta=True, text="skill text"), rec(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer")])
    run(True, [rec(isMeta=True, text="skill text"), rec(**human)])
    # fallbacks that must neither raise, hang nor lose the prompt
    run(True, [rec(origin={"kind": "peer"})], extra={"prompt_id": None})
    run(True, [rec(origin={"kind": "peer"})], extra={"prompt_id": 7})
    run(True, [rec(origin={"kind": "peer"})], extra={"prompt_id": ""})
    run(True, [rec(origin={"kind": "peer"})], extra={"transcript_path": None})
    run(True, [rec(origin={"kind": "peer"})], extra={"transcript_path": 12})
    run(True, [rec(origin={"kind": "peer"})], extra={"transcript_path": "/nonexistent/dir/t.jsonl"})
    run(True, [rec(origin={"kind": "peer"})], extra={"transcript_path": tempfile.gettempdir()})  # a directory
    run(True, [], raw='{"type":"user","promptId":"%s","origin":{"kind":"pe\n' % pid)  # a malformed record
    run(True, [], raw='{"type":"user","promptId":"%s","origin":[1,2]}\n[1,2,%s]\n' % (pid, pid.replace("-", "")))
    run(True, [], raw="not json at all %s\n" % pid)
    # a record that arrives after the hook has started is still found (the wait is 3 s)
    run(False, [], late=rec(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer"))
    run(True, [], late=rec(**human))
    # a record that arrives 1.5 s after the hook has started is found too
    run(False, [], late=rec(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer"), late_after=1.5)
    # a record longer than the first window is found in the second; one longer than both falls back
    run(False, [rec(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer", pad="x" * (TAIL_BYTES[0] + 5))])
    run(False, [rec(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer")], size=TAIL_BYTES[0] * 2)
    run(True, [rec(origin={"kind": "peer"}, promptSource="system", turnOrigin="peer", pad="x" * (TAIL_BYTES[1] + 5))])
    # a big transcript with the record nowhere in it: the prompt is kept after at most the wait
    t0 = time.monotonic()
    run(True, [rec(promptId="other", origin={"kind": "peer"})], size=TAIL_BYTES[1] + 10)
    assert time.monotonic() - t0 < 6
    # decision function, direct
    assert human_prompt({"prompt_id": pid, "transcript_path": "/nonexistent/t.jsonl"}, wait=0) is None
    assert scan_tail(b"", pid, True) == (None, False)
    assert record_mark({"origin": {"kind": "human"}, "turnOrigin": "sdk"}) is True
    assert record_mark({"origin": {"kind": "peer"}, "turnOrigin": "human"}) is False
    assert record_mark({"promptSource": "sdk", "entrypoint": None}) is None
    assert record_mark({}) is None


def selftest_lab_root():
    """The E0 cases: which lab a prompt lands in, given the session's first cwd, the payload cwd and CLAUDE_PROJECT_DIR."""
    import subprocess
    import tempfile

    def mkdir(*parts, lab=False, git=None):
        path = os.path.join(*parts)
        os.makedirs(os.path.join(path, STORE) if lab else path, exist_ok=True)
        if git == "dir":
            os.makedirs(os.path.join(path, ".git"), exist_ok=True)
        elif git == "file":  # a linked worktree has a `.git` file
            with open(os.path.join(path, ".git"), "w", encoding="utf-8") as fh:
                fh.write("gitdir: /elsewhere/.git/worktrees/x\n")
        return path

    def transcript(path, cwds, lead=2, pad=0):
        """A session file: `lead` queue records without cwd, `pad` records without cwd, then one record per cwd."""
        with open(path, "w", encoding="utf-8") as fh:
            for _ in range(lead + pad):
                fh.write(json.dumps({"type": "queue-operation", "operation": "enqueue"}) + "\n")
            for cwd in cwds:
                fh.write(json.dumps({"type": "user", "cwd": cwd, "message": "m"}) + "\n")
        return path

    def fire(tmp, marker, cwd, tpath=None, project_dir=None):
        """Send one prompt; return the sorted names of the lab folders (under tmp) that now hold the marker."""
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        if project_dir is not None:
            env["CLAUDE_PROJECT_DIR"] = project_dir
        event = {"prompt": marker, "cwd": cwd, "hook_event_name": "UserPromptSubmit"}
        if tpath is not None:
            event["transcript_path"] = tpath
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input=json.dumps(event),
                              capture_output=True, text=True, env=env, cwd=tmp, encoding="utf-8")
        assert proc.returncode == 0 and proc.stdout == "", (proc.returncode, proc.stdout, proc.stderr)
        hit = []
        for dirpath, dirs, files in os.walk(tmp):
            if FILE_NAME in files and os.path.basename(dirpath) == STORE:
                if marker in open(os.path.join(dirpath, FILE_NAME), encoding="utf-8").read():
                    hit.append(os.path.relpath(os.path.dirname(dirpath), tmp))
        return sorted(hit)

    with tempfile.TemporaryDirectory() as tmp:
        main = mkdir(tmp, "main", lab=True, git="dir")
        wt = mkdir(tmp, "wt", lab=True, git="file")
        wtsub = mkdir(wt, "sub", "deep")
        other = mkdir(tmp, "other", lab=True, git="dir")
        wtb = mkdir(tmp, "wtb", lab=True, git="file")
        bare_wt = mkdir(tmp, "bare_wt", git="file")  # a worktree that has no lab (wave 1)
        plain = mkdir(tmp, "plain", git="dir")
        n = [0]

        def land(**kw):
            n[0] += 1
            return fire(tmp, "words number %d" % n[0], **kw)

        T = lambda name, cwds, **k: transcript(os.path.join(tmp, name + ".jsonl"), cwds, **k)
        # E0-1 Desktop worktree pair: CLAUDE_PROJECT_DIR = main checkout, session started in the worktree, both with a lab.
        assert land(cwd=wt, tpath=T("a", [wt, wt]), project_dir=main) == ["wt"]
        # the same on the first prompt, before any transcript record exists: no file, and an empty file
        assert land(cwd=wt, project_dir=main) == ["wt"]
        assert land(cwd=wt, tpath=os.path.join(tmp, "missing.jsonl"), project_dir=main) == ["wt"]
        assert land(cwd=wt, tpath=T("empty", []), project_dir=main) == ["wt"]
        # E0-2 the Bash tool `cd`'d into another checkout (the payload cwd follows it): the session's lab still wins
        for moved in (main, other, wtb, plain, tmp):
            assert land(cwd=moved, tpath=T("b", [wt, moved, moved]), project_dir=main) == ["wt"], moved
        # the same when the session started in main: a later cd into the worktree does not move the words
        assert land(cwd=wt, tpath=T("c", [main, wt]), project_dir=main) == ["main"]
        # a subfolder of the worktree (start, or shell) resolves to the worktree
        assert land(cwd=wtsub, tpath=T("d", [wtsub]), project_dir=main) == ["wt"]
        assert land(cwd=wtsub, project_dir=main) == ["wt"]
        # E0-3 headless start in a lab, CLAUDE_PROJECT_DIR the same lab or not set at all
        assert land(cwd=main, tpath=T("e", [main]), project_dir=main) == ["main"]
        assert land(cwd=main, tpath=T("e", [main])) == ["main"]
        assert land(cwd=main) == ["main"]
        # the session started in a worktree that has no lab: the lookup stops at its `.git`, CLAUDE_PROJECT_DIR's lab takes it (w01-c10 case A)
        assert land(cwd=bare_wt, tpath=T("f", [bare_wt]), project_dir=main) == ["main"]
        assert land(cwd=bare_wt, project_dir=main) == ["main"]
        assert land(cwd=bare_wt, tpath=T("f", [bare_wt])) == []  # nothing set, nothing found
        # the first cwd is the first record that carries one, not the first record
        assert land(cwd=wt, tpath=T("g", [wt, other], lead=5), project_dir=main) == ["wt"]
        # a head with no cwd within the limit counts as no transcript yet: the payload cwd decides
        assert land(cwd=other, tpath=T("h", [wt], pad=HEAD_LINES), project_dir=main) == ["other"]
        # a damaged head: an unparsable record and a relative cwd are skipped, a later good record is used
        with open(os.path.join(tmp, "i.jsonl"), "w", encoding="utf-8") as fh:
            fh.write('{"type":"user","cwd": truncated\n{"type":"user","cwd":"relative/dir"}\n{"cwd":7}\n')
            fh.write(json.dumps({"type": "user", "cwd": wt}) + "\n")
        assert land(cwd=main, tpath=os.path.join(tmp, "i.jsonl"), project_dir=main) == ["wt"]
        # a first line larger than the byte budget is not read in full: the head gives up and the payload cwd decides
        with open(os.path.join(tmp, "big.jsonl"), "w", encoding="utf-8") as fh:
            fh.write('{"type":"attachment","pad":"' + "x" * (HEAD_BYTES + 10) + '"}\n')
            fh.write(json.dumps({"type": "user", "cwd": wt}) + "\n")
        assert land(cwd=other, tpath=os.path.join(tmp, "big.jsonl"), project_dir=main) == ["other"]
        # E0-4 no lab anywhere: nothing is written, and no `__statera__` appears
        before = sorted(os.listdir(plain))
        assert land(cwd=plain, tpath=T("j", [plain]), project_dir=plain) == []
        assert land(cwd=plain, project_dir=os.path.join(tmp, "nowhere")) == []
        assert land(cwd=plain) == [] and sorted(os.listdir(plain)) == before
        assert not os.path.exists(os.path.join(plain, STORE))
        # a repository nested in a folder that has a lab: the walk stops at the inner `.git`
        outer = mkdir(tmp, "outer", lab=True)
        inner = mkdir(outer, "inner", "src", git=None)
        os.makedirs(os.path.join(outer, "inner", ".git"))
        assert land(cwd=inner, tpath=T("k", [inner])) == []
        # a plain folder inside a lab without `.git` in between: the lab above is found
        assert land(cwd=mkdir(outer, "plainsub", "x"), tpath=T("l", [os.path.join(outer, "plainsub", "x")])) == ["outer"]
        # a payload without a usable cwd falls to the process directory (the hook's own), then CLAUDE_PROJECT_DIR
        assert fire(tmp, "no cwd here", cwd=None, project_dir=wt) == ["wt"]
        assert fire(tmp, "garbage cwd", cwd=12, project_dir=wt) == ["wt"]
    # resume_brief and the writer must agree on the root: same function, tested in resume_brief --selftest


def selftest():
    import subprocess
    import tempfile

    assert is_genuine("what is the best split?")
    assert not is_genuine('<cross-session-message from="x">hi</cross-session-message>')
    assert not is_genuine("<task-notification><summary>done</summary></task-notification>")
    assert not is_genuine('<agent-message from="author">hello</agent-message>')
    assert is_genuine("<task-notifications are fun>")
    assert is_lab_command("/lab why?") and is_lab_command("/murmuration:lab") and is_lab_command("/lab-status")
    assert not is_lab_command("/labrador") and not is_lab_command("lab")
    assert is_bare_command("/clear") and is_bare_command("/compact ") and is_bare_command("/foo:bar")
    assert not is_bare_command("/compact keep the proofs") and not is_bare_command("/home/me/data.csv looks odd")
    assert not is_bare_command("hello /clear")

    def fire(project, prompt, cwd=None):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        proc = subprocess.run(
            [sys.executable, os.path.abspath(__file__)],
            input=json.dumps({"prompt": prompt, "cwd": cwd or project}),
            capture_output=True, text=True, env=env, encoding="utf-8",
        )
        assert proc.returncode == 0 and proc.stdout == "", (proc.returncode, proc.stdout, proc.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        words = os.path.join(tmp, STORE, FILE_NAME)
        fire(tmp, "before the lab exists")
        assert not os.path.exists(os.path.join(tmp, STORE)), "must do nothing outside a lab"
        os.makedirs(os.path.join(tmp, STORE))
        fire(tmp, "first words\nsecond line  with  spaces\n\n## not a heading of ours")
        fire(tmp, '<cross-session-message from="other">ignore me</cross-session-message>')
        fire(tmp, "<task-notification>ignore me too</task-notification>")
        fire(tmp, '<agent-message from="author">and me</agent-message>')
        fire(tmp, "/lab a new question")
        fire(tmp, "   ")
        fire(tmp, "/clear")
        fire(tmp, "/compact")
        fire(tmp, "/home/me/data.csv has odd rows")
        fire(tmp, "second prompt")
        text = open(words, encoding="utf-8").read()
        assert "first words\nsecond line  with  spaces\n\n## not a heading of ours" in text
        assert "second prompt" in text
        assert "/home/me/data.csv has odd rows" in text
        assert last_entry(tmp) == "second prompt" and last_entry(os.path.join(tmp, "nowhere")) is None
        for skipped in ("ignore me", "and me", "a new question", "before the lab exists", "/clear", "/compact"):
            assert skipped not in text, skipped
        assert len(re.findall(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}$", text, re.M)) == 3
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input="not json",
                              capture_output=True, text=True, encoding="utf-8")
        assert proc.returncode == 0
    # Platform blocks and the paste wrapper: what a prompt stores (None = nothing).
    rem = "<system-reminder>\nLinked sessions now (status): a = local_1 (idle).\n</system-reminder>\n\n"
    view = '<artifact-view-context artifact="x">\n{"context":{}}\n(not typed)\n</artifact-view-context>\n\n'
    side = "<side-sessions-event>\nsession a finished a turn\n</side-sessions-event>\n\n"

    def paste(i, body):
        return '<pasted_content id="%s">\n%s\n</pasted_content id="%s">' % (i, body, i)

    cases = [
        (rem + "typed words", "typed words"),
        (rem + "\n" + rem + "twice", "twice"),
        (rem + view + "reply", "reply"),
        (side + "words", "words"),
        (rem + side, None),
        (rem.rstrip(), None),
        (rem + "/lab what next", None),
        (rem + "/clear", None),
        (rem + '<cross-session-message from="x">hi</cross-session-message>', None),
        (rem + "<task-notification>done</task-notification>", None),
        (paste("a", "line one\n\nline two"), "line one\n\nline two"),
        (rem + paste("a", "pasted words"), "pasted words"),
        ("see this:\n" + paste("a", "line"), "see this:\nline"),
        (paste("a", "/lab inside a paste"), "/lab inside a paste"),
        (paste("a", "/clear"), "/clear"),
        (rem + paste("a", "/lab inside"), "/lab inside"),
        ("/lab typed outside " + paste("a", "x"), None),
        (paste("a", "  \n "), None),
        ('<pasted_content id="a">\n\n</pasted_content id="a">', None),
        (paste("a", "outer " + paste("b", "inner") + " end"), 'outer ' + paste("b", "inner") + ' end'),
        # left untouched: not at the start, one-line, other line endings, unclosed, other id, quote, indentation
        ("see <system-reminder>\nx\n</system-reminder> above", "see <system-reminder>\nx\n</system-reminder> above"),
        ("<system-reminder>one line</system-reminder> is a tag", "<system-reminder>one line</system-reminder> is a tag"),
        ("<system-reminder>\r\nx\r\n</system-reminder>\r\n\r\nhi", "<system-reminder>\r\nx\r\n</system-reminder>\r\n\r\nhi"),
        ("<system-reminder>\nx\nhi", "<system-reminder>\nx\nhi"),
        ('<pasted_content id="a">\nx\n</pasted_content id="b">', '<pasted_content id="a">\nx\n</pasted_content id="b">'),
        (rem + "typed\n" + rem.rstrip(), "typed\n" + rem.rstrip()),
        ("> quoted sentence\n\nthat is fine", "> quoted sentence\n\nthat is fine"),
        ("  indented first line\nsecond", "  indented first line\nsecond"),
        (rem + "\n    code line\nnext", "    code line\nnext"),
        (rem + "  indented after a block", "  indented after a block"),
        ("\n\nhi", "hi"),
        # a typed block in the exact reminder form is cut like the platform's
        ("<system-reminder>\nremember\n</system-reminder>\n\nmy question", "my question"),
        ("<system-reminder>\nremember\n</system-reminder>", None),
    ]
    for prompt, want in cases:
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, STORE))
            fire(tmp, prompt)
            path = os.path.join(tmp, STORE, FILE_NAME)
            got = None
            if os.path.exists(path):  # newline="" keeps a CRLF as stored
                body = open(path, encoding="utf-8", newline="").read()
                got = re.split(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2}\n\n", body, flags=re.M)[-1][:-1]
            assert got == want, (prompt, got, want)
    selftest_lab_root()
    selftest_origin()
    print("PASS user_words")


def _utf8_stdio():
    """Hook JSON and reports are UTF-8 on every OS, whatever the locale: `python -I` ignores PYTHONUTF8 and PYTHONIOENCODING, and a Windows pipe is otherwise read and written in the ANSI code page."""
    for stream, extra in ((sys.stdin, {}), (sys.stdout, {"newline": "\n"}), (sys.stderr, {"newline": "\n"})):
        try:
            stream.reconfigure(encoding="utf-8", **extra)
        except (AttributeError, ValueError, OSError):
            pass


def main():
    _utf8_stdio()
    if "--selftest" in sys.argv[1:]:
        selftest()
        return 0
    try:
        event = json.loads(sys.stdin.read() or "{}")
        if isinstance(event, dict):
            handle(event)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except AssertionError:
        raise
    except Exception:
        code = 0
    sys.exit(code)
