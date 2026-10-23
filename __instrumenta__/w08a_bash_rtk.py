# Groups the Bash tool results in items.tsv (w08a_cost.py) by command word and sums their context USD, and sums the part that rtk's page lists (git, search by shell, ls/tree, cat); input: items.tsv; output: bash_by_command.tsv and the rtk estimate line on stdout. Usage: w08a_bash_rtk.py FOLDER
import csv, collections, sys, os
folder = sys.argv[1]
R = list(csv.DictReader(open(os.path.join(folder, "items.tsv")), delimiter="\t"))
usd = lambda r: float(r["first_write_usd"]) + float(r["read_usd"]) + float(r["rewrite_usd"])
tot = sum(usd(r) for r in R)
agg = collections.defaultdict(lambda: [0, 0.0])
for r in R:
    if r["tool"] != "Bash":
        continue
    k, c = r["kind"], r["cls"]
    if c == "git": g = "git"
    elif c == "search": g = k
    elif c in ("bashdoc", "bashsrc", "bashother"):
        what = {"bashdoc": "document", "bashsrc": "source code", "bashother": "data/scratch file"}[c]
        g = ("cat " if k.endswith("via cat") else "sed/head/tail/wc/awk/cut/jq/diff ") + what
    elif c == "script":
        g = "lab script run" if k.startswith(("scripts/", "__instrumenta__/")) else "worker's own code (" + ("inline python" if "inline" in k else "scratch script") + ")"
    elif k.startswith("shell ls"): g = "ls"
    else: g = "other shell"
    agg[g][0] += 1; agg[g][1] += usd(r)
bt = sum(v[1] for v in agg.values())
LISTED_NOCAT = ("git", "find (shell)", "ls")
with open(os.path.join(folder, "bash_by_command.tsv"), "w") as fh:
    fh.write("command_group\tresults\tusd\tshare_of_all_context_usd\n")
    for g, v in sorted(agg.items(), key=lambda kv: -kv[1][1]):
        fh.write("%s\t%d\t%.4f\t%.4f\n" % (g, v[0], v[1], v[1] / tot))
        print("| %s | %d | %.2f | %.1f%% |" % (g, v[0], v[1], 100 * v[1] / tot))
isnocat = lambda g: g in LISTED_NOCAT or g.startswith("grep") or g.startswith("egrep")
strict = sum(v[1] for g, v in agg.items() if isnocat(g) or g.startswith("cat "))
nocat = sum(v[1] for g, v in agg.items() if isnocat(g))
print("all context USD %.2f; Bash results %.2f (%.1f%%); rtk-listed (git, search by shell, ls, cat) %.2f (%.1f%%); same without cat %.2f (%.1f%%)" % (tot, bt, 100 * bt / tot, strict, 100 * strict / tot, nocat, 100 * nocat / tot))
