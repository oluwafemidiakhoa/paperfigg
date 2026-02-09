from __future__ import annotations

from pathlib import Path


def export_png(svg_path: Path, png_path: Path) -> None:
    try:
        import cairosvg  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "cairosvg is required for PNG export. Run: paperfig doctor --fix png"
        ) from exc

    png_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), background_color="transparent")
