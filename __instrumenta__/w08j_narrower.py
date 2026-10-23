# w08-j: tries narrower tests as offline variants of scripts/permission_guard.py (the guard file is loaded and patched in memory only, never written) on the frozen replay set; input: the frozen set JSON (argv[1]); output: per variant the false denials cleared, the true denials lost (new false allows, listed by id and source) and the registered attack payloads still denied, on stdout. Usage: python3 -I w08j_narrower.py SET.json
import importlib.util, json, os, re, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def load():
    spec = importlib.util.spec_from_file_location("pgv", REPO + "/scripts/permission_guard.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n\s*\2\s*(?=\n|$)", re.S)
DATA_TARGET = re.compile(r"""^\s*(?:cat|tee)\b[^\n<]*?>>?\s*['"]?[^\s'"<>|;&]*\.(?:md|txt|tsv|csv|json|jsonl|log|rst)['"]?""")
SCRIPT_EXT = re.compile(r"\.(?:py|sh|bash|zsh|js|ts|mjs|ipynb)\b")


def strip_data_heredocs(cmd):
    """Remove the body of a heredoc that feeds `cat`/`tee` into a data file (.md .txt .json ...): text, not code."""
    def sub(m):
        ls = cmd.rfind("\n", 0, m.start()) + 1
        end = cmd.find("\n", m.start())
        first = cmd[ls:end if end != -1 else len(cmd)]
        if DATA_TARGET.match(first) and not SCRIPT_EXT.search(first.split("<<")[0]):
            return m.group(0).split("\n", 1)[0] + "\n" + m.group(2)
        return m.group(0)
    return HEREDOC.sub(sub, cmd)


def make(variant):
    G = load()
    if variant in ("V1", "V12", "V123"):
        old_expand = G.expand
        def expand(cmd, depth=0):
            return old_expand(strip_data_heredocs(cmd), depth)
        G.expand = expand
        old_g1 = G.g1
        def g1(cmd, segs):
            return old_g1(strip_data_heredocs(cmd), segs)
        G.g1 = g1
    if variant in ("V2", "V12", "V123"):
        old_g2 = G.g2
        def g2(cmd, segs):
            r = old_g2(cmd, segs)
            if r and "CLAUDE_CONFIG_DIR" in r[1] and not G.NAMES_CLAUDE.search(cmd):
                return None
            return r
        G.g2 = g2
    if variant in ("V3", "V123"):
        old_g3 = G.g3_bash
        def g3_bash(cmd, segs, cwd):
            return old_g3(strip_data_heredocs(cmd), segs, cwd)
        G.g3_bash = g3_bash
        old_dec = G.decide
    if variant == "V4":
        old_g4 = G.g4_script
        LAUNCH = re.compile(r"subprocess|os\.system|Popen|spawn|execv|\bexec\(|shell=")
        def g4(inp, cwd=""):
            r = old_g4(inp, cwd)
            body = str(inp.get("content") or inp.get("new_string") or inp.get("new_source") or "") + "".join(str(e.get("new_string") or "") for e in (inp.get("edits") or []) if isinstance(e, dict))
            if r and not LAUNCH.search(body) and not re.search(r"^\s*(?:claude|env|exec)\b", body, re.M):
                return None
            return r
        G.g4_script = g4
    return G


def main():
    cases = json.load(open(sys.argv[1]))["cases"]
    base = load()
    ev = lambda c: dict(tool_name=c["tool"], tool_input=c["input"], cwd=c.get("cwd") or "")
    b = {c["id"]: bool(base.decide(ev(c))) for c in cases}
    for v in ("V1", "V2", "V3", "V4", "V123"):
        G = make(v)
        d = {c["id"]: G.decide(ev(c)) for c in cases}
        cleared = [c["id"] for c in cases if c["label"] == "false" and b[c["id"]] and not d[c["id"]]]
        lost = [c for c in cases if c["label"] == "true" and b[c["id"]] and not d[c["id"]]]
        still = sum(1 for c in cases if c["label"] == "false" and d[c["id"]])
        newdeny = [c["id"] for c in cases if not b[c["id"]] and d[c["id"]]]
        att = [c for c in cases if c["source"].startswith("registered:e3_attacks")]
        print("%s: false denials %d -> %d (cleared %d); true denials lost (new false allows) %d %s; registered attacks denied %d of %d; new denials %s" % (
            v, sum(1 for c in cases if c["label"] == "false" and b[c["id"]]), still, len(cleared), len(lost),
            [(c["id"], c["source"].split(":")[0], c["rule_expected"], "indirect" if c["indirect"] else "direct") for c in lost][:12], sum(1 for c in att if d[c["id"]]), len(att), newdeny[:5]))
        print("   still false-denied by rule:", {k: sum(1 for c in cases if c["label"] == "false" and d[c["id"]] and d[c["id"]][0] == k) for k in ("G1", "G2", "G3", "G4")})


main()
