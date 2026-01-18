# Depscope for CMake

Build-derived **CycloneDX SBOM** and **dependency graph** for **C++/CMake** projects.

This tool aims to generate reliable outputs from the *actual build* (not heuristic source scanning), helping you spot:
- duplicate libraries (same lib from different paths)
- version drift (same component at different versions across the graph)
- untracked / unexpected dependencies

## Status

This project is in **early MVP development**.

Expect breaking changes and incomplete features. The immediate goal is to ship an end-to-end CLI that produces:
- `out/report.html` (human-friendly report)
- `out/sbom.cdx.json` (CycloneDX SBOM)

## What the MVP does (today)

The initial MVP focuses on:
- a working CLI (`depscope scan`)
- generating placeholder-but-valid outputs (HTML + CycloneDX JSON)
- setting the foundation for parsing build graph data next

## Outputs

When you run:

```bash
depscope scan --build-dir build --out out/ ```

You will get:
out/report.html
out/sbom.cdx.json

## Quickstart (MVP)

1. Create a build directory (as you already do today)

```bash
cmake -S . -B build
cmake --build build ```

2. Run depscope
```bash
depscope scan --build-dir build --out out/ ```

3. Open the report

# macOS
```bash

open out/report.html ```

# Linux
```bash
xdg-open out/report.html ```

# Windows (PowerShell)
```bash
start out/report.html ```

## Installation (dev)
For now, the simplest dev install is:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -U pip
pip install -e .

Then:

depscope --help
depscope scan --help ```


## Roadmap

Parse build graph from CMake

CMake File API (preferred)

Graphviz output (optional/secondary)

Generate HTML report from real graph

targets, transitive deps, origin paths

duplicates + drift detection with traces

Generate CycloneDX SBOM from real graph

components + dependencies

best-effort metadata (name/version/license when available)

GitHub Action example workflow

produces report.html + sbom.cdx.json as artifacts

Policy checks (CI gating)

fail CI on forbidden duplicates

fail CI on disallowed licenses/components

## Design partners

If you maintain a medium/large C++/CMake codebase and want to influence the MVP, please open an issue:

go to Issues

click New issue

choose MVP Feedback

Your real constraints (CI, OS, CMake version, size) are the fastest path to a useful tool.

## License
Licensed under the Apache License 2.0. See LICENSE.
