"""Build a deck from a declarative spec.

This exists so the system is usable by an agent that can write a file and run a
command, without needing to write Python. Every coding agent can emit YAML or
JSON; not every agent can be trusted to write correct python-pptx calls.

The spec is a mapping with optional `lang`, `theme`, and a list of `slides`.
Each slide is a mapping with a `type` and the fields that type needs — see
`SLIDE_TYPES` below, or run `consulting-deck schema` for the full list.

    lang: en
    theme: slate                # or {base: mono, accent: "#0B5FFF"}
    slides:
      - type: title
        title: Market entry study
        subtitle: Ready-to-drink tea · China
      - type: section
        number: 1
        title: Market size
        scope: What the category looks like today
      - type: content
        category: Industry status
        message: The category is large, growing fast, and priced down.
        body:
          - Revenue reached ¥181bn in 2022, up 108% since 2018
          - ["Mid-tier brands hold 70% of outlets", true]   # [text, bold]
        source: CIC, Xinhua
        body_width: 5.4
        chart:
          kind: column
          categories: ["2018", "2022"]
          values: [870, 1810]
          at: [6.6, 2.75, 5.2, 3.2]
          unit: ¥100m
          callout: {text: "+108%", at: [8.4, 3.1]}
"""

from __future__ import annotations

import json
import os
from typing import Any

from .deck import Deck
from .themes import THEMES

SLIDE_TYPES = {
    "title": "title, subtitle, kicker",
    "section": "number, title, scope",
    "content": "category, message, body[], source, body_width, chart{}",
    "canvas": "category, message, source, chart{}",
    "stat": "number, caption, unit, variant(ink|paper), source, eyebrow",
    "quote": "label, quote, note",
    "columns": "title, category, columns[{head, items[]}], source",
    "table": "category, message, rows[[]], col_widths[], highlight_rows[], source",
    "image": "title, body[], image, category, source",
    "closing": "org, contact, note",
}

CHART_KINDS = ("column", "grouped_column", "bar", "pie", "doughnut")


class SpecError(ValueError):
    """Raised with a message aimed at whoever wrote the spec, not at a stack trace."""


def _body(items) -> list:
    """Body lines accept a plain string, or [text, bold], or a list of those
    pairs for mid-sentence emphasis. JSON has no tuples, so lists are coerced."""
    out = []
    for item in items or []:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, list) and item and isinstance(item[0], str) \
                and len(item) == 2 and isinstance(item[1], bool):
            out.append((item[0], item[1]))
        elif isinstance(item, list):
            out.append([(p[0], bool(p[1])) for p in item])
        else:
            raise SpecError(f"body item {item!r} must be a string or [text, bold]")
    return out


def _add_chart(deck: Deck, slide, chart: dict):
    kind = chart.get("kind", "column")
    if kind not in CHART_KINDS:
        raise SpecError(f"chart kind {kind!r} must be one of {', '.join(CHART_KINDS)}")
    at = chart.get("at") or [6.6, 2.75, 5.2, 3.2]
    if len(at) != 4:
        raise SpecError("chart 'at' must be [left, top, width, height] in inches")
    common = dict(unit=chart.get("unit"), source=chart.get("source"))
    fmt = chart.get("number_format", "0")
    if kind == "grouped_column":
        series = [(s["name"], s["values"]) for s in chart["series"]]
        obj = deck.grouped_column_chart(slide, chart["categories"], series, *at,
                                        number_format=fmt, **common)
    elif kind == "bar":
        obj = deck.bar_chart(slide, chart["categories"], chart["values"], *at,
                             number_format=fmt, **common)
    elif kind in ("pie", "doughnut"):
        obj = deck.pie_chart(slide, chart["categories"], chart["values"], *at,
                             doughnut=(kind == "doughnut"), source=chart.get("source"))
    else:
        obj = deck.column_chart(slide, chart["categories"], chart["values"], *at,
                                number_format=fmt, **common)
    callout = chart.get("callout")
    if callout:
        deck.callout(slide, callout["text"], *callout.get("at", [at[0] + 1, at[1] + 0.4]))
    return obj


