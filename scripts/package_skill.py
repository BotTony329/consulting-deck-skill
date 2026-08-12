#!/usr/bin/env python3
"""Package skill/ as a .skill bundle for Claude, and as a plain folder for others.

    python scripts/package_skill.py            -> dist/consulting-deck.skill
"""
from __future__ import annotations

import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skill"
DIST = ROOT / "dist"


def main() -> int:
    DIST.mkdir(exist_ok=True)
    out = DIST / "consulting-deck.skill"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(SKILL.rglob("*")):
            if path.is_file() and not path.name.startswith("."):
                z.write(path, pathlib.Path("consulting-deck") / path.relative_to(SKILL))
        # the engine travels with the skill so it works without a pip install
        for path in sorted((ROOT / "src" / "consulting_deck").glob("*.py")):
            z.write(path, pathlib.Path("consulting-deck") / "scripts" / path.name)
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
