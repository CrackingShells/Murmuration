#!/bin/sh
for c in python3 git uv colgrep claude; do printf "%s=%s\n" $c "$(command -v $c)"; done
python3 -c "import sys;print(sys.executable)"
