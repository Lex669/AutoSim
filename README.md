# AutoSim

A personal marketplace for Claude Code agent plugins focused on scientific simulation and academic research. Features tools I use frequently, including FDTD photonics simulation and COMSOL (coming soon).

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
