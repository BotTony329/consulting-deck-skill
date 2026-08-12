# Argument discipline

The layout catalog governs how a slide looks. This governs whether it earns its
place. Read it when scoping a deck, when a slide feels like it's presenting data
rather than making a point, and again at the end as a review checklist.

## Define the deck before building it

Six answers, written down before any slide exists. If the user hasn't supplied
them, ask — these change the deck more than any styling decision. Unattended,
state your assumptions on the first content slide so a returning reader can
correct them cheaply.

| | |
|---|---|
| **Audience** | who reads or watches this |
| **Decision** | what judgement it has to support |
| **Objective** | what the deck must achieve |
| **Core question** | the one question the deck answers |
| **Final message** | the single sentence they should retain |
| **Evidence standard** | how much proof this audience demands |

The evidence standard varies more than people expect:

- **Investor** — market size + traction + differentiation + unit economics + scalability
- **Executive** — problem + evidence + options + recommendation + impact
- **Competition judge** — problem + innovation + implementation + validation + potential
- **Client** — situation + diagnosis + solution + value + implementation path
- **Internal / technical review** — is it actually built, does it hold under load

A deck built to the wrong evidence standard fails even when every slide is
individually good.

## Spec the slides before you build them

Between the storyline and the file, write one line per slide:

```
#   Purpose            Message title                        Evidence        Form        Takeaway
12  size the market    Market grew 108% in four years       CIC, 2018-22    column      category is expanding fast
13  qualify the growth Growth is drawing entrants, not …    store counts    line+note   growth alone isn't a reason to enter
```

This is where redundancy becomes obvious and where you notice you have three
slides making the same point. Deleting a row costs nothing; deleting a built
slide costs an argument with yourself.

## The "so what?" ladder

The single most reliable way to turn research into consulting. Take each
significant piece of evidence and push it down the ladder until it reaches a
decision:

```
EVIDENCE     The market grew 108% between 2018 and 2022.
so what?  →  The category is expanding quickly.
so what?  →  Growth on that scale attracts entrants and compresses margin.
so what?  →  Category growth alone is not a reason to enter; position and
             differentiation decide whether entry pays.
```

The first rung is description — most decks stop there. The second is analysis.
The third is where the client's decision actually changes, and it's where the fee
is earned.

Another worked example:

```
EVIDENCE     68.5% of consumers are female.
weak      →  "Female consumers are important."
better    →  Demand is structurally concentrated among younger women.
implication  Product design, brand voice, and channel selection should be built
             around that group's media behaviour rather than a general audience.
```

Never leave a significant number uninterpreted. A chart with no stated
implication is raw material that the audience is being asked to process on your
behalf.

## Evidence taxonomy

When working from supplied material — research files, screenshots, notes,
interview transcripts — you may restructure aggressively, but you may not
silently invent. Keep four categories distinct, because clients read them
completely differently:

- **Fact** — directly supplied or verifiable, with a source
- **Inference** — a reasonable reading of the facts, and labelled as such
- **Hypothesis** — plausible, requires validation, say so on the slide
- **Recommendation** — a proposed action, resting on the three above

Where a number is needed and doesn't exist, write `数据待补 / DATA REQUIRED` or
`待验证 / TO BE VALIDATED` on the slide. A visible gap is a normal part of an
interim deck. A fabricated statistic, citation, institution, customer quote, or
case result is not recoverable — it destroys the credibility of every other
number in the deck, including the true ones.

## Frameworks are tools, not the storyline

PEST, Five Forces, value chain, SWOT, 2×2 matrices, segmentation — reach for one
when it genuinely organises the evidence, and drop it the moment it starts
generating empty cells you feel obliged to fill.

The test: if a framework quadrant has nothing real in it, the framework is wrong
for this problem, not the evidence. A PEST section where "Political" is three
tenuous paragraphs is worse than a deck that skips it and spends the space on the
two forces that actually drive the market.

Use frameworks to structure sections. Let findings, not the framework's shape,
determine the storyline.

## Features → capability → value

For product, AI, and platform decks, never present a feature list. Features tell
the buyer what was built; they need to know what changes for them.

