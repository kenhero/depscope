from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .report_html import render_report_html
from .sbom_cyclonedx import build_cyclonedx_sbom


def _log(verbose: bool, msg: str) -> None:
    if verbose:
        print(msg)


def _detect_cmake_file_api_reply(build_dir: Path) -> dict[str, Any] | None:
    """
    Best-effort: reads CMake File API reply index if present.
    We keep this minimal for MVP; it's a proof that we're build-derived.

    CMake usually writes replies under:
      build/.cmake/api/v1/reply/index-*.json
    """
    reply_dir = build_dir / ".cmake" / "api" / "v1" / "reply"
    if not reply_dir.is_dir():
        return None

    indexes = sorted(reply_dir.glob("index-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not indexes:
        return None

    try:
        return json.loads(indexes[0].read_text(encoding="utf-8"))
    except Exception:
        return None


def run_scan(build_dir: str, out_dir: str, project_name: str | None, verbose: bool) -> int:
    bdir = Path(build_dir).expanduser().resolve()
    odir = Path(out_dir).expanduser().resolve()

    if not bdir.exists() or not bdir.is_dir():
        print(f"ERROR: build dir not found: {bdir}")
        return 1

    odir.mkdir(parents=True, exist_ok=True)
    _log(verbose, f"[depscope] build_dir={bdir}")
    _log(verbose, f"[depscope] out_dir={odir}")

    file_api = _detect_cmake_file_api_reply(bdir)
    _log(verbose, f"[depscope] CMake File API detected: {bool(file_api)}")

    # Minimal "graph" placeholder for MVP
    context: dict[str, Any] = {
        "project": project_name or bdir.name,
        "build_dir": str(bdir),
        "file_api_present": bool(file_api),
        "notes": [
            "MVP placeholder outputs. Real graph parsing is coming next (CMake File API).",
        ],
    }

    report_html = render_report_html(context)
    (odir / "report.html").write_text(report_html, encoding="utf-8")
    _log(verbose, f"[depscope] wrote {odir / 'report.html'}")

    sbom = build_cyclonedx_sbom(context)
    (odir / "sbom.cdx.json").write_text(json.dumps(sbom, indent=2), encoding="utf-8")
    _log(verbose, f"[depscope] wrote {odir / 'sbom.cdx.json'}")

    print(f"OK: wrote {odir / 'report.html'} and {odir / 'sbom.cdx.json'}")
    return 0
