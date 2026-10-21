## h1: each doubt falls back, visibly

| fault | installed | notice on stdout (additionalContext) | stderr line | exit | named cause | decisions equal the tree's permission_guard.py (registered, malformed, 300+60 fuzz: events differing) |
|:--|:--|:--|:--|--:|:--|:--|
| permission_guard.py edited after the build | launcher | yes | yes | 0 | yes | equal: registered 121 71 0; malformed 4 3 0; fuzz_bash 300 122 0; fuzz_write 60 20 0 |

first notice text: `murmuration guard: the permission guard runs as the Python script scripts/permission_guard.py, not the Rust binary, because scripts/permission_guard.py changed since the binaries were built. Decisions are the Python guard's. To get the binary back, rebuild it with the pre-commit hook or `cargo build --release --offline` followed by `python3 scripts/build_manifest.py`, or reinstall the plugin; until then the Python guard decides, which is correct and slower.`

| rust source edited after the build | launcher | yes | yes | 0 | yes | equal: registered 121 71 0; malformed 4 3 0; fuzz_bash 300 122 0; fuzz_write 60 20 0 |
| one byte flipped in the binary | launcher | yes | yes | 0 | yes | equal: registered 121 71 0; malformed 4 3 0; fuzz_bash 300 122 0; fuzz_write 60 20 0 |
| a binary that answers wrongly (stub allows everything; manifest rebuilt so only the self-test can catch it) | launcher | yes | yes | 0 | yes | equal: registered 121 71 0; malformed 4 3 0; fuzz_bash 300 122 0; fuzz_write 60 20 0 |
| bin/manifest.json missing (extra case) | launcher | yes | yes | 0 | yes | equal: registered 121 71 0; malformed 4 3 0; fuzz_bash 300 122 0; fuzz_write 60 20 0 |

h1 (first 4 faults): 4 of 4 install the launcher, name the cause and decide like permission_guard.py

## h2: the clean tree installs the binary

- native (aarch64-apple-darwin): exit 0, installed binary, stdout '', stderr '', binary sha equals manifest: True, stamp present: True, 1039 ms cold
- native decisions: equal registered 121 71 0; malformed 4 3 0; fuzz_bash 300 126 0; fuzz_write 60 25 0
- x86_64 under Rosetta (`arch -x86_64 /usr/bin/python3`, Python 3.9.6 x86_64): exit 0, installed binary, stdout '', stderr '', binary sha equals the x86_64 manifest entry: True, 2724 ms cold

