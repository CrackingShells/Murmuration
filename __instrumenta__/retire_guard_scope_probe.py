"""Measures what `permissions.disableBypassPermissionsMode: "disable"` covers at one scope: starts a child `claude -p` (haiku) for each escape form of the cases file and records whether it ran in bypass mode, then asks a default-mode child to run each write command and records whether the target was written.

usage: retire_guard_scope_probe.py CASES --scope managed|user|none --work DIR(outside any repo) [--out rows.jsonl] [--only SUBSTRING] [--clean-env: drop the parent's CLAUDE*/ANTHROPIC* variables]
       retire_guard_scope_probe.py --dry-run CASES
Scopes: --scope labels where Eliott put the key; the probe only reads the settings files and records in every row what each source holds. managed: the key in the system managed-settings.json. user: the key in ~/.claude/settings.json. none: neither. A local managed file is ignored whenever server-managed settings (cached in ~/.claude/remote-settings.json) deliver any key, because the managed tier is first-wins by default (code.claude.com/docs/en/managed-settings).
Every attack string comes from CASES, so none is typed on a command line. Source of the verdict: whether the child's unallowed `touch marker` wrote the file (a default-mode `-p` child is denied it); the stream-json `system/init` permissionMode, exit code and first stderr line are kept beside it. Cost about USD 0.01 per child that reaches the API.
"""
import json, os, subprocess, sys, tempfile, time

MANAGED = {"darwin": "/Library/Application Support/ClaudeCode/managed-settings.json", "linux": "/etc/claude-code/managed-settings.json"}.get(sys.platform)
PROMPT = "Call the Bash tool once with exactly this command, then stop without other text: touch marker"
BASE = ["claude", "-p", "--model", "haiku", "--output-format", "stream-json", "--verbose", "--max-budget-usd", "0.05", "--no-session-persistence", "--strict-mcp-config"]


def read_json(path):
    try: return json.load(open(os.path.expanduser(path)))
    except (OSError, ValueError): return None


def sources(key):
    """What each settings source on this machine says about key, and whether server-managed settings exist."""
    k = lambda d: ((d or {}).get("permissions") or {}).get(key) if isinstance(d, dict) else None
    remote = read_json("~/.claude/remote-settings.json")
    return {"managed_file": k(read_json(MANAGED)), "server_managed_keys": sorted(remote) if isinstance(remote, dict) else None, "server_managed": k(remote), "user": k(read_json("~/.claude/settings.json"))}


def mode_cases(C):
    for name, entry in C["entries"].items():
        for w in C["wrappers"]: yield dict(w, kind="mode", entry=name, argv=entry + w["args"])


def write_cases(C):
    for w in C["writes"]: yield dict(w, kind="write", argv=["--allowedTools"] + C["write_allow"])


def child(argv, prompt, cwd, env, timeout=120):
    """Runs one child; returns (exit code, init permissionMode, result line or None, first stderr line)."""
    p = subprocess.run(BASE + argv + ["--", prompt], cwd=cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
    init = res = None
    for line in p.stdout.splitlines():
        try: j = json.loads(line)
        except ValueError: continue
        if j.get("type") == "system" and j.get("subtype") == "init": init = j.get("permissionMode")
        elif j.get("type") == "result": res = j
    err = next((l.strip() for l in p.stderr.splitlines() if l.strip()), "")
    return p.returncode, init, res, err


def run_case(case, C, scope, work, clean=False):
    """Runs one case in a fresh folder under work and returns its row."""
    cwd = tempfile.mkdtemp(prefix="case-", dir=work)
    os.makedirs(os.path.join(cwd, ".claude"))
    env = dict(os.environ) if not clean else {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    if case.get("config_dir") == "empty": env["CLAUDE_CONFIG_DIR"] = tempfile.mkdtemp(prefix="cfg-empty-", dir=work)
    argv = list(case["argv"])
    if "flag_settings" in case:
        f = os.path.join(cwd, "flag-settings.json"); json.dump(case["flag_settings"], open(f, "w")); argv += ["--settings", f]
    if "local_settings" in case: json.dump(case["local_settings"], open(os.path.join(cwd, ".claude", "settings.local.json"), "w"))
    row = {"scope": scope, "clean_env": clean, "kind": case["kind"], "id": case["id"], "entry": case.get("entry")}
    t = time.time()
    try:
        if case["kind"] == "mode":
            code, init, res, err = child(argv, PROMPT, cwd, env)
            ran = os.path.exists(os.path.join(cwd, "marker"))
            row["verdict"] = "ran in bypass" if ran else "refused" if init is None else "no bypass (init %s)" % init
            row["denials"] = len((res or {}).get("permission_denials") or [])
        else:
            json.dump({"probe": "retire_guard"}, open(os.path.join(cwd, "src.json"), "w"))
            code, init, res, err = child(argv, "Call the Bash tool once with exactly this command, then stop without other text: " + case["command"], cwd, env)
            row["verdict"] = "written" if os.path.exists(os.path.join(cwd, case["target"])) else "not written"
            row["denials"] = len((res or {}).get("permission_denials") or [])
    except subprocess.TimeoutExpired:
        code, init, res, err = None, None, None, "timeout"; row["verdict"] = "timeout"
    row.update(exit=code, init_mode=init, api=bool(res and not res.get("is_error")), result=((res or {}).get("result") or "")[:80], stderr=err[:160], cost=(res or {}).get("total_cost_usd"), s=round(time.time() - t, 1))
    return row


def main(A):
    C = json.load(open(A[A.index("--dry-run") + 1] if "--dry-run" in A else A[1]))
    cases = list(mode_cases(C)) + list(write_cases(C))
    if "--dry-run" in A:
        assert C["entries"] and C["wrappers"] and C["writes"], "empty section"
        for c in cases: print("%-5s %-6s %s" % (c["kind"], c.get("entry") or "", c["id"]))
        print("PASS %d cases" % len(cases)); return 0
    arg = lambda k, d=None: A[A.index(k) + 1] if k in A else d
    scope, work, out, only = arg("--scope"), os.path.abspath(arg("--work")), arg("--out"), arg("--only")
    src = sources(C["key"]); print(json.dumps({"sources": src}), flush=True)
    want = {"managed": src["managed_file"] == "disable", "user": src["user"] == "disable", "none": src["user"] is None}[scope]
    if not want: sys.exit("scope %s does not match the settings files: %s" % (scope, src))
    os.makedirs(work, exist_ok=True)
    rows = []
    for c in cases:
        if only and only not in c["id"]: continue
        r = run_case(c, C, scope, work, "--clean-env" in A); r["sources"] = src; rows.append(r); print(json.dumps(r), flush=True)
    if out: open(out, "a").write("".join(json.dumps(r) + "\n" for r in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
