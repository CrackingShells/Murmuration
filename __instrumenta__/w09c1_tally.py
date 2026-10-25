"""Re-counts the 33 rows of table A of explorer-w09-f's findings: rows per current-label word of the claim column and per category of the last column, against the row lists named in the findings' own tally line and Result paragraph; input: the findings file (argv[1]); output: text on stdout."""
import re, sys, collections
t = open(sys.argv[1]).read()
rows = {}
for l in t.splitlines():
    m = re.match(r"\| (\d+) \| (.*) \|$", l)
    if m and 1 <= int(m.group(1)) <= 40:
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) == 6: rows[int(c[0])] = c
print("rows parsed:", len(rows), "ids", min(rows), "-", max(rows), "complete:", sorted(rows) == list(range(1, 34)))
lab = collections.defaultdict(list)
for i, c in rows.items():
    cl = c[2]; first = re.sub(r"^[^·]*· ", "", cl)
    w = "below MEASURED" if "below MEASURED" in first.split(",")[0] else ("CHECKED" if "CHECKED" in first.split(",")[0] else ("CONJECTURE" if "CONJECTURE" in first.split(",")[0] else "MEASURED"))
    lab[w].append(i)
print("claim-column label (first claim on the row):", {k: (len(v), v) for k, v in lab.items()})
cat = collections.defaultdict(list)
for i, c in rows.items():
    last = c[5]
    k = "done here" if "done here" in last else ("R" if re.match(r"R\b", last) and "R-" not in last[:3] else ("P" if last.startswith("P") else ("N" if last.startswith("N") else ("thin" if "too thin" in last else "other:" + last[:20]))))
    cat[k].append(i)
print("last column by category:", {k: (len(v), v) for k, v in cat.items()})
tally = {"done here": [4, 7, 13, 16, 20, 23, 25, 28, 31], "thin": [27], "R": [8, 10, 11, 14, 19, 21, 22], "P": [3, 15, 26], "N": [1, 2, 5, 6, 9, 12, 17, 18, 24, 29, 30, 32, 33]}
allr = sorted(sum(tally.values(), []))
print("tally line: sizes", {k: len(v) for k, v in tally.items()}, "sum", len(allr), "distinct", len(set(allr)), "covers 1-33:", allr == list(range(1, 34)))
for k in tally: print(" ", k, "lines agree with column:", sorted(tally[k]) == sorted(cat.get(k, [])), "only in tally", sorted(set(tally[k]) - set(cat.get(k, []))), "only in column", sorted(set(cat.get(k, [])) - set(tally[k])))
