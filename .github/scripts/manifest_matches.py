"""Exit 0 when plugins/murmuration/bin/manifest.json was written from the sources in this checkout, else 1.

    python3 -I .github/scripts/manifest_matches.py

Compares scripts_sha256 and rust_sources_sha256, the two fields install_binary.py trusts, against what build_manifest.py computes from the tree now, and requires a binary for every target in ALL_TARGETS.
Used by the `changes` job (a stale manifest makes a push gated) and by the `release` job (never release a tree whose binaries are not its own).
Standard library only; lives outside plugins/murmuration so that it is not shipped.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PLUGIN = os.path.join(ROOT, "plugins", "murmuration")
KEYS = ("scripts_sha256", "rust_sources_sha256")


def main():
    sys.dont_write_bytecode = True  # no __pycache__ in the plugin tree: the release job bumps a clean checkout
    sys.path.insert(0, os.path.join(PLUGIN, "scripts"))
    import build_manifest

    try:
        with open(os.path.join(PLUGIN, "bin", "manifest.json"), encoding="utf-8") as fh:
            have = json.load(fh)
    except (OSError, ValueError) as err:
        print("manifest_matches: cannot read bin/manifest.json: %s" % err)
        return 1
    now = build_manifest.build(PLUGIN)
    differ = [k for k in KEYS if have.get(k) != now[k]]
    missing = [t for t in build_manifest.ALL_TARGETS if t not in (have.get("binaries") or {})]
    if missing:
        print("manifest_matches: bin/manifest.json has no binary for %s" % ", ".join(missing))
        return 1
    if differ:
        print("manifest_matches: bin/manifest.json differs from the sources in %s: %s" % (", ".join(differ), PLUGIN))
        return 1
    print("manifest_matches: bin/manifest.json matches the sources (rust %s)" % now["rust_sources_sha256"][:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
