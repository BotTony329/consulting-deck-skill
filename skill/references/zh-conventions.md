# Chinese-language deck conventions

Read this when the deck is in Chinese. Match the language of the user's request;
these decks are frequently Chinese content inside an English-titled template, and
that mix is fine and normal.

## Typography

Set the East Asian face and the latin face separately on every run — PowerPoint
tracks them as different attributes, and Chinese text renders in a default
fallback if only the latin face is set. This is the most common reason a
Chinese deck looks subtly wrong. `deckkit.set_font` handles it.

| Role | East Asian | Latin |
|---|---|---|
| Titles, assertions | 微软雅黑 | Arial |
| Body, supporting lines | 黑体 | Arial |
| Numerals in big-stat slides | 微软雅黑 | Arial |

Numerals and Latin words inside Chinese sentences stay in the latin face — this
is why runs get split mid-sentence ("从" / "2018" / "年到"). It's worth the
effort: mixed-script text set in a single face reads noticeably cheaper.

Don't add manual spaces around Latin words or numbers inside Chinese text; the
renderer handles the spacing. Manual spaces produce ragged gaps at other zoom
levels.

## Line length and wrapping

Chinese has no word breaks, so a Chinese line packs 1.6–1.8× the information of a
Latin line of the same width. Practical limits at the standard content width:

- assertion line (28pt): ≤ 30 characters, one line
- supporting line (20pt): ≤ 45 characters
- dense column text (16pt): ≤ 28 characters per line

Break long sentences at 、 or ，rather than letting them wrap arbitrarily —
a wrap that splits a four-character phrase across lines is jarring in a way the
Latin equivalent isn't.

## Punctuation

Use full-width punctuation throughout: ，。、；：""（）. Half-width punctuation
in Chinese text is the second-most-common tell of a hastily made deck.

Quotation marks are "" for the outer level and '' inside. Enumerations inside a
sentence use 、 not ，.

## Source and unit lines

- Source: `数据来源：新华社，灼识咨询等` — 12pt, grey, bottom of slide.
- Material/document source: `资料来源：中华人民共和国商务部，中央人民政府网站等公开网站`
- Example source, when citing an incident: `实例来源：新华社等公开新闻网站`
- Own survey: `数据来源：调查问卷` — always labelled distinctly from third-party
  data, because a client reads them very differently.
- Chart unit: `单位：亿元` / `单位：元` / `单位：十亿元`, near the top-right of the
  chart. Chinese financial reporting uses 亿 and 万 rather than thousands
  separators — don't silently convert to millions.

Multiple sources on one slide each get their own line, positioned near the chart
they belong to, rather than merged into one footnote.

## The compressed formula idiom

Chinese business writing rewards numerical compression far more than English
does, and it's why the running-thesis habit works so well in Chinese decks:

- 一大，一高一低，三层 — one large, one high one low, three tiers
- 两轮驱动 — twin-engine driven
- 双促双旺 — dual promotion, dual prosperity

The structure is [number][single-character summary], repeated. Four to six
characters total is the sweet spot. If you're writing a Chinese deck and the
section makes a compound claim, try to compress it this way before falling back
to a plain summary sentence — a formula in this shape gets repeated in the
client's own meetings, which a sentence never does.

## Section and framework naming

Frameworks keep their English names with a Chinese gloss: `PEST分析`,
`4P营销理论`, `SWOT`. Section titles are noun phrases (`外部环境PEST分析`,
`竞争态势`, `行业发展现状`), not sentences. The assertion in the body is where the
verb goes.

Scope lines on dividers follow: 本章节关注[外部因素]对[市场]产生的影响 —
"this section examines the effect of X on Y".

## Common tells to avoid

- Half-width punctuation in Chinese sentences
- Latin face applied to Chinese characters (renders as a fallback)
- Manual spaces padding Latin words inside Chinese text
- 万/亿 silently converted to Western units without relabelling
- English framework names with no Chinese gloss on first use
- A 400-character paragraph in a body placeholder — in Chinese this is roughly
  650 English characters, and it is unreadable at presentation distance
