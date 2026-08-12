"""The same deck as market_entry.json, written against the Python API.

Use this route when you need control the spec doesn't expose — custom diagrams,
hand-placed shapes, charts with unusual formatting.

    python examples/market_entry.py && consulting-deck check deck.pptx
"""

from consulting_deck import Deck

d = Deck(lang="en", theme="editorial")

d.title_slide("Market entry study", "Ready-to-drink tea · China",
              kicker="External research")

d.section(1, "Market size and demand",
          "What the category looks like today, and who is buying")

s = d.content(
    "Industry status",
    "The category is large, growing fast, and priced down.",
    ["Revenue reached ¥181bn in 2022, up 108% since 2018",
     [("Mid-tier brands hold 70% of outlets", True), (" — the most crowded tier", False)],
     "Average price fell 19% between 2021 and 2023"],
    source="CIC, Xinhua",
    body_width=5.4)                      # leave the right half for the chart
d.column_chart(s, ["2018", "2019", "2020", "2021", "2022"],
               [870, 1060, 1140, 1450, 1810],
               6.6, 2.75, 5.2, 3.1, unit="¥100m")
d.callout(s, "+108%", 8.4, 3.15)         # say what the chart means

d.big_stat("108", "growth in market size over four years — and the reason margin "
                  "is compressing", unit_suffix="%", source="CIC")

d.content("Implication",
          "Category growth alone is not a reason to enter.",
          ["Growth on this scale attracts entrants and compresses margin",
           [("Position and differentiation decide whether entry pays", True)]],
          source="Analysis")

d.two_columns(
    "Opportunities and threats",
    "Opportunities", ["Category still expanding",
                      "Lower-tier cities barely contested",
                      "High repeat purchase"],
    "Threats", ["Strong incumbents in every tier",
                "Low barriers to entry",
                "Mid-tier margin compression"],
    source="Analysis", category="Synthesis")

d.closing(org="Your organisation", contact="yourdomain.com",
          note="Prepared as a decision aid. Figures sourced per slide.")

print(d.save("deck.pptx"))
