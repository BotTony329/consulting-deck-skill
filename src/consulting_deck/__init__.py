"""consulting-deck — build consulting slide decks that argue instead of describe.

Two things ship here: a *method* (framework-driven narrative, message-first
titles, sourced numbers, statement slides) documented in skill/, and an
*engine* (this package) that renders it as .pptx.

    from consulting_deck import Deck

    d = Deck(lang="en")
    d.title_slide("Market entry study", "Ready-to-drink tea · China")
    d.big_stat("108", "growth over four years", unit_suffix="%", source="CIC")
    d.save("deck.pptx")

Or from a spec file, for agents that would rather not write Python:

    consulting-deck build spec.yaml -o deck.pptx
    consulting-deck check deck.pptx
"""

from .deck import COLORS, Deck, set_font
from .check import check, storyline
from .spec import SpecError, build, load

__version__ = "0.1.0"
__all__ = ["Deck", "COLORS", "set_font", "check", "storyline",
           "build", "load", "SpecError", "__version__"]
