# Consulting Deck Skill

[![CI](https://github.com/BotTony329/consulting-deck-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/BotTony329/consulting-deck-skill/actions/workflows/ci.yml)
[![skills.sh](https://skills.sh/b/BotTony329/consulting-deck-skill)](https://skills.sh/BotTony329/consulting-deck-skill)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Consulting Deck Skill is a cross-agent AI skill for turning structured business
analysis into consulting-grade PowerPoint presentations.

This is not just a prompt. It is a reusable presentation-generation workflow with
consulting-style information hierarchy, structured slide planning, six visual themes,
theme-aware layout behaviour, editable PowerPoint output, a CLI, automated validation,
tests, CI, and synchronized instructions for multiple coding agents.

The skill asks for the intended visual identity instead of silently imposing one
default style. Its six themes change layout behaviour—not merely colours—including
dark or light content fields, divider and statement-slide treatment, typography
emphasis, rule weight, eyebrow casing, and accent handling.

## Why this exists

AI can write a `.pptx`, but without a presentation system the result often has
inconsistent hierarchy, weak executive storytelling, arbitrary layouts, poor spacing,
theme drift, and unreliable output. Consulting Deck Skill encodes a repeatable process:
research first, write the storyline as assertions, distinguish evidence from inference,
build with a coherent visual system, validate mechanically, and then inspect the render.

The output is an editable 16:9 PowerPoint deck with message-first titles, restrained
rules and whitespace, explicit source lines, and theme-aware content, divider, and
statement slides. It is generated from Python or a declarative YAML/JSON specification,
not exported as flattened slide images.

## What this is not

- Not a collection of static PowerPoint templates
- Not a single hardcoded visual style or a six-colour theme pack
- Not a prompt-only repository
- Not a collection of proprietary consulting or client slides

## Key features

- Message-first consulting workflow with source discipline and storyline review
- Editable `.pptx` output built with `python-pptx`
- YAML, JSON, and Python authoring routes
- Six themes plus per-deck accent overrides
- Theme-aware content, divider, statement, eyebrow, and rule treatments
- CLI commands to build, validate, print titles, list themes, and inspect the schema
- Checks for off-canvas text, likely overflow, unsourced figures, and repetitive layouts
- Agent guidance generated from one source of truth
- Automated regression tests and a Python 3.9–3.13 GitHub Actions matrix

## Supported agents

`AGENTS.md` is the source of truth. `scripts/sync_agent_files.py` generates the other
entry points so their guidance cannot drift.

| Agent | Instruction file |
|---|---|
| OpenAI Codex and agents configured to read AGENTS.md (including Kimi where enabled) | `AGENTS.md` |
| Claude | `CLAUDE.md` |
| Gemini | `GEMINI.md` |
| Cursor | `.cursor/rules/consulting-deck.mdc` |
| Cline / Roo | `.clinerules` |
| Windsurf | `.windsurfrules` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Other agents | YAML/JSON spec plus the CLI |

## Install as an Agent Skill

Install the complete skill from GitHub with the current skills CLI (Node.js 22.20 or
newer):

```bash
npx skills add BotTony329/consulting-deck-skill --skill consulting-deck
```

The CLI installs GitHub-hosted Agent Skills for supported AI coding agents. The
installed skill includes the workflow, references, Python engine, CLI, themes, and
examples; `SKILL.md` explains the isolated Python setup used at runtime.

## Install the Python package directly

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/BotTony329/consulting-deck-skill.git
cd consulting-deck-skill
pip install -e ".[dev]"
```

Confirm the installation:

```bash
consulting-deck --version
consulting-deck themes
pytest
```

## Quick start

Build the bundled YAML example and run the checker:

```bash
consulting-deck build examples/market_entry.yaml -o deck.pptx --check
consulting-deck titles deck.pptx
```

JSON specifications use the same command. `consulting-deck schema` lists the exact
supported slide types and fields.

The equivalent Python route is:

```python
from consulting_deck import Deck

deck = Deck(lang="en", theme={"base": "slate", "accent": "#7A1FA2"})
deck.title_slide("Market entry study", "Ready-to-drink tea · China")
deck.big_stat("108", "growth over four years", unit_suffix="%", source="CIC")
deck.save("deck.pptx")
```

## Themes

All themes use the same Arial/CJK font pairings and message-first hierarchy. They differ
structurally through field treatment, eyebrow casing, statement style, and rule weight;
the accent remains deliberately scarce in every theme.

| Theme | Palette and content field | Dividers / statements | Eyebrow and rules |
|---|---|---|---|
| `editorial` | Warm paper, dark ink, terracotta; light content | Dark / dark | Uppercase, 0.012-inch rules |
| `slate` | Cool white, navy, corporate blue; light content | Dark / dark | Uppercase, 0.012-inch rules |
| `mono` | Black, white, restrained green; light content | Light / light | Uppercase, 0.010-inch rules |
| `midnight` | Charcoal, pale text, amber; dark content | Dark / dark | Uppercase, 0.014-inch rules |
| `sand` | Cream, brown, deep teal; light content | Dark / light | Mixed case, 0.012-inch rules |
| `press` | Near-monochrome with dark red; light content | Light / light | Uppercase, 0.018-inch rules |

Apply a custom accent without creating global theme state:

```python
theme={"base": "slate", "accent": "#7A1FA2"}
```

Each `Deck` owns its resolved palette, so multiple themes can be rendered safely in the
same Python process. Bars and chart marks retain the exact accent; if that colour lacks
enough contrast for text on a dark field, text automatically uses the theme's readable
foreground instead.

## Cross-agent workflow

```text
AGENTS.md
    ↓
scripts/sync_agent_files.py
    ↓
CLAUDE.md · GEMINI.md · .clinerules · .windsurfrules
.cursor/rules/consulting-deck.mdc · .github/copilot-instructions.md
```

Edit `AGENTS.md`, regenerate the derived files, and verify there is no drift:

```bash
python scripts/sync_agent_files.py
python scripts/sync_agent_files.py --check
```

## Development and validation

```bash
pip install -e ".[dev]"
pytest -q
python scripts/sync_agent_files.py --check
consulting-deck build examples/market_entry.yaml -o /tmp/deck.pptx --check
consulting-deck titles /tmp/deck.pptx
```

The checker is intentionally not a substitute for visual inspection. If LibreOffice
and Poppler are installed, render the result before shipping it:

```bash
soffice --headless --convert-to pdf deck.pptx
pdftoppm -png -r 70 deck.pdf page
```

Project layout:

```text
SKILL.md               Canonical agent workflow and runtime instructions
references/            Design, narrative, evidence, and language guidance
src/consulting_deck/   Python engine, themes, CLI, spec loader, and checker
scripts/              Agent-file synchronization and skill packaging
examples/             Working Python, YAML, and JSON examples
tests/                Unit and regression tests
.github/workflows/    CI configuration
```

## Security and permissions

The Python package requires no API key, contains no networking client, uploads no data,
and does not spawn subprocesses. Depending on the command or API used, it may read a
local YAML/JSON specification, an existing presentation, an optional PowerPoint
template, or an optional image. It writes the requested `.pptx`; the synchronization
and packaging scripts also write generated instruction files and a local `.skill`
archive when explicitly run.

The agent guidance recommends research and optional visual rendering. A host AI agent
may therefore use its own tools or execute explicit commands such as `consulting-deck`,
`soffice`, and `pdftoppm`; those actions and any network access belong to the host agent
or user environment, not to this Python package.

Do not place client-confidential material, third-party logos, licensed photography, or
copied proprietary slide layouts in public examples or contributions.

## Contributing

Bug reports, fixes, and original themes are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md),
install the development dependencies, run the tests, and confirm agent-file synchronization
before opening a pull request.

## License

Released under the [MIT License](LICENSE). Copyright © 2026 BotTony329.
