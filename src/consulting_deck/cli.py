"""Command-line entry point.

The point of this file is portability: any agent that can write a file and run
a shell command can produce a checked deck, without being able to write
python-pptx correctly.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .check import check, storyline
from .spec import SLIDE_TYPES, SpecError, build, load
from .themes import THEMES, describe


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="consulting-deck",
        description="Build and check consulting decks.")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a .pptx from a spec (.yaml/.json)")
    b.add_argument("spec")
    b.add_argument("-o", "--out", default="deck.pptx")
    b.add_argument("--theme", choices=sorted(THEMES),
                   help="override the theme named in the spec")
    b.add_argument("--check", action="store_true",
                   help="run the checker on the result and fail on errors")

    c = sub.add_parser("check", help="check a .pptx for the things that go wrong")
    c.add_argument("deck")
    c.add_argument("--strict", action="store_true", help="treat warnings as failures")

    t = sub.add_parser("titles", help="print the storyline read (titles + assertions)")
    t.add_argument("deck")

    sub.add_parser("schema", help="print the spec slide types")
    sub.add_parser("themes", help="list the available visual themes")

    args = parser.parse_args(argv)

    if args.cmd == "schema":
        print("slide types and their fields:\n")
        for name, fields in SLIDE_TYPES.items():
            print(f"  {name:<9} {fields}")
        print("\nSee references/design-system.md for geometry and palette.")
        return 0

    if args.cmd == "themes":
        print("available themes — pick one deliberately, or ask the reader:\n")
        print(describe())
        print("\nOverride any colour: theme: {base: slate, accent: \"#7A1FA2\"}")
        return 0

    if args.cmd == "check":
        return check(args.deck, args.strict)

    if args.cmd == "titles":
        return storyline(args.deck)

    try:
        path = build(load(args.spec), args.out, theme=args.theme)
    except SpecError as exc:
        print(f"spec error: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {path}")
    return check(path) if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
