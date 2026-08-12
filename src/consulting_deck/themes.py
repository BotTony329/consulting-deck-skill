"""Themes — the visual identities the deck can be rendered in.

A theme is not just a palette swap. Each one also decides whether dividers and
statement slides sit on a dark or light field, whether the eyebrow is set in
caps, and how heavy the rules are — which is what stops the six of them from
looking like one design in six colours.

Pick one deliberately. The theme is part of the argument: a bid deck for a bank
and a research report for a school do not want the same voice, and defaulting
everything to one look is how decks start feeling generic.

    Deck(theme="slate")                          # a shipped theme
    Deck(theme={"base": "mono", "accent": "#0B5FFF"})   # a theme, re-accented
    Deck(theme={"accent": "#7A1FA2", "ink": "#1A1024"}) # your brand, on the default base

Adding one: copy an entry, change the values, and keep `accent` scarce — the
system's coherence depends on it marking one thing per slide.
"""

from __future__ import annotations

from pptx.dml.color import RGBColor

# Keys every theme must define. `switches` are the non-colour decisions.
COLOR_KEYS = ("ink", "paper", "accent", "second", "third",
              "slate", "rule", "rule_d", "muted", "band")


def hex_to_rgb(value) -> RGBColor:
    if isinstance(value, RGBColor):
        return value
    v = str(value).lstrip("#")
    if len(v) != 6:
        raise ValueError(f"colour {value!r} must be a 6-digit hex like '#C8442A'")
    return RGBColor(int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))


THEMES: dict[str, dict] = {

    # Warm paper, near-black ink, terracotta. Reads like a printed report.
    # Good default for research and market studies.
    "editorial": {
        "label": "Editorial — warm paper, terracotta accent, print-report feel",
        "colors": {
            "ink": "#16181D", "paper": "#F7F6F3", "accent": "#C8442A",
            "second": "#2E6F6B", "third": "#C08A2E", "slate": "#5A6472",
            "rule": "#D8D4CC", "rule_d": "#3A3E47", "muted": "#8A8F98",
            "band": "#EEEBE5",
        },
        "switches": {"dark_dividers": True, "stat_default": "ink",
                     "caps_eyebrow": True, "rule_weight": 0.012},
    },

    # Cool white and deep navy with a saturated blue. The most conventionally
    # "consulting" of the set — safe for banks, insurers, and boards.
    "slate": {
        "label": "Slate — cool white, deep navy, corporate blue",
        "colors": {
            "ink": "#0F1E2E", "paper": "#FFFFFF", "accent": "#0B5FFF",
            "second": "#0F8B8D", "third": "#E4A11B", "slate": "#4A5A6A",
            "rule": "#DCE3EA", "rule_d": "#25384B", "muted": "#8593A3",
            "band": "#EFF3F7",
        },
        "switches": {"dark_dividers": True, "stat_default": "ink",
                     "caps_eyebrow": True, "rule_weight": 0.012},
    },

    # Black on white with one restrained green. Swiss, quiet, high contrast.
    # Light-field statement slides keep it from ever feeling heavy.
    "mono": {
        "label": "Mono — black on white, one restrained accent, Swiss and quiet",
        "colors": {
            "ink": "#111111", "paper": "#FFFFFF", "accent": "#1F6F4A",
            "second": "#444444", "third": "#8A8A8A", "slate": "#4D4D4D",
            "rule": "#DDDDDD", "rule_d": "#333333", "muted": "#909090",
            "band": "#F4F4F4",
        },
        "switches": {"dark_dividers": False, "stat_default": "paper",
                     "caps_eyebrow": True, "rule_weight": 0.010},
    },

    # Dark-first: charcoal fields throughout, amber accent. Product and
    # engineering audiences; reads well on a screen, badly on cheap printers.
    "midnight": {
        "label": "Midnight — dark fields throughout, amber accent, screen-first",
        "colors": {
            "ink": "#12141A", "paper": "#E8E9EC", "accent": "#F0A030",
            "second": "#3FA9A5", "third": "#B58AE0", "slate": "#9AA1AC",
            "rule": "#C9CCD2", "rule_d": "#2A2E38", "muted": "#7A818D",
            "band": "#D8DAE0",
        },
        "switches": {"dark_dividers": True, "stat_default": "ink",
                     "caps_eyebrow": True, "rule_weight": 0.014,
                     "dark_content": True},
    },

    # Cream and dark brown with deep teal. Softer and less corporate — suits
    # education, health, culture, and non-profit work.
    "sand": {
        "label": "Sand — cream and brown with deep teal, softer register",
        "colors": {
            "ink": "#2B2118", "paper": "#FBF7EF", "accent": "#1F6F6B",
            "second": "#A8622C", "third": "#7C8B3A", "slate": "#5E5445",
            "rule": "#E2D9C8", "rule_d": "#463A2C", "muted": "#928878",
            "band": "#F2EADB",
        },
        "switches": {"dark_dividers": True, "stat_default": "paper",
                     "caps_eyebrow": False, "rule_weight": 0.012},
    },

    # Almost no colour and heavier rules. For decks that will be printed in
    # black and white, or read as a document rather than presented.
    "press": {
        "label": "Press — near-monochrome, heavier rules, built to photocopy",
        "colors": {
            "ink": "#1A1A1A", "paper": "#FAFAF8", "accent": "#8C1D18",
            "second": "#3F3F3F", "third": "#707070", "slate": "#3F3F3F",
            "rule": "#B8B8B4", "rule_d": "#3A3A3A", "muted": "#7A7A7A",
            "band": "#EDEDE9",
        },
        "switches": {"dark_dividers": False, "stat_default": "paper",
                     "caps_eyebrow": True, "rule_weight": 0.018},
    },
}

