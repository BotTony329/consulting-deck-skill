"""The slide system — an original editorial design, drawn from scratch.

Every slide is drawn from scratch onto a blank canvas. There is no template
file and no inherited master, which means the design here is defined entirely
by the constants below and is nobody else's property.

What the system is trying to do, so you can extend it coherently:

  *The assertion is the largest thing on the slide.* Most corporate decks make
  a category label big and the finding small, which inverts the reader's job.
  Here a small letterspaced eyebrow names the category and the finding gets the
  30pt line, so someone flipping pages reads the argument, not the table of
  contents.

  *A hairline frame, not filled furniture.* A rule under the header and above
  the footer, page numbers, and a short accent bar. Structure comes from
  alignment and whitespace rather than coloured bands, which keeps dense
  analytical slides from feeling boxed in.

  *Everything is left-aligned to one margin.* Including the big statement
  numerals. A centred numeral reads as a poster; a left-aligned one reads as
  part of a document, which is what a consulting deck is.

  *One accent colour, used sparingly.* The accent marks the operative thing on
  a slide and nothing else. When every element is coloured, colour stops
  meaning anything.

Typical use:

    from consulting_deck import Deck

    d = Deck(lang="en")
    d.title_slide("Market entry study", "Ready-to-drink tea, China")
    d.section(1, "Market size and demand", "What the category looks like today")
    s = d.content("Industry status",
                  "The category is large, growing fast, and priced down.",
                  ["Revenue reached ¥181bn in 2022, up 108% since 2018"],
                  source="CIC, Xinhua")
    d.column_chart(s, ["2018", "2022"], [870, 1810], 6.6, 2.6, 5.4, 3.2, unit="¥100m")
    d.big_stat("108", "growth in market size over four years", unit_suffix="%",
               source="CIC")
    d.closing(org="Your organisation")
    d.save("deck.pptx")

Slide-creating methods return the slide so you can keep drawing on it.
All geometry is in inches.
"""

from __future__ import annotations

import os
from typing import Sequence

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

from .themes import DEFAULT_THEME, describe, resolve

# ---------------------------------------------------------------------------
# The design system. Change it here; every method reads from these.
# ---------------------------------------------------------------------------

SLIDE_W, SLIDE_H = 13.333, 7.5

MARGIN = 0.75                       # single left/right margin for everything
CONTENT_W = SLIDE_W - 2 * MARGIN    # 11.833
HEAD_RULE_Y = 0.55                  # hairline under the header
BAR_Y = 0.88                        # accent bar
EYEBROW_Y = 1.03                    # small category label
TITLE_Y = 1.32                      # the assertion
BODY_TOP = 2.32                     # first supporting line
FOOT_RULE_Y = 6.72                  # hairline above the footer
SOURCE_Y = 6.82                     # provenance line

# Module-level palette = the default theme, kept so `from consulting_deck import
# COLORS` still resolves. Per-deck colours live on the instance (`self.c`) so two
# decks with different themes can be built in one process.
COLORS, _SWITCHES, _ = resolve(DEFAULT_THEME)

SZ_STAT, SZ_CHAPTER = 190, 132
SZ_TITLE, SZ_LEAD, SZ_BODY, SZ_SMALL = 30, 19, 16, 13
SZ_EYEBROW, SZ_SOURCE = 11, 9.5
# Back-compat names used by existing build scripts.
SZ_THESIS, SZ_SUPPORT, SZ_DENSE = SZ_TITLE, SZ_BODY, SZ_SMALL

FONT_HEAD = ("Arial", "微软雅黑")
FONT_BODY = ("Arial", "黑体")
FONT_NUM = ("Arial", "微软雅黑")

A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

LABELS = {
    "zh": {"source": "数据来源：", "unit": "单位：", "chapter": "第 %s 章"},
    "en": {"source": "Source: ", "unit": "Unit: ", "chapter": "Chapter %s"},
}
SOURCE_PREFIXES = ("数据来源", "资料来源", "实例来源", "图片来源", "Source", "source")


# ---------------------------------------------------------------------------
# Text primitives
# ---------------------------------------------------------------------------

