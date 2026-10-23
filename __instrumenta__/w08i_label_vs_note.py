# Lists every line of __statera__/synthesis.md and of the wave notes that names one claim id (wNN-cK) next to a label word (MEASURED, CHECKED, ESTIMATE, CONJECTURE, THEOREM) when that claim's current state per scripts/lab_status.py is not that label (below, escalated, superseded, withdrawn, unverified); input: those notes and __pondus__; output: TSV on stdout (file, line, claim, current state, label word on the line, text).
# usage: python3 -I __instrumenta__/w08i_label_vs_note.py > __reports__/wave-08/explorer-w08-i/label_vs_note.tsv
import sys, os, re, glob
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(root, "scripts"))
import lab_status as L
st = {c["id"]: c for c in L.read_claims(root)}
files = sorted(glob.glob(os.path.join(root, "__statera__", "wave-*.md")), key=L.natural) + [os.path.join(root, "__statera__", "synthesis.md")]
ID = re.compile(r"\bw0[1-8]-c\d+\b"); LAB = re.compile(r"\b(MEASURED|CHECKED|ESTIMATE|CONJECTURE|THEOREM)\b")
print("file\tline\tclaim\tcurrent\tlabel_on_line\tids_on_line\ttext")
for f in files:
    for n, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
        ids = sorted(set(ID.findall(line))); labs = sorted(set(LAB.findall(line)))
        if len(ids) != 1 or not labs: continue   # one claim per line, so the label word belongs to it
        i = ids[0]
        c = st.get(i)
        if not c: continue
        cur = c["current"]
        if cur in labs or any(cur.startswith(l) for l in labs): continue
        print(f"{os.path.relpath(f, root)}\t{n}\t{i}\t{cur}\t{','.join(labs)}\t1\t{line.strip()[:260]}")
