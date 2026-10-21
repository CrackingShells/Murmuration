#!/bin/zsh
# Runs one headless haiku probe of a research-pi variant (plugin dir) with the dummy MCP server attached and prints init tools, request contexts and cost; inputs: label, plugin dir; output: <scratch>/p_<label>/out.jsonl and a summary on stdout. Scratch folder is hard-coded to the wave-5 author-w05-2 run folder.
# usage: probe.sh <label> <plugin dir> [extra claude args]
B=/private/tmp/murmuration-w05/author-w05-2; L=$1; P=$2; shift 2
rm -rf $B/p_$L; mkdir -p $B/p_$L; cd $B/p_$L
python3 -I $P/scripts/lab_init.py --project $B/p_$L <<< "Smoke" >/dev/null
env -u CLAUDE_PROJECT_DIR COLGREP_DATA_DIR=$B/p_$L/colgrep CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 timeout 300 claude -p --model haiku --agent murmuration:research-pi --plugin-dir $P --setting-sources project,local --strict-mcp-config --mcp-config $B/mcp.json --permission-mode auto --output-format stream-json --verbose "Call the echo tool of the dummy MCP server with text hi if you have it, else say NOECHO. Then say DONE." > out.jsonl 2> err.txt
python3 -I - $B/p_$L/out.jsonl <<'PY'
import json,sys
for l in open(sys.argv[1]):
    r=json.loads(l)
    if r.get("type")=="system" and r.get("subtype")=="init": print("init tools:",r["tools"], r["mcp_servers"])
    if r.get("type")=="assistant":
        for b in r["message"]["content"]:
            if b["type"]=="tool_use": print("tool_use",b["name"],json.dumps(b["input"])[:80])
            if b["type"]=="text": print("text",b["text"][:100])
        u=r["message"]["usage"]; print("ctx", u["input_tokens"]+u["cache_creation_input_tokens"]+u["cache_read_input_tokens"])
    if r.get("type")=="result": print("cost",r["total_cost_usd"],r["is_error"])
PY
