#!/usr/bin/env bash
# Probe: asyncRewake handler. Active only when PROBE_REWAKE=1. Logs, then exits 2 with a message on stderr.
cat > /dev/null
[ "${PROBE_REWAKE:-}" = 1 ] || exit 0
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
printf '{"ts":"%s","run":"%s","label":"rewake_fired"}\n' "$(date -u +%FT%TZ)" "${PROBE_RUN:-}" >> "${PROBE_OUT:-$HERE/out/events.jsonl}"
sleep 1
echo "PROBE-REWAKE: a new scrupulus was raised (stderr of an asyncRewake hook)." >&2
exit 2
