"""
fabric/types.py — Shared type definitions for The Forge fabric layer.
Extracted here to break the circular import between:
  fabric.overseer  <->  fabric.bind.openvino_seat
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Finding:
    id: str
    organ: str
    severity: str  # 'info', 'warn', 'error', 'critical'
    title: str
    detail: str
    timestamp: float = field(default_factory=__import__('time').time)
    metadata: Dict[str, Any] = field(default_factory=dict)

def make_finding(
    *,
    id: str = "unknown",
    organ: str = "fabric",
    severity: str | int = "1",
    title: str = "finding",
    detail: str = "",
    section_id: str | None = None,
    kind: str | None = None,
    **_extra: Any,
) -> "Finding":
    """Map old (section_id/kind/int severity) and new fields to live Finding."""
    if section_id is not None:
        id = str(section_id)
    if kind is not None:
        title = str(kind)
        if organ == "fabric":
            organ = str(kind)
    if isinstance(severity, int):
        # Map 0..3 → live labels used by this tree
        severity = {0: "info", 1: "info", 2: "warn", 3: "critical"}.get(
            max(0, min(3, severity)), "info"
        )
    return Finding(
        id=str(id),
        organ=str(organ),
        severity=str(severity),
        title=str(title),
        detail=str(detail),
    )

