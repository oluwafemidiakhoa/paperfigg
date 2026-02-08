from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any


@dataclass
class SourceSpan:
    section: str
    start: int
    end: int
    quote: str


@dataclass
class ElementTrace:
    element_id: str
    element_type: str
    label: str
    source_spans: List[SourceSpan] = field(default_factory=list)


@dataclass
class TraceabilityRecord:
    figure_id: str
    elements: List[ElementTrace] = field(default_factory=list)

    def validate(self) -> None:
        for element in self.elements:
            if not element.source_spans:
                raise ValueError(f"Traceability missing for element {element.element_id}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_traceability(figure_id: str, elements: List[Dict[str, Any]]) -> TraceabilityRecord:
    element_traces: List[ElementTrace] = []
    for element in elements:
        spans = [SourceSpan(**span) for span in element.get("source_spans", [])]
        element_traces.append(
            ElementTrace(
                element_id=str(element.get("id")),
                element_type=str(element.get("type")),
                label=str(element.get("label", "")),
                source_spans=spans,
            )
        )
    record = TraceabilityRecord(figure_id=figure_id, elements=element_traces)
    record.validate()
    return record


def write_traceability(path: str, record: TraceabilityRecord) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(record.to_dict(), handle, indent=2)