```
USER NEED     "What should I improve after this teaching session?"
CAPABILITY    analyse teaching behaviour against prior sessions
SYSTEM ACTION compare current performance to history, surface deltas
OUTPUT        structured evaluation + trend visualisation
USER VALUE    the learner sees not just what went wrong, but whether repeated
              practice is producing measurable improvement
```

One capability walked down this chain persuades more than twelve bullet-pointed
features. When several capabilities need covering, run them through the chain
individually and then pull them together in a single App → How → Value table.

Concrete scenarios beat capability lists for the same reason: a named question a
real user would ask ("Which direction should our next transformation take?"),
followed by what the system does with it and what comes back, is
self-demonstrating in a way a feature grid never is.

## Screenshot discipline

Before placing any screenshot, answer: *what does this prove?* The answer decides
the treatment.

| What it proves | Treatment |
|---|---|
| the thing actually runs | crop to the moment of interaction, enlarge |
| a complete loop exists | place small stills inside a workflow diagram |
| results are measurable | zoom hard into the metrics panel |
| nothing in particular | cut it |

One aggressive crop beats five thumbnails. Add callouts only where they carry
analytical meaning — arrows and circles pointing at things the reader can't read
anyway are an admission that the image is too small.

## Choosing the visual form

| Relationship | Form |
|---|---|
| change over time | clustered column (house habit) or line for many periods |
| comparison across categories | bar, sorted by value |
| composition of a whole | pie or donut, ≤6 slices |
| position on two axes | 2×2 matrix |
| sequence | left-to-right flow with arrows |
| hierarchy or tiers | pyramid |
| stages of value creation | horizontal value chain |
| plan over time | timeline |
| system structure | architecture diagram |

Charts exist to make a relationship visible, not to prove that numbers were
collected. Every chart needs a visual answer to "what am I supposed to notice?"
that lands in about three seconds — usually a callout, a highlighted bar, or a
trend line with a delta on it. If nothing stands out, the chart is decoration and
the number belongs in the text.

## Executive summary

For executive and client audiences, add a summary slide near the front — written
last, once you know what the deck actually concluded. Three to five findings, the
recommendation, and the expected impact. A reader who sees only that slide should
understand the argument and the proposed action.

Skip it for research reports that build to a conclusion the reader is meant to
reach with you, which is how both of the source decks are built.

## Review gates

Run these three before delivering. They catch different failures.

**Title-only read.** Extract every slide's title and assertion, in order, and
read them as continuous prose (`check_deck.py --titles` prints this). They should
form a coherent argument on their own.

Fails: *Market · Customer · Technology · Competition · Conclusion.*
Passes: *Demand keeps expanding · Core customers increasingly prioritise price-performance ·
Digital channels now carry most transactions · This opens a mid-tier position ·
Our solution addresses it · Pilot results validate the approach.*

**Per-slide logic.** For each slide: what question does it answer, what is the
conclusion, what supports it, is that enough, what does it imply, and why does
the next slide follow? Any unclear answer is a slide to revise or cut.

**Red team.** Then attack it. Which claim is weakest? Which conclusion outruns
its evidence? Which slide is redundant? Where is correlation being read as
causation, or an assumption presented as fact? Where would an executive ask "so
what?", an investor "prove it?", a client "how?", a technical reviewer "is this
actually built?" Fix those before delivery, not after the meeting.

## Failure patterns to avoid

Machine-made decks have a recognisable signature. Watch for it in your own
output:

- every slide built from exactly four cards, each with an icon
- the same layout ten slides in a row (the checker warns on this)
- short generic bullets that restate the title
- icon walls and decorative dashboards with no analytical purpose
- gradient backgrounds, glow effects, and 3D that serve no reading purpose
- fabricated statistics, quotes, or case results
- false precision — "42.7% efficiency gain" from a rough estimate
- buzzwords standing in for specifics
- the same point restated three times in different words
- conclusions with no visible evidence behind them

Vary layout because the information structure changed, never for variety's own
sake. A consulting deck should look designed, not decorated.

## What the deck has to leave behind

The audience should walk out knowing what is happening, why it matters, and what
should be done next. Data without interpretation is research; interpretation
without evidence is opinion; a recommendation without reasoning is an assertion.
The job is connecting evidence to insight to implication to decision.
