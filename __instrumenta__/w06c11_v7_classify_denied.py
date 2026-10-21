# Classify denied lab Bash calls (denied.json from dump_denied_full.py) by what the command executes: heredoc bodies fed to cat/tee/git are data, bodies fed to a shell or interpreter are code; input: guard path, denied.json; output: classified.json and a table on stdout
import re, json, sys, os, importlib.util, collections
guard, inp, outp = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("pg", guard); G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
HD = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][\w]*)\1")
CODE = {"bash","sh","zsh","dash","python","python3","node","perl","ruby","claude","osascript","deno","bun"}
def split_heredocs(cmd):
    lines = cmd.split("\n"); out_exec, out_data = [], []
    i = 0
    while i < len(lines):
        ln = lines[i]; out_exec.append(ln)
        ms = list(HD.finditer(ln))
        i += 1
        for m in ms:
            delim = m.group(2); body = []
            while i < len(lines) and lines[i].strip() != delim:
                body.append(lines[i]); i += 1
            i += 1  # delimiter
            head = ln[:m.start()]
            toks = G.words(G.split_segments(head)[-1]) if G.split_segments(head) else []
            k, _ = G.program(toks)
            prog = os.path.basename(toks[k]) if k < len(toks) else ""
            # python3 -I - etc
            if re.match(r"python[\d.]*$", prog) or prog in CODE:
                out_exec.extend(body)
            else:
                out_data.append("\n".join(body))
        
    return "\n".join(out_exec), out_data
d = json.load(open(inp)); rows = []
for x in d:
    ex, data = split_heredocs(x["command"])
    r2 = G.decide(dict(tool_name="Bash", tool_input={"command": ex}, cwd=x["cwd"] or ""))
    segs = G.expand(ex)
    runs_claude = any((lambda k, t: k < len(t) and os.path.basename(t[k]) == "claude")(*(G.program(t)[0], t)) for s, t in segs)
    names_claude_exec = bool(G.NAMES_CLAUDE.search(ex))
    x2 = dict(x); x2.update(denied_without_data_heredocs=bool(r2), group_after=(r2[0] if r2 else None), runs_claude_seg=runs_claude, names_claude_exec=names_claude_exec, n_data_heredocs=len(data), exec_len=len(ex))
    rows.append(x2)
json.dump(rows, open(outp, "w"), indent=1)
c = collections.Counter((r["group"], r["denied_without_data_heredocs"], r["runs_claude_seg"]) for r in rows)
for k, v in sorted(c.items(), key=str): print(k, v)
