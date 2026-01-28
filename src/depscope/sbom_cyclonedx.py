from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

import json
from pathlib import Path
from .cmake_file_api import BuildGraph, TargetInfo

def _cdx_type_for_target(t: TargetInfo) -> str:
    tt = (t.type or "").upper()
    if "EXECUTABLE" in tt:
        return "application"
    if "LIBRARY" in tt:
        return "library"
    return "library"


def _bomref_target(t: TargetInfo) -> str:
    # preferisci id (univoco). fallback su name se serve.
    if t.id:
        return f"target:{t.id}"
    return f"targetname:{t.name}"


def write_sbom_cyclonedx(graph: BuildGraph, out_path: Path) -> None:
    # Root component (il "progetto")
    project_name = Path(graph.build_dir).name
    root_ref = "target:__root__"
    root = {
        "type": "application",
        "name": project_name,
        "bom-ref": root_ref,
        "properties": [
            {"name": "depscope.build_dir", "value": graph.build_dir},
            {"name": "depscope.generator", "value": str(graph.generator or "")},
        ],
    }

    components: list[dict[str, Any]] = []
    dependencies: list[dict[str, Any]] = []

    # Componenti = targets
    for t in graph.targets:
        comp = {
            "type": _cdx_type_for_target(t),
            "name": t.name,
            "bom-ref": _bomref_target(t),
            "properties": [
                {"name": "depscope.targetId", "value": t.id},
                {"name": "depscope.targetType", "value": t.type},
            ],
        }

        # Artifacts come properties (MVP)
        for a in (t.artifacts or []):
            comp["properties"].append({"name": "depscope.artifact", "value": a})

        components.append(comp)

    # Dependencies: target -> target (risolvi dep_ids con targets_by_id)
    for t in graph.targets:
        depends_on: list[str] = []
        for dep_id in (t.dep_ids or []):
            dep_t = graph.targets_by_id.get(dep_id)
            if dep_t:
                depends_on.append(_bomref_target(dep_t))
        if depends_on:
            dependencies.append(
                {
                    "ref": _bomref_target(t),
                    "dependsOn": depends_on,
                }
            )

    # Root depends on all targets (MVP semplice e ok)
    dependencies.insert(
        0,
        {
            "ref": root_ref,
            "dependsOn": [_bomref_target(t) for t in graph.targets],
        },
    )

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": root,
            "tools": [{"vendor": "Depscope", "name": "depscope", "version": "0.0.1"}],
        },
        "components": components,
        "dependencies": dependencies,
    }

    out_path.write_text(json.dumps(sbom, indent=2), encoding="utf-8")