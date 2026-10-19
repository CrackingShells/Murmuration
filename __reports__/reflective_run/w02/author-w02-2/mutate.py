#!/usr/bin/env python3
"""Does the selftest of scripts/user_words.py fail when the rule is broken? Each mutant is a copy of the file in a
temporary folder with one edit; the selftest must exit nonzero. Usage: python3 -I mutate.py   (about 5 s)"""
import os
import subprocess
import sys
import tempfile

SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "scripts", "user_words.py"))
text = open(SRC).read()
MUTANTS = [
    ("unwrap the paste before the command tests",
     "    prompt = strip_leading(prompt)  # the command tests below see the paste wrapper, so pasted `/lab ...` is kept\n",
     "    prompt = unwrap_pasted(strip_leading(prompt))\n"),
    ("never cut the leading blocks", "    prompt = strip_leading(prompt)  #", "    prompt = prompt  #"),
    ("cut the reminder anywhere, not only at the start", 'r"\\A\\s*<system-reminder>', 'r"\\s*<system-reminder>'),
    ("cut a one-line reminder too", 'r"\\A\\s*<system-reminder>\\n.*?\\n</system-reminder>', 'r"\\A\\s*<system-reminder>.*?</system-reminder>'),
    ("eat the indentation after a block", '</system-reminder>(?:[ \\t]*\\n)*"', '</system-reminder>\\s*"'),
    ("drop the third block", '    re.compile(r"\\A\\s*<side-sessions-event>.*?</side-sessions-event>(?:[ \\t]*\\n)*", re.S),\n', ""),
    ("cut one block only", "    changed = True\n    while changed:", "    changed = False\n    while changed:"),
    ("store a wrapper with nothing inside", "    if not words.strip() or not os.path.isdir", "    if not os.path.isdir"),
    ("ignore the closing id of the wrapper", "</pasted_content id=\"\\1\">'", "</pasted_content id=\"[^\"]*\">'"),
    ("trim the typed text", "    return append_words(root, words)", "    return append_words(root, words.strip())"),
]
for name, old, new in MUTANTS:
    assert text.count(old) == 1, name
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "user_words.py")
        open(path, "w").write(text.replace(old, new))
        r = subprocess.run([sys.executable, "-I", path, "--selftest"], capture_output=True, text=True)
        print("%-52s selftest %s" % (name, "FAILS (caught)" if r.returncode != 0 else "passes (NOT caught)"))
r = subprocess.run([sys.executable, "-I", SRC, "--selftest"], capture_output=True, text=True)
print("%-52s %s" % ("unmutated file", r.stdout.strip() or r.stderr.strip()[-200:]))
