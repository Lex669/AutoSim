# AutoSim

A personal marketplace for agent plugins supporting both **Claude Code and Codex CLI** ecosystems, focused on scientific simulation and academic research. Features tools I use frequently, including Zemax OpticStudio lens design, FDTD photonics simulation, and COMSOL (coming soon).

## Getting Started

### 1. Add the marketplace

```bash
/plugin marketplace add Lex669/AutoSim
```

This registers AutoSim as a plugin source in Claude Code. You only need to do this once.

### 2. Install a plugin

```bash
/plugin install <plugin-name>@AutoSim
```

### 3. Update a plugin

```bash
/plugin update <plugin-name>@AutoSim
```

## Codex CLI (v0.121+)

The same marketplace is Codex-ready. Each plugin ships a `.codex-plugin/plugin.json` manifest exposing its skills, and Codex auto-discovers the catalog at `.agents/plugins/marketplace.json`.

```bash
# 1. Add the marketplace
codex plugin marketplace add Lex669/AutoSim

# 2. Install a plugin (`autosim` is the marketplace name registered in the manifest)
codex plugin add AutoZemax@autosim
codex plugin add LumericalFDTD@autosim
codex plugin add img-prompt@autosim

# 3. Refresh the marketplace snapshot after plugin updates
codex plugin marketplace upgrade autosim
```

> [!NOTE]
> On Codex, plugins expose only their skills — invoked through natural language. Slash commands and agents remain Claude Code only. `img-prompt` is registered with a local source (`./Img-Prompt`), so it is not installable by remote marketplace consumers.

## Available Plugins

### LumericalFDTD

Automates Ansys Lumerical FDTD simulation workflows using the Python API — build structures, run simulations, debug errors, and generate result plots. Also includes deep academic paper summarization with structured Chinese-language output and per-figure interpretation.

```bash
/plugin install LumericalFDTD@AutoSim
```

**Skills included:**

| Skill | Description |
|-------|-------------|
| LumericalFDTD | FDTD simulation automation — build, run, debug, output `.fsp` / `.npz` / `.png` |
| paper-summarizer | Deep academic paper summarization in Chinese with figure-by-figure analysis |

Repository: [Lex669/LumericalFDTD-skill](https://github.com/Lex669/LumericalFDTD-skill)

### AutoZemax

Automates Zemax OpticStudio optical design workflows using the ZOS-API — create and edit lens systems (sequential & NSC), run ray traces and analyses, perform optimization and tolerance analysis, export CAD, and generate result visualizations. Driven through four slash commands backed by nine functional skills and three autonomous debug/validation agents.

```bash
/plugin install AutoZemax@AutoSim
```

**Skills included:**

| Skill | Description |
|-------|-------------|
| system-setup | Create/load systems, aperture, fields, wavelengths |
| sequential-modeling | Lens Data Editor: surfaces, materials, solves |
| non-sequential-modeling | NSC Editor: objects, sources, detectors |
| ray-tracing | Batch ray trace & NSC ray trace |
| analysis | MTF, PSF, spot diagrams, wavefront, ray fans |
| optimization | Merit function, DLS & Hammer optimization |
| tolerance-analysis | Sensitivity & Monte Carlo tolerance analysis |
| cad-export | Export to STEP, IGES, SAT, STL |
| data-processing | numpy/matplotlib visualization & reporting |

Repository: [Lex669/AutoZemax](https://github.com/Lex669/AutoZemax)

### Img-Prompt

Turns a one-line theme into a structured JSON prompt for image generation tools — **knowledge-atlas infographics** (system cutaways, process chains, principle diagrams) and **posters**. The skill first decides the genre, then derives the skeleton from the subject: an infographic always orbits one photoreal cutaway hero visual and rebuilds the subject as an ordered chain (for coherent diffraction imaging: source → pinhole/shaping → sample → detector → phase retrieval → reconstruction), while a poster is organized as a sub-type with a fully specified text layer, layout sections, and print-craft vocabulary. Prompts are emitted as all-Chinese JSON and ship with a validator that also flattens a prompt into prose. The plugin never calls an image API.

```bash
codex plugin add img-prompt@autosim
```

**Skills included:**

| Skill | Description |
|-------|-------------|
| img-prompt | Write all-Chinese JSON prompts for knowledge-atlas infographics and posters, with genre routing, skeleton derivation, and offline validation |

## Changelog

### 2026-09-23 — Img-Prompt (refactored from Img-Gen)

- Reworked the `Img-Gen` plugin into **Img-Prompt**: it no longer calls DashScope or any image API. `generate_image.py`, the dashscope dependency, and the API-key setup are gone; the deliverable is now a structured JSON prompt you paste into any image tool.
- Extracted the regularities of the reference prompt sets (`Img-Prompt/sample_prompt/`): infographic/atlas samples and poster samples now back `references/infographic-atlas.md` and `references/poster.md`, with the field contract in `references/prompt-json-spec.md`.
- The skill routes by intent (infographic vs. poster), derives the skeleton from the subject, and emits all-Chinese JSON; `references/examples/cdi-infographic.json` and `poster-example.json` anchor the format.
- Added `scripts/validate_prompt_json.py` to check required fields, panel counts, `avoid` minimums, Chinese-text rules, and leftover placeholders, and to flatten a prompt into prose on demand.
- Deleted the old academic-figure and PPT-figure templates; renamed the plugin folder to `Img-Prompt` and the marketplace entry to `img-prompt` (`./Img-Prompt`).

### 2026-09-07 — Codex CLI support & Img-Gen plugin

- Added `.agents/plugins/marketplace.json`, so Codex CLI (v0.121+) auto-discovers this repository as the `autosim` marketplace.
- Added the **Img-Gen** plugin — DashScope `qwen-image-3.0-pro` text-to-image for academic figures and PPT/defense slides. It is registered with a local source (`./Img-Gen`), so it is not installable by remote marketplace consumers.
- `.gitignore` now excludes locally cloned plugin repositories (`AutoZemax/`, `LumericalFDTD/`, `.claude/`, `asset/`); each plugin keeps its own repository.
- README: new **Codex CLI (v0.121+)** section covering `codex plugin marketplace add`, `codex plugin add`, and `codex plugin marketplace upgrade`.

### 2026-06-15 — AutoZemax added

- Registered **AutoZemax** (Zemax OpticStudio automation through the ZOS-API) in `.claude-plugin/marketplace.json`, sourced from [Lex669/AutoZemax](https://github.com/Lex669/AutoZemax).
- README: added the AutoZemax plugin card with its skill table.

### 2026-05-29 — Marketplace established

- Converted this repository into a Claude Code plugin marketplace: `.claude-plugin/marketplace.json` aggregates plugins that live in separate repositories, starting with **LumericalFDTD** from [Lex669/LumericalFDTD-skill](https://github.com/Lex669/LumericalFDTD-skill).
- README rewritten as a three-step guide — add the marketplace, install a plugin, update a plugin.
- Initial commit: repository created under the MIT license.
