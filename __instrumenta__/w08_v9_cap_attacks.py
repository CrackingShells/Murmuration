# Tries to break the PI-decision cap of a lab_status.py on synthetic claim files; inputs: path of lab_status.py; output: one line per attack with the state shown and warnings.
import os, re, subprocess, sys, tempfile
LS = sys.argv[1]
def head(label="MEASURED", cid="w01-c1", extra=""):
    return f"# {cid}: a statement\n\nlabel: {label}\nscope: s\nevidence: e\nmethod: m\nauthor: a\n{extra}\n"
def ver(name, v, extra=""):
    return f"\n## verdict: {name}\n\n### independent result\nx\n\n{extra}verdict: {v}\nreason: r\n"
def dec(d, ref="__statera__/wave-01.md:3", stmt=True, writer="research-pi", cid=None):
    s = f"\n## decision: {writer}\n\ndecision: {d}\nref: {ref}\n"
    if stmt and d.startswith("restated"): s += "statement: the restated one\n"
    return s + "reason: r\n"
def run(files, note="line1\nline2\n- PI decision on w01-c1\n"):
    tmp = tempfile.mkdtemp(dir="/private/tmp/murmuration-w08/reproducer-w08-9")
    for d in ("__pondus__", "__statera__", "__scrupuli__"): os.makedirs(os.path.join(tmp, d))
    open(os.path.join(tmp, "__statera__", "wave-01.md"), "w").write(note)
    for n, t in files.items(): open(os.path.join(tmp, "__pondus__", n + ".md"), "w").write(t)
    r = subprocess.run([sys.executable, LS, "--project", tmp], capture_output=True, text=True, cwd=tmp, env=dict(os.environ, CLAUDE_PROJECT_DIR=tmp))
    out = r.stdout.splitlines()
    cl = [l for l in out if re.match(r"- w\d\d-c\d+", l)]
    wn = [l.strip() for l in out if l.strip().startswith("! ") and "git is not available" not in l]
    return cl, wn
def show(name, files, **kw):
    cl, wn = run(files, **kw)
    print(f"[{name}]")
    for l in cl: print("   ", l[:170])
    for w in wn: print("    WARN", w[:200])
