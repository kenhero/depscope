from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

import json
from pathlib import Path
from .cmake_file_api import BuildGraph


def build_cyclonedx_sbom(context: dict[str, Any]) -> dict[str, Any]:
    """
    Minimal CycloneDX JSON BOM.
    We keep it intentionally small but structurally valid:
    - bomFormat/specVersion/version
    - serialNumber (URN UUID)
    - metadata: timestamp + tool + component (project)
    - components/dependencies empty for now (MVP placeholder)
    """
    project = str(context.get("project", "unknown"))
    timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "metadata": {
            "timestamp": timestamp,
            "tools": [
                {
                    "vendor": "Depscope",
                    "name": "depscope",
                    "version": "0.0.1",
                }
            ],
            "component": {
                "type": "application",
                "name": project,
                "version": "0.0.0",
            },
        },
        "components": [],
        "dependencies": [],
    }

def write_sbom_cyclonedx(graph: BuildGraph, out_path: Path) -> None:
    # MVP: 1 componente per ogni artifact prodotto dai target
    components = []
    deps = []

    def ref_for(path: str) -> str:
        return f"artifact:{path}"

    # root component (progetto)
    root_ref = "component:depscope-project"
    root = {
        "type": "application",
        "name": "depscope-project",
        "bom-ref": root_ref,
    }

    for t in graph.targets:
        for a in t.artifacts:
            comp = {
                "type": "file",
                "name": Path(a).name,
                "bom-ref": ref_for(a),
                "properties": [
                    {"name": "depscope.path", "value": a},
                    {"name": "depscope.target", "value": t.name},
                    {"name": "depscope.targetType", "value": t.type},
                ],
            }
            components.append(comp)

    # dependency graph: root dipende da tutti gli artifact (MVP)
    deps.append({
        "ref": root_ref,
        "dependsOn": [c["bom-ref"] for c in components],
    })

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": root,
            "tools": [{"vendor": "Depscope", "name": "depscope", "version": "0.0.1"}],
        },
        "components": components,
        "dependencies": deps,
    }

    out_path.write_text(json.dumps(sbom, indent=2), encoding="utf-8")