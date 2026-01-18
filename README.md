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
depscope scan --build-dir build --out out/
```

You will get:
```text
out/report.html
out/sbom.cdx.json
```

## Quickstart (MVP)

Create a build directory (as you already do today)
```bash
cmake -S . -B build
cmake --build build
```

Run depscope
```bash
depscope scan --build-dir build --out out/
```

Open the report
macOS:
```bash
open out/report.html
```

Linux:
```bash
xdg-open out/report.html
```

Windows (PowerShell):
```bash
start out/report.html
```

## Installation (dev)
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -U pip
pip install -e .
```

Verify:
```bash
depscope --help
depscope scan --help
```

## Roadmap

1) Parse build graph from CMake  
2) CMake File API (preferred)  
3) Graphviz output (optional/secondary)  
4) Generate HTML report from real graph  
5) targets, transitive deps, origin paths  
6) duplicates + drift detection with traces  
7) Generate CycloneDX SBOM from real graph  
8) components + dependencies  
9) best-effort metadata (name/version/license when available)  
10) GitHub Action example workflow  
11) produces report.html + sbom.cdx.json as artifacts  
12) Policy checks (CI gating)  
13) fail CI on forbidden duplicates  
14) fail CI on disallowed licenses/components  

## Design partners

If you maintain a medium/large C++/CMake codebase and want to influence the MVP, please open an issue:

1) go to Issues  
2) click New issue  
3) choose MVP Feedback  
4) share your constraints (CI, OS, CMake version, size)

## License

Licensed under the Apache License 2.0. See `LICENSE`.


