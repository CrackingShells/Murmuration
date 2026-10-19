"""Independent re-derivation of w01-c9 headline: distinct typed prompts, how many the patched
rule changes, how many it drops. Imports the SCRATCH (patched) hook and the SHIPPED hook only for
the rule under test; the extraction is my own."""
import glob, importlib.util, json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
SHIPPED = load("/Users/hacker/Documents/tmp/claude-worktrees/Murmuration/murmuration-system-optimization-8cff9e/scripts/user_words.py", "shipped")
PATCHED = load(os.path.join(HERE, "scratch/scripts/user_words.py"), "patched")
D = "/Users/hacker/.claude/projects/-Users-hacker-Documents-explore-combinatorics-on-binary/"
THIS = "/Users/hacker/.claude/projects/-Users-hacker-Documents-tmp-claude-worktrees-Murmuration-murmuration-system-optimization-8cff9e/ab96c5ed-ead3-4b36-9671-6076e3914087.jsonl"
FILES = sorted(glob.glob(D + "*.jsonl")) + [THIS]

def text_of(content):
    if isinstance(content, str): return content
    return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")

def human(o): return isinstance(o, dict) and o.get("kind") == "human"

def stored(mod, prompt):
    """What the hook would store (None if skipped): run handle() into a temp lab."""
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, "__statera__"))
        old = os.environ.pop("CLAUDE_PROJECT_DIR", None)
        try:
            p = mod.handle({"prompt": prompt, "cwd": t})
        finally:
            if old: os.environ["CLAUDE_PROJECT_DIR"] = old
        if not p: return None
        s = open(p).read().split("\n## ", 1)[1]
        return s.split("\n", 2)[2].rstrip("\n")

typed, other = {}, {}
raw_fired = collections.Counter()
for f in FILES:
    for l in open(f):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("isSidechain"): continue
        if r.get("type") == "user" and not r.get("isMeta") and "toolUseResult" not in r and "sourceToolUseID" not in r:
            c = r.get("message", {}).get("content")
            if isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c): continue
            t = text_of(c)
            if human(r.get("origin")): typed.setdefault(("u", r["uuid"]), t); raw_fired[f[-14:-6]] += 1
            elif r.get("origin") is None and not r.get("turnOrigin"): other.setdefault(("u", r["uuid"]), ("noorigin", t))
            else: other.setdefault(("u", r["uuid"]), (json.dumps(r.get("origin"))[:30], t))
        elif r.get("type") == "attachment" and r["attachment"].get("type") == "queued_command" and r["attachment"].get("commandMode") == "prompt":
            a = r["attachment"]
            if human(a.get("origin")) and not a.get("isMeta"): typed.setdefault(("q", a["delivery_id"]), a["prompt"] if isinstance(a["prompt"], str) else text_of(a["prompt"]))
            else: other.setdefault(("q", a["delivery_id"]), (json.dumps(a.get("origin"))[:30], a["prompt"] if isinstance(a["prompt"], str) else text_of(a["prompt"])))
print("typed distinct keys:", len(typed), " by kind:", collections.Counter(k[0] for k in typed))
print("other (non-typed, non-meta-tool) keys:", len(other), collections.Counter(v[0] for v in other.values()))
# distinct by text too
print("distinct texts among typed:", len(set(typed.values())))
changed = dropped = unchanged = 0; chars = [0, 0]
for k, t in typed.items():
    a, b = stored(SHIPPED, t), stored(PATCHED, t)
    chars[0] += len(a or ""); chars[1] += len(b or "")
    if b is None and a is not None: dropped += 1; print("DROPPED", k, repr(t[:80]))
    elif a != b: changed += 1
    else: unchanged += 1
print("changed", changed, "unchanged", unchanged, "dropped", dropped, "chars shipped->patched", chars)
# non-typed
sh = pa = diff = 0
for k, (kind, t) in other.items():
    a, b = stored(SHIPPED, t), stored(PATCHED, t)
    sh += a is not None; pa += b is not None; diff += a != b
print("non-typed:", len(other), "shipped stores", sh, "patched stores", pa, "differ", diff)
for k, (kind, t) in other.items():
    if stored(PATCHED, t) is not None: print("  still stored:", k, kind, repr(t[:70]))
print("--- non-typed, shipped stores:")
for k, (kind, t) in other.items():
    a, b = stored(SHIPPED, t), stored(PATCHED, t)
    if a is not None:
        print(k[0], k[1][:8], kind, "| patched:", "stored" if b is not None else "skipped", "|", repr(t[:60]), len(t))
