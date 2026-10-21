# Like script_run_check.py but looks for the execution of written files only in the command text outside heredoc bodies fed to cat/tee (exec text); input: classified.json idx...; output: stdout
import json, re, sys, importlib.util, os
spec = importlib.util.spec_from_file_location("cd", "/private/tmp/murmuration-w06/reproducer-w06-7/tools/classify_denied.py")
# avoid executing classify's main: re-implement split_heredocs
HD = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][\w]*)\1")
CODE = {"bash","sh","zsh","dash","python","python3","node","perl","ruby","claude"}
def split(cmd):
    lines = cmd.split("\n"); ex = []; i = 0; targets = []
    while i < len(lines):
        ln = lines[i]; ex.append(ln); i += 1
        for m in HD.finditer(ln):
            d = m.group(2); body = []
            while i < len(lines) and lines[i].strip() != d: body.append(lines[i]); i += 1
            i += 1
            head = ln[:m.start()]
            prog = re.findall(r"([\w./-]+)\s+(?:-[\w-]+\s+)*-?\s*$", head)
            seg = re.split(r"[;&|]", head)[-1].split()
            p = os.path.basename(seg[0]) if seg else ""
            if re.match(r"python[\d.]*$", p) or p in CODE: ex.extend(body)
            else:
                t = re.findall(r">>?\s*(\S+)", head); targets.append((t[-1] if t else None, body))
    return "\n".join(ex), targets
rows = json.load(open("/private/tmp/murmuration-w06/reproducer-w06-7/out/classified.json"))
for i in map(int, sys.argv[1:]):
    ex, tg = split(rows[i]["command"]); out = []
    for t, body in tg:
        if not t: continue
        b = re.escape(os.path.basename(t)); exl = "\n".join(l for l in ex.split("\n") if "<<" not in l)
        ran = re.findall(r"(?:(?:python3?|bash|sh|zsh|source)\s+(?:-\w+\s+)*\S*|\./|\S*/)" + b + r"\b", exl)
        spawn = [l.strip()[:90] for l in body if re.search(r"claude", l) and re.search(r"bypass|dangerously", "\n".join(body))][:1]
        out.append((os.path.basename(t), "RUN" if ran else "norun", len(body), spawn))
    print("#%d" % i, out)
