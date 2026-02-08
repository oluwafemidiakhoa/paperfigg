from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class PaperSection:
    name: str
    text: str
    start: int
    end: int


@dataclass
class PaperContent:
    source_path: str
    full_text: str
    sections: Dict[str, PaperSection]


@dataclass
class FigurePlan:
    figure_id: str
    title: str
    kind: str
    order: int
    abstraction_level: str
    description: str
    justification: str
    template_id: str = ""
    source_spans: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FigureCandidate:
    figure_id: str
    svg_path: str
    element_metadata_path: str
    traceability_path: str


@dataclass
class CritiqueReport:
    figure_id: str
    score: float
    threshold: float
    quality_dimensions: Dict[str, float]
    dimension_threshold: float
    failed_dimensions: List[str]
    issues: List[str]
    recommendations: List[str]
    passed: bool


@dataclass
class ArchitectureCritiqueFinding:
    finding_id: str
    severity: str
    title: str
    description: str
    evidence: str
    suggestion: str


@dataclass
class ArchitectureCritiqueReport:
    run_id: str
    block_severity: str
    findings: List[ArchitectureCritiqueFinding] = field(default_factory=list)
    blocked: bool = False
    summary: str = ""
    generated_at: str = ""


@dataclass
class ReproAuditCheck:
    check_id: str
    description: str
    required: bool
    passed: bool
    severity: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReproAuditReport:
    run_id: str
    mode: str
    checks: List[ReproAuditCheck] = field(default_factory=list)
    passed: bool = True
    summary: str = ""
    generated_at: str = ""
    environment: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowTemplate:
    template_id: str
    title: str
    kind: str
    order_hint: int
    required_sections: List[str]
    trigger_rules: List[Dict[str, Any]]
    element_blueprint: Dict[str, Any]
    caption_style: str
    traceability_requirements: Dict[str, Any]
    critique_focus: List[str]


@dataclass
class FlowTemplateCatalog:
    pack_id: str
    templates: List[FlowTemplate] = field(default_factory=list)
