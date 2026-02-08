#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
from paperfig.docsgen import run_docs_regeneration

report = run_docs_regeneration(
    manifest_path=Path("docs/docs_manifest.yaml"),
    check_only=True,
    repo_root=Path("."),
)

print(f"checked={len(report.get('documents', []))}")
print(f"drift_detected={report.get('drift_detected')}")

raise SystemExit(1 if report.get("drift_detected") else 0)
PY
