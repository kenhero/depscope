from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid


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
