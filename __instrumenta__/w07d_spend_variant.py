"""Runs scripts/lab_status.py's report_spend with its transcript parsing replaced by a variant (algorithm, process pool, or the Rust helper), from a lab root to the same `--spend` text on stdout.

usage: w07d_spend_variant.py <lab root> VARIANT [W]   VARIANT (suffix +nogit: no git process): orig | cache (lab_status's own cache, left on) | alg (whole-file read + one regex) | par (alg in W forked workers) | rust (w07d_rs on W threads, $W07D_RS = binary)
The import is lab_status.py unchanged; only L.read_transcript is replaced, by a lookup into results computed up front for every file load_sessions would read (mains + subagent files). The cache is forced off except for variant `cache`.
"""
import sys, os, glob, subprocess, tempfile
root = os.path.abspath(sys.argv[1]); variant = sys.argv[2]; nogit = variant.endswith("+nogit"); variant = variant.replace("+nogit", ""); W = int(sys.argv[3]) if len(sys.argv) > 3 else 1
sys.path.insert(0, os.path.join(root, "scripts"))
if variant != "cache":
    os.environ["LAB_STATUS_CACHE"] = "off"
import lab_status as L
if nogit:   # the worktree list read from .git files instead of a `git worktree list` process (w07d_stages.py checks it gives the same paths)
    def _git_files(root):
        p = os.path.join(root, ".git")
        common = os.path.dirname(os.path.dirname(open(p).read().strip()[len("gitdir:"):].strip())) if os.path.isfile(p) else p
        return [os.path.dirname(common)] + [os.path.dirname(open(g).read().strip()) for g in sorted(glob.glob(os.path.join(common, "worktrees", "*", "gitdir")))]
    L.git_worktrees = _git_files
if variant not in ("orig", "cache"):
    sys.argv = [sys.argv[0], root]   # w07d_parsers reads argv[1] only at import
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import w07d_parsers as P
    orig_load = L.load_sessions
    def rust_parse(files):
        with tempfile.TemporaryDirectory() as td:
            lst, dmp = os.path.join(td, "files"), os.path.join(td, "dump")
            open(lst, "w").write("\n".join(files) + "\n")
            subprocess.run([os.environ["W07D_RS"], "--files", lst, "--threads", str(W), "--item", "--dump", dmp], check=True, stderr=subprocess.DEVNULL)
            res = {f: ({}, None, None) for f in files}
            for line in open(dmp):
                p = line.rstrip("\n").split("\t")
                if p[0] == "S" and p[2] != "-":
                    res[p[1]] = (res[p[1]][0], res[p[1]][1], p[2])
                elif p[0] == "C" and p[2] != "-":
                    res[p[1]] = (res[p[1]][0], {"totalCostUSD": float(p[2])}, res[p[1]][2])
                elif p[0] == "M":
                    _, path, key, model, i, o, cr, cw, c1, c5, ts, sid, fin = p
                    k = key[2:] if key[0] == "s" else int(key[2:])
                    usage = {"input_tokens": int(i), "output_tokens": int(o), "cache_read_input_tokens": int(cr), "cache_creation_input_tokens": int(cw),
                             "cache_creation": {"ephemeral_1h_input_tokens": int(c1), "ephemeral_5m_input_tokens": int(c5)}}
                    res[path][0][k] = {"model": model, "usage": usage, "ts": None if ts == "-" else ts, "sid": None if sid == "-" else sid, "final": fin == "1"}
            return res
    def prefetch(mains, warnings):
        files = list(mains)
        for m in mains:
            files += sorted(glob.glob(os.path.join(m[:-len(".jsonl")], "subagents", "**", "agent-*.jsonl"), recursive=True))
        if variant == "alg":
            return {f: P.parse_buf_re(f, warnings) for f in files}
        if variant == "par":
            return P.parse_many(files, W, P.parse_buf_re)
        return rust_parse(files)
    def load(mains, warnings):
        got = prefetch(mains, warnings)
        L.read_transcript = lambda path, w: got[path]
        return orig_load(mains, warnings)
    L.load_sessions = load
print("\n".join(L.report_spend(root)))
