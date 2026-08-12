#!/usr/bin/env python3
"""Generate every agent's entry file from AGENTS.md.

Each coding agent looks for its own filename, and hand-maintaining six copies of
the same guidance guarantees they drift. AGENTS.md is the single source; this
script writes the rest and CI fails if they are stale.

    python scripts/sync_agent_files.py           # write
    python scripts/sync_agent_files.py --check   # verify, non-zero if stale
"""

from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "AGENTS.md"

BANNER = ("<!-- Generated from AGENTS.md by scripts/sync_agent_files.py. "
          "Edit AGENTS.md, not this file. -->\n\n")

# path -> (prefix, suffix). Formats that need front-matter get it here.
TARGETS = {
    "CLAUDE.md": (BANNER, ""),
    "GEMINI.md": (BANNER, ""),
    ".clinerules": (BANNER, ""),
    ".windsurfrules": (BANNER, ""),
    ".github/copilot-instructions.md": (BANNER, ""),
    ".cursor/rules/consulting-deck.mdc": (
        "---\ndescription: Build consulting slide decks that argue instead of "
        "describe\nglobs: ['**/*.pptx', '**/*deck*', '**/*slide*']\n"
        "alwaysApply: false\n---\n\n" + BANNER, ""),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    body = SOURCE.read_text(encoding="utf-8")
    stale = []
    for rel, (prefix, suffix) in TARGETS.items():
        path = ROOT / rel
        want = prefix + body + suffix
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != want:
                stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(want, encoding="utf-8")

    if args.check:
        if stale:
            print("stale agent files (run scripts/sync_agent_files.py): "
                  + ", ".join(stale), file=sys.stderr)
            return 1
        print("agent files are in sync")
        return 0
    print(f"wrote {len(TARGETS)} agent entry files from AGENTS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
