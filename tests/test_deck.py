"""Tests aimed at the things that actually break: every slide type renders,
every theme resolves, the checker catches real faults, and the spec route
produces the same deck as the Python route."""

from __future__ import annotations

import json
from importlib.metadata import metadata
import pathlib

import pytest
from pptx import Presentation

from consulting_deck import Deck, build, check, load
from consulting_deck.spec import SpecError
from consulting_deck.themes import THEMES, resolve


def test_distribution_metadata_uses_public_identity():
    package = metadata("consulting-deck")
    assert package["Name"] == "consulting-deck"
    assert package["Version"] == "0.1.1"
    assert package["Author"] == "BotTony329"


# --- themes ---------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(THEMES))
def test_every_theme_resolves_and_builds(name, tmp_path):
    d = Deck(theme=name)
    d.title_slide("T", "S", kicker="K")
    d.section(1, "Chapter", "Scope line")
    s = d.content("Cat", "An assertion.", ["a line"], source="X", body_width=5.4)
    d.column_chart(s, ["a", "b"], [1, 2], 6.6, 2.75, 5.2, 3.0, unit="u")
    d.big_stat("42", "caption", unit_suffix="%", source="X")
    d.two_columns("T", "L", ["x"], "R", ["y"], source="X")
    d.closing(org="Org")
    out = tmp_path / f"{name}.pptx"
    d.save(str(out))
    assert Presentation(str(out)).slides


def test_theme_override_applies_brand_colour():
    d = Deck(theme={"base": "mono", "accent": "#0B5FFF"})
    assert str(d.c["accent"]) == "0B5FFF"
    assert d.theme == "mono"


def test_unknown_theme_names_the_alternatives():
    with pytest.raises(ValueError, match="editorial"):
        resolve("nonexistent")


def test_unknown_override_key_is_rejected():
    with pytest.raises(ValueError, match="not a colour or a switch"):
        resolve({"base": "slate", "accnt": "#000000"})


def test_two_decks_can_hold_different_themes():
    """Regression: the palette used to be a module global, so the second deck
    silently repainted the first."""
    a, b = Deck(theme="slate"), Deck(theme="sand")
    assert a.c["accent"] != b.c["accent"]


def test_theme_state_is_per_deck_and_custom_accent_survives():
    light = Deck(theme={"base": "slate", "accent": "#7A1FA2"})
    dark = Deck(theme="midnight")
    assert str(light.c["accent"]) == "7A1FA2"
    assert str(dark.c["accent"]) == "F0A030"
    assert light.sw["dark_content"] is False
    assert dark.sw["dark_content"] is True


def test_custom_accent_text_remains_readable_on_dark_fields():
    deck = Deck(theme={"base": "slate", "accent": "#7A1FA2"})
    divider = deck.section(1, "Readable divider")
    statement = deck.big_stat("42", "Readable statement", unit_suffix="%", source="Test")

    assert str(deck.c["accent"]) == "7A1FA2"
    divider_number = next(shape for shape in divider.shapes
                          if getattr(shape, "has_text_frame", False)
                          and shape.text.strip() == "1")
    number_color = divider_number.text_frame.paragraphs[0].runs[0].font.color.rgb
    assert deck._contrast(number_color, deck.c["ink"]) >= 3.0

    statement_run = next(run for shape in statement.shapes
                         if getattr(shape, "has_text_frame", False)
                         for paragraph in shape.text_frame.paragraphs
                         for run in paragraph.runs if run.text.strip() == "%")
    assert deck._contrast(statement_run.font.color.rgb, deck.c["ink"]) >= 3.0


def test_theme_foreground_contrast_for_key_slide_text():
    """Titles and column heads must remain readable on their actual fields."""
    def luminance(rgb):
        channels = [value / 255 for value in rgb]
        channels = [value / 12.92 if value <= 0.04045
                    else ((value + 0.055) / 1.055) ** 2.4
                    for value in channels]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    def contrast(a, b):
        high, low = sorted((luminance(a), luminance(b)), reverse=True)
        return (high + 0.05) / (low + 0.05)

    for name in THEMES:
        deck = Deck(theme=name)
        content_dark = deck.sw["dark_content"]
        content_foreground = deck.c["paper"] if content_dark else deck.c["ink"]
        content_background = deck.c["ink"] if content_dark else deck.c["paper"]
        assert contrast(content_foreground, content_background) >= 4.5
        if content_dark:
            assert contrast(deck.c["muted"], content_background) >= 4.5
        else:
            assert contrast(deck.c["slate"], content_background) >= 4.5

        divider_dark = deck.sw["dark_dividers"]
        divider_foreground = deck.c["paper"] if divider_dark else deck.c["ink"]
        divider_background = deck.c["ink"] if divider_dark else deck.c["paper"]
        assert contrast(divider_foreground, divider_background) >= 4.5
        if divider_dark:
            assert contrast(deck.c["muted"], divider_background) >= 4.5


# --- slide types ----------------------------------------------------------

