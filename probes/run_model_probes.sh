#!/usr/bin/env bash
# Probes that need a model (subagents, SendMessage, compaction). Needs an authenticated `claude`
# (run `claude auth login` first; `claude auth status` must say loggedIn: true).
#   probes/run_model_probes.sh [tag]      # about 7 short sessions, a few cents each; each capped at 0.60 USD
# Then: probes/analyze.sh <tag>
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAG="${1:-$(date +%H%M)}"
CAP=(--max-budget-usd 0.60)

# M1: author <-> verifier. Two named plugin subagents; the author messages the verifier directly,
# the verifier is resumed and answers the author directly; the main thread only asks for the outcome at the end.
M1='This is a platform probe. Follow these steps exactly and do nothing else.
Step 1. In ONE message make two Agent tool calls in parallel:
 (a) subagent_type "probe:probe-verifier", name "verifier", run_in_background true, prompt: "You are the verifier. Reply with the single line VERIFIER-READY and finish."
 (b) subagent_type "probe:probe-author", name "author", run_in_background true, prompt: "You are the author. Use SendMessage with to=verifier and message: PING-FROM-AUTHOR nonce=4412. Please reply to author with SendMessage, text PONG-FROM-VERIFIER nonce=4412. Then finish with AUTHOR-DONE."
Step 2. Wait until both have reported back.
Step 3. Use SendMessage with to=author and message: "Quote verbatim any message you received from verifier, then finish." Wait for its report.
Step 4. Reply with the single line PAIR-DONE, then one line per agent giving the agent id it was given.'
PROBE_INJECT=1 "$HERE/run.sh" "m1_pair_$TAG" --model sonnet "${CAP[@]}" -- "$M1"

# M2: one foreground plugin subagent: SubagentStart additionalContext reaches it (CONTEXT-SEEN),
# and SubagentStop `decision: block` is honoured once (the author must append PINEAPPLE).
M2='This is a platform probe. Call the Agent tool once, in the foreground: subagent_type "probe:probe-author", name "solo", prompt "Say hello in one short line, then finish." When it returns, reply with its full report verbatim and nothing else.'
PROBE_INJECT=1 PROBE_BLOCK=1 "$HERE/run.sh" "m2_inject_block_$TAG" --model sonnet "${CAP[@]}" -- "$M2"

# M3: the same small task with and without the main-thread agent.
M3='Create a file named hello.txt in the current directory containing the word hi. Then list which tools you used and say what you know about the git state of this directory.'
"$HERE/run.sh" "m3_default_$TAG" --model sonnet "${CAP[@]}" -- "$M3"
"$HERE/run.sh" "m3_agent_$TAG" --model sonnet --agent probe:probe-author "${CAP[@]}" -- "$M3"

# M4: real compaction: PostCompact fields; SessionStart(compact); additionalContext after compact.
PROBE_INJECT=1 "$HERE/run_stream.sh" "m4_compact_$TAG" --model haiku "${CAP[@]}" -- \
  'msg "Remember the word FIG. Reply OK."; sleep 12; msg "Remember the word PLUM. Reply OK."; sleep 12; msg "/compact"; sleep 25; msg "Which two words did I ask you to remember?"; sleep 12'

# M5: SendMessage from the main thread to a finished named subagent (resume by name) + hand-back UPS.
M5='This is a platform probe. Step 1: Agent tool, subagent_type "probe:probe-verifier", name "v2", run_in_background true, prompt "Reply VERIFIER-READY and finish." Step 2: wait for its report. Step 3: SendMessage to=v2 message "Reply AGAIN and finish." Step 4: wait for its report, then reply DONE.'
"$HERE/run.sh" "m5_resume_$TAG" --model sonnet "${CAP[@]}" -- "$M5"
# M6: as M5 but in auto mode, where subagents report through SubagentHandback (hooks.md, tools-reference.md).
"$HERE/run.sh" "m6_auto_resume_$TAG" --model sonnet --permission-mode auto "${CAP[@]}" -- "$M5"
echo "tag=$TAG; now: $HERE/analyze.sh $TAG"
