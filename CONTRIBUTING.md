# Contributing

Bug reports and theme submissions are welcome. A few things that will save us both time.

## The thing to know first

Two parts live here and they have different bars. The **method** (`skill/`) changes
slowly and only with a reason — it encodes practice that survives contact with a
skeptical audience, not personal preference. The **engine** (`src/`) is ordinary
Python and moves faster.

## Before opening a PR

```bash
pip install -e ".[dev]"
pytest -q
python scripts/sync_agent_files.py --check
```

`AGENTS.md` is the single source for agent guidance. Never edit `CLAUDE.md`,
`GEMINI.md`, `.clinerules`, `.windsurfrules`, `.cursor/rules/*`, or
`.github/copilot-instructions.md` directly — edit `AGENTS.md` and run the sync script.
CI fails if they drift.

## Adding a theme

Copy an entry in `src/consulting_deck/themes.py`, change the colours and switches, and
add it to the README table. Two things a theme has to do:

- **Differ structurally, not just chromatically.** Use the switches — `dark_dividers`,
  `stat_default`, `caps_eyebrow`, `rule_weight`, `dark_content`. Six palettes on one
  layout is one theme in six colours.
- **Keep the accent scarce.** It marks the operative thing on a slide and nothing else.
  A theme where three elements compete for attention isn't finished.

Then render it and look — `tests/` proves it builds, not that it reads well:

```bash
python examples/market_entry.py
soffice --headless --convert-to pdf deck.pptx && pdftoppm -png -r 70 deck.pdf page
```

## Adding a slide type

Start from `_new()` for the field and `_header()` for the eyebrow and assertion, keep
everything on the `MARGIN` axis, and reach for `rule()` rather than a filled shape. Add
it to `SLIDE_TYPES` in `spec.py` so the CLI route reaches it too, and add a test.

If you find yourself introducing a second accent colour or centring something, that's
the signal to reconsider — the system's coherence rests on those two constraints more
than on anything else.

## What won't be merged

Anything that puts a third party's logo, wordmark, tagline, licensed photography, or
copied layout composition into the project. Method is portable; visual identity isn't.
