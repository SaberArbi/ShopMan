#!/usr/bin/env python3
"""Fail if any locale file is missing keys present in en.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "locales"
REFERENCE = "en.json"


def load(name):
    with open(ROOT / name, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ref = load(REFERENCE)
    ok = True
    for path in sorted(ROOT.glob("*.json")):
        if path.name == REFERENCE:
            continue
        data = load(path.name)
        missing = set(ref) - set(data)
        extra = set(data) - set(ref)
        if missing:
            ok = False
            print(f"[{path.name}] missing {len(missing)} key(s):")
            for k in sorted(missing):
                print(f"    - {k}")
        if extra:
            print(f"[{path.name}] has {len(extra)} extra key(s) "
                  f"(not in {REFERENCE}):")
            for k in sorted(extra):
                print(f"    + {k}")
    if ok:
        print("Locales OK.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())