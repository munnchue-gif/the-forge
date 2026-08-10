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
