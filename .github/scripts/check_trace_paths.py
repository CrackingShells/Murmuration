"""Fail when a commit typed as research trace touches the shipped plugin (D4 of __reports__/release_lifecycle/commit_vocabulary_v0.md).

    python3 -I .github/scripts/check_trace_paths.py <rev-range>

`cz check` reads messages and sees no paths, so this is the other half of the vocabulary: a commit whose type is one of TRACE and that changes a file under plugins/murmuration/
would ship code under a type that never releases. Merge commits are skipped (their files belong to the commits they merge). Standard library only; lives outside plugins/murmuration so that it is not shipped.
"""
import re
import subprocess
import sys

TRACE = {"claim", "verdict", "wave", "synthesis", "user_words", "reports", "rdm", "merge"}
SHIPPED = "plugins/murmuration/"


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True, encoding="utf-8").stdout


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    bad = 0
    for sha in git("rev-list", "--no-merges", "--reverse", argv[1]).split():
        subject = git("log", "-1", "--format=%s", sha).rstrip("\n")
        m = re.match(r"([a-z_]+)(?:\(|:|!)", subject)
        if not m or m.group(1) not in TRACE:
            continue
        files = [f for f in git("diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "-z", sha).split("\0") if f]
        hits = [f for f in files if f.startswith(SHIPPED)]
        if hits:
            bad += 1
            more = " (and %d more)" % (len(hits) - 5) if len(hits) > 5 else ""
            print("::error title=trace type on the shipped plugin::%s %s: type `%s` releases nothing, yet it changes %s%s. Use feat, fix, perf, refactor, test, build, ci, chore or docs for plugin changes, or split the commit." % (sha[:7], subject, m.group(1), ", ".join(hits[:5]), more))
    if bad:
        return 1
    print("check_trace_paths: no trace-typed commit in %s touches %s" % (argv[1], SHIPPED))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
