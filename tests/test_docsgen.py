from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from paperfig.docsgen.drift import run_docs_regeneration


class DocsGenTests(unittest.TestCase):
    def test_docs_check_detects_drift_and_regenerate_fixes_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs = root / "README.md"
            docs.write_text(
                "# Title\n\n"
                "## CLI Usage\n"
                "<!-- AUTO-GEN:START demo-block -->\n"
                "stale\n"
                "<!-- AUTO-GEN:END demo-block -->\n",
                encoding="utf-8",
            )

            manifest = {
                "documents": [
                    {
                        "path": "README.md",
                        "mode": "hybrid",
                        "required_sections": ["## CLI Usage"],
                    }
                ],
                "auto_blocks": {
                    "demo-block": {
                        "type": "static",
                        "content": "fresh-content",
                    }
                },
            }
            manifest_path = root / "docs_manifest.yaml"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            check_report = run_docs_regeneration(
                manifest_path=manifest_path,
                check_only=True,
                repo_root=root,
            )
            self.assertTrue(check_report["drift_detected"])

            apply_report = run_docs_regeneration(
                manifest_path=manifest_path,
                check_only=False,
                repo_root=root,
            )
            self.assertTrue(apply_report["drift_detected"])
            self.assertIn("fresh-content", docs.read_text(encoding="utf-8"))

            clean_report = run_docs_regeneration(
                manifest_path=manifest_path,
                check_only=True,
                repo_root=root,
            )
            self.assertFalse(clean_report["drift_detected"])


if __name__ == "__main__":
    unittest.main()
