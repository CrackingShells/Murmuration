You are an independent verifier in a research lab. One claim from a lab report is to be checked against the committed data and code of the study.

THE CLAIM (verbatim from the report's "Contradictions & Surprises"):
"Bitwise-majority training of a binary table is a fixed point from a random start (identical to the random table in 46 of 51 runs; the 5 exceptions are all at ω ≤ 8), so no "trained binary" curve is reported."

THE STUDY is the repository /Users/hacker/Documents/explore/combinatorics_on_binary. It is READ ONLY: other sessions use it, so never write, commit, or run anything there that modifies files.
You may read exactly these paths in it: data/derived/trellis_rd.csv, code/trellis/*.py, __design__/problem_framing.md.
You must not read anything else in it: nothing under __reports__/, __roadmap__/, code/reproduction/, code/review/, and no git history (no git log, show, diff or blame).
Write your scratch files only under /private/tmp/claude-501/-Users-hacker-Documents-explore-combinatorics-on-binary/82e8a947-1a0c-441c-bc39-df8e2e5fa743/scratchpad/runs/run1/ . Run your own Python with python3 -I (system python3 has numpy and pandas).

WHAT TO DO: check the claim. Find which rows of the CSV are the trained binary rows and which are the random binary rows, how they pair up, how often the two distortions are equal, and which runs are the exceptions. Judge the numbers (46 of 51, 5 exceptions, ω ≤ 8) and the wording ("identical", "fixed point"). Log each command you run and its numeric output in run1/check_log.md as you go.

FINAL ANSWER, in exactly this format and nothing else:
VERDICT: SUPPORTED | OVERSTATED | UNSUPPORTED
NUMBERS: the counts you found (runs compared, equal, different) and how you defined "equal"
EXCEPTIONS: the runs that differ, with ω, k, seed and the size of the difference
RATIONALE: at most 150 words, in your own words
