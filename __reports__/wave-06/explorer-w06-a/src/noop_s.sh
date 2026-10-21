#!/bin/sh
t0=$("${0%/*}/nowms")
read -r _
echo "noop-shs $1"
t1=$("${0%/*}/nowms")
[ -n "$W06_LOG" ] && echo "{\"lang\":\"shs\",\"tag\":\"$1\",\"t0_ms\":$t0,\"t1_ms\":$t1,\"pid\":$$}" >> "$W06_LOG"
exit 0
