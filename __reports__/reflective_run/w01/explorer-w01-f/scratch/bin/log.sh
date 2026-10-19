#!/bin/bash
# usage: log.sh <outfile>  ; appends {ts_ms, input} with raw stdin JSON
out="$1"; in="$(cat)"
python3 -I - "$out" "$in" <<'PY'
import sys,json,time
out,raw=sys.argv[1],sys.argv[2]
try: d=json.loads(raw)
except Exception: d={"_raw":raw}
open(out,"a").write(json.dumps({"t":time.time(),"input":d})+"\n")
PY
exit 0
