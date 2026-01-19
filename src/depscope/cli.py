import argparse
import sys
from .scan import run_scan


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="depscope",
        description="Depscope: build-derived SBOM and dependency reporting for C++/CMake.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan a CMake build directory and emit outputs.")
    scan.add_argument("--build-dir", required=True, help="Path to CMake build directory (e.g., build/).")
    scan.add_argument("--out", required=True, help="Output directory (e.g., out/).")
    scan.add_argument("--project-name", default=None, help="Override project name shown in outputs.")
    scan.add_argument("--verbose", action="store_true", help="Verbose logging.")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        return run_scan(
            build_dir=args.build_dir,
            out_dir=args.out,
            project_name=args.project_name,
            verbose=args.verbose,
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
