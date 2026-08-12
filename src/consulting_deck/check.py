#!/usr/bin/env python3
"""Deck checker — catch the things that actually go wrong in a consulting deck.

    consulting-deck check deck.pptx [--strict]
    consulting-deck titles deck.pptx

Two classes of finding:

  ERROR   the deck is visibly broken — a shape off the canvas, text that will
          overflow its box, a figure with no source. Fix before delivering.
  WARN    a style drift — a title that labels instead of asserting, a paragraph
          long enough that it should have been a chart, a section with no
          statement slide to break the rhythm.

Warnings are judgement calls; read them, then decide. `--strict` makes them
exit non-zero too, which is useful in a build loop.

This checker is static — it estimates overflow from character counts and box
geometry. It will not catch overlap or truncation. Render the deck and look at
it as well:

    soffice --headless --convert-to pdf deck.pptx && pdftoppm -png -r 70 deck.pdf p
"""

from __future__ import annotations

import re
import sys
from collections import Counter

from pptx import Presentation
from pptx.util import Emu

EMU_IN = 914400.0
SLIDE_W, SLIDE_H = 13.333, 7.5

DIGIT = re.compile(r"\d")
SOURCE_HINT = re.compile(r"(数据来源|资料来源|实例来源|图片来源|来源|待验证|数据待补|source|Source|SOURCE|DATA REQUIRED|Unit:|单位)")
# A figure that needs a citation, as opposed to a date, a list number, or a
# version. Percentages, large numbers, and multiples are claims about the world.
CLAIM = re.compile(r"(\d+(\.\d+)?\s*%|\d+(\.\d+)?\s*[亿万倍]|\b\d{3,}\b)")
# Titles that name a topic rather than state a finding.
LABEL_ONLY = re.compile(
    r"^(概述|简介|背景|现状|分析|总结|结论|趋势|市场|行业|问题|方案|介绍|目录|附录"
    r"|overview|introduction|background|summary|conclusion|analysis|agenda|appendix"
    r"|market|industry|trends?|context|approach|methodology)[\s:：]*$",
    re.IGNORECASE)

A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

# One CJK glyph is about one em wide; a latin character about half that. Counting
# in half-em "units" lets one formula cover mixed-script text, which these decks
# always are.
def visual_len(s: str) -> float:
    return sum(2.0 if ord(c) > 0x2E80 else 1.0 for c in s)


def capacity(width_in: float, height_in: float, size_pt: float) -> float:
    """Half-em units that fit in a box: (units per line) × (number of lines),
    at 1.25 line spacing. Deliberately generous — this is a static estimate and
    a false alarm costs more attention than it saves."""
    if size_pt <= 0:
        return float("inf")
    per_line = 144.0 * width_in / size_pt
    lines = 57.6 * height_in / size_pt
    return per_line * lines


def autofit(shape):
    """Returns ('shrink', scale) | ('grow', 1.0) | (None, 1.0).

    A box set to shrink text on overflow, or to grow to fit it, is not going to
    clip — checking it against fixed geometry produces noise."""
    try:
        bodyPr = shape.text_frame._bodyPr
    except Exception:
        return None, 1.0
    if bodyPr.find(A_NS + "spAutoFit") is not None:
        return "grow", 1.0
    na = bodyPr.find(A_NS + "normAutofit")
    if na is not None:
        return "shrink", int(na.get("fontScale", 100000)) / 100000.0
    return None, 1.0


def shape_text(shape):
    if not shape.has_text_frame:
        return ""
    return "\n".join(p.text for p in shape.text_frame.paragraphs)


def dominant_size(shape, default=18.0):
    counts = Counter()
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            if r.font.size:
                counts[r.font.size.pt] += visual_len(r.text)
    return counts.most_common(1)[0][0] if counts else default


def slide_kind(slide):
    """Coarse structural class of a slide, used for the rhythm check."""
    has_chart = has_table = False
    biggest = 0.0
    for sh in slide.shapes:
        if getattr(sh, "has_chart", False):
            has_chart = True
        if getattr(sh, "has_table", False):
            has_table = True
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size and r.font.size.pt > biggest:
                        biggest = r.font.size.pt
    if biggest >= 100:
        return "statement/divider"
    if has_chart:
        return "chart"
    if has_table:
        return "table"
    return "text"


def storyline(path):
    """Print each slide's title and leading assertion, in order.

    The title-only read is the fastest way to find out whether a deck argues or
    merely covers ground. Read the output as continuous prose: if it runs
    "Market · Customer · Technology · Conclusion" the deck has topics where it
    needs findings, and no amount of formatting will fix that."""
    prs = Presentation(path)
    print(f"{path} — storyline read ({len(prs.slides)} slides)\n")
    for i, slide in enumerate(prs.slides, 1):
        lines = []
        for sh in slide.shapes:
            txt = shape_text(sh).strip()
            if not txt:
                continue
            # The assertion is the *first* paragraph of the body, and it is
            # usually outweighed by the supporting lines beneath it — so size
            # the lead paragraph, not the shape as a whole.
            head = txt.split("\n")[0].strip()
            size = 0.0
            for p in sh.text_frame.paragraphs:
                if p.text.strip():
                    size = max((r.font.size.pt for r in p.runs if r.font.size),
                               default=18.0)
                    break
            if size >= 24 and 2 < visual_len(head) < 130:
                lines.append((size, head))
        lines.sort(key=lambda x: -x[0])
        said = " — ".join(dict.fromkeys(t for _, t in lines[:2])) or "(no text)"
        flag = "  ← labels a topic" if lines and LABEL_ONLY.match(lines[0][1]) else ""
        print(f"{i:>3}. {said}{flag}")
    print("\nRead that as prose. Does it argue, or does it just cover ground?")
    return 0


