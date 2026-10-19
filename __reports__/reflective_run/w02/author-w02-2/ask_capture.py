#!/usr/bin/env python3
"""Keep the user's answers to dialog questions, verbatim, in a lab project.

PROTOTYPE for a PostToolUse hook with matcher `AskUserQuestion`. The dialog's answers come back to the
agent as a tool result, so UserPromptSubmit never sees them. This script reads the hook JSON from stdin
and, when the project is an initialized lab, appends each question and the user's answer to
`__statera__/user_words.md` under a dated heading, through the same writer as user_words.py.

The answer is taken from `tool_response["answers"]` (question text -> text, or a list of texts for a
multi-select), else from `tool_input["answers"]`, else a string `tool_response` is stored as it is.
A dialog the user declined fires no PostToolUse hook, so nothing is stored for it.

The script never blocks and always exits 0. Anything unexpected is dropped silently.

Usage:
    ask_capture.py              read a hook event from stdin
    ask_capture.py --selftest   check the script on a temporary project
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for candidate in (HERE, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts"))):
    if os.path.exists(os.path.join(candidate, "user_words.py")):
        sys.path.insert(0, candidate)
        break
import user_words  # noqa: E402  (a sibling script: one writer for the user's words)

TOOL = "AskUserQuestion"
MARK = "(answer in the question dialog)"


def answers_of(event):
    """The `answers` mapping of the event, or None."""
    for field in ("tool_response", "tool_input"):
        value = event.get(field)
        if isinstance(value, dict) and isinstance(value.get("answers"), dict) and value["answers"]:
            return value["answers"]
    return None


def questions_of(event):
    """The question texts in the order they were asked."""
    for field in ("tool_response", "tool_input"):
        value = event.get(field)
        if isinstance(value, dict) and isinstance(value.get("questions"), list):
            return [q["question"] for q in value["questions"] if isinstance(q, dict) and isinstance(q.get("question"), str)]
    return []


def render(event):
    """The text to store, or None when the event carries no answer."""
    answers = answers_of(event)
    if answers is None:
        raw = event.get("tool_response")
        return "%s\n%s" % (MARK, raw) if isinstance(raw, str) and raw.strip() else None
    asked = questions_of(event)
    order = [q for q in asked if q in answers] + [q for q in answers if q not in asked]
    lines = [MARK]
    for question in order:
        answer = answers[question]
        lines.append("Q: %s" % question)
        if isinstance(answer, list):
            lines.append("A:")
            lines.extend("- %s" % item for item in answer)
        else:
            lines.append("A: %s" % answer)
    return "\n".join(lines)


def handle(event):
    """Record the answers of an AskUserQuestion event if the project is a lab. Returns the path or None."""
    if event.get("tool_name") != TOOL:
        return None
    text = render(event)
    root = user_words.project_root(event.get("cwd"))
    if text is None or not os.path.isdir(os.path.join(root, user_words.STORE)):
        return None
    return user_words.append_words(root, text)


def selftest():
    import subprocess
    import tempfile

    q = [{"question": "Which colour?", "header": "Pick", "options": [{"label": "red"}, {"label": "blue"}], "multiSelect": False},
         {"question": "Which extras?", "header": "Data", "options": [{"label": "a"}], "multiSelect": True}]
    answers = {"Which extras?": ["imatrix quants", "another family, but newer, 日本語", "FP8 pair"], "Which colour?": "blue\nand a second line"}
    event = {"tool_name": TOOL, "tool_input": {"questions": q, "answers": answers},
             "tool_response": {"questions": q, "answers": answers}}
    want = ("%s\nQ: Which colour?\nA: blue\nand a second line\nQ: Which extras?\nA:\n- imatrix quants\n"
            "- another family, but newer, 日本語\n- FP8 pair" % MARK)
    assert render(event) == want, render(event)
    assert render({"tool_name": TOOL, "tool_input": {"questions": q, "answers": answers}}) == want   # input only
    assert render({"tool_name": TOOL, "tool_response": "The user answered: x"}) == MARK + "\nThe user answered: x"
    assert render({"tool_name": TOOL, "tool_response": {"questions": q}}) is None
    assert render({"tool_name": TOOL}) is None and render({"tool_name": TOOL, "tool_response": {"answers": {}}}) is None

    def fire(project, payload):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input=json.dumps(payload),
                              capture_output=True, text=True, env=env)
        assert proc.returncode == 0 and proc.stdout == "", (proc.returncode, proc.stdout, proc.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        fire(tmp, dict(event, cwd=tmp))
        assert not os.path.exists(os.path.join(tmp, user_words.STORE)), "must do nothing outside a lab"
        os.makedirs(os.path.join(tmp, user_words.STORE))
        fire(tmp, dict(event, cwd=tmp))
        fire(tmp, dict(event, cwd=tmp, tool_name="Bash"))
        fire(tmp, {"tool_name": TOOL, "cwd": tmp, "tool_response": {"questions": q}})
        assert user_words.last_entry(tmp) == want
        text = open(os.path.join(tmp, user_words.STORE, user_words.FILE_NAME), encoding="utf-8").read()
        assert text.count(MARK) == 1
        proc = subprocess.run([sys.executable, os.path.abspath(__file__)], input="not json", capture_output=True, text=True)
        assert proc.returncode == 0
    print("PASS ask_capture")


def main():
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
