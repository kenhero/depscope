from __future__ import annotations

import html
from datetime import datetime
from typing import Any
from pathlib import Path
from html import escape
from .cmake_file_api import BuildGraph


def render_report_html(context: dict[str, Any]) -> str:
    project = html.escape(str(context.get("project", "unknown")))
    build_dir = html.escape(str(context.get("build_dir", "")))
    file_api_present = "yes" if context.get("file_api_present") else "no"
    generated = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")

    notes = context.get("notes", [])
    notes_html = "".join(f"<li>{html.escape(str(n))}</li>" for n in notes)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Depscope Report - {project}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; margin: 24px; }}
    .card {{ border: 1px solid #ddd; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    code {{ background: #f6f8fa; padding: 2px 6px; border-radius: 6px; }}
    h1 {{ margin-top: 0; }}
  </style>
</head>
<body>
  <h1>Depscope Report</h1>

  <div class="card">
    <div><strong>Project:</strong> {project}</div>
    <div><strong>Build dir:</strong> <code>{build_dir}</code></div>
    <div><strong>CMake File API present:</strong> {file_api_present}</div>
    <div><strong>Generated:</strong> {generated}</div>
  </div>

  <div class="card">
    <h2>Status</h2>
    <p>This is an early MVP placeholder report. Next iterations will parse the build graph and show:</p>
    <ul>
      <li>Targets and transitive dependencies</li>
      <li>Duplicate libraries and version drift</li>
      <li>Origin paths and attribution</li>
    </ul>
  </div>

  <div class="card">
    <h2>Notes</h2>
    <ul>
      {notes_html}
    </ul>
  </div>
</body>
</html>
"""

def write_report_html(graph: BuildGraph, out_path: Path) -> None:
    rows = []
    for t in graph.targets:
        arts = "<br/>".join(escape(a) for a in t.artifacts) if t.artifacts else "-"
        rows.append(
            f"<tr><td>{escape(t.name)}</td><td>{escape(t.type)}</td><td>{len(t.dep_ids)}</td><td>{arts}</td></tr>"
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Depscope Report</title>
<style>
body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
th {{ background: #f6f6f6; text-align: left; }}
.small {{ color: #666; font-size: 12px; }}
</style>
</head>
<body>
<h1>Depscope Report</h1>
<div class="small">build_dir: {escape(str(graph.build_dir))} | generator: {escape(str(graph.generator or "-"))}</div>

<h2>Targets</h2>
<table>
  <thead>
    <tr><th>Name</th><th>Type</th><th>Deps</th><th>Artifacts</th></tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")