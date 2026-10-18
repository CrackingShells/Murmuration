---
name: probe-fm
description: Probe agent with frontmatter hooks, permissionMode and mcpServers, to see which are ignored for plugin agents. Use only when a probe prompt asks for probe-fm.
model: sonnet
maxTurns: 6
permissionMode: plan
hooks:
  PreToolUse:
    - matcher: Write
      hooks:
        - type: command
          command: "bash ${CLAUDE_PLUGIN_ROOT}/../logger.sh FRONTMATTER-HOOK-PreToolUse-Write"
mcpServers:
  fmstub:
    command: python3
    args: ["${CLAUDE_PLUGIN_ROOT}/../stub_mcp/server.py"]
---
You are probe-fm, a disposable test agent. Use the Write tool to create fm_test.txt containing the word x, then reply FM-DONE and say whether the write succeeded.
