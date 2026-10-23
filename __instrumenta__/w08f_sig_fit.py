# Fits platform-reported thinking tokens against the thinking block's signature length (characters) over every request of the w08-f runs that carry a thinking block: from <S>/runs/{T,C,think}-*.jsonl to a fit line and residual summary on stdout, one row per request in <out.tsv>.
# usage: w08f_sig_fit.py S OUT.tsv   (the signature is the only part of a redacted thinking block that is stored in a transcript, so this is the conversion a transcript reader can use; request-level, n = requests with thinking_tokens > 0)
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w08f_requests import parse
import numpy as np
S, out = sys.argv[1], sys.argv[2]; X = []; Y = []; rows = []
for pre in ("T-", "C-", "think-"):
    for f in sorted(glob.glob(os.path.join(S, "runs", pre + "*.jsonl"))):
        for r in parse(f)[0]:
            if (r["think"] or 0) > 0 and r["sig"] > 0:
                X.append(r["sig"]); Y.append(r["think"]); rows.append((os.path.basename(f)[:-6], r["k"], r["sig"], r["think"]))
X = np.array(X, float); Y = np.array(Y, float)
A = np.vstack([X, np.ones_like(X)]).T; (a, b), *_ = np.linalg.lstsq(A, Y, rcond=None); res = Y - A @ (a, b)
a0 = (X @ Y) / (X @ X)
open(out, "w").write("run\tk\tsignature_chars\tthinking_tokens\n" + "".join("%s\t%d\t%d\t%d\n" % r for r in rows))
print("n=%d requests; thinking_tokens = %.4f*signature_chars + %.1f ; R2 %.4f ; resid sd %.1f tokens ; through origin: %.4f tokens/char (%.2f chars/token)" % (len(Y), a, b, 1 - res.var() / Y.var(), res.std(), a0, 1 / a0))
print("signature chars range %d-%d, thinking tokens range %d-%d" % (X.min(), X.max(), Y.min(), Y.max()))
