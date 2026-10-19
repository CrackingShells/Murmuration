"""List every `## verdict:` section (all claim files) with more than one line the script reads as `verdict:`."""
import glob, importlib.util, os, sys
root = sys.argv[1]
sp = importlib.util.spec_from_file_location("l", os.path.join(root, "scripts", "lab_status.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
n = 0
for path in sorted(glob.glob(os.path.join(root, "__pondus__", "*.md")), key=m.natural):
    for name, lines in m.parse_claim(m.read(path))["sections"]:
        hits = [(i, l.strip()) for i, l in enumerate(lines) if m.VERDICT_RE.match(l)]
        n += 1
        if len(hits) > 1:
            print("%s section %s: %d verdict lines: %s; changed_by below the earlier: %s" % (
                os.path.basename(path), name, len(hits), [h[1] for h in hits],
                any(m.CHANGED_BY_RE.match(l) for l in lines[hits[-2][0] + 1:])))
print("%d verdict sections read" % n)
