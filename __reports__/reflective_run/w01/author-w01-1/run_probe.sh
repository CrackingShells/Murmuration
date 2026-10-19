#!/bin/bash
# Usage: run_probe.sh <tag> <permission-mode> <claude-binary> <raw:0|1> <hooks:0|1> <prompt-file> [lab:1|0]
# Runs one headless haiku session in scratch/<tag>/work with the scratch plugin loaded.
#   raw=1   : also log every hook payload to scratch/<tag>/RAWLOG (settings_raw)
#   hooks=1 : load plugin/hooks/hooks.json (the proposal); hooks=0 : the hooks file is hidden by a copy without it
# Why bash: it only assembles a command line; the checks are in check_*.py.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TAG="$1"; MODE="$2"; BIN="$3"; RAW="$4"; HOOKS="$5"; PROMPT="$6"; LAB="${7:-1}"; WORK="${8:-}"
D="$HERE/scratch/$TAG"; rm -rf "$D"; mkdir -p "$D/work"; if [ -n "$WORK" ]; then rm -rf "$WORK"; mkdir -p "$WORK"; ln -s "$WORK" "$D/work_link"; fi
if [ "$LAB" = 1 ]; then mkdir -p "$D/work/__design__" "$D/work/__statera__"; echo "# framing (scratch)" > "$D/work/__design__/framing.md"; echo "# wave-01" > "$D/work/__statera__/wave-01.md"; fi
# plugin copy per run, so hooks on/off is a property of the run
P="$D/plugin"; mkdir -p "$P"; cp -R "$HERE/plugin/.claude-plugin" "$HERE/plugin/agents" "$HERE/plugin/scripts" "$P/"
if [ "$HOOKS" = 1 ]; then mkdir -p "$P/hooks"; cp "$HERE/plugin/hooks/hooks.json" "$P/hooks/"; fi
if [ "$HOOKS" = 2 ]; then mkdir -p "$P/hooks"; cp "$HERE/hooks_stoponly.json" "$P/hooks/hooks.json"; fi   # SubagentStop only: the capture route of auto mode removed
SET=()
if [ "$RAW" = 1 ]; then
python3 - "$HERE" "$D" <<'PY'
import json,sys
A,D=sys.argv[1:3]
ev=["SubagentStart","SubagentStop","PostToolUse","Stop"]
s={"hooks":{e:[{"hooks":[{"type":"command","command":f"{A}/scratch/bin/log.sh {D}/RAWLOG","timeout":10}]}] for e in ev}}
json.dump(s,open(f"{D}/settings_raw.json","w"),indent=1)
PY
SET=(--settings "$D/settings_raw.json")
fi
mkdir -p "${WORK:-$D/work}/notes"; echo "old text" > "${WORK:-$D/work}/REPORT-old.md"
cd "${WORK:-$D/work}"
"$BIN" -p "$(cat "$HERE/$PROMPT")" --model haiku --setting-sources project --plugin-dir "$P" ${SET[@]+"${SET[@]}"} \
  --permission-mode "$MODE" --max-budget-usd 0.50 --output-format json > "$D/out.json" 2> "$D/err.txt"
echo "exit=$?" > "$D/exit.txt"
