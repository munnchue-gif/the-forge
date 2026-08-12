"""
forge/fabric/ledger.py — Tamper-evident AuditLedger for The Forge fabric.

DESIGN
──────
Every recorded entry is HMAC-SHA-256 signed over a deterministic canonical
form that includes the previous entry's HMAC tag (prev_hash).  Deletion,
insertion, or reordering of any entry breaks the chain; payload mutation
breaks the per-entry signature.  This gives two layers of tamper evidence:

    1. Per-entry integrity   — signature covers (seq, topic, payload, prev_hash)
    2. Chain integrity       — each entry's entry_hash is the prev_hash of the
                               next entry, so skipping or reordering breaks
                               the pointer.

Thread-safety
─────────────
A threading.Lock guards all writes and the full verify scan.  read-only
operations (size, head, entries) also hold the lock for snapshot consistency.

Key derivation
──────────────
The ledger derives its HMAC key from the supplied secret using a fixed
domain-separation label so it never shares a raw key with the Gate or any
other organ.

Public surface (what the living system and tests use)
─────────────────────────────────────────────────────
    GENESIS             — sentinel prev_hash for the first entry
    LedgerEntry         — frozen dataclass (seq, topic, payload, timestamp,
                          prev_hash, entry_hash, signature)
    AuditLedger(secret) — .record(topic, payload) → LedgerEntry
                        — .verify() → (ok: bool, bad: int | None)
                        — .size() → int
                        — .head() → LedgerEntry | None
                        — .entries() → list[LedgerEntry]
                        — .entries_since(since: float) → list[LedgerEntry]
                        — .close() → None
"""
from __future__ import annotations

import hmac
import json
import logging
import threading
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

logger = logging.getLogger("forge.ledger")

# ── Sentinel ──────────────────────────────────────────────────────────────────
GENESIS: str = "0" * 64
"""The prev_hash of the very first ledger entry — a fixed public constant."""

# ── Domain-separation label ───────────────────────────────────────────────────
_DOMAIN = b"forge.fabric.ledger.v1"


def _derive_key(secret: bytes) -> bytes:
    """Derive a ledger-specific HMAC key from the master secret."""
    return hmac.new(secret, _DOMAIN, sha256).digest()


# ── Entry ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LedgerEntry:
    """
    A single immutable audit record.

    seq         — monotonically increasing position (0-indexed)
    topic       — dotted-name event label, e.g. "gate.allowed"
    payload     — arbitrary JSON-serialisable mapping
    timestamp   — wall-clock seconds (float, from time.time())
    prev_hash   — entry_hash of the previous entry (GENESIS for seq==0)
    entry_hash  — HMAC-SHA-256(canonical(this entry), key)
    signature   — same as entry_hash (exposed separately for easy forgery tests)
    """
    seq: int
    topic: str
    payload: dict
    timestamp: float
    prev_hash: str
    entry_hash: str
    signature: str

    def __repr__(self) -> str:
        return (
            f"LedgerEntry(seq={self.seq}, topic={self.topic!r}, "
            f"ts={self.timestamp:.3f})"
        )


# ── Canonical serialisation ───────────────────────────────────────────────────

def _canonical(seq: int, topic: str, payload: dict,
               timestamp: float, prev_hash: str) -> bytes:
    """
    Deterministic canonical form that covers every security-relevant field.
    Using json.dumps with sort_keys=True and separators=(','':') gives a
    stable byte string regardless of insertion order in payload dicts.
    """
    doc = {
        "seq": seq,
        "topic": topic,
        "payload": payload,
        "timestamp": timestamp,
        "prev_hash": prev_hash,
    }
    return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign(key: bytes, seq: int, topic: str, payload: dict,
          timestamp: float, prev_hash: str) -> str:
    """Compute the HMAC-SHA-256 tag for a candidate entry. Returns hex string."""
    canon = _canonical(seq, topic, payload, timestamp, prev_hash)
    tag = hmac.new(key, canon, sha256).hexdigest()
    return tag


