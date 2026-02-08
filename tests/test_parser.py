from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from paperfig.utils.pdf_parser import parse_paper


class ParserTests(unittest.TestCase):
    def test_parse_markdown_extracts_required_sections(self) -> None:
        content = """
# Title

## 1 Methodology
We optimize with a staged pipeline.

## 2 System Architecture
The architecture uses parser, planner, generator, critic.

## 3 Results
We improve accuracy by 7 points.
""".strip()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "paper.md"
            path.write_text(content, encoding="utf-8")
            parsed = parse_paper(path)

        self.assertIn("methodology", parsed.sections)
        self.assertIn("system", parsed.sections)
        self.assertIn("results", parsed.sections)
        self.assertGreater(len(parsed.sections["methodology"].text), 0)
        self.assertGreater(len(parsed.sections["system"].text), 0)
        self.assertGreater(len(parsed.sections["results"].text), 0)


if __name__ == "__main__":
    unittest.main()
