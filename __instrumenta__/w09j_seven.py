# w09-j: finds the recorded refusals that every judge arm of slices.md (qwen full, Granite short, gemma short, gemma full, safeguard short) allowed, from the committed result rows, prints only their ids and kinds (no text), and with --private OUT.md writes their redacted full text, the preceding user prompt as collected, the classifier's stated reason, date and a transcript pointer to OUT.md (a private file outside every repository). Usage: python3 -I w09j_seven.py REPORTS_WAVE09_DIR PRIVATE_DIR [--private OUT.md]   (PRIVATE_DIR = /private/tmp/murmuration-w09/explorer-w09-c holding refusals.jsonl and classified.jsonl)
import sys, os, json, re, importlib.util
BASE, PRIV = sys.argv[1], sys.argv[2]
out = sys.argv[sys.argv.index("--private") + 1] if "--private" in sys.argv else None
RC, RI = os.path.join(BASE, "explorer-w09-c", "results"), os.path.join(BASE, "explorer-w09-i", "results")
files = {"qwen full": RI + "/qwen36_full.jsonl", "gemma full": RI + "/gemma4_full.jsonl", "gemma short": RI + "/gemma4_short.jsonl", "granite short": RC + "/granite_short.jsonl", "safeguard short": RC + "/safeguard_short.jsonl", "qwen short": RI + "/qwen36_short.jsonl"}
V = {}
for k, f in files.items():
    V[k] = {r["cid"]: r["verdict"] for r in map(json.loads, open(f)) if "cid" in r and r.get("group") == "refusal"}
refs = sorted(V["qwen full"])
five = ["qwen full", "gemma full", "gemma short", "granite short", "safeguard short"]
seven = [c for c in refs if all(V[k].get(c) == "allow" for k in five)]
six = [c for c in seven if V["qwen short"].get(c) == "allow"]
print("refusals allowed by all five arms:", len(seven), seven, "; also by qwen short:", len(six))
R = {r["id"][-8:]: r for r in map(json.loads, open(os.path.join(PRIV, "refusals.jsonl")))}
for c in seven:
    r = R[c[2:]]
    print(c, r["tool"], r["cmd_family"], "prompt_chars", len(r["prompt_context"] or ""), "reason", r["classifier_reason"], "era", r["recorded_decision_era"])
if out:
    spec = importlib.util.spec_from_file_location("w09a_collect", os.path.join(os.path.dirname(os.path.abspath(__file__)), "w09a_collect.py")); col = importlib.util.module_from_spec(spec); spec.loader.exec_module(col)
    want = {R[c[2:]]["id"]: c for c in seven}; ptr = {}
    for l in open(os.path.join(PRIV, "classified.jsonl")):
        if any(i in l[:200] for i in want):
            d = json.loads(l)
            if d["id"] in want: ptr[d["id"]] = d["file"]
    B = os.path.expanduser("~/.claude/projects/")
    with open(out, "w") as f:
        f.write("# The refusals every judge allowed (private; do not commit, do not paste into a repository)\n\nSelection: recorded classifier refusals that qwen3.6 (full rules), gemma-4 (full and short), Granite Guardian (short) and gpt-oss-safeguard (short) all allowed, from the committed result rows. Text is redacted for obvious secrets by the collector's patterns (keys, tokens, emails, assignments); paths and prose are as the transcript has them. 'Preceding user prompt' is the last plain user message of that transcript file before the call, as collected (capped at 2,000 characters; empty when the call is inside a subagent file that has no such message). 'Stated reason' is what the classifier returned to the agent. The classifier's own context (what it saw) is not in the transcript.\n\n")
        for c in seven:
            r = R[c[2:]]; line = None
            fp = B + ptr.get(r["id"], "") if r["id"] in ptr else None
            if fp:
                # the transcript file name is stored without its extension tail; find the jsonl that holds the id
                cand = fp if os.path.exists(fp) else None
                import glob
                if not cand:
                    g = glob.glob(fp + "*")
                    cand = g[0] if g else None
                if cand:
                    for n, l in enumerate(open(cand, errors="replace"), 1):
                        if r["id"] in l and '"tool_use"' in l: line = (cand, n); break
            f.write(f"## {c}\n\n- date (UTC): {r['ts']}\n- tool: {r['tool']}; command family: {r['cmd_family']}; Claude Code {r['version']}; model {r['model']}; project group: {r['project_group']}; subagent file: {r['sub']}\n- recorded-decision era (CLI 2.1.293 or later): {r['recorded_decision_era']}\n- classifier's stated reason: {r['classifier_reason']}\n- verdicts of the six arms: " + ", ".join(f"{k}={V[k].get(c)}" for k in V) + "\n")
            f.write(f"- transcript pointer: {line[0]} line {line[1]}\n" if line else "- transcript pointer: not found\n")
            f.write("\n### preceding user prompt (as collected)\n\n```\n" + col.redact(r["prompt_context"] or "(none: the preceding message is not a plain user prompt in this file)") + "\n```\n\n### tool input (redacted)\n\n```\n" + col.redact(str(r["input"])) + "\n```\n\n### what the classifier told the agent\n\n```\n" + col.redact(str(r["result_text_head"])) + "\n```\n\n")
    print("wrote", out)
