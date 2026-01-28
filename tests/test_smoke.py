import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_smoke_real_cmake_build(tmp_path: Path):
    """
    Smoke test:
    - runs `depscope scan` on a REAL CMake build dir
    - checks report.html exists
    - checks sbom.cdx.json exists and is valid JSON

    To enable this test, set:
      DEPSCOPE_TEST_BUILD_DIR=/absolute/path/to/cmake-build-xxx
    """

    build_dir = os.environ.get("DEPSCOPE_TEST_BUILD_DIR")
    if not build_dir:
        pytest.skip("DEPSCOPE_TEST_BUILD_DIR not set")

    build_dir = Path(build_dir).expanduser().resolve()
    if not build_dir.is_dir():
        pytest.skip(f"Build dir does not exist: {build_dir}")

    out_dir = tmp_path / "out"

    cmd = [
        sys.executable, "-m", "depscope.cli",
        "scan",
        "--build-dir",
        str(build_dir),
        "--out",
        str(out_dir),
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    report = out_dir / "report.html"
    sbom = out_dir / "sbom.cdx.json"

    assert report.exists(), "report.html not generated"
    assert sbom.exists(), "sbom.cdx.json not generated"

    # JSON must be parseable
    with sbom.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("bomFormat") == "CycloneDX"
    assert "components" in data
