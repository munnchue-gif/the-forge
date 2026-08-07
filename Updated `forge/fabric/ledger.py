"""
Forge-NG — Ledger: the auditing and logging layer.

The ledger is responsible for recording all decisions made by the gate and
other components of the system. It provides a way to audit and review these
decisions.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


logger = logging.getLogger("forge_ng.ledger")


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    timestamp: float
    topic: str
    payload: dict[str, Any]


class AuditLedger:
    """
    The ledger is responsible for recording all decisions made by the gate and
    other components of the system. It provides a way to audit and review these
    decisions.
    """

    def __init__(self) -> None:
        self._entries: List[LedgerEntry] = []
        self.stats = LedgerStats()

    async def record(self, topic: str, payload: dict[str, Any]) -> None:
        """Record a ledger entry."""
        entry = LedgerEntry(timestamp=time.time(), topic=topic, payload=payload)
        self._entries.append(entry)
        self.stats.entries += 1
        await self._flush()

    async def _flush(self) -> None:
        """Flush the ledger to disk or another storage system."""
        # Placeholder for actual flushing logic
        logger.info("Flushing %d entries", len(self._entries))
        self._entries = []


@dataclass
class LedgerStats:
    entries: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "entries": self.entries,
        }
