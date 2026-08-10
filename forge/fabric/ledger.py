from __future__ import annotations
import time
import logging
from typing import Any, List, Optional, Tuple

logger = logging.getLogger("forge_ng.ledger")


class LedgerEntry:
    __slots__ = ("timestamp", "topic", "payload")

    def __init__(self, timestamp: float, topic: str, payload: dict) -> None:
        self.timestamp = timestamp
        self.topic = topic
        self.payload = payload

    def __repr__(self) -> str:
        return f"LedgerEntry({self.topic!r}, {self.timestamp:.3f})"


class AuditLedger:
    def __init__(self, secret: bytes = b"") -> None:
        self.secret = secret
        self._entries: List[LedgerEntry] = []
        self.stats: Any = None

    def record(self, topic: str, payload: dict) -> None:
        entry = LedgerEntry(time.time(), topic, payload)
        self._entries.append(entry)
        if self.stats is not None and hasattr(self.stats, "entries"):
            self.stats.entries += 1

    async def entries_since(self, since: float) -> List[LedgerEntry]:
        return [e for e in self._entries if e.timestamp > since]

    async def verify(self) -> Tuple[bool, list]:
        return True, []

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def head(self) -> Optional[LedgerEntry]:
        return self._entries[-1] if self._entries else None

    def close(self) -> None:
        pass
