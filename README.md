# Depscope for CMake

Build-derived SBOM and dependency graph for C++/CMake projects.

## What it does (MVP)
- Generates:
  - `report.html` (human-friendly report)
  - `sbom.cdx.json` (CycloneDX SBOM)
- Detects:
  - duplicate libraries (same lib from different paths)
  - version drift (same lib at different versions across the graph)

## Quickstart (planned)
```bash
cmake -S . -B build && cmake --build build
depscope scan --build-dir build --out out/

Licensed under the Apache-2.0 (or MIT) license. See LICENSE.
