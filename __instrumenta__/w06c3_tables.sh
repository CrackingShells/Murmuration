#!/bin/sh
# w06-c3: writes the stage-1 metric tables (m1 to m6) to stdout from the run directories of w06c3_run_all.py; input: the runs directory (default the full one); output: markdown
R=${1:-/private/tmp/murmuration-w06/author-w06-3/runs}
A="python3 -I $(dirname "$0")/w06c3_analyze.py"
echo "## m1 fields (platform stdin, recorded by a command hook beside the server, against what the server received)"; $A m1 $R/t_auto0/plugin $R/t_auto*[0-9] $R/t_byp*[0-9] 2>&1 | grep -v "^|:--" | sed 's/^/ /' | sed 's/^ //'
echo; echo "## m2 firing (server log against what the transcript implies: runs t_*, v*, m3_on_*, m3_open; one row per thread and event)"
$A m2 $R/t_auto*[0-9] $R/t_byp*[0-9] $R/v*[0-9] $R/m3_on_* $R/m3_open > /tmp/w06c3_m2.$$ 2>&1
grep -c "| yes |" /tmp/w06c3_m2.$$ | sed 's/^/rows equal: /'; grep -c "| NO |" /tmp/w06c3_m2.$$ | sed 's/^/rows NOT equal: /'; tail -1 /tmp/w06c3_m2.$$; rm -f /tmp/w06c3_m2.$$
echo; echo "## m3 request 0 (ON = plugin with the server answering nothing, OFF = same agents, no server, OPEN = control with the tool allowed)"; $A m3 off=$(ls -d $R/m3_off* | tr '\n' ',' | sed 's/,$//') on=$(ls -d $R/m3_on_* | tr '\n' ',' | sed 's/,$//') open=$R/m3_open 2>&1
echo; echo "## m4 outage"; $A m4 $R/m4a*[0-9] $R/m4b*[0-9] $R/m4c*[0-9] 2>&1
echo; echo "## m5 latency (server alone, runs v*)"; $A m5 $R/v*[0-9] 2>&1
echo; echo "## m6 effects"; $A m6 $R/t_auto*[0-9] $R/t_byp*[0-9] 2>&1
