from __future__ import annotations

from typing import List


def get_command_catalog() -> List[str]:
    return [
        "generate",
        "rerun",
        "diff",
        "critique",
        "export",
        "doctor",
        "inspect",
        "docs regenerate",
        "docs check",
        "templates list",
        "templates validate",
        "templates lint",
        "critique-architecture",
        "audit",
        "lab init",
        "lab propose",
        "lab run",
        "lab review",
        "lab status",
    ]
