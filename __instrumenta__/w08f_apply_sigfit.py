# Applies the w08-f signature-to-thinking-tokens fit (thinking_tokens = A*(signature_chars - B), from w08f_sig_fit.py) to the per-turn signature lengths that explorer-w08-a stored for the 68 workers of waves 4-7, and compares the total with explorer-w08-a's fitted thinking tokens and USD; from <items dir>/*.json and explorer-w08-a's items.tsv to numbers on stdout.
# usage: w08f_apply_sigfit.py ITEMS_DIR ITEMS_TSV A B   (A, B from the fit; USD per carried token taken from explorer-w08-a's own thinking rows: their thinking USD / their thinking tokens) [ESTIMATE: assumes a lab worker's signature-to-token relation is that of these runs]
import sys, glob, json, csv
d, tsv, A, B = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
sig = []; n_turn = 0
for f in glob.glob(d + "/*.json"):
    for t in json.load(open(f))["turns"]:
        n_turn += 1
        if t.get("sig_chars", 0) > 0: sig.append(t["sig_chars"])
mine = [max(0.0, A * (s - B)) for s in sig]
rows = [r for r in csv.DictReader(open(tsv), delimiter="\t") if r["kind"] == "the agent's thinking blocks"]
tok = sum(float(r["est_tokens"]) for r in rows); usd = sum(float(r["first_write_usd"]) + float(r["read_usd"]) + float(r["rewrite_usd"]) for r in rows)
allusd = sum(float(r["first_write_usd"]) + float(r["read_usd"]) + float(r["rewrite_usd"]) for r in csv.DictReader(open(tsv), delimiter="\t"))
print("turns %d, with a thinking block %d; signature chars: mean %.0f median %d max %d; below B (fit gives 0): %d" % (n_turn, len(sig), sum(sig) / len(sig), sorted(sig)[len(sig) // 2], max(sig), sum(1 for s in sig if s <= B)))
print("explorer-w08-a thinking tokens (fit on context growth): %.0f ; USD %.2f of %.2f (%.1f%%)" % (tok, usd, allusd, 100 * usd / allusd))
print("this fit, signature -> tokens: %.0f tokens (%.2fx); same USD per token -> USD %.2f (%.1f%% of context USD)" % (sum(mine), sum(mine) / tok, usd / tok * sum(mine), 100 * usd / tok * sum(mine) / allusd))
