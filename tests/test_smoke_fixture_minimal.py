from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def test_smoke_fixture_minimal(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    fixture_src = repo_root / "tests" / "fixtures" / "minimal"
    assert fixture_src.is_dir(), f"Missing fixture dir: {fixture_src}"

    build_dir = tmp_path / "build"
    out_dir = tmp_path / "out"
    build_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # IMPORTANT: ask CMake File API to generate replies
    query_dir = build_dir / ".cmake" / "api" / "v1" / "query"
    query_dir.mkdir(parents=True, exist_ok=True)

    # Richiedi codemodel (e volendo toolchains/cache)
    (query_dir / "codemodel-v2").write_text("", encoding="utf-8")
    (query_dir / "cache-v2").write_text("", encoding="utf-8")


    # Build fixture (generates CMake File API replies)
    _run(["cmake", "-S", str(fixture_src), "-B", str(build_dir)], cwd=repo_root)
    _run(["cmake", "--build", str(build_dir)], cwd=repo_root)

    # Run depscope via module (no reliance on console script)
    _run(
        [
            sys.executable,
            "-m",
            "depscope.cli",
            "scan",
            "--build-dir",
            str(build_dir),
            "--out",
            str(out_dir),
            "--verbose",
        ],
        cwd=repo_root,
    )

    report = out_dir / "report.html"
    sbom = out_dir / "sbom.cdx.json"

    assert report.exists() and report.stat().st_size > 0
    assert sbom.exists() and sbom.stat().st_size > 0

    html = report.read_text(encoding="utf-8")
    assert "<h1>Depscope Report</h1>" in html

    # JSON parseable
    data = json.loads(sbom.read_text(encoding="utf-8"))
    assert data.get("bomFormat") == "CycloneDX"
    assert "components" in data

    print("BUILD_DIR=", build_dir)
    print("OUT_DIR=", out_dir)
