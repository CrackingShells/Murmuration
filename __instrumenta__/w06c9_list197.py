# w06-c9: writes the 197 distinct worker-transcript paths of waves 1-5 (sorted unique, ~ expanded) from the committed list of 291; inputs: __reports__/reflective_run/w04/author-w04-4/derived/replay_transcripts_291.txt; output: the paths, one per line, on stdout
import os
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "__reports__/reflective_run/w04/author-w04-4/derived/replay_transcripts_291.txt")
print("\n".join(sorted({os.path.expanduser(l.strip()) for l in open(src) if l.strip()})))
