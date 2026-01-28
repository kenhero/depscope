from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TargetInfo:
    id: str
    name: str
    type: str
    artifacts: List[str]
    dep_ids: List[str]


@dataclass
class BuildGraph:
    generator: Optional[str]
    build_dir: str
    targets: List[TargetInfo]
    targets_by_id: Dict[str, TargetInfo]


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def detect_reply_dir(build_dir: Path) -> Optional[Path]:
    reply = build_dir / ".cmake" / "api" / "v1" / "reply"
    return reply if reply.is_dir() else None


def load_latest_index(reply_dir: Path) -> Path:
    indexes = sorted(reply_dir.glob("index-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not indexes:
        raise FileNotFoundError(f"No index-*.json found in {reply_dir}")
    return indexes[0]


def parse_build_graph(build_dir: Path) -> BuildGraph:
    reply_dir = detect_reply_dir(build_dir)
    if not reply_dir:
        raise FileNotFoundError(f"CMake File API reply dir not found under: {build_dir}")

    index_path = load_latest_index(reply_dir)
    index = _read_json(index_path)

    objects = index.get("objects", [])
    codemodel_obj = next((o for o in objects if o.get("kind") == "codemodel"), None)
    if not codemodel_obj or "jsonFile" not in codemodel_obj:
        raise RuntimeError("CMake File API index does not contain a codemodel object")

    codemodel_path = reply_dir / codemodel_obj["jsonFile"]
    codemodel = _read_json(codemodel_path)

    # generator è spesso nel campo "cmake" dell'index (dipende dalla versione), teniamolo best-effort
    generator = None
    cmake_info = index.get("cmake", {})
    if isinstance(cmake_info, dict):
        gen = cmake_info.get("generator")

        if isinstance(gen, str):
            generator = gen
        elif isinstance(gen, dict):
            generator = gen.get("name") or str(gen)

        # fallback best-effort (alcune varianti lo chiamano così)
        if generator is None:
            alt = cmake_info.get("cmakeGenerator")
            if isinstance(alt, str):
                generator = alt



    configs = codemodel.get("configurations", [])
    if not configs:
        raise RuntimeError("codemodel has no configurations[]")

    # MVP: prendiamo la prima config (es: Release)
    cfg0 = configs[0]
    target_refs = cfg0.get("targets", [])

    targets: List[TargetInfo] = []

    for tref in target_refs:
        tjson = tref.get("jsonFile")
        tid = tref.get("id", "")
        if not tjson:
            continue

        tpath = reply_dir / tjson
        tdata = _read_json(tpath)

        name = tdata.get("name", tpath.stem)
        ttype = tdata.get("type", "UNKNOWN")

        artifacts = []
        for a in tdata.get("artifacts", []) or []:
            p = a.get("path")
            if p:
                artifacts.append(p)

        dep_ids = []
        for d in tdata.get("dependencies", []) or []:
            did = d.get("id")
            if did:
                dep_ids.append(did)

        targets.append(TargetInfo(
            id=tid,
            name=name,
            type=ttype,
            artifacts=artifacts,
            dep_ids=dep_ids,
        ))

    targets_by_id = {t.id: t for t in targets if t.id}
    return BuildGraph(
        generator=generator,
        build_dir=str(build_dir),
        targets=targets,
        targets_by_id=targets_by_id,
    )
