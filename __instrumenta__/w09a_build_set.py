# w09-a: builds the labelled set from classified.jsonl (w09a_classify.py): refusals.jsonl (every classifier refusal), allowed_sample.jsonl (stratified random sample of recorded classifier allows with stratum weights N_h/n_h), allowed_inferred_sample.jsonl (older versions, no recorded decision), and strata.md (stratum sizes, sample sizes, weights, duplicate rates). Usage: python3 -I w09a_build_set.py IN_DIR STRATA_MD [TOTAL_N=1500] [SEED=20261024]
import json, os, random, re, sys, collections, hashlib, math

FIRST_PD_VERSION = (2, 1, 293)  # first version that records permissionDecision on tool results (measured)

RISK = re.compile(r"(\bgit\s+(push|reset|checkout\s+--|clean|rebase|branch\s+-D|stash\s+(drop|clear))|\bgh\s+(pr\s+merge|repo|release|workflow|api|secret)|\brm\s+-[a-zA-Z]*[rf]|\bssh\b|\bscp\b|\brsync\b|\bcurl\b|\bwget\b|\bsudo\b|\bchmod\b|\bchown\b|\bkill\b|\bpkill\b|\bpip3?\s+install|\bnpm\s+(install|publish)|\bcargo\s+publish|\beval\b|\bbase64\b|\bnc\b|settings(\.local)?\.json|\.claude/|\.ssh|\.env\b|\.zshenv|\.aws|credentials|BYPASS|--no-verify|--force|-f\b.*push|\bdd\s+if=|\bmkfs|\blaunchctl|\bcrontab|\bdefaults\s+write|\bosascript)")


def vtuple(v):
    try:
        return tuple(int(x) for x in (v or "").split("."))
    except ValueError:
        return (0,)


ENVA = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*=(?:\"[^\"]*\"|'[^']*'|\S*)\s+)+")


def cmd_family(cmd):
    s = (cmd or "").strip()
    # skip leading cd/env assignments to the first real program
    for _ in range(4):
        s = ENVA.sub("", s, count=1)
        m = re.match(r"^(cd|export|set|source|\.)\s+[^;&|\n]*(?:&&|;|\n)\s*", s)
        if m:
            s = s[m.end():]
        else:
            break
    s = s.lstrip()
    if re.match(r"^(python3?|uv|pytest|pip3?|pipx|ruff)\b", s):
        return "python/uv"
    if re.match(r"^(cargo|rustc|rustfmt|make|cmake|npm|node|npx|pnpm|yarn|go|swift|xcodebuild)\b", s):
        return "build/toolchain"
    if re.match(r"^git\b", s):
        return "git"
    if re.match(r"^gh\b", s):
        return "gh"
    if re.match(r"^(ssh|scp|rsync|sftp)\b", s):
        return "remote"
    if re.match(r"^(curl|wget|nc|http)\b", s):
        return "network"
    if re.match(r"^(rm|rmdir|mv|cp|mkdir|touch|ln|chmod|chown|tee|truncate)\b", s):
        return "fs-mutate"
    if re.match(r"^(kill|pkill|ps|lsof|sleep|timeout|wait|launchctl|pgrep)\b", s):
        return "process"
    if re.match(r"^(colgrep|grep|rg|egrep|find|fd|ag)\b", s):
        return "search"
    if re.match(r"^(ls|cat|head|tail|wc|sed|awk|cut|sort|uniq|jq|stat|file|echo|printf|pwd|date|diff|tree|du|df|realpath|basename|dirname|test|\[|which|type|env|printenv|nl|tr|column|xxd|od|shasum|md5|sha256sum)\b", s):
        return "read-shell"
    if re.match(r"^(claude|umbod|murmuration|colgrep-mcp|hf|lms|ollama)\b", s):
        return "agent-cli"
    if s.startswith(("cat >", "cat <<", "python3 - <<", "python - <<")) or "<<" in s[:40]:
        return "heredoc"
    return "other"


def cmd_text(c):
    i = c.get("input") or {}
    if not isinstance(i, dict):
        return ""
    return i.get("command") or i.get("file_path") or i.get("url") or i.get("query") or i.get("prompt") or json.dumps(i, sort_keys=True)[:400]


def norm_text(t):
    t = re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "<uuid>", t)
    t = re.sub(r"\d+", "<n>", t)
    return hashlib.md5(t.encode()).hexdigest()[:12]


def slim(c, extra):
    r = c.get("res") or {}
    d = {
        "id": c["id"], "decider": c["decider"], "tool": c["tool"], "tool_family": c["tool_family"], "input": c["input"],
        "ts": c["ts"], "month": c["month"], "session": c["session"], "project_group": c["pgroup"], "sub": c["sub"],
        "mode_seen": c["mode"], "auto_attachment_seen": c["auto_att"], "version": c["version"], "model": c.get("model"),
        "prompt_context": c["prompt"], "classifier_ctx_recorded": r.get("ctx"),
        "result_text_head": (r.get("text") or "")[:500] if c["decider"] != "classifier_allow" else None,
        "classifier_reason": c.get("reason"), "classifier_category_field": r.get("cat"),
    }
    d.update(extra)
    return d