def check(path, strict=False):
    prs = Presentation(path)
    errors, warns = [], []
    stat_slides = 0
    total = len(prs.slides)
    layout_run, last_layout, run_start = 0, None, 1

    for i, slide in enumerate(prs.slides, 1):
        tag = f"slide {i}"
        texts, has_claim, has_source, has_chart = [], False, False, False
        biggest, biggest_text = 0.0, ""

        # Rhythm: a long run of structurally identical slides is the signature
        # of a deck that stopped thinking and started filling pages. Keyed on
        # what the slide *is* rather than which layout produced it, since a
        # drawn deck uses one blank layout throughout.
        name = slide_kind(slide)
        if name == last_layout:
            layout_run += 1
        else:
            if layout_run >= 8:
                warns.append(f"slides {run_start}-{i - 1}: {layout_run} consecutive "
                             f"{last_layout} slides — break the run with a "
                             f"statement slide, a comparison, or a synthesis")
            layout_run, last_layout, run_start = 1, name, i

        for sh in slide.shapes:
            if sh.has_chart if hasattr(sh, "has_chart") else False:
                has_chart = True

            txt = shape_text(sh).strip()

            # Off-canvas only matters for shapes carrying text. Decorative
            # freeforms and images bleed past the edge on purpose — that's what
            # gives the template its full-bleed look.
            if txt and None not in (sh.left, sh.top, sh.width, sh.height):
                l, t = sh.left / EMU_IN, sh.top / EMU_IN
                r, b = l + sh.width / EMU_IN, t + sh.height / EMU_IN
                if l < -0.3 or t < -0.3 or r > SLIDE_W + 0.3 or b > SLIDE_H + 0.3:
                    errors.append(f"{tag}: text runs off the canvas "
                                  f"({l:.2f},{t:.2f})–({r:.2f},{b:.2f}) — "
                                  f"{txt[:28]!r}")

            if not txt:
                continue
            texts.append(txt)

            if SOURCE_HINT.search(txt) and visual_len(txt) < 200:
                has_source = True
            if CLAIM.search(txt) and not SOURCE_HINT.search(txt):
                has_claim = True

            size = dominant_size(sh)
            if size > biggest:
                biggest, biggest_text = size, txt.split("\n")[0].strip()

            # overflow estimate
            mode, scale = autofit(sh)
            if mode != "grow" and None not in (sh.width, sh.height):
                w, h = sh.width / EMU_IN, sh.height / EMU_IN
                if w > 0.4 and h > 0.25:
                    cap = capacity(w, h, size * scale)
                    load = visual_len(txt)
                    if load > cap * 2.2:
                        errors.append(
                            f"{tag}: text overflows its box "
                            f"(~{load:.0f} units in ~{cap:.0f} at {size * scale:.0f}pt) "
                            f"— {txt[:36]!r}")
                    elif load > cap * 1.4:
                        warns.append(
                            f"{tag}: text is tight in its box "
                            f"(~{load:.0f} units in ~{cap:.0f}) — {txt[:36]!r}")

            # paragraph walls
            for p in sh.text_frame.paragraphs:
                if visual_len(p.text) > 180:
                    warns.append(f"{tag}: {visual_len(p.text):.0f}-unit paragraph — "
                                 f"convert to a chart, a table, or an appendix page")
                    break

        joined = "\n".join(texts)
        if not joined.strip():
            continue

        # Statement slides: a lone huge figure. A bare single digit at that size
        # is a chapter divider, not a statistic, and counting those would make
        # every well-structured deck look over-punctuated.
        if biggest >= 100 and DIGIT.search(biggest_text) \
                and not re.fullmatch(r"\d", biggest_text.strip()):
            stat_slides += 1

        if (has_claim or has_chart) and not has_source:
            errors.append(f"{tag}: carries a figure but has no source line — "
                          f"add 数据来源 / Source, or cut the figure")

        if biggest_text and LABEL_ONLY.match(biggest_text.strip()):
            # only a problem if nothing else on the slide asserts anything
            others = [t for t in texts if t.strip() != biggest_text]
            if not any(visual_len(t) > 20 for t in others):
                warns.append(f"{tag}: title {biggest_text!r} labels a topic but the "
                             f"slide states no finding")

        if visual_len(joined) > 900:
            warns.append(f"{tag}: ~{visual_len(joined):.0f} units of text on one "
                         f"slide — split it or move detail to an appendix")

    if layout_run >= 8:
        warns.append(f"slides {run_start}-{total}: {layout_run} consecutive "
                     f"{last_layout} slides — break the run with a statement "
                     f"slide, a comparison, or a synthesis")

    if total >= 12 and stat_slides == 0:
        warns.append("deck: no big-statement slides — a long deck with no rhythm "
                     "break is exhausting; pull one number per section onto its own "
                     "dark slide")
    if total >= 20 and stat_slides > total / 6:
        warns.append(f"deck: {stat_slides} statement slides in {total} — they stop "
                     f"landing when frequent; aim for about one per section")

    print(f"{path}: {total} slides, {len(errors)} error(s), {len(warns)} warning(s)\n")
    for e in errors:
        print("  ERROR  " + e)
    if errors and warns:
        print()
    for w in warns:
        print("  WARN   " + w)
    if not errors and not warns:
        print("  clean — now render it and look at it before you ship")

    return 1 if errors or (strict and warns) else 0
