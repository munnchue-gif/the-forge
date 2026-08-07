from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("forge_ng.ledger")

@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """A single entry in the ledger."""
    timestamp: float
    topic: str
    payload: dict[str, Any]

@dataclass
class AuditLedger:
    """
    The ledger is responsible for recording all decisions made by the gate and
    other components of the system. It provides a way to audit and review these
    decisions.
    """

    _entries: List[LedgerEntry] = field(default_factory=list)
    stats: Any = None  # Assuming this is initialized elsewhere

    async def record(self, topic: str, payload: dict[str, Any]) -> None:
        """Record a ledger entry."""
        entry = LedgerEntry(timestamp=time.time(), topic=topic, payload=payload)
        self._entries.append(entry)
        self.stats.entries += 1
        await self._flush()

    async def _flush(self) -> None:
        """Flush the entries to persistent storage (if needed)."""
        # Placeholder for actual flushing logic
        pass

    async def entries_since(self, since: float) -> List[LedgerEntry]:
        """Retrieve entries recorded after a certain timestamp."""
        return [entry for entry in self._entries if entry.timestamp > since]

    async def verify(self) -> Tuple[bool, Optional[str]]:
        """Verify the integrity of the ledger."""
        # Placeholder for actual verification logic
        return True, None

    @property
    def size(self) -> int:
        """Return the number of entries in the ledger."""
        return len(self._entries)

    @property
    def head(self) -> Optional[LedgerEntry]:
        """Return the most recent entry in the ledger."""
        if self._entries:
            return self._entries[-1]
        return None

    async def close(self) -> None:
        """Close the ledger and perform any necessary cleanup."""
        await self._flush()
