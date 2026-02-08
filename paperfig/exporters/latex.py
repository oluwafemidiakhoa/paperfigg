from __future__ import annotations

from pathlib import Path


def export_latex(figure_id: str, svg_filename: str, caption: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    snippet = (
        "\\begin{figure}[t]\n"
        "  \\centering\n"
        f"  \\includegraphics[width=\\linewidth]{{{svg_filename}}}\n"
        f"  \\caption{{{caption}}}\n"
        f"  \\label{{fig:{figure_id}}}\n"
        "\\end{figure}\n"
    )
    output_path.write_text(snippet, encoding="utf-8")
