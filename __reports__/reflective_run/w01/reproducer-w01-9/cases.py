"""Fire the patched hook (scratch copy) on my own inputs; print what is stored."""
import json, os, subprocess, sys, tempfile
HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch/scripts/user_words.py")
REM = "<system-reminder>\nLinked sessions now (status): a = local_1 (idle).\n</system-reminder>\n\n"
def P(i, body): return '<pasted_content id="%s">\n%s\n</pasted_content id="%s">' % (i, body, i)
CASES = [
 ("pasted /lab", P("p1", "/lab does this survive")),
 ("pasted /clear", P("p2", "/clear")),
 ("typed /lab outside wrapper + paste", "/lab why " + P("p3", "pasted tail")),
 ("typed /lab, no wrapper", "/lab why?"),
 ("whitespace-only wrapper", P("p4", "  \n ")),
 ("empty wrapper", '<pasted_content id="p4b">\n\n</pasted_content id="p4b">'),
 ("nested wrapper", P("a", "outer " + P("b", "inner") + " end")),
 ("reminder then /lab", REM + "/lab what next"),
 ("reminder then plain words", REM + "plain words"),
 ("reminder then paste", REM + P("p5", "pasted words")),
 ("reminder then pasted /lab", REM + P("p6", "/lab inside")),
 ("reminder only", REM.rstrip()),
 ("reminder then /clear", REM + "/clear"),
 ("user types a reminder tag (leading, exact form)", "<system-reminder>\nremember to cite\n</system-reminder>\n\nand then my question"),
 ("user types reminder tag leading, nothing after", "<system-reminder>\nremember to cite\n</system-reminder>"),
 ("user types reminder mid-text", "look at this <system-reminder>\nx\n</system-reminder> tag"),
 ("user types reminder one-line", "<system-reminder>x</system-reminder> hi"),
 ("reminder CRLF form", "<system-reminder>\r\nx\r\n</system-reminder>\r\n\r\nhi"),
 ("unclosed reminder", "<system-reminder>\nx\nhi"),
 ("two reminders, second after typed text", REM + "typed\n" + REM),
 ("paste wrapper mismatched id", '<pasted_content id="a">\nx\n</pasted_content id="b">'),
 ("cross-session after reminder", REM + '<cross-session-message from="x">hi</cross-session-message>'),
 ("task-notification after reminder", REM + "<task-notification>done</task-notification>"),
 ("text before then paste", "see this:\n" + P("p7", "line")),
]
for name, prompt in CASES:
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, "__statera__"))
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        r = subprocess.run([sys.executable, "-I", HOOK], input=json.dumps({"prompt": prompt, "cwd": t}), capture_output=True, text=True, env=env)
        f = os.path.join(t, "__statera__", "user_words.md")
        stored = None
        if os.path.exists(f):
            s = open(f).read().split("\n## ", 1)[1]
            stored = s.split("\n", 2)[2].rstrip("\n") if s.count("\n") >= 2 else s
        print("%-52s rc=%d -> %r" % (name, r.returncode, stored))
