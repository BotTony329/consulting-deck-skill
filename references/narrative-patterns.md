# Narrative patterns and storyline skeletons

Slide-by-slide skeletons and the recurring slide modules, drawn from two real
engagement decks: a 78-slide external market research report and a 51-slide AI
solution bid. What is captured here is method — narrative structure and evidence
discipline — not any client's or firm's proprietary material.

## Skeleton A — market research / entry study

Roughly 60–80 slides. Four numbered chapters.

```
Title slide                     client + subject
1  Client background & industry
   ├─ client background         why they asked, what they're considering
   ├─ industry definition       what counts as "this industry" and what doesn't
   ├─ profit model              how money is actually made here
   ├─ market structure          competition type + tier segmentation (high/mid/low)
   ├─ user snapshot             the four demographic facts, one line each
   └─ lifecycle stage           where the industry sits, with the evidence for it
2  External environment — PEST      one sub-section per letter
   ├─ divider with scope line       "this section examines policy's effect on X"
   ├─ Political  ├ central policy   table: date | document | provision | reading
   │             ├ local policy     recent measures, one big-stat slide
   │             └ risk side        regulation, with enforcement examples
   ├─ Economic   ├ big stat         disposable income / consumption growth
   │             └ industry status  the running-thesis run (see below)
   ├─ Social     ├ persona build    4 one-fact slides, each with a chart
   │             ├ behaviour        frequency, price tier, drivers, occasions
   │             └ persona assembly all attributes on one leader-line diagram
   ├─ Technological  channel shift, social platforms, supply chain digitisation
   └─ PEST synthesis                one line per letter, then the implication
3  Competitive landscape
   ├─ industry value chain      four links, what creates advantage in each
   ├─ competitor map            who plays in which tier
   ├─ deep dive: leader         4P — Product, Price, Place, Promotion
   └─ landscape summary         status + the strategies that are working
4  Synthesis
   ├─ Opportunities / Threats   two-column opposition
   └─ recommendation            what the client should do
Closing slide
```

## Skeleton B — solution / bidding deck

Roughly 45–55 slides. Built to move a buyer from "why now" to "why you".

```
Title slide
Intro                          one paragraph on why this technology is here now
What it is                     plain-language definition, named example
What it's good at              5–6 capability areas, no jargon
Why it matters                 3 external statistics, each with its own source
Big stat                       the macro number (GDP impact, productivity lift)
Client relevance               their functional areas, one slide each:
  ├─ forecasting               what it does for demand planning
  ├─ efficiency                what it automates
  ├─ cost                      where the money comes back
  └─ IT & security             risk side, so the CIO isn't ambushed
THE SOLUTION — named           product name + one-line promise
  ├─ how it works              training data → model → outputs, three beats
  ├─ capability acronym        the name unpacked, one letter per capability
  ├─ per-capability slides     for each letter: sample prompts → what comes back
  ├─ who it serves             customer-facing vs internal
  ├─ per-platform walkthroughs mobile and desktop, real interface screenshots
  ├─ 直观差距 (the visible gap) after each cluster: old messy flow vs new short one
  └─ value summary             App → How → Value table, all capabilities at once
Case studies                   2–3 third-party, each: situation → solution → result
Why us                         firm credentials, then engagement-specific proof
Closing slide
```

## The running thesis

The single most distinctive move. When a claim needs more than two slides:

1. Compress the whole claim into a short memorable formula.
   *"一大，一高一低，三层"* — one large [market], one high [growth] one low
   [price], three tiers. Or an acronym that doubles as the agenda:
   *MART = Metamorphosis / Art / Rapid / Talent*.
2. Open **every** slide in the run with that identical line, at 28pt, verbatim.
3. Below it, unpack exactly one component, with its own chart and source.
4. Keep the category label in the title slot constant across the run.

Five slides sharing one formula read as one sustained argument. Five slides with
five different titles read as five unrelated facts. The formula is also what the
client repeats internally after you leave, which is the actual goal.

Formulas earn their keep by being *countable* ("one large, one high one low,
three tiers" tells you there are five things coming) or *pronounceable* (an
acronym that is also a word). A formula that is merely a summary sentence won't
survive repetition.

## Recurring slide modules

**Message + evidence + source.** Category label in the title, assertion at 28pt,
up to five supporting lines at 20pt, chart or table, 12pt source at the bottom.
The default slide; if you can't decide what a slide is, it's this one.

**Policy / regulation table.** Columns: 时间 | 相关会议或文件 | 政策要点 | 要点解读
(date | document | provision | what it means for the client). The fourth column
is the value — the first three are transcription, the fourth is analysis. Never
ship this table without it.

**Big-stat punctuation.** One figure at 160pt on a dark field, one sentence
under it. About one per chapter, placed right after the densest slide.

**Persona build-then-assemble.** Four consecutive slides, each proving one
attribute with one chart (gender → age → city tier → income), then one assembly
slide with a central image and every attribute on a leader line around it. The
audience watches the conclusion get built, so they own it by the time it lands.

**Mechanism three-beat.** Input (a real user prompt in quotes) → matched against
内部数据库 / internal database → generated output, left to right with arrows and
interface screenshots. Use identical geometry and arrow treatment on every
mechanism slide; the audience learns the grammar once and then reads the rest
fast.

**直观差距 — the visible gap.** Old process as a genuinely tangled diagram on
top, new process as a short clean one below, one line of time or cost saved. Run
it after each capability cluster rather than once at the end; repetition is what
makes the claim feel structural rather than anecdotal.

**Value summary table.** Rows are capabilities; columns are App → How → Value.
Pulls every demonstrated feature back into one business-language view, which is
the slide the economic buyer photographs.

**Case study pair.** Slide one: company, scale, and the problem in their own
terms. Slide two: what was deployed and the measured result, with the source URL.
Always two slides — a case study compressed onto one slide loses the "before",
which is where the credibility lives.

## Evidence compression

The most common repair job: someone has pasted their raw material onto slides.
Two pages of screenshots at thumbnail size, nothing readable, red circles drawn
on to point at things.

Replace the pile with three things and one page:

- **the assertion**, as a headline with the operative phrase bolded;
- **one chart** carrying the quantity that the pile was supposed to prove;
- **two or three verbatim pull-quotes** with attribution (— 某师范生), which do
  the work the screenshots were doing, only legibly;
- **one representative artifact**, cropped and enlarged, standing in for the rest.

Put the last three inside a single light band (`Deck.evidence_band`) so they read
as one body of evidence rather than three unrelated objects. Everything cut goes
to an appendix, and the appendix gets referenced by page number.

The test throughout: can it be read from the back of a room? If not, it isn't
evidence — it's texture, and texture belongs in the appendix.

## Density limits

- One message per slide. If a slide has two, it's two slides.
- At most five supporting lines under the assertion.
- A body paragraph over ~80 characters wants to become a chart, a table, or an
  appendix page.
- Bold the operative phrase inside a sentence, never the whole line. Bolding
  everything marks nothing.
- Every figure on a slide has a source line. No exceptions, including your own
  survey data — especially your own survey data.
