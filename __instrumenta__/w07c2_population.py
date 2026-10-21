# Lists the transcript JSONL files of the lab's recorded sessions (project folders whose name holds "urmuration", plus the combinatorics study) from ~/.claude/projects; output: one path per line on stdout; used by the other w07c2_* scripts as their population.
import os, sys
def population(base=None):
    base = base or os.path.expanduser("~/.claude/projects")
    out = []
    for d in sorted(os.listdir(base)):
        if "urmuration" in d or "combinatorics-on-binary" in d:
            p = os.path.join(base, d)
            out += sorted(os.path.join(p, f) for f in os.listdir(p) if f.endswith(".jsonl"))
    return out
if __name__ == "__main__":
    print("\n".join(population()))
