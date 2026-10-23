# Lists every line in later waves' puzzle files, wave notes, synthesis and claim files that names an earlier claim id (wNN-cK) together with a correction word (wrong, overstated, defect, bug, ...); input: __scrupuli__, __statera__, __pondus__ files; output: TSV (referring file, line number, referred claim, that claim's current state, line text) on stdout.
# usage: python3 -I __instrumenta__/w08i_later_refs.py > __reports__/wave-08/explorer-w08-i/later_refs.tsv
import sys, os, re, glob
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(root, "scripts"))
import lab_status as L
state = {c["id"]: c["current"] for c in L.read_claims(root)}
KW = re.compile(r"\b(wrong|overstat\w*|defect\w*|bug\w*|error\w*|mistake\w*|misread\w*|misaligned|untimed|confound\w*|did not hold|does not hold|not hold|incorrect\w*|retract\w*|withdr\w*|correct(ed|ion)\w*|fail(ed|s|ure)\w*|too (strong|wide)|missed|rests on|errata|artefact|artifact)\b", re.I)
ID = re.compile(r"\bw0([1-8])-c(\d+)\b")
files = sorted(glob.glob(os.path.join(root, "__scrupuli__", "*.md")) + glob.glob(os.path.join(root, "__statera__", "wave-*.md")) + [os.path.join(root, "__statera__", "synthesis.md")] + glob.glob(os.path.join(root, "__pondus__", "*.md")), key=L.natural)
print("file\tline\tclaim\tstate\ttext")
for f in files:
    rel = os.path.relpath(f, root)
    own = os.path.basename(f)[:-3] if rel.startswith("__pondus__") else ""
    m = re.search(r"wave-(\d\d)", rel)
    fwave = int(m.group(1)) if m else (int(own[1:3]) if own else 99)
    for n, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
        ids = {f"w0{a}-c{b}" for a, b in ID.findall(line)}
        if not ids or not KW.search(line): continue
        for i in sorted(ids):
            if i == own: continue
            if int(i[1:3]) < fwave or (rel.startswith("__pondus__") and int(i[1:3]) <= fwave and i < own):
                print(f"{rel}\t{n}\t{i}\t{state.get(i,'?')}\t{line.strip()[:400].replace(chr(9),' ')}")
