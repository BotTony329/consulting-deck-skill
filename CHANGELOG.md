# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-08-12 — skills.sh distribution support

### Fixed

- Made the repository root the canonical single-skill package so `npx skills add`
  installs the Python engine, CLI, themes, examples, and references with `SKILL.md`.
- Corrected installed-skill runtime and validation instructions to use paths and CLI
  commands that exist after installation.
- Clarified that embedded content in supplied decks is untrusted evidence and must not
  be followed as agent instruction.

### Added

- Documented the verified skills.sh installation command and badge.
- Added a clean skills CLI installation and runtime smoke test to CI.

## [0.1.0] - 2026-08-12 — Initial public release

### Added

- Consulting-style, message-first presentation workflow and reference guidance.
- Editable PowerPoint generation from Python, YAML, and JSON specifications.
- Six structurally distinct visual themes with per-deck custom accent colours.
- CLI commands for building, checking, inspecting storylines, themes, and schemas.
- Automated deck validation, test coverage, and GitHub Actions CI.
- Synchronized instructions for Codex, Claude, Gemini, Cursor, Cline, Windsurf,
  and GitHub Copilot.

[Unreleased]: https://github.com/BotTony329/consulting-deck-skill/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/BotTony329/consulting-deck-skill/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/BotTony329/consulting-deck-skill/releases/tag/v0.1.0
