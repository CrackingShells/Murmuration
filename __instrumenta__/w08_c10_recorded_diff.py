# w08-c10: decides every recorded Bash/Write/Edit/MultiEdit/NotebookEdit call of the lab's transcript folders (the set of scripts/check_guard_equal.py) with the Python guard of two checkouts (before, after), in process, and lists the calls whose decision changed; inputs: --before DIR, --after DIR (checkouts with scripts/permission_guard.py), the folders ~/.claude/projects/*Murmuration* (read only); output: stdout (counts; newly denied with the first 200 characters of the command; newly allowed, which must be none) and --out JSON.
# usage: python3 -I w08_c10_recorded_diff.py --before DIR --after DIR [--out FILE] [--show N]
import argparse, glob, importlib.util, json, os, sys


def load(repo, tag):
    spec = importlib.util.spec_from_file_location("pg_" + tag, os.path.join(repo, "scripts", "permission_guard.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def calls(folders):
    seen = set()
    for folder in folders:
        for f in sorted(glob.glob(folder + "/**/*.jsonl", recursive=True)):
            for line in open(f, errors="replace"):
                if '"tool_use"' not in line:
                    continue
                try:
                    m = json.loads(line)
                except ValueError:
                    continue
                if m.get("type") != "assistant":
                    continue
                for b in (m.get("message", {}).get("content") or []):
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Bash", "Write", "Edit", "MultiEdit", "NotebookEdit") and b["id"] not in seen:
                        seen.add(b["id"])
                        yield b["id"], dict(tool_name=b["name"], tool_input=b["input"], cwd=m.get("cwd") or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out")
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args()
    pb, pa = load(a.before, "b"), load(a.after, "a")
    folders = sorted(glob.glob(os.path.expanduser("~/.claude/projects/*Murmuration*")))
    n, den_b, den_a, newly_denied, newly_allowed = 0, 0, 0, [], []
    for cid, ev in calls(folders):
        n += 1
        try:
            db = pb.decide(ev)
        except Exception:
            db = ("G?", "exception")
        try:
            da = pa.decide(ev)
        except Exception:
            da = ("G?", "exception")
        den_b += bool(db)
        den_a += bool(da)
        txt = (ev["tool_input"].get("command") or ev["tool_input"].get("file_path") or "") if isinstance(ev["tool_input"], dict) else ""
        if da and not db:
            newly_denied.append(dict(id=cid, tool=ev["tool_name"], rule=da[0], text=txt[:300]))
        if db and not da:
            newly_allowed.append(dict(id=cid, tool=ev["tool_name"], rule=db[0], text=txt[:300]))
    print("recorded calls %d in %d folders; denied before %d, after %d; newly denied %d; newly allowed %d" % (n, len(folders), den_b, den_a, len(newly_denied), len(newly_allowed)))
    for r in newly_denied[:a.show]:
        print("  NEWLY DENIED %s %s %s | %s" % (r["id"], r["tool"], r["rule"], r["text"][:200].replace("\n", "\\n")))
    for r in newly_allowed[:a.show]:
        print("  NEWLY ALLOWED %s %s %s | %s" % (r["id"], r["tool"], r["rule"], r["text"][:200].replace("\n", "\\n")))
    if a.out:
        json.dump(dict(calls=n, denied_before=den_b, denied_after=den_a, newly_denied=newly_denied, newly_allowed=newly_allowed), open(a.out, "w"), indent=1)


main()
