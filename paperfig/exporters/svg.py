from __future__ import annotations

import shutil
from pathlib import Path


def export_svg(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