def test_all_slide_types_render(tmp_path):
    d = Deck()
    d.title_slide("T")
    d.section(1, "C", "scope")
    d.canvas("Cat", "Message", source="S")
    d.quote_slide("Label", "A verbatim finding.", "Source: X")
    d.three_columns("T", [("A", ["1"]), ("B", ["2"]), ("C", ["3"])])
    s = d.canvas("Table", "A message.", source="S")
    d.table(s, [["h1", "h2"], ["a", "b"]], highlight_rows=(1,))
    q = d.canvas("Band", "A message.")
    d.evidence_band(q)
    d.pull_quote(q, "quoted", "someone", 8.6, 3.1, 3.5)
    out = tmp_path / "all.pptx"
    d.save(str(out))
    assert len(Presentation(str(out)).slides) == 7


def test_page_numbers_skip_covers_and_dividers(tmp_path):
    d = Deck()
    d.title_slide("T")
    d.section(1, "C")
    d.content("Cat", "Assertion.")
    assert d.page == 1


# --- checker --------------------------------------------------------------

def test_checker_flags_a_figure_with_no_source(tmp_path, capsys):
    d = Deck()
    d.content("Cat", "Revenue grew 108% to 1810 units.")
    out = tmp_path / "nosource.pptx"
    d.save(str(out))
    assert check(str(out)) == 1
    assert "no source line" in capsys.readouterr().out


def test_checker_passes_a_sourced_figure(tmp_path):
    d = Deck()
    d.content("Cat", "Revenue grew 108%.", source="CIC")
    out = tmp_path / "sourced.pptx"
    d.save(str(out))
    assert check(str(out)) == 0


def test_checker_flags_text_off_the_canvas(tmp_path, capsys):
    d = Deck()
    s = d.content("Cat", "Fine.")
    d.textbox(s, "runaway", 12.9, 3.0, 4.0, 0.4)
    out = tmp_path / "offcanvas.pptx"
    d.save(str(out))
    assert check(str(out)) == 1
    assert "off the canvas" in capsys.readouterr().out


def test_chapter_numerals_are_not_counted_as_statement_slides(tmp_path, capsys):
    """Regression: dividers use a 132pt numeral and were inflating the count,
    making well-structured decks look over-punctuated."""
    d = Deck()
    for i in range(1, 7):
        d.section(i, f"Chapter {i}")
        d.content("Cat", "An assertion with no figures in it.")
    out = tmp_path / "chapters.pptx"
    d.save(str(out))
    check(str(out))
    printed = capsys.readouterr().out
    # The over-punctuation warning must not fire...
    assert "they stop landing" not in printed
    # ...and the deck genuinely has no statement slides, so the opposite
    # warning should, which proves the counter is looking at the right thing.
    assert "no big-statement slides" in printed


# --- spec route -----------------------------------------------------------

SPEC = {
    "lang": "en",
    "theme": "slate",
    "slides": [
        {"type": "title", "title": "T", "subtitle": "S"},
        {"type": "section", "number": 1, "title": "C", "scope": "scope"},
        {"type": "content", "category": "Cat", "message": "An assertion.",
         "body": ["plain", ["bold bit", True]], "source": "X", "body_width": 5.4,
         "chart": {"kind": "column", "categories": ["a", "b"], "values": [1, 2],
                   "at": [6.6, 2.75, 5.2, 3.0], "unit": "u",
                   "callout": {"text": "+2x", "at": [7.5, 3.1]}}},
        {"type": "stat", "number": "42", "unit": "%", "caption": "c", "source": "X"},
        {"type": "columns", "title": "T",
         "columns": [{"head": "A", "items": ["1"]}, {"head": "B", "items": ["2"]}]},
        {"type": "closing", "org": "Org"},
    ],
}


def test_spec_builds_and_passes_the_checker(tmp_path):
    out = build(SPEC, str(tmp_path / "spec.pptx"))
    assert check(out) == 0
    assert len(Presentation(out).slides) == 6


def test_cli_theme_overrides_the_spec(tmp_path):
    out = build(SPEC, str(tmp_path / "themed.pptx"), theme="sand")
    assert Presentation(out).slides


def test_spec_errors_name_the_problem(tmp_path):
    with pytest.raises(SpecError, match="no 'type'"):
        build({"slides": [{"title": "x"}]}, str(tmp_path / "x.pptx"))
    with pytest.raises(SpecError, match="unknown slide type"):
        build({"slides": [{"type": "banana"}]}, str(tmp_path / "x.pptx"))
    with pytest.raises(SpecError, match="Available themes"):
        build({"theme": "chartreuse", "slides": []}, str(tmp_path / "x.pptx"))


def test_json_spec_loads(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps(SPEC), encoding="utf-8")
    assert load(str(p))["theme"] == "slate"


def test_bundled_example_spec_is_valid(tmp_path):
    example = pathlib.Path(__file__).parent.parent / "examples" / "market_entry.json"
    out = build(load(str(example)), str(tmp_path / "example.pptx"))
    assert check(out) == 0
