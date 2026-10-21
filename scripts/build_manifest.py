#!/usr/bin/env python3
"""Write bin/manifest.json: what the committed guard binaries were built from.

Python standard library only. Run after the binaries under bin/<target>/ are built and copied (the pre-commit hook and the CI job do it):

    python3 -I scripts/build_manifest.py [--root DIR]

The manifest holds the sha256 of each bin/<target>/murmuration, the sha256 of scripts/permission_guard.py, the sha256 of each Rust source file (rust/Cargo.toml, Cargo.lock,
gen_tables.py and rust/src/*.rs) and one hash over those (`rust_sources_sha256`). scripts/install_binary.py installs a binary only when all of them still match the tree it runs in.
`sources_hash()` is also what the installer imports to recompute the source hash, so both sides use one definition.
"""
import hashlib
import json
import os
import sys

RUST_FILES = ["rust/Cargo.toml", "rust/Cargo.lock", "rust/gen_tables.py"]


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rust_source_paths(root):
    src = os.path.join(root, "rust", "src")
    names = sorted(os.path.join("rust", "src", n) for n in os.listdir(src) if n.endswith(".rs")) if os.path.isdir(src) else []
    return [p for p in RUST_FILES if os.path.isfile(os.path.join(root, p))] + names


def sources_hash(root):
    """(per-file hashes, one combined hash) of the Rust sources under root."""
    per = {p: sha256_file(os.path.join(root, p)) for p in rust_source_paths(root)}
    combined = hashlib.sha256("".join("%s\0%s\n" % (p, h) for p, h in sorted(per.items())).encode()).hexdigest()
    return per, combined


def build(root):
    binaries = {}
    bindir = os.path.join(root, "bin")
    for target in sorted(os.listdir(bindir)):
        p = os.path.join(bindir, target, "murmuration")
        if os.path.isfile(p):
            binaries[target] = sha256_file(p)
    per, combined = sources_hash(root)
    return {"format": 1, "binaries": binaries, "permission_guard_py_sha256": sha256_file(os.path.join(root, "scripts", "permission_guard.py")),
            "rust_sources": per, "rust_sources_sha256": combined}


def main():
    root = sys.argv[sys.argv.index("--root") + 1] if "--root" in sys.argv else os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    m = build(root)
    with open(os.path.join(root, "bin", "manifest.json"), "w") as fh:
        json.dump(m, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("bin/manifest.json: %d binaries, %d rust sources" % (len(m["binaries"]), len(m["rust_sources"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
