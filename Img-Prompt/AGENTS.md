# Repository Guidelines

## Project Structure & Module Organization

This repository packages the **Img Prompt** Codex plugin, a skill that turns a topic into a structured all-Chinese JSON image prompt.

- `.codex-plugin/plugin.json` — plugin manifest (name, version, interface, `defaultPrompt`).
- `skills/img-prompt/` — the skill itself: `SKILL.md` (workflow, routing table, hard constraints), `references/` (JSON spec, infographic/poster derivation rules, `examples/`), `scripts/validate_prompt_json.py` (validator).
- `sample_prompt/` — raw human-readable source material behind the derived rules, including `信息图与科普图提示词规律.md` (statistics over 79 infographic cases). Some larger galleries are kept locally and may stay untracked. Read-only reference; never cited in generated prompts.
- `prompts/` — **not part of this repository**: the skill saves generated prompt JSON into the consuming project's `prompts/` directory.

There is no compiled source and no test directory; Markdown docs plus one Python script are the entire codebase.

## Build, Test, and Development Commands

The validator uses only the Python standard library, so there is nothing to install or build. Run from the repository root:

```powershell
python skills\img-prompt\scripts\validate_prompt_json.py skills\img-prompt\references\examples\poster-example.json
python skills\img-prompt\scripts\validate_prompt_json.py --stdin < prompt.json   # pipe a candidate prompt
python skills\img-prompt\scripts\validate_prompt_json.py --stdin --out prompts < prompt.json  # validate, then save
python skills\img-prompt\scripts\validate_prompt_json.py prompt.json --flatten  # flatten to one prose prompt
python skills\img-prompt\scripts\validate_prompt_json.py prompt.json --json     # machine-readable report
```

`--out <dir>` writes the prompt only when validation passes, naming it `{genre}-{主题}.json` and appending `-2`, `-3` on name clashes. Exit codes: `0` pass (warnings allowed), `1` validation errors, `2` usage, read, or write failure.

## Coding Style & Naming Conventions

- Python: 4-space indent, `from __future__ import annotations`, type hints, `snake_case` functions and variables. Keep `UPPER_SNAKE_CASE` for module-level constants.
- JSON fields: `snake_case`, mirroring `references/prompt-json-spec.md` (`genre`, `subtype`, `canvas`, `centerpiece`, `layout`, `avoid`).
- Prompt content: all visible text in Chinese; proper nouns (CDI, FDTD, model numbers) may stay in original script but must share a string with Chinese text. Never emit placeholders such as `TODO`, `[TITLE]`, `xxx`.
- Files: `kebab-case.md` for docs; example JSON named after its subject (`cdi-infographic.json`); saved prompts follow `{genre}-{主题}.json` under `prompts/`, UTF-8 with 2-space indent and unescaped Chinese.

## Testing Guidelines

`validate_prompt_json.py` is the test harness: `prompt-json-spec.md` is its single source of truth. Before opening a PR, validate every file under `skills/img-prompt/references/examples/` (all three must pass without warnings) and any edited `sample_prompt/*.json`, and confirm rule changes are reflected in both the script and the spec in the same commit. New rules need an example that fails before the change and passes after. Saving is part of the contract: check that `--out` writes a file on pass, skips writing on failure, and never overwrites an existing prompt.

## Prompt Rules Derived From Samples

The infographic rules come from measured case statistics, so keep them evidence-based: required fields now include `subtype` and `canvas.aspect` (79% of strong cases failed here when omitted), and `avoid` must cover "poster feel" plus garbled-text modes. When adding a rule, cite the sample doc or the failing example that justifies it.

## Commit & Pull Request Guidelines

Follow the existing Conventional Commits style, optionally scoped: `feat: ...`, `docs: ...`, `fix(validator): ...`. Use imperative, Chinese or English summaries.

PRs should state the motivation, list modified skill/reference paths, include the validator command and its output, and note any behavior change for existing prompts. Link related issues and attach example JSON before/after where output shape changes.
