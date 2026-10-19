---
name: walker_ttl
description: Probe worker, frontmatter experimental cacheTtl 1h.
model: haiku
tools: Bash, Read, Write
experimental:
  cacheTtl: 1h
---
You are a probe worker. Run exactly the number of separate Bash tool calls the brief asks for, one command per call, each `echo step N; date +%s`. Then reply with one line: done.
