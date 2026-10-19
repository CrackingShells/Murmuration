import json,os,sys,time
d=json.load(sys.stdin)
rec={"event":d.get("hook_event_name"),"payload_cwd":d.get("cwd"),"env_CLAUDE_PROJECT_DIR":os.environ.get("CLAUDE_PROJECT_DIR"),"proc_cwd":os.getcwd(),"prompt":d.get("prompt")}
open(sys.argv[1],"a").write(json.dumps(rec)+"\n")
