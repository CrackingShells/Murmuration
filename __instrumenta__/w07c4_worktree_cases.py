"""Compares git_worktrees of two copies of lab_status.py (A = the `git worktree list` child, B = reads the git directory) on scratch repositories, from the two script paths to one line per case on stdout (o1 list equality, o3 failure cases of protocol P4); exit 1 on any difference or exception.

usage: w07c4_worktree_cases.py A.py B.py SCRATCH_DIR
Cases cover a removed, a locked and a prunable worktree, odd names, a symlinked path, calls from subfolders and other worktrees, then failures
(unreadable git directory, empty/garbage/missing `gitdir` files, missing HEAD, bare repository, submodule, separate git dir, GIT_DIR, core.worktree, no repository).
Each call has a 20 s alarm so that a hang shows as a failure.
"""
import importlib.util
import os
import shutil
import signal
import subprocess
import sys
import time


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(cwd, *args, env=None):
    e = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
             GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        e.pop(k, None)
    e.update(env or {})
    return subprocess.run(["git", "-C", cwd] + list(args), check=True, capture_output=True, text=True, env=e, timeout=30).stdout


def make_repo(path):
    os.makedirs(path)
    git(path, "init", "-q", "-b", "main")
    git(path, "commit", "-q", "--allow-empty", "-m", "x")


class Timeout(Exception):
    pass


def alarm(_sig, _frame):
    raise Timeout("hang over 20 s")