def build(spec: dict[str, Any], out_path: str, theme=None) -> str:
    """Build a .pptx from a spec mapping. Returns the written path.

    `theme` overrides whatever the spec names, so one spec can be rendered in
    several identities without editing it."""
    if not isinstance(spec, dict) or "slides" not in spec:
        raise SpecError("spec must be a mapping with a 'slides' list")
    try:
        d = Deck(lang=spec.get("lang", "en"), theme=theme or spec.get("theme"))
    except (ValueError, TypeError) as exc:
        raise SpecError(f"{exc}. Available themes: {', '.join(sorted(THEMES))}") from exc

    for i, raw in enumerate(spec["slides"], 1):
        if "type" not in raw:
            raise SpecError(f"slide {i} has no 'type'")
        kind = raw["type"]
        s = dict(raw)
        s.pop("type")
        try:
            if kind == "title":
                d.title_slide(s.get("title", ""), s.get("subtitle"), s.get("kicker"))
            elif kind == "section":
                d.section(s.get("number", i), s.get("title", ""), s.get("scope"))
            elif kind in ("content", "canvas"):
                if kind == "content":
                    slide = d.content(s.get("category", ""), s.get("message", ""),
                                      _body(s.get("body")), s.get("source"),
                                      body_width=s.get("body_width"))
                else:
                    slide = d.canvas(s.get("category", ""), s.get("message"),
                                     s.get("source"))
                if s.get("chart"):
                    _add_chart(d, slide, s["chart"])
            elif kind == "stat":
                d.big_stat(s.get("number", ""), s.get("caption", ""),
                           unit_suffix=s.get("unit", ""),
                           variant=s.get("variant"),   # None = theme default
                           source=s.get("source"), eyebrow=s.get("eyebrow"))
            elif kind == "quote":
                d.quote_slide(s.get("label", ""), s.get("quote", ""), s.get("note"))
            elif kind == "columns":
                cols = [(c["head"], _body(c.get("items"))) for c in s.get("columns", [])]
                if len(cols) == 2:
                    d.two_columns(s.get("title", ""), cols[0][0], cols[0][1],
                                  cols[1][0], cols[1][1], source=s.get("source"),
                                  category=s.get("category"))
                elif len(cols) == 3:
                    d.three_columns(s.get("title", ""), cols, source=s.get("source"),
                                    category=s.get("category"))
                else:
                    raise SpecError("columns slides take exactly 2 or 3 columns")
            elif kind == "table":
                slide = d.canvas(s.get("category", ""), s.get("message"), s.get("source"))
                d.table(slide, s["rows"], col_widths=s.get("col_widths"),
                        highlight_rows=tuple(s.get("highlight_rows", ())))
            elif kind == "image":
                d.rh_image(s.get("title", ""), _body(s.get("body")), s.get("image"),
                           source=s.get("source"), category=s.get("category"))
            elif kind == "closing":
                d.closing(s.get("org"), s.get("contact"), s.get("note"))
            else:
                raise SpecError(f"unknown slide type {kind!r}; "
                                f"known: {', '.join(sorted(SLIDE_TYPES))}")
        except SpecError:
            raise
        except KeyError as exc:
            raise SpecError(f"slide {i} ({kind}) is missing required field {exc}") from exc
    return d.save(out_path)


def load(path: str) -> dict:
    """Read a spec from .json, or .yaml/.yml if PyYAML is available."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if os.path.splitext(path)[1].lower() in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError as exc:
            raise SpecError(
                "YAML specs need PyYAML — `pip install consulting-deck[yaml]`, "
                "or write the spec as .json instead") from exc
        return yaml.safe_load(text)
    return json.loads(text)
