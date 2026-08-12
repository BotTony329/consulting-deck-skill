#!/usr/bin/env python3
"""Package the installable skill and its Python runtime as a .skill bundle.

    python scripts/package_skill.py            -> dist/consulting-deck.skill
"""
from __future__ import annotations

import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

ROOT_FILES = ("SKILL.md", "README.md", "LICENSE", "pyproject.toml")
RUNTIME_DIRS = ("references", "src/consulting_deck", "examples")


def main() -> int:
    DIST.mkdir(exist_ok=True)
    out = DIST / "consulting-deck.skill"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in ROOT_FILES:
            path = ROOT / rel
            z.write(path, pathlib.Path("consulting-deck") / rel)
        for rel in RUNTIME_DIRS:
            base = ROOT / rel
            for path in sorted(base.rglob("*")):
                if (path.is_file()
                        and path.suffix not in {".pyc", ".pyo"}
                        and "__pycache__" not in path.parts
                        and not any(part.startswith(".") for part in path.parts)):
                    z.write(path, pathlib.Path("consulting-deck") / path.relative_to(ROOT))
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
