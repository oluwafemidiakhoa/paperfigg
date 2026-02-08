from __future__ import annotations

from typing import Dict, List

from paperfig.utils.types import FlowTemplate, PaperContent


def _section_has_text(paper: PaperContent, section_name: str) -> bool:
    section = paper.sections.get(section_name)
    return bool(section and section.text.strip())


def _rule_matches(rule: Dict[str, object], paper: PaperContent) -> bool:
    section_name = str(rule.get("section", ""))
    if not section_name:
        return True

    section = paper.sections.get(section_name)
    if not section:
        return False

    text = section.text.lower()
    keywords = rule.get("keywords", [])
    if not keywords:
        return True

    return any(str(keyword).lower() in text for keyword in keywords)


def select_templates(templates: List[FlowTemplate], paper: PaperContent) -> List[FlowTemplate]:
    selected: List[FlowTemplate] = []

    for template in templates:
        if any(not _section_has_text(paper, section) for section in template.required_sections):
            continue

        if any(not _rule_matches(rule, paper) for rule in template.trigger_rules):
            continue

        selected.append(template)

    selected.sort(key=lambda item: item.order_hint)
    return selected