DEFAULT_THEME = "editorial"

DEFAULT_SWITCHES = {"dark_dividers": True, "stat_default": "ink",
                    "caps_eyebrow": True, "rule_weight": 0.012,
                    "dark_content": False}


def resolve(theme) -> tuple[dict, dict, str]:
    """Return (colors, switches, name) for a theme name, mapping, or None.

    A mapping may name a `base` to start from and override any colour or
    switch, which is how a brand colour gets applied without redesigning
    everything around it."""
    if theme is None:
        theme = DEFAULT_THEME
    if isinstance(theme, str):
        if theme not in THEMES:
            raise ValueError(f"unknown theme {theme!r}; available: "
                             f"{', '.join(sorted(THEMES))}")
        spec, name, overrides = THEMES[theme], theme, {}
    elif isinstance(theme, dict):
        name = theme.get("base", DEFAULT_THEME)
        if name not in THEMES:
            raise ValueError(f"unknown base theme {name!r}; available: "
                             f"{', '.join(sorted(THEMES))}")
        spec = THEMES[name]
        overrides = {k: v for k, v in theme.items() if k != "base"}
    else:
        raise TypeError("theme must be a name, a mapping, or None")

    colors = {k: hex_to_rgb(v) for k, v in spec["colors"].items()}
    switches = dict(DEFAULT_SWITCHES)
    switches.update(spec.get("switches", {}))

    for key, value in overrides.items():
        if key in COLOR_KEYS:
            colors[key] = hex_to_rgb(value)
        elif key in DEFAULT_SWITCHES:
            switches[key] = value
        else:
            raise ValueError(
                f"theme override {key!r} is not a colour or a switch. "
                f"Colours: {', '.join(COLOR_KEYS)}. "
                f"Switches: {', '.join(DEFAULT_SWITCHES)}")

    # Aliases kept so older call sites and hand-written build scripts that
    # reach for a colour by its old name keep working.
    colors.update({
        "white": RGBColor(0xFF, 0xFF, 0xFF),
        "text": colors["ink"], "blue": colors["accent"], "cyan": colors["accent"],
        "navy": colors["ink"], "purple": colors["ink"], "magenta": colors["accent"],
        "green": colors["second"], "teal": colors["second"],
        "amber": colors["third"], "ochre": colors["third"],
    })
    return colors, switches, name


def describe() -> str:
    """One line per theme, for `consulting-deck themes` and for asking a user."""
    width = max(len(n) for n in THEMES)
    return "\n".join(f"  {n:<{width}}  {THEMES[n]['label']}" for n in THEMES)
