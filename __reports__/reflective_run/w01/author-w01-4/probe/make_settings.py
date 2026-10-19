import json,sys
log,out=sys.argv[1:3]
hook=lambda: [{"hooks":[{"type":"command","command":"python3 -I %s/probe/bin/hookdump.py %s"%(sys.argv[3],log),"timeout":10}]}]
json.dump({"hooks":{"UserPromptSubmit":hook(),"Stop":hook(),"SessionStart":hook()}},open(out,"w"))
