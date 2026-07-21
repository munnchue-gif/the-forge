"""
Forge-NG — AuditLedger: the tamper-evident memory of the door.

WHY (M4 observer review, missing #1)
──────────────────────────────────────────────────────────────────────────────
The Gate already stops REPLAY (you can't reuse a token). But it kept no
forensic trail: after an incident there was no way to prove what the door
decided, in what order, or that the record wasn't edited afterward. This organ
fixes that.

WHAT IT IS
──────────────────────────────────────────────────────────────────────────────
An append-only, hash-CHAINED log. Every entry carries the hash of the entry
before it, so the whole log is a chain:

    entry_hash[i] = sha256( prev_hash | seq | ts | kind | audit_id | detail )

Change ANY past entry and every hash after it breaks — tampering is evident on
a single verify() walk. Each entry is also HMAC-signed with the gate's key, so
an attacker can't recompute a valid chain without the secret. This is the same
construction certificate-transparency / blockchain logs use, kept thin.

HOW IT BONDS TO THE GATE
──────────────────────────────────────────────────────────────────────────────
The gate emits events already (`emit(topic, payload)`). The ledger is just a
sink for those events — bind `ledger.record` as (or alongside) the gate's emit
hook and every allow/deny is chained automatically. The gate stays pure; the
ledger stays a passive recorder. Bonded, not fused.
"""

from __future__ import annotations

import hmac
import json
import time
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

GENESIS = "0" * 64


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    seq: int
    ts: float
    topic: str                 # e.g. "gate.allowed" / "gate.denied"
    payload: dict[str, Any]
    prev_hash: str
    entry_hash: str
    signature: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq, "ts": self.ts, "topic": self.topic,
            "payload": self.payload, "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash, "signature": self.signature,
        }


class AuditLedger:
    """
    Append-only hash-chained audit log. In-memory here; a real deployment flushes
    each entry to an fsync'd append-only file (the interface is identical — the
    fabric doesn't care where the bytes land).
    """

    __slots__ = ("_key", "_entries", "_head")

    def __init__(self, secret: bytes) -> None:
        self._key = secret
        self._entries: list[LedgerEntry] = []
        self._head = GENESIS

    # ── core hash + sign ─────────────────────────────────────────────────────

    def _digest(self, seq: int, ts: float, topic: str,
                payload: dict[str, Any], prev_hash: str) -> str:
        body = json.dumps(
            {"seq": seq, "ts": ts, "topic": topic,
             "payload": payload, "prev": prev_hash},
            separators=(",", ":"), sort_keys=True,
        )
        return sha256(body.encode()).hexdigest()

    def _sign(self, entry_hash: str) -> str:
        return hmac.new(self._key, entry_hash.encode(), sha256).hexdigest()

    # ── append (the only write) ──────────────────────────────────────────────

    def record(self, topic: str, payload: dict[str, Any] | None = None,
               *, ts: float | None = None) -> LedgerEntry:
        """Append one event. Chains to the current head and signs it. This is
        the method you bind to the gate's emit hook."""
        seq = len(self._entries)
        t = ts if ts is not None else time.time()
        pl = dict(payload or {})
        entry_hash = self._digest(seq, t, topic, pl, self._head)
        entry = LedgerEntry(
            seq=seq, ts=t, topic=topic, payload=pl,
            prev_hash=self._head, entry_hash=entry_hash,
            signature=self._sign(entry_hash),
        )
        self._entries.append(entry)
        self._head = entry_hash
        return entry

    # ── verify (tamper detection) ────────────────────────────────────────────

    def verify(self) -> tuple[bool, int | None]:
        """
        Walk the whole chain. Returns (ok, first_bad_seq). ok=True means every
        entry's hash matches its recomputation AND its signature is valid AND it
        correctly links to the previous entry. A single edited/inserted/removed
        entry makes ok=False and points at the first broken seq.
        """
        prev = GENESIS
        for i, e in enumerate(self._entries):
            if e.seq != i:
                return False, i
            if e.prev_hash != prev:
                return False, i
            recomputed = self._digest(e.seq, e.ts, e.topic, e.payload, e.prev_hash)
            if not hmac.compare_digest(recomputed, e.entry_hash):
                return False, i
            if not hmac.compare_digest(self._sign(e.entry_hash), e.signature):
                return False, i
            prev = e.entry_hash
        return True, None

    # ── introspection ────────────────────────────────────────────────────────

    def head(self) -> str:
        return self._head

    def size(self) -> int:
        return len(self._entries)

    def tail(self, n: int = 20) -> list[dict[str, Any]]:
        return [e.as_dict() for e in self._entries[-n:]]

    def entries(self) -> list[LedgerEntry]:
        return list(self._entries)

    def entries_since(self, seq: int = 0) -> list[dict[str, Any]]:
        """JSON-safe audit entries from `seq` onward — for the App /ledger view.
        Read-only; returns dicts, not the frozen entries, so nothing downstream
        can mutate the chain."""
        if seq < 0:
            seq = 0
        return [e.as_dict() for e in self._entries[seq:]]