cases = []
show("1 no ESCALATE: verified SUPPORTED + restated at MEASURED", {"w01-c1": head()+ver("v1","SUPPORTED")+dec("restated at MEASURED")})
show("1b SUPPORTED + stands at ESTIMATE", {"w01-c1": head()+ver("v1","SUPPORTED")+dec("stands at ESTIMATE")})
show("1c unverified + stands at MEASURED", {"w01-c1": head()+dec("stands at MEASURED")})
show("2 OVERSTATED + stands at MEASURED (head)", {"w01-c1": head()+ver("v1","OVERSTATED")+dec("stands at MEASURED")})
show("2b OVERSTATED + restated at MEASURED", {"w01-c1": head()+ver("v1","OVERSTATED")+dec("restated at MEASURED")})
show("2c OVERSTATED + restated at CHECKED", {"w01-c1": head()+ver("v1","OVERSTATED")+dec("restated at CHECKED")})
show("2d OVERSTATED + stands at ESTIMATE", {"w01-c1": head()+ver("v1","OVERSTATED")+dec("stands at ESTIMATE")})
show("3 decision then later OVERSTATED (v2)", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED")+ver("v2","OVERSTATED")})
show("3b decision then later SUPPORTED (v2)", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED")+ver("v2","SUPPORTED")})
show("3c decision stands ESTIMATE then later SUPPORTED v2", {"w01-c1": head()+ver("v1","ESCALATE")+dec("stands at ESTIMATE")+ver("v2","SUPPORTED")})
show("3d decision then v1 revises ABOVE decision (in place) to UNSUPPORTED", {"w01-c1": head()+ver("v1","ESCALATE", "")+dec("restated at MEASURED")})
show("3e decision between: v1 ESCALATE, v2 OVERSTATED above, decision restated", {"w01-c1": head()+ver("v1","ESCALATE")+ver("v2","OVERSTATED")+dec("restated at MEASURED")})
show("3f v1 ESCALATE, v2 SUPPORTED above, decision restated (dispute)", {"w01-c1": head()+ver("v1","ESCALATE")+ver("v2","SUPPORTED")+dec("restated at MEASURED")})
show("3g v1 ESCALATE, v2 SUPPORTED above, decision stands at MEASURED", {"w01-c1": head()+ver("v1","ESCALATE")+ver("v2","SUPPORTED")+dec("stands at MEASURED")})
show("4 malformed: no colon heading", {"w01-c1": head()+ver("v1","ESCALATE")+"\n## decision research-pi\n\ndecision: restated at MEASURED\nref: __statera__/wave-01.md:3\nstatement: s\n"})
show("4b malformed: decision lowercase label", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at measured")})
show("4c malformed: label with trailing text", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED (and more)")})
show("4d decision inside a fenced block in verifier section", {"w01-c1": head()+ver("v1","ESCALATE", "```markdown\n## decision: research-pi\n\ndecision: restated at MEASURED\nref: __statera__/wave-01.md:3\nstatement: s\n```\n")})
show("4e decision under ### (not ##)", {"w01-c1": head()+ver("v1","ESCALATE")+"\n### decision: research-pi\n\ndecision: restated at MEASURED\nref: __statera__/wave-01.md:3\nstatement: s\n"})
show("4f writer research-pi-2", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED", writer="research-pi-2")})
show("4g decision in HTML comment", {"w01-c1": head()+ver("v1","ESCALATE")+"<!--"+dec("restated at MEASURED")+"-->"})
show("5 two decisions: first ok, second above-cap", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED")+dec("restated at THEOREM")})
show("5b two decisions: first stands at ESTIMATE, second restated MEASURED", {"w01-c1": head()+ver("v1","ESCALATE")+dec("stands at ESTIMATE")+dec("restated at MEASURED")})
show("5c two decisions: first restated, second withdrawn", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED")+dec("withdrawn")})
show("6 substring: ref note names w01-c10 only, claim w01-c1", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED")}, note="a\nb\n- PI decision on w01-c10\n")
show("6b ref line past: note names w01-c1 elsewhere only", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED", ref="__statera__/wave-01.md:1")}, note="a\nb\n- PI decision on w01-c1\n")
show("7 superseded by nonexistent id", {"w01-c1": head()+ver("v1","ESCALATE")+dec("superseded by w99-c99")})
show("7b withdrawn on verified SUPPORTED", {"w01-c1": head()+ver("v1","SUPPORTED")+dec("withdrawn")})
show("7c withdrawn over ESCALATE then v2 SUPPORTED later", {"w01-c1": head()+ver("v1","ESCALATE")+dec("withdrawn")+ver("v2","SUPPORTED")})
show("8 compound label head 'MEASURED (c1-c3); c4 ESTIMATE'", {"w01-c1": head("MEASURED (c1-c3, haiku); c4 is an ESTIMATE inside it")+ver("v1","ESCALATE")+dec("restated at MEASURED")})
show("8b head ESTIMATE, restated at MEASURED", {"w01-c1": head("ESTIMATE")+ver("v1","ESCALATE")+dec("restated at MEASURED")})
show("8c head CONJECTURE, v ESCALATE, restated at ESTIMATE", {"w01-c1": head("CONJECTURE")+ver("v1","ESCALATE")+dec("restated at ESTIMATE")})
show("9 head CITED + ESCALATE + restated at CITED/MEASURED", {"w01-c1": head("CITED")+ver("v1","ESCALATE")+dec("restated at MEASURED")})
show("10 decision before the verdict sections in the file (file order)", {"w01-c1": head()+dec("restated at MEASURED")+ver("v1","ESCALATE")})
show("11 verdict OVERSTATED v1 then v1 later UNSUPPORTED below decision", {"w01-c1": head()+ver("v1","OVERSTATED")+dec("restated at MEASURED")+ver("v1","UNSUPPORTED")})
show("12 LABEL TOO STRONG (proof-adversary) + stands at THEOREM head", {"w01-c1": head("THEOREM")+ver("p1","LABEL TOO STRONG")+dec("stands at THEOREM")})
show("12b LABEL TOO STRONG + restated at THEOREM", {"w01-c1": head("THEOREM")+ver("p1","LABEL TOO STRONG")+dec("restated at THEOREM")})
print("=== all warnings for selected cases")
def allwarn(name, files, **kw):
    tmp = None
    cl, wn = run(files, **kw)
for name, files, kw in [
 ("6 substring", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED")}, dict(note="a\nb\n- PI decision on w01-c10\n")),
 ("6b line not naming", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at MEASURED", ref="__statera__/wave-01.md:1")}, dict(note="a\nb\n- PI decision on w01-c1\n")),
 ("8b above head", {"w01-c1": head("ESTIMATE")+ver("v1","ESCALATE")+dec("restated at MEASURED")}, {}),
 ("4b lowercase theorem on MEASURED", {"w01-c1": head()+ver("v1","ESCALATE")+dec("restated at theorem")}, {}),
 ("4d fence", {"w01-c1": head()+ver("v1","ESCALATE", "```markdown\n## decision: research-pi\n\ndecision: restated at MEASURED\nref: __statera__/wave-01.md:3\nstatement: s\n```\n")}, {}),
]:
    tmp = tempfile.mkdtemp(dir="/private/tmp/murmuration-w08/reproducer-w08-9")
    for d in ("__pondus__", "__statera__", "__scrupuli__"): os.makedirs(os.path.join(tmp, d))
    open(os.path.join(tmp, "__statera__", "wave-01.md"), "w").write(kw.get("note", "line1\nline2\n- PI decision on w01-c1\n"))
    for n, t in files.items(): open(os.path.join(tmp, "__pondus__", n + ".md"), "w").write(t)
    r = subprocess.run([sys.executable, LS, "--project", tmp], capture_output=True, text=True, cwd=tmp, env=dict(os.environ, CLAUDE_PROJECT_DIR=tmp))
    print("[%s]" % name, [l[:230] for l in r.stdout.splitlines() if (l.strip().startswith("!") and "git is not" not in l) or l.startswith("- w01-c1")])