# ── AuditLedger ───────────────────────────────────────────────────────────────

class AuditLedger:
    """
    Thread-safe, tamper-evident audit log.

    Construct with a secret (bytes).  The secret may be the kernel's master
    FORGE_SECRET or any domain-separated derivative — the ledger re-derives its
    own key internally, so sharing the raw secret with the Gate is fine.

    Usage::

        ledger = AuditLedger(secret)
        entry  = ledger.record("gate.allowed", {"kind": "fabric.splice"})
        ok, bad = ledger.verify()   # bad is None on success, int index on fail
    """

    def __init__(self, secret: bytes = b"") -> None:
        self._key: bytes = _derive_key(secret) if secret else _derive_key(b"__no_secret__")
        self._entries: list[LedgerEntry] = []
        self._lock: threading.Lock = threading.Lock()

    # ── write ─────────────────────────────────────────────────────────────────

    def record(self, topic: str, payload: dict) -> LedgerEntry:
        """
        Append a new entry to the chain.  Thread-safe; returns the new entry.

        The returned LedgerEntry is immutable (frozen dataclass) and carries
        its HMAC tag so callers can inspect or log it immediately.
        """
        with self._lock:
            seq = len(self._entries)
            prev_hash = self._entries[-1].entry_hash if self._entries else GENESIS
            ts = time.time()
            tag = _sign(self._key, seq, topic, payload, ts, prev_hash)
            entry = LedgerEntry(
                seq=seq,
                topic=topic,
                payload=payload,
                timestamp=ts,
                prev_hash=prev_hash,
                entry_hash=tag,
                signature=tag,
            )
            self._entries.append(entry)
            logger.debug("ledger.record seq=%d topic=%s", seq, topic)
            return entry

    # ── verify ────────────────────────────────────────────────────────────────

    def verify(self) -> tuple[bool, Optional[int]]:
        """
        Walk the entire chain and verify:
          1. Each entry's signature matches its canonical form.
          2. Each entry's prev_hash matches the previous entry's entry_hash
             (or GENESIS for seq 0).

        Returns
        -------
        (True, None)     — chain is intact
        (False, int)     — first bad index (0-based seq position in the
                           *current* list, which may differ from entry.seq
                           if entries were deleted or reordered)
        """
        with self._lock:
            entries = list(self._entries)  # snapshot

        expected_prev = GENESIS
        for idx, e in enumerate(entries):
            # 1. Chain pointer
            if e.prev_hash != expected_prev:
                logger.warning("ledger chain broken at idx=%d seq=%d", idx, e.seq)
                return False, idx

            # 2. Signature
            expected_tag = _sign(
                self._key, e.seq, e.topic, e.payload, e.timestamp, e.prev_hash
            )
            if not hmac.compare_digest(e.signature, expected_tag):
                logger.warning("ledger signature invalid at idx=%d seq=%d", idx, e.seq)
                return False, idx

            expected_prev = e.entry_hash

        return True, None

    # ── read accessors ────────────────────────────────────────────────────────

    def size(self) -> int:
        """Return the number of recorded entries (thread-safe)."""
        with self._lock:
            return len(self._entries)

    def head(self) -> Optional[LedgerEntry]:
        """Return the most recent entry, or None if the ledger is empty."""
        with self._lock:
            return self._entries[-1] if self._entries else None

    def entries(self) -> list[LedgerEntry]:
        """Return a snapshot of all entries (oldest first)."""
        with self._lock:
            return list(self._entries)

    def entries_since(self, since: float) -> list[LedgerEntry]:
        """Return all entries whose timestamp is strictly after *since*."""
        with self._lock:
            return [e for e in self._entries if e.timestamp > since]

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def close(self) -> None:
        """No-op lifecycle hook (kept for interface compatibility)."""