def main(d, strata_md, total=1500, seed=20261024):
    rows = [json.loads(l) for l in open(os.path.join(d, "classified.jsonl"))]
    # ---- refusals
    ref = [r for r in rows if r["decider"] in ("classifier_block", "classifier_unavailable", "interrupted_by_safety_classifier")]
    with open(os.path.join(d, "refusals.jsonl"), "w") as fo:
        for c in ref:
            fo.write(json.dumps(slim(c, {"label": "refuse" if c["decider"] == "classifier_block" else "NOT_A_DECISION",
                                         "recorded_decision_era": vtuple(c["version"]) >= FIRST_PD_VERSION,
                                         "cmd_family": cmd_family(cmd_text(c)) if c["tool"] == "Bash" else "-"})) + "\n")
    # ---- recorded allows: strata
    allows = [r for r in rows if r["decider"] == "classifier_allow"]
    for c in allows:
        t = cmd_text(c)
        src = "arena" if c["pgroup"] == "murmuration-arena" else "natural"
        fam = cmd_family(t) if c["tool"] == "Bash" else "-"
        risky = bool(RISK.search(t)) if c["tool"] in ("Bash", "Write", "Edit", "MultiEdit") else False
        c["_text"] = t
        c["_h"] = (c["tool_family"], src, fam, "risky" if risky else "plain")
        c["_nh"] = norm_text(t)
    N = collections.Counter(c["_h"] for c in allows)
    sq = {h: math.sqrt(n) for h, n in N.items()}
    S = sum(sq.values())
    # allocation: n_h = min(N_h, max(floor, round(total * sqrt(N_h) / sum sqrt(N)))), floor 8 (risky strata: floor 25)
    nh = {}
    for h, n in N.items():
        floor = 25 if h[3] == "risky" else 8
        nh[h] = min(n, max(floor, round(total * sq[h] / S)))
    rng = random.Random(seed)
    by_h = collections.defaultdict(list)
    for c in allows:
        by_h[c["_h"]].append(c)
    uniq = {h: len({c["_nh"] for c in v}) for h, v in by_h.items()}
    sess = {h: len({c["session"] for c in v}) for h, v in by_h.items()}
    picked = []
    for h in sorted(by_h):
        v = sorted(by_h[h], key=lambda c: c["id"])
        pick = rng.sample(v, nh[h])
        w = N[h] / nh[h]
        for c in pick:
            picked.append(slim(c, {"label": "allow", "stratum": "|".join(h), "N_h": N[h], "n_h": nh[h], "weight": w,
                                   "cmd_family": h[2], "risky": h[3] == "risky", "source": h[1], "norm_text_hash": c["_nh"]}))
    with open(os.path.join(d, "allowed_sample.jsonl"), "w") as fo:
        for p in picked:
            fo.write(json.dumps(p) + "\n")
    # ---- inferred allows (older versions: auto mode seen, no decision record) -- counts and a small sample
    inf = [r for r in rows if r["decider"] == "no_decision_record" and vtuple(r["version"]) < FIRST_PD_VERSION
           and (r["mode"] == "auto" or r["auto_att"]) and r["tool"] in ("Bash", "Write", "Edit", "MultiEdit", "WebFetch", "Agent")
           and r.get("res") and not r["res"]["is_error"]]
    infN = collections.Counter(r["tool_family"] for r in inf)
    rng2 = random.Random(seed + 1)
    inf_pick = rng2.sample(sorted(inf, key=lambda c: c["id"]), min(300, len(inf)))
    with open(os.path.join(d, "allowed_inferred_sample.jsonl"), "w") as fo:
        for c in inf_pick:
            fo.write(json.dumps(slim(c, {"label": "allow_inferred", "weight": len(inf) / len(inf_pick)})) + "\n")
    # ---- strata table
    L = ["# strata of recorded classifier allows (version >= 2.1.293)", "",
         "population N = %d; sample n = %d; seed %d; allocation n_h = min(N_h, max(floor, round(%d * sqrt(N_h) / sum sqrt(N)))), floor 8 (25 for risky-word strata)" % (len(allows), len(picked), seed, total), "",
         "| tool family | source | Bash command family | risk words | N_h | n_h | weight N_h/n_h | unique texts (digits and uuids masked) | sessions |", "|:--|:--|:--|:--|--:|--:|--:|--:|--:|"]
    for h in sorted(N, key=lambda h: -N[h]):
        L.append("| %s | %s | %s | %s | %d | %d | %.1f | %d | %d |" % (h[0], h[1], h[2], h[3], N[h], nh[h], N[h] / nh[h], uniq[h], sess[h]))
    L += ["", "## marginals (N / n)", ""]
    for name, ix in (("tool family", 0), ("source", 1), ("risk", 3)):
        cn, cs = collections.Counter(), collections.Counter()
        for h in N:
            cn[h[ix]] += N[h]
            cs[h[ix]] += nh[h]
        L.append("- %s: " % name + "; ".join("%s %d / %d" % (k, cn[k], cs[k]) for k in sorted(cn, key=lambda k: -cn[k])))
    L += ["", "## refusals file", ""]
    cnt = collections.Counter(r["decider"] for r in ref)
    L.append("- " + "; ".join("%s %d" % kv for kv in cnt.items()))
    era = collections.Counter((r["decider"], vtuple(r["version"]) >= FIRST_PD_VERSION) for r in ref)
    L.append("- by (decider, recorded-decision era): " + "; ".join("%s %s %d" % (k[0], "era" if k[1] else "pre-era", v) for k, v in era.items()))
    L.append("- classifier_block by tool: " + str(dict(collections.Counter(r["tool_family"] for r in ref if r["decider"] == "classifier_block"))))
    L.append("- classifier_block by source: " + str(dict(collections.Counter("arena" if r["pgroup"] == "murmuration-arena" else "natural" for r in ref if r["decider"] == "classifier_block"))))
    L += ["", "## inferred allows (pre-2.1.293, auto mode seen, no decision record, tool result not an error)", "",
          "- N = %d by tool: %s; sample written: %d" % (len(inf), dict(infN), len(inf_pick))]
    open(strata_md, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], int(a[3]) if len(a) > 3 else 1500, int(a[4]) if len(a) > 4 else 20261024)
