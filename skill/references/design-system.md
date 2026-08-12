# Design system

Every slide is drawn from scratch onto a blank canvas. There is no template
file, no inherited master, and no layout placeholders — which means this design
is defined entirely by the constants in `scripts/deckkit.py` and belongs to
whoever ships it.

Read this when you need to place shapes directly, extend the system with a new
slide type, or re-skin it for a brand.

## The idea behind it

Four decisions do most of the work. Understanding them matters more than
memorising the coordinates, because they tell you what a *new* slide type
should look like.

**The assertion is the largest thing on the slide.** Corporate decks usually
set a category label large ("Market analysis") and the finding small. That
inverts the reader's job. Here a small letterspaced eyebrow names the category
and the finding takes the 30pt line, so someone flipping pages reads the
argument rather than the table of contents.

**A hairline frame, not filled furniture.** A rule under the header, a rule
above the footer, page numbers, and one short accent bar. Structure comes from
alignment and whitespace. Coloured bands and boxes make dense analytical slides
feel cramped, and they age badly.

**Everything left-aligns to one margin — including the big numerals.** A
centred 190pt figure reads as a poster. A left-aligned one reads as a page in a
document, which is what a consulting deck is.

**One accent colour, used sparingly.** The accent marks the operative thing and
nothing else: the bar, the eyebrow, a callout, the emphasised series. When
everything is coloured, colour stops carrying meaning.

## Canvas and grid

13.333 × 7.5 in (16:9). Inches throughout.

| Constant | Value | What it is |
|---|---|---|
| `MARGIN` | 0.75 | the only left/right margin; everything aligns here |
| `CONTENT_W` | 11.833 | margin to margin |
| `HEAD_RULE_Y` | 0.55 | hairline under the header |
| `BAR_Y` | 0.88 | accent bar, 0.62 × 0.045 |
| `EYEBROW_Y` | 1.03 | category label |
| `TITLE_Y` | 1.32 | the assertion |
| `BODY_TOP` | 2.32 | first supporting line |
| `FOOT_RULE_Y` | 6.72 | hairline above the footer |
| `SOURCE_Y` | 6.82 | provenance line and page number |

Column tracks are computed, not fixed: `_column_track` divides `CONTENT_W` by
the number of columns with a 0.55 gutter, so two- and three-column slides share
the same outer edges.

When a chart occupies part of a slide, pass `body_width` to `content()` so the
supporting text stops before it. Text running under a chart is the most common
way these slides break.

## Type scale

| Role | Size | Treatment |
|---|---|---|
| Statement numeral | 190 | bold, left-aligned, paper on ink or ink on paper |
| Chapter numeral | 132 | bold, accent, on ink |
| Cover title | 46 | bold, paper on ink |
| Chapter title | 34 | bold, paper on ink |
| Quote | 32 | bold, paper on ink |
| Assertion (`SZ_TITLE`) | 30 | bold, ink |
| Lead / column head (`SZ_LEAD`) | 19 | bold for heads, regular for captions |
| Body (`SZ_BODY`) | 16 | slate; ink when bolded for emphasis |
| Dense lists (`SZ_SMALL`) | 13 | column tracks, pull quotes |
| Eyebrow (`SZ_EYEBROW`) | 11 | uppercase, accent, 1.4pt letterspacing |
| Source, unit, page (`SZ_SOURCE`) | 9.5 | muted |

Fonts default to Arial with 微软雅黑 / 黑体 as the East Asian faces, so a deck
renders the same on a machine that has no brand fonts installed. `set_font`
writes the East Asian face directly — PowerPoint tracks it separately, and
Chinese text falls back to an ugly default if only the latin face is set.

## Palette

| Name | Hex | Use |
|---|---|---|
| `ink` | `16181D` | all primary text; dark fields |
| `paper` | `F7F6F3` | default field; text on ink |
| `accent` | `C8442A` | bars, eyebrows, callouts, primary series |
| `teal` | `2E6F6B` | second series |
| `ochre` | `C08A2E` | third series |
| `slate` | `5A6472` | supporting prose |
| `rule` / `rule_d` | `D8D4CC` / `3A3E47` | hairlines on paper / on ink |
| `muted` | `8A8F98` | sources, units, axis labels |
| `band` | `EEEBE5` | evidence band, table zebra |

To re-skin for a brand: change `accent` first, then `ink` if the brand's dark
is not near-black. Everything reads from `COLORS`, so those two edits carry the
whole deck. Keep the accent to one colour — the system depends on it being
scarce.

## Slide types

`title_slide(title, subtitle, kicker)` — ink field, accent bar, 46pt title.

`section(number, title, scope)` — chapter divider. Oversized accent numeral at
the margin, rule, title, and a one-line statement of what the chapter covers.
Number them for real; the reader uses it to gauge remaining runway.

`content(category, message, body, source, body_width)` — the workhorse.
Eyebrow, assertion, hanging-dash supporting lines, source.

`canvas(category, message, source)` — header only; the base for diagrams,
matrices, and tables.

`big_stat(number, caption, unit_suffix, variant, source, eyebrow)` — one figure
at 190pt with the caption beneath. `variant="ink"` (default) or `"paper"`.
Alternate them so consecutive statement slides don't repeat.

`quote_slide(label, quote, note)` — verbatim finding on ink, oversized accent
quotation mark.

`two_columns` / `three_columns` — column tracks with an accent bar over each
head. Two columns is for genuine opposition; three is for parallel items only.

`rh_image(title, body, image, source, category)` — statement left, full-height
image right.

`table(rows, ..., highlight_rows)` — ink header, hairline zebra, accent tint on
highlighted rows. Reserve the last column for what the row *means*.

`evidence_band()` + `pull_quote()` — the compressed-evidence pattern: one
artifact, one chart, two or three attributed quotes inside a tinted band.

`closing(org, contact, note)` — ink field with your own details. There is no
built-in wordmark; supply your own.

## Charts

`column_chart` (single series, the default for time or few categories),
`grouped_column_chart` (two or three series max), `bar_chart` (when category
labels are words, not years), `pie_chart` (composition only, ≤6 slices,
doughnut by default).

All of them: labels on, value axis hidden, gridlines off, chart chrome
stripped so the plot sits directly on the paper field. Pass `unit=` and it is
right-aligned above the chart's right edge; pass `source=` and it lands on the
footer line. Add a `callout()` for the thing the reader is meant to notice — a
chart states a fact, the callout states the point of it.

## Extending it

New slide type? Start from `_new()` for the field, `_header()` for the eyebrow
and assertion, and keep everything on the `MARGIN` axis. Reach for `rule()`
rather than a filled shape when you need to separate things. If you find
yourself adding a second accent colour or a centred element, that is the signal
to reconsider — the system's coherence comes from those two constraints more
than from anything else.