def set_font(run, pair=FONT_BODY, size=None, bold=None, color=None, spacing=None):
    """Set the latin and East Asian typefaces together.

    PowerPoint stores them as separate attributes and python-pptx only exposes
    the latin one, so Chinese text silently falls back to a default face unless
    the East Asian face is written directly. `spacing` is letter-spacing in
    points, used for the small uppercase eyebrow labels."""
    latin, ea = pair
    run.font.name = latin
    rPr = run._r.get_or_add_rPr()
    for tag, face in (("ea", ea), ("cs", latin)):
        el = rPr.find(A_NS + tag)
        if el is None:
            el = rPr.makeelement(A_NS + tag, {})
            rPr.append(el)
        el.set("typeface", face)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color if isinstance(color, RGBColor) else COLORS[color]
    if spacing is not None:
        rPr.set("spc", str(int(spacing * 100)))
    return run


def no_bullet(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    if pPr.find(A_NS + "buNone") is None:
        pPr.append(pPr.makeelement(A_NS + "buNone", {}))
    return paragraph


def _runs_of(block, default_bold=False):
    """A block is a string, a (text, bold) pair, or a list of such pairs for
    mid-sentence emphasis — which is how the operative phrase gets bolded
    without bolding a whole line."""
    if isinstance(block, list):
        return block
    if isinstance(block, tuple):
        return [block]
    return [(block, default_bold)]


class Deck:
    """A deck under construction.

    `lang` sets the provenance labels ("en" or "zh"). Nothing else about the
    system is language-specific."""

    def __init__(self, template: str | None = None, lang: str = "en", theme=None):
        """`theme` is a name from `themes.THEMES`, or a mapping that names a
        `base` and overrides colours or switches — which is how a brand colour
        gets applied without redesigning the system around it."""
        self.prs = Presentation(template) if template else Presentation()
        self.prs.slide_width = Inches(SLIDE_W)
        self.prs.slide_height = Inches(SLIDE_H)
        self.lang = lang if lang in LABELS else "en"
        self.labels = LABELS[self.lang]
        self.c, self.sw, self.theme = resolve(theme)
        self._blank = self._find_blank_layout()
        self.page = 0

    def _rgb(self, color):
        """Colours may be given as a palette name or a literal RGBColor."""
        return color if isinstance(color, RGBColor) else self.c[color]

    @staticmethod
    def _contrast(a, b):
        """WCAG contrast ratio for two RGBColor values."""
        def luminance(color):
            channels = [value / 255 for value in color]
            channels = [value / 12.92 if value <= 0.04045
                        else ((value + 0.055) / 1.055) ** 2.4
                        for value in channels]
            return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

        high, low = sorted((luminance(a), luminance(b)), reverse=True)
        return (high + 0.05) / (low + 0.05)

    def _accent_text(self, dark, large=False):
        """Keep custom accents for text only when they contrast with the field.

        Bars and chart marks always retain the exact brand accent. Text on a dark
        field falls back to the theme's paper colour when the accent would be
        unreadable; large text uses WCAG's lower 3:1 threshold.
        """
        if not dark:
            return self.c["accent"]
        threshold = 3.0 if large else 4.5
        return (self.c["accent"] if self._contrast(self.c["accent"], self.c["ink"])
                >= threshold else self.c["paper"])

    def _find_blank_layout(self):
        """Everything is drawn explicitly, so the only thing wanted from the
        base file is a layout that contributes nothing of its own."""
        for layout in self.prs.slide_layouts:
            if layout.name.strip().lower() == "blank":
                return layout
        return min(self.prs.slide_layouts, key=lambda l: len(l.placeholders))

    # -- canvas ------------------------------------------------------------

    def _new(self, dark=None, numbered=True):
        dark = self.sw.get("dark_content", False) if dark is None else dark
        s = self.prs.slides.add_slide(self._blank)
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)
        fill = s.background.fill
        fill.solid()
        fill.fore_color.rgb = self.c["ink"] if dark else self.c["paper"]
        s._dark = dark
        if numbered:
            self.page += 1
            self._footer(s, dark)
        return s

    def rule(self, slide, x, y, w, thickness=None, color=None, dark=None):
        dark = getattr(slide, "_dark", False) if dark is None else dark
        thickness = self.sw["rule_weight"] if thickness is None else thickness
        if color is None:
            color = "rule_d" if dark else "rule"
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                                     Inches(w), Inches(thickness))
        bar.fill.solid()
        bar.fill.fore_color.rgb = self._rgb(color)
        bar.line.fill.background()
        bar.shadow.inherit = False
        return bar

    def _footer(self, slide, dark):
        self.rule(slide, MARGIN, FOOT_RULE_Y, CONTENT_W, dark=dark)
        self.textbox(slide, f"{self.page:02d}", SLIDE_W - MARGIN - 1.0, SOURCE_Y,
                     1.0, 0.3, size=SZ_SOURCE,
                     color="muted" if not dark else "rule_d",
                     align=PP_ALIGN.RIGHT)

    def _eyebrow(self, text):
        return text.upper() if self.sw["caps_eyebrow"] else text

    def _header(self, slide, eyebrow, title, dark=None, title_color=None,
                title_size=SZ_TITLE, width=None):
        """Accent bar, letterspaced eyebrow, then the assertion at full size.

        The bar is the only fixed ornament in the system; it gives the eye a
        consistent starting point on every slide."""
        width = width or CONTENT_W
        dark = getattr(slide, "_dark", False) if dark is None else dark
        self.rule(slide, MARGIN, HEAD_RULE_Y, CONTENT_W, dark=dark)
        self.rule(slide, MARGIN, BAR_Y, 0.62, thickness=0.045, color="accent")
        if eyebrow:
            self.textbox(slide, self._eyebrow(eyebrow), MARGIN, EYEBROW_Y, width, 0.3,
                         size=SZ_EYEBROW, pair=FONT_HEAD,
                         color="accent", bold=True, spacing=1.4)
        if title:
            self.textbox(slide, title, MARGIN, TITLE_Y, width, 0.95,
                         size=title_size, pair=FONT_HEAD,
                         color=title_color or ("paper" if dark else "ink"),
                         bold=True)
        return slide

    # -- text --------------------------------------------------------------

    def textbox(self, slide, text, left, top, width, height, size=SZ_BODY,
                pair=FONT_BODY, color="ink", bold=False, align=PP_ALIGN.LEFT,
                anchor=MSO_ANCHOR.TOP, spacing=None, line_gap=5):
        box = slide.shapes.add_textbox(Inches(left), Inches(top),
                                       Inches(width), Inches(height))
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = 0
        tf.margin_top = tf.margin_bottom = 0
        blocks = text if isinstance(text, (list, tuple)) and not isinstance(text, str) else [text]
        rgb = self._rgb(color)
        if color == "accent":
            dark = getattr(slide, "_dark", False)
            large = size >= 24 or (bold and size >= 18)
            rgb = self._accent_text(dark, large=large)
        first = True
        for block in blocks:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            no_bullet(p)
            p.alignment = align
            p.space_after = Pt(line_gap)
            for t, b in _runs_of(block, bold):
                set_font(p.add_run(), pair, size, b, rgb, spacing).text = t
        return box

    def bullets(self, slide, items, left=MARGIN, top=BODY_TOP, width=CONTENT_W,
                height=3.9, size=SZ_BODY, marker="—", gap=9):
        """Supporting lines with a hanging accent dash. No bullet glyphs: the
        dash sits in the accent colour and the text hangs off it, which keeps a
        dense list readable without adding furniture."""
        box = slide.shapes.add_textbox(Inches(left), Inches(top),
                                       Inches(width), Inches(height))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = 0
        tf.margin_top = tf.margin_bottom = 0
        first = True
        for item in items:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            no_bullet(p)
            p.space_after = Pt(gap)
            pPr = p._p.get_or_add_pPr()
            pPr.set("indent", str(-int(0.26 * 914400)))
            pPr.set("marL", str(int(0.26 * 914400)))
            if marker:
                set_font(p.add_run(), FONT_BODY, size, False, self.c["accent"]).text = marker + " "
            dark = getattr(slide, "_dark", False)
            strong = self.c["paper"] if dark else self.c["ink"]
            plain = self.c["muted"] if dark else self.c["slate"]
            for t, b in _runs_of(item):
                set_font(p.add_run(), FONT_BODY, size, b,
                         strong if b else plain).text = t
        return box

    def source(self, slide, text, left=MARGIN, top=SOURCE_Y, width=9.5, prefix=None):
        """The provenance line. Put one on every slide carrying a figure — it
        is the difference between analysis and assertion."""
        prefix = self.labels["source"] if prefix is None else prefix
        already = any(text.strip().startswith(p) for p in SOURCE_PREFIXES)
        color = "muted" if getattr(slide, "_dark", False) else "slate"
        return self.textbox(slide, text if already else prefix + text, left, top,
                            width, 0.3, size=SZ_SOURCE, color=color)

    def unit(self, slide, text, right_edge, top, prefix=None, width=3.0):
        """Sits at the top-right of the chart it belongs to. Right-aligned so it
        never wanders into body text occupying the other half of the slide."""
        prefix = self.labels["unit"] if prefix is None else prefix
        already = text.startswith("单位") or text.lower().startswith("unit")
        color = "muted" if getattr(slide, "_dark", False) else "slate"
        return self.textbox(slide, text if already else prefix + text,
                            right_edge - width, top, width, 0.28,
                            size=SZ_SOURCE, color=color, align=PP_ALIGN.RIGHT)

    # -- slide types -------------------------------------------------------

    def title_slide(self, title, subtitle=None, kicker=None):
        dark = self.sw["dark_dividers"]
        s = self._new(dark=dark, numbered=False)
        self.rule(s, MARGIN, 2.55, 1.5, thickness=0.06, color="accent")
        if kicker:
            self.textbox(s, self._eyebrow(kicker), MARGIN, 2.05, CONTENT_W, 0.3,
                         size=SZ_EYEBROW, pair=FONT_HEAD, color="accent",
                         bold=True, spacing=1.6)
        self.textbox(s, title, MARGIN, 2.95, 10.2, 1.9, size=46,
                     pair=FONT_HEAD, color="paper" if dark else "ink", bold=True)
        if subtitle:
            self.textbox(s, subtitle, MARGIN, 5.05, 9.4, 0.7,
                         size=SZ_LEAD, color="muted")
        return s

    def section(self, number, title, scope=None):
        """Chapter divider: an oversized numeral at the margin, the title
        beneath it, and the scope of the chapter in one line.

        Numbering and scope both exist so a reader always knows where they are
        and what this chapter is about to cover."""
        dark = self.sw["dark_dividers"]
        s = self._new(dark=dark, numbered=False)
        self.textbox(s, str(number), MARGIN, 1.55, 4.0, 2.4, size=SZ_CHAPTER,
                     pair=FONT_NUM, color="accent", bold=True)
        self.rule(s, MARGIN, 4.30, 1.5, thickness=0.05, color="accent")
        self.textbox(s, title, MARGIN, 4.62, 8.6, 0.9, size=34,
                     pair=FONT_HEAD, color="paper" if dark else "ink", bold=True)
        if scope:
            self.textbox(s, scope, MARGIN, 5.62, 8.2, 0.8, size=SZ_BODY,
                         color="muted")
        return s

    # Kept so existing build scripts keep working; the scope line is the point.
    def section_wide(self, title, scope, subtitle=None, image=None):
        return self.section(subtitle or "", title, scope)

    def content(self, category, message, body=(), source=None, thesis_size=None,
                body_width=None):
        """The workhorse: eyebrow category, assertion, supporting lines.

        Keeping the category small and the assertion large is what makes a
        run of slides readable as one argument — the reader sees findings, not
        a repeated topic heading."""
        s = self._new()
        self._header(s, category, message, title_size=thesis_size or SZ_TITLE)
        if body:
            self.bullets(s, list(body), width=body_width or CONTENT_W)
        if source:
            self.source(s, source)
        return s

    def canvas(self, category, message=None, source=None):
        """Header only. The base for diagrams, matrices, and tables."""
        s = self._new()
        self._header(s, category, message)
        if source:
            self.source(s, source)
        return s

    def big_stat(self, number, caption, unit_suffix="", variant=None, source=None,
                 eyebrow=None):
        """One figure, left-aligned at 190pt, with the caption directly beneath.

        Left alignment is deliberate: it keeps the statement slide part of the
        document rather than a poster interrupting it. `variant` picks an ink
        field ('ink') or a paper field with the numeral in accent ('paper')."""
        variant = self.sw["stat_default"] if variant is None else variant
        dark = variant != "paper"
        s = self._new(dark=dark)
        self.rule(s, MARGIN, HEAD_RULE_Y, CONTENT_W, dark=dark)
        self.rule(s, MARGIN, BAR_Y, 0.62, thickness=0.045, color="accent")
        if eyebrow:
            self.textbox(s, self._eyebrow(eyebrow), MARGIN, EYEBROW_Y, CONTENT_W, 0.3,
                         size=SZ_EYEBROW, pair=FONT_HEAD, color="accent",
                         bold=True, spacing=1.4)
        box = self.textbox(s, "", MARGIN, 1.95, CONTENT_W, 2.6,
                           anchor=MSO_ANCHOR.MIDDLE)
        p = box.text_frame.paragraphs[0]
        set_font(p.add_run(), FONT_NUM, SZ_STAT, True,
                 self.c["paper"] if dark else self.c["ink"]).text = str(number)
        if unit_suffix:
            set_font(p.add_run(), FONT_NUM, 34, True,
                     self._accent_text(dark, large=True)).text = " " + unit_suffix
        self.rule(s, MARGIN, 4.75, 2.4, thickness=0.05, color="accent")
        self.textbox(s, caption, MARGIN, 5.05, 9.8, 1.2, size=SZ_LEAD,
                     color="paper" if dark else "ink")
        if source:
            self.source(s, source)
        return s

    def quote_slide(self, label, quote, note=None):
        """A verbatim finding given the whole page."""
        dark = self.sw["dark_dividers"]
        s = self._new(dark=dark)
        self.rule(s, MARGIN, HEAD_RULE_Y, CONTENT_W, dark=dark)
        self.rule(s, MARGIN, BAR_Y, 0.62, thickness=0.045, color="accent")
        if label:
            self.textbox(s, self._eyebrow(label), MARGIN, EYEBROW_Y, CONTENT_W, 0.3,
                         size=SZ_EYEBROW, pair=FONT_HEAD, color="accent",
                         bold=True, spacing=1.4)
        self.textbox(s, "“", MARGIN, 1.75, 1.6, 1.6, size=120,
                     pair=FONT_NUM, color="accent", bold=True)
        self.textbox(s, quote, MARGIN + 0.95, 2.35, 10.3, 2.6, size=32,
                     pair=FONT_HEAD, color="paper" if dark else "ink", bold=True)
        if note:
            self.textbox(s, note, MARGIN + 0.95, 5.35, 9.0, 0.6,
                         size=SZ_BODY, color="muted")
        return s

    def rh_image(self, title, body, image=None, source=None, category=None):
        """Statement on the left, full-height image on the right."""
        s = self._new()
        self._header(s, category or "", title, width=7.2)
        lines = [body] if isinstance(body, str) else list(body)
        self.bullets(s, lines, width=7.2)
        if image:
            s.shapes.add_picture(image, Inches(8.35), Inches(0), height=Inches(SLIDE_H))
        if source:
            self.source(s, source)
        return s

    def _column_track(self, slide, columns, top=2.45, height=3.9):
        n = len(columns)
        gutter = 0.55
        w = (CONTENT_W - gutter * (n - 1)) / n
        for i, (head, items) in enumerate(columns):
            x = MARGIN + i * (w + gutter)
            self.rule(slide, x, top, 0.42, thickness=0.045, color="accent")
            on_dark = getattr(slide, "_dark", False)
            self.textbox(slide, head, x, top + 0.22, w, 0.45, size=SZ_LEAD,
                         pair=FONT_HEAD, color="paper" if on_dark else "ink",
                         bold=True)
            self.bullets(slide, list(items), left=x, top=top + 0.95, width=w,
                         height=height - 0.95, size=SZ_SMALL, gap=7)
        return slide

    def two_columns(self, title, left_head, left_items, right_head, right_items,
                    source=None, category=None):
        """For a genuine opposition — opportunities against threats, current
        against target. Two unrelated lists want two slides instead."""
        s = self._new()
        self._header(s, category or "", title)
        self._column_track(s, [(left_head, left_items), (right_head, right_items)])
        if source:
            self.source(s, source)
        return s

    def three_columns(self, title, columns, source=None, category=None):
        s = self._new()
        self._header(s, category or "", title)
        self._column_track(s, list(columns))
        if source:
            self.source(s, source)
        return s

    def closing(self, org=None, contact=None, note=None):
        dark = self.sw["dark_dividers"]
        s = self._new(dark=dark, numbered=False)
        self.rule(s, MARGIN, 4.25, 1.5, thickness=0.06, color="accent")
        if org:
            self.textbox(s, org, MARGIN, 4.62, 9.5, 0.9, size=30,
                         pair=FONT_HEAD, color="paper" if dark else "ink", bold=True)
        if contact:
            self.textbox(s, contact, MARGIN, 5.55, 9.5, 0.5, size=SZ_BODY,
                         color="accent")
        if note:
            self.textbox(s, note, MARGIN, 6.65, 10.5, 0.6, size=SZ_SOURCE,
                         color="muted")
        return s

    def blank(self):
        return self._new()

    # -- composed elements -------------------------------------------------

    def evidence_band(self, slide, top=2.55, height=3.9):
        """The tinted band that holds compressed evidence — one artifact, one
        chart, two or three attributed quotes. The antidote to a page of
        unreadable screenshots."""
        band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(MARGIN),
                                      Inches(top), Inches(CONTENT_W), Inches(height))
        band.fill.solid()
        band.fill.fore_color.rgb = self.c["band"]
        band.line.fill.background()
        band.shadow.inherit = False
        band.text_frame.text = ""
        self.rule(slide, MARGIN, top, CONTENT_W, thickness=0.03, color="accent")
        return band

    def pull_quote(self, slide, text, attribution, left, top, width, height=1.2):
        box = slide.shapes.add_textbox(Inches(left), Inches(top),
                                       Inches(width), Inches(height))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        no_bullet(p)
        set_font(p.add_run(), FONT_BODY, SZ_SMALL, False, self.c["ink"]).text = f"“{text}”"
        q = tf.add_paragraph()
        no_bullet(q)
        q.space_before = Pt(3)
        set_font(q.add_run(), FONT_BODY, SZ_SOURCE, False, self.c["accent"]).text = f"— {attribution}"
        return box

    def table(self, slide, rows, left=MARGIN, top=2.45, width=CONTENT_W, height=3.4,
              col_widths=None, highlight_rows=(), size=10.5):
        """Ink header, hairline zebra, accent-tinted highlight rows. Reserve the
        last column for what the row means — the others are transcription."""
        shp = slide.shapes.add_table(len(rows), len(rows[0]), Inches(left),
                                     Inches(top), Inches(width), Inches(height))
        tbl = shp.table
        tbl.first_row = True
        if col_widths:
            for i, w in enumerate(col_widths):
                tbl.columns[i].width = Inches(w)
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                cell = tbl.cell(r, c)
                cell.text = ""
                p = cell.text_frame.paragraphs[0]
                no_bullet(p)
                hit = r in highlight_rows
                set_font(p.add_run(), FONT_HEAD if r == 0 or hit else FONT_BODY,
                         size, r == 0 or hit,
                         self.c["paper"] if r == 0 else self.c["ink"]).text = val
                cell.margin_left = cell.margin_right = Inches(0.1)
                cell.margin_top = cell.margin_bottom = Inches(0.05)
                cell.fill.solid()
                cell.fill.fore_color.rgb = (
                    self.c["ink"] if r == 0
                    else RGBColor(0xF2, 0xE3, 0xDE) if hit
                    else self.c["paper"] if r % 2 else self.c["band"])
        return tbl

    def callout(self, slide, text, left, top, width=1.8):
        """The tag that says what a chart means. A chart states a fact; the
        callout states the point of it."""
        return self.textbox(slide, text, left, top, width, 0.36,
                            size=SZ_LEAD, pair=FONT_NUM, color="accent", bold=True)

    # -- charts ------------------------------------------------------------

    def _strip_chart_chrome(self, chart):
        """Charts sit directly on the page — no plot border, no white box
        interrupting the paper field."""
        cs = chart._chartSpace
        for tag in ("c:spPr", "c:roundedCorners"):
            el = cs.find(qn(tag))
            if el is not None:
                cs.remove(el)
        spPr = cs.makeelement(qn("c:spPr"), {})
        spPr.append(spPr.makeelement(qn("a:noFill"), {}))
        ln = spPr.makeelement(qn("a:ln"), {})
        ln.append(ln.makeelement(qn("a:noFill"), {}))
        spPr.append(ln)
        cs.insert(len(cs), spPr)
        return chart

    def _style_chart(self, chart, labels=True, legend=False, number_format="0",
                     dark=False):
        chart.font.size = Pt(10)
        chart.font.color.rgb = self.c["muted"]
        chart.has_title = False
        chart.has_legend = legend
        if legend:
            chart.legend.position = XL_LEGEND_POSITION.BOTTOM
            chart.legend.include_in_layout = False
        plot = chart.plots[0]
        plot.has_data_labels = labels
        if labels:
            plot.data_labels.number_format = number_format
            plot.data_labels.number_format_is_linked = False
            plot.data_labels.font.size = Pt(11)
            plot.data_labels.font.bold = True
            plot.data_labels.font.color.rgb = (self.c["paper"] if dark
                                               else self.c["ink"])
        self._strip_chart_chrome(chart)
        return chart

    def _axes(self, chart, hide_value_axis=True):
        chart.value_axis.has_major_gridlines = False
        chart.value_axis.visible = not hide_value_axis
        try:
            chart.category_axis.format.line.color.rgb = self.c["rule"]
        except Exception:
            pass
        return chart

    def column_chart(self, slide, categories, values, left, top, width, height,
                     unit=None, source=None, color="accent", series_name="value",
                     number_format="0"):
        """Single-series columns — the default for anything over time or across
        a handful of categories. Labels on, axis off, one colour."""
        data = CategoryChartData()
        data.categories = list(categories)
        data.add_series(series_name, tuple(values))
        gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(left),
                                    Inches(top), Inches(width), Inches(height), data)
        chart = gf.chart
        self._style_chart(chart, number_format=number_format, dark=getattr(slide, '_dark', False))
        ser = chart.plots[0].series[0]
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = self.c[color] if isinstance(color, str) else color
        self._axes(chart)
        if unit:
            self.unit(slide, unit, left + width, top - 0.3)
        if source:
            self.source(slide, source)
        return chart

    def grouped_column_chart(self, slide, categories, series, left, top, width,
                             height, unit=None, source=None, number_format="0"):
        """`series` is a sequence of (name, values). Two or three at most —
        beyond that a column chart stops being readable and wants a table."""
        data = CategoryChartData()
        data.categories = list(categories)
        for name, values in series:
            data.add_series(name, tuple(values))
        gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(left),
                                    Inches(top), Inches(width), Inches(height), data)
        chart = gf.chart
        self._style_chart(chart, legend=len(series) > 1, number_format=number_format, dark=getattr(slide, '_dark', False))
        palette = [self.c["accent"], self.c["teal"], self.c["ochre"]]
        for i, ser in enumerate(chart.plots[0].series):
            ser.format.fill.solid()
            ser.format.fill.fore_color.rgb = palette[i % 3]
        self._axes(chart)
        if unit:
            self.unit(slide, unit, left + width, top - 0.3)
        if source:
            self.source(slide, source)
        return chart

    def bar_chart(self, slide, categories, values, left, top, width, height,
                  unit=None, source=None, color="accent", number_format="0"):
        """Horizontal bars — better than columns when the category labels are
        words rather than years."""
        data = CategoryChartData()
        data.categories = list(categories)
        data.add_series("value", tuple(values))
        gf = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(left),
                                    Inches(top), Inches(width), Inches(height), data)
        chart = gf.chart
        self._style_chart(chart, number_format=number_format, dark=getattr(slide, '_dark', False))
        ser = chart.plots[0].series[0]
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = self.c[color] if isinstance(color, str) else color
        self._axes(chart)
        if unit:
            self.unit(slide, unit, left + width, top - 0.3)
        if source:
            self.source(slide, source)
        return chart

    def pie_chart(self, slide, categories, values, left, top, width, height,
                  source=None, doughnut=True):
        """Composition only, and only when the parts sum to a whole."""
        data = CategoryChartData()
        data.categories = list(categories)
        data.add_series("share", tuple(values))
        kind = XL_CHART_TYPE.DOUGHNUT if doughnut else XL_CHART_TYPE.PIE
        gf = slide.shapes.add_chart(kind, Inches(left), Inches(top),
                                    Inches(width), Inches(height), data)
        chart = gf.chart
        self._style_chart(chart, legend=True, number_format="0.0%", dark=getattr(slide, '_dark', False))
        if not doughnut:
            chart.plots[0].data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
        palette = [self.c["accent"], self.c["teal"], self.c["ochre"],
                   self.c["slate"], self.c["muted"], self.c["rule"]]
        for i, pt in enumerate(chart.plots[0].series[0].points):
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = palette[i % len(palette)]
        if source:
            self.source(slide, source)
        return chart

    # -- output ------------------------------------------------------------

    def save(self, path):
        self.prs.save(path)
        return path
