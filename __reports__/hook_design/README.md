# hook_design

How to design a Claude Code hook so that it costs little and fails the way it should. Written from
wave 7 of the Murmuration reflective run; meant to be copied into other repositories.

## Round 00 (2026-10-22)

- `00-knowledge_transfer_v0.md` (latest): where a hook's start time goes (exec counts, the shell in
  front of every string-form hook), which hooks the loop must wait for and which can be `async`,
  platform behaviour found by testing, and the practice that follows.

## Status

v0, from headless runs on Claude Code 2.1.304 on one macOS machine. Not yet checked in the Desktop
app, in interactive mode, or on Linux and Windows.
