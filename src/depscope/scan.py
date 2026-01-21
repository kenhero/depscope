from __future__ import annotations

from pathlib import Path

from .cmake_file_api import parse_build_graph
from .report_html import write_report_html
from .sbom_cyclonedx import write_sbom_cyclonedx


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

    if verbose:
        print(f"[depscope] build_dir={bdir}")
        print(f"[depscope] out_dir={odir}")

    try:
        graph = parse_build_graph(bdir)
    except Exception as e:
        print(f"ERROR: failed to parse CMake File API: {e}")
        return 2

    report_path = odir / "report.html"
    sbom_path = odir / "sbom.cdx.json"

    write_report_html(graph, report_path)
    write_sbom_cyclonedx(graph, sbom_path)

    if verbose:
        print(f"[depscope] wrote {report_path}")
        print(f"[depscope] wrote {sbom_path}")

    print(f"OK: wrote {report_path} and {sbom_path}")
    return 0