# w06-c8 (E3 v1, side check): how many tracked script files of this repository (.py .sh .bash .zsh .js .ts .mjs) carry text the v1 content check would deny (the bypass words, or a literal --setting-sources value without user), i.e. the files an agent could no longer Write or Edit without the user's yes; inputs: git ls-files of the repository; outputs: counts and file names on stdout. Run from the repository root.
import os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import permission_guard as G

files = [f for f in subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n") if f.lower().endswith(G.SCRIPT_EXT)]
hit = []
for f in files:
    try:
        t = open(f, errors="replace").read()
    except OSError:
        continue
    if G.g4_script({"file_path": f, "content": t}):
        hit.append(f)
print("script files %d, would be denied on a full rewrite %d" % (len(files), len(hit)))
for f in hit:
    print(" ", f)
