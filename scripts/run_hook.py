"""Start one hook script lean: `python3 -S -I run_hook.py budget` (or `handback`) reads the hook JSON from stdin and runs that script's `main()`.

The script is imported, not run as `__main__`, so Python keeps its bytecode in `scripts/__pycache__` (a script run directly is compiled at every start: 6 to 10 ms for
`budget.py`), and `-S -I` skip `site` and the environment (11 ms). Same behaviour as `python3 <script>`: the hook never fails an agent and exits 0.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.argv[1:] in (["budget"], ["handback"]):
    __import__(sys.argv[1]).main()