def run(mod, root, env=None):
    saved = {k: os.environ.get(k) for k in (env or {})}
    os.environ.update(env or {})
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(20)
    try:
        t = time.perf_counter()
        out = mod.git_worktrees(root)
        return out, time.perf_counter() - t
    except Exception as err:   # recorded as a difference, never swallowed
        return "EXC %s: %s" % (type(err).__name__, err), 0.0
    finally:
        signal.alarm(0)
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def main(a_path, b_path, scratch):
    A, B = load(a_path, "A"), load(b_path, "B")
    shutil.rmtree(scratch, ignore_errors=True)
    os.makedirs(scratch)
    scratch = os.path.realpath(scratch)
    cases = []   # (name, root, env)

    # ---- o1: a repository with the awkward worktrees
    main_repo = os.path.join(scratch, "repo")
    make_repo(main_repo)
    plain = os.path.join(scratch, "wt plain")           # a space in the name
    git(main_repo, "worktree", "add", "-q", "-b", "b/plain", plain)
    removed = os.path.join(scratch, "wt-removed")
    git(main_repo, "worktree", "add", "-q", "-b", "removed", removed)
    shutil.rmtree(removed)                              # prunable: directory gone
    locked = os.path.join(scratch, "wt-locked")
    git(main_repo, "worktree", "add", "-q", "-b", "locked", locked)
    git(main_repo, "worktree", "lock", "--reason", "because", locked)
    locked_gone = os.path.join(scratch, "wt-locked-gone")
    git(main_repo, "worktree", "add", "-q", "-b", "lockedgone", locked_gone)
    git(main_repo, "worktree", "lock", locked_gone)
    shutil.rmtree(locked_gone)
    detached = os.path.join(scratch, "wt-detached-é")
    git(main_repo, "worktree", "add", "-q", "--detach", detached)
    elsewhere = os.path.join(scratch, "other", "deep", "wt-far")
    os.makedirs(os.path.dirname(elsewhere))
    git(main_repo, "worktree", "add", "-q", "-b", "far", elsewhere)
    os.makedirs(os.path.join(main_repo, "sub", "dir"))
    link = os.path.join(scratch, "link")
    os.symlink(main_repo, link)
    cases += [("repo main", main_repo, None), ("repo main subfolder", os.path.join(main_repo, "sub", "dir"), None),
              ("repo via symlink", link, None), ("repo via symlink subfolder", os.path.join(link, "sub"), None),
              ("from linked 'wt plain'", plain, None), ("from linked detached", detached, None),
              ("from linked far", elsewhere, None), ("from linked locked", locked, None)]
    # a repository with no linked worktree
    solo = os.path.join(scratch, "solo")
    make_repo(solo)
    cases.append(("repo without worktrees", solo, None))
    # a new worktree on the lab's own repository, as a real run would have
    # ---- o3: failure cases, each on its own copy
    def fresh(name):
        d = os.path.join(scratch, name)
        make_repo(d)
        w = os.path.join(scratch, name + "-wt")
        git(d, "worktree", "add", "-q", "-b", name, w)
        return d, w

    d, w = fresh("f-nogit-perm")
    cases.append(("git dir unreadable (chmod 000 .git)", d, "chmod:" + os.path.join(d, ".git")))
    d, w = fresh("f-nowt-perm")
    cases.append(("worktrees dir unreadable (chmod 000 .git/worktrees)", d, "chmod:" + os.path.join(d, ".git", "worktrees")))
    d, w = fresh("f-wt-adm-perm")
    cases.append(("from linked worktree, admin dir unreadable", w, "chmod:" + os.path.join(d, ".git", "worktrees", os.listdir(os.path.join(d, ".git", "worktrees"))[0])))
    d, w = fresh("f-gitdir-missing")
    shutil.rmtree(w)
    cases.append(("gitdir points at a missing path (worktree removed)", d, None))
    d, w = fresh("f-gitdir-empty")
    open(os.path.join(d, ".git", "worktrees", os.listdir(os.path.join(d, ".git", "worktrees"))[0], "gitdir"), "w").close()
    cases.append(("gitdir file empty", d, None))
    d, w = fresh("f-gitdir-garbage")
    open(os.path.join(d, ".git", "worktrees", os.listdir(os.path.join(d, ".git", "worktrees"))[0], "gitdir"), "w").write("not a path\n")
    cases.append(("gitdir file garbage", d, None))
    d, w = fresh("f-gitdir-relative")
    open(os.path.join(d, ".git", "worktrees", os.listdir(os.path.join(d, ".git", "worktrees"))[0], "gitdir"), "w").write("../../../f-gitdir-relative-wt/.git\n")
    cases.append(("gitdir file relative", d, None))
    d, w = fresh("f-gitdir-nosuffix")
    open(os.path.join(d, ".git", "worktrees", os.listdir(os.path.join(d, ".git", "worktrees"))[0], "gitdir"), "w").write(w + "\n")
    cases.append(("gitdir file without /.git", d, None))
    d, w = fresh("f-gitdir-isdir")
    adm = os.path.join(d, ".git", "worktrees", os.listdir(os.path.join(d, ".git", "worktrees"))[0], "gitdir")
    os.remove(adm)
    os.mkdir(adm)
    cases.append(("gitdir is a directory", d, None))
    d, w = fresh("f-gitdir-absent")
    os.remove(os.path.join(d, ".git", "worktrees", os.listdir(os.path.join(d, ".git", "worktrees"))[0], "gitdir"))
    cases.append(("gitdir file absent", d, None))
    d, w = fresh("f-stray-file")
    open(os.path.join(d, ".git", "worktrees", "stray"), "w").write("x")
    cases.append(("stray file in .git/worktrees", d, None))
    d, w = fresh("f-nohead")
    os.remove(os.path.join(d, ".git", "HEAD"))
    cases.append(("HEAD missing: not a repository for git", d, None))
    d, w = fresh("f-dotgit-garbage")
    open(os.path.join(w, ".git"), "w").write("garbage\n")
    cases.append(("linked worktree's .git file garbage", w, None))
    d, w = fresh("f-dotgit-missing-admin")
    shutil.rmtree(os.path.join(d, ".git", "worktrees"))
    cases.append(("linked worktree whose admin dir is gone", w, None))
    d, w = fresh("f-commondir-bad")
    adm = os.path.join(d, ".git", "worktrees", os.listdir(os.path.join(d, ".git", "worktrees"))[0], "commondir")
    open(adm, "w").write("../../nowhere\n")
    cases.append(("commondir points nowhere (from the linked worktree)", w, None))
    d, w = fresh("f-corewt")
    git(d, "config", "core.worktree", d)
    cases.append(("core.worktree set", d, None))
    d, w = fresh("f-env")
    cases.append(("GIT_DIR set in the environment", w, "env:GIT_DIR=" + os.path.join(d, ".git")))
    bare = os.path.join(scratch, "bare.git")
    subprocess.run(["git", "init", "-q", "--bare", bare], check=True, capture_output=True)
    bw = os.path.join(scratch, "bare-wt")
    cases.append(("bare repository", bare, None))
    sep = os.path.join(scratch, "sep")
    os.makedirs(sep)
    subprocess.run(["git", "-C", sep, "init", "-q", "--separate-git-dir", os.path.join(scratch, "sepgit")], check=True, capture_output=True)
    cases.append(("separate git dir (.git is a file)", sep, None))
    sm_up = os.path.join(scratch, "sm-up")
    make_repo(sm_up)
    sm = os.path.join(scratch, "sm")
    make_repo(sm)
    git(sm, "-c", "protocol.file.allow=always", "submodule", "add", "-q", sm_up, "mod")
    cases.append(("submodule", os.path.join(sm, "mod"), None))
    outer = os.path.join(scratch, "outer")   # folders below a repository that are not (or not in) it, as git sees them
    make_repo(outer)
    git(outer, "worktree", "add", "-q", "-b", "outerwt", os.path.join(scratch, "outer-wt"))
    os.makedirs(os.path.join(outer, "plain", "sub"))
    open(os.path.join(outer, "file.txt"), "w").write("x")
    subprocess.run(["git", "init", "-q", "--bare", os.path.join(outer, "inner.git")], check=True, capture_output=True)
    cases += [("below a repo: plain folder two levels down", os.path.join(outer, "plain", "sub"), None),
              ("below a repo: folder that does not exist", os.path.join(outer, "plain", "nope"), None),
              ("below a repo: a file", os.path.join(outer, "file.txt"), None),
              ("below a repo: a bare repository", os.path.join(outer, "inner.git"), None),
              ("below a repo: inside .git", os.path.join(outer, ".git", "refs"), None)]
    plainfolder = os.path.join(scratch, "not-a-repo")
    os.makedirs(plainfolder)
    cases.append(("folder that is not a repository", plainfolder, None))
    cases.append(("folder that does not exist", os.path.join(scratch, "nope"), None))
    cases.append(("empty string root", "", None))

    bad = 0
    print("case | A | B | same | A ms | B ms")
    for name, root, mode in cases:
        env, restore = None, []
        if mode and mode.startswith("chmod:"):
            target = mode[6:]
            restore.append((target, os.stat(target).st_mode))
            os.chmod(target, 0)
        elif mode and mode.startswith("env:"):
            k, v = mode[4:].split("=", 1)
            env = {k: v}
        try:
            a, ta = run(A, root, env)
            b, tb = run(B, root, env)
        finally:
            for target, m in restore:
                os.chmod(target, m)
        same = a == b
        bad += not same
        short = lambda x: x if isinstance(x, str) else [os.path.relpath(p, scratch) if p.startswith(scratch) else p for p in x]
        print("%s | %s | %s | %s | %.1f | %.1f" % (name, short(a), short(b), "SAME" if same else "DIFFERENT", ta * 1e3, tb * 1e3))
    print("cases: %d, different: %d" % (len(cases), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
