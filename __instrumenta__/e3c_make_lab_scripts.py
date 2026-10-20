# writes the E3c lab scripts: the 429 scripts of E3b with the fit and the near-fit script renamed so that both sort after position 200 of `ls -1`; input: OUTDIR (argv[1]); output: the scripts in OUTDIR and the positions of the two targets
"""usage: python3 -I e3c_make_lab_scripts.py OUTDIR

Names only change; the first lines and bodies are the E3b ones.  Fit: `binary_max_distinct_substrings_bruteforce.py` ->
`strings_binary_maximum_distinct_substrings_bruteforce.py`; near fit: `collatz_longest_stopping_time.py` ->
`steps_longest_collatz_stopping_time_below_limit.py`.  Stdlib only; no seeds.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
out = os.path.abspath(sys.argv[1])
subprocess.run([sys.executable, "-I", os.path.join(HERE, "e3b_make_lab_scripts.py"), out], check=True, capture_output=True)
RENAME = {"binary_max_distinct_substrings_bruteforce.py": "strings_binary_maximum_distinct_substrings_bruteforce.py",
          "collatz_longest_stopping_time.py": "steps_longest_collatz_stopping_time_below_limit.py"}
for a, b in RENAME.items():
    os.rename(os.path.join(out, a), os.path.join(out, b))
names = subprocess.run(["ls", out], capture_output=True, text=True).stdout.split()   # the order `ls` gives, as the workers see it
print(len(names), "scripts; positions in ls -1:", {b: names.index(b) + 1 for b in RENAME.values()}, "; ls -1 chars", sum(len(n) + 1 for n in names))
