from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from paperfig.command_catalog import get_command_catalog
from paperfig.templates.loader import load_template_catalog


AUTO_BLOCK_RE = re.compile(
    r"<!--\s*AUTO-GEN:START\s+(?P<block_id>[A-Za-z0-9_\-]+)\s*-->"
    r"(?P<body>.*?)"
    r"<!--\s*AUTO-GEN:END\s+(?P=block_id)\s*-->",
    re.DOTALL,
)


def render_auto_block(block_id: str, block_config: Dict[str, object], repo_root: Path) -> str:
    block_type = str(block_config.get("type", ""))

    if block_type == "cli_commands":
        commands = get_command_catalog()
        return "\n" + "\n".join(f"- `paperfig {command}`" for command in commands) + "\n"

    if block_type == "flow_template_catalog":
        template_dir = repo_root / str(block_config.get("template_dir", "paperfig/templates/flows"))
        pack_id = str(block_config.get("pack_id", "expanded_v1"))
        catalog = load_template_catalog(template_dir=template_dir, pack_id=pack_id)
        lines = [f"- `{tmpl.template_id}` ({tmpl.kind})" for tmpl in catalog.templates]
        return "\n" + "\n".join(lines) + "\n"

    if block_type == "static":
        content = str(block_config.get("content", ""))
        return "\n" + content.strip("\n") + "\n"

    raise RuntimeError(f"Unknown auto block type for '{block_id}': {block_type}")


def render_hybrid_document(
    text: str,
    auto_blocks: Dict[str, Dict[str, object]],
    repo_root: Path,
) -> Tuple[str, List[str], List[str]]:
    rendered_blocks: List[str] = []
    missing_block_configs: List[str] = []

    def _replace(match: re.Match[str]) -> str:
        block_id = match.group("block_id")
        block_config = auto_blocks.get(block_id)
        if not isinstance(block_config, dict):
            missing_block_configs.append(block_id)
            return match.group(0)

        rendered = render_auto_block(block_id, block_config, repo_root)
        rendered_blocks.append(block_id)
        return f"<!-- AUTO-GEN:START {block_id} -->{rendered}<!-- AUTO-GEN:END {block_id} -->"

    rendered_text = AUTO_BLOCK_RE.sub(_replace, text)
    return rendered_text, rendered_blocks, missing_block_configs
