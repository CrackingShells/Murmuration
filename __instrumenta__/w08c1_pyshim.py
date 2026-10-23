# Runs scripts/budget.py or scripts/handback.py as the hook does (`main()` of run_hook.py) with the clock fixed to the MURMURATION_NOW of the environment (time.time and datetime.datetime.now), so a replay against the Rust test build needs no normalization.
# usage: MURMURATION_NOW=<epoch seconds> python3 -S -I w08c1_pyshim.py <scripts dir> budget|handback   (stdin: the hook event)
import os, sys, time, types
import datetime as _dt

NOW = float(os.environ["MURMURATION_NOW"])
time.time = lambda: NOW


class _DT(_dt.datetime):
    @classmethod
    def now(cls, tz=None):
        return _dt.datetime.fromtimestamp(NOW, tz)


_mod = types.ModuleType("datetime")
_mod.__dict__.update(_dt.__dict__)
_mod.datetime = _DT
sys.modules["datetime"] = _mod
sys.path.insert(0, sys.argv[1])
which = sys.argv[2]
sys.argv = ["run_hook.py", which]
__import__(which).main()
