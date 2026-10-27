# Settings record

`settings.local.json` here is a copy of the `.claude/settings.local.json` this repository tracked
until 2026-10-27 (commits 4586446 and 5eafc47). It is kept as part of the design record: it shows
how the lab was run during waves 1–9 (main agent `murmuration:research-pi`, the local development
marketplace, the deny rules for `pkill` and `killall`, and the compaction window).

Claude Code does not load it from this path. The live file is no longer tracked, because in a public
repository it would make every clone open as the research PI and point at a marketplace path that
exists only on the maintainer's machine. `/lab` writes the parts a lab project needs.
