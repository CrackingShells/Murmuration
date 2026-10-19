import json,os,sys,time
d=json.load(sys.stdin)
rec={"t":time.time(),"event":d.get("hook_event_name"),"payload_cwd":d.get("cwd"),
     "env_CLAUDE_PROJECT_DIR":os.environ.get("CLAUDE_PROJECT_DIR"),"proc_cwd":os.getcwd(),
     "prompt":d.get("prompt"),"prompt_id":d.get("prompt_id"),"session_id":d.get("session_id"),
     "transcript_path":d.get("transcript_path"),"keys":sorted(d)}
open(sys.argv[1],"a").write(json.dumps(rec)+"\n")
