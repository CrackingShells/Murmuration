# Shows that the w08-c5 replay can fail: copies the tree of a git revision, applies one deliberate fault to the Python script or to the Rust source, builds the test binary (cargo, offline, feature testclock), runs w08_c5_replay_extra.py on the c5_ scenarios (exact pass, quick), and prints how many scenarios differ between Python and Rust. The unmutated copy must print 0.
# usage: python3 -I w08_c5_mutants.py REPO REV SCRATCH > table.md      (about 20 s per row)
import json, os, shutil, subprocess, sys, io, tarfile
repo, rev, S = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
HERE = os.path.dirname(os.path.abspath(__file__))
MUT = [("none", None, None, None),
       ("rust: no pool (names never flagged)", "rust/src/budget.rs", "if all_str && names.len() > 1 {", "if false && all_str && names.len() > 1 {"),
       ("rust: the answer does not move the record", "rust/src/budget.rs", "|| std::fs::remove_file(&path).is_err() {\n            continue;", "|| true {\n            continue;"),
       ("rust: note path is the main checkout's", "rust/src/budget.rs", "root = root.trim_end_matches('/')", 'root = format!("/main{}", &root[..0])'),
       ("python: no `named` line", "scripts/budget.py", 'handback.log_line(root, dict(event="named"', 'None and handback.log_line(root, dict(event="named"'),
       ("python: pool without sorting", "scripts/budget.py", 'pool = ",".join(sorted(set(names)))', 'pool = ",".join(list(dict.fromkeys(names))[::-1])'),
       ("python: start claims by order only", "scripts/budget.py", "claim_by_id(root, aid) or claim_pending", "None or claim_pending")]
print("| mutation | scenarios | differing scenarios | differing events |\n|:--|--:|--:|--:|")
for i, (label, path, a, b) in enumerate(MUT):
    d = os.path.join(S, "mut%d" % i); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    tarfile.open(fileobj=io.BytesIO(subprocess.run(["git", "-C", repo, "archive", rev, "scripts", "rust", "__instrumenta__"], capture_output=True, check=True).stdout)).extractall(d, filter="fully_trusted")
    for f in os.listdir(HERE):
        if f.startswith("w08_c5_") or f.startswith("w08c1_"):
            shutil.copy(os.path.join(HERE, f), os.path.join(d, "__instrumenta__", f))
    if path:
        s = open(os.path.join(d, path)).read()
        assert a in s, (label, a)
        open(os.path.join(d, path), "w").write(s.replace(a, b, 1))
    subprocess.run(["cargo", "build", "--release", "--offline", "--features", "testclock", "--target-dir", d + "/T", "--manifest-path", d + "/rust/Cargo.toml"], capture_output=True, check=True)
    out = d + "/out"
    subprocess.run([sys.executable, "-I", d + "/__instrumenta__/w08_c5_replay_extra.py", "--repo", d, "--rust", d + "/T/release/murmuration", "--scratch", d + "/scr", "--out", out, "--only", "c5_", "--quick", "--jobs", "4"], capture_output=True)
    res = json.load(open(out + "/replay_exact.json"))["total"]
    print("| %s | %d | %d | %d |" % (label, res["scenarios"], res["differing_scenarios"], res["differing_events"]))
