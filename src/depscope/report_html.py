from __future__ import annotations

import html
from datetime import datetime
from typing import Any


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
