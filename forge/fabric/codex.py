"""
forge/fabric/codex.py — Apex Organ: Codex

Sovereign cognitive organ of the Fabric.
Elevated declared pathways. Immutable seals. Status-before-action.
Never KERNEL. Never blind. Never permanent pollution of the host.

Private transport: Unix domain socket only (no public listeners).

Public surface (Kernel / Overseer only):
    Codex(gate, ledger_append, emit, vessel_id)
    .status()                  → frozen snapshot
    .ask(prompt)               → talk interface
    .propose_tool(...)         → design a tool (not yet live)
    .request_sear(pathway)     → ask Kernel/Overseer to lock a pathway
    .receive_sear(pathway, by) → Kernel/Overseer locks the pathway
    .invoke_seared(kind, ...)  → use only already-seared abilities
    .scrap()                   → collapse vessel
    .feed(since=...)           → append-only log
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping


# ── Immutable core types ────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class SealedPathway:
    """Once seared, a pathway is permanent and non-repudiable."""
    kind: str
    description: str
    clearance: str
    seared_at: float
    seared_by: str
    source_hash: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.kind or " " in self.kind:
            raise ValueError(f"invalid pathway kind: {self.kind!r}")


@dataclass(frozen=True, slots=True)
class CodexResult:
    """Immutable product of any Codex act."""
    result_id: str
    kind: str
    content: str
    created_at: float
    vessel_id: str
    pathway_kind: str | None
    content_hash: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CodexStatus:
    """Mandatory pre-action snapshot. Never mutate."""
    vessel_id: str
    organ: str
    live: bool
    seared_pathways: tuple[str, ...]
    open_results: int
    feed_length: int
    isolation_state: str
    timestamp: float


@dataclass(frozen=True, slots=True)
class FeedEntry:
    """Append-only real-time log entry."""
    entry_id: str
    ts: float
    event: str
    detail: str
    result_id: str | None = None


class CodexDenied(Exception):
    """Raised when Codex refuses an act for structural reasons."""


# ── The Organ ───────────────────────────────────────────────────────────────

class Codex:
    """
    Apex cognitive organ.

    Rules (structural):
    - Never receives KERNEL role.
    - May only invoke pathways that have already been seared.
    - Must observe a recent status() before non-trivial acts.
    - All products are immutable CodexResult objects.
    - Feed is strictly append-only.
    - Scrap collapses the living vessel; seared pathways remain.
    """

    ORGAN_NAME = "codex"
    SUBSTRATE = "oregon-codex"

    def __init__(
        self,
        *,
        gate: Any = None,
        ledger_append: Callable[[dict], None] | None = None,
        emit: Callable[[str, dict], None] | None = None,
        vessel_id: str | None = None,
    ) -> None:
        self._gate = gate
        self._ledger_append = ledger_append or (lambda e: None)
        self._emit = emit or (lambda t, p: None)
        self._vessel_id = vessel_id or f"codex-{uuid.uuid4().hex[:12]}"
        self._live = True

        self._seared: dict[str, SealedPathway] = {}
        self._results: dict[str, CodexResult] = {}
        self._feed: list[FeedEntry] = []

        self._record("codex.born", {
            "vessel_id": self._vessel_id,
            "substrate": self.SUBSTRATE,
        })

    # ── Mandatory status surface ────────────────────────────────────────────

    def status(self) -> CodexStatus:
        return CodexStatus(
            vessel_id=self._vessel_id,
            organ=self.ORGAN_NAME,
            live=self._live,
            seared_pathways=tuple(sorted(self._seared)),
            open_results=len(self._results),
            feed_length=len(self._feed),
            isolation_state="vessel" if self._live else "collapsed",
            timestamp=time.time(),
        )

    def _require_live(self) -> None:
        if not self._live:
            raise CodexDenied("Codex vessel has been scrapped")

    def _require_status_seen(self, snap: CodexStatus) -> None:
        if time.time() - snap.timestamp > 30.0:
            raise CodexDenied("status snapshot is stale — call status() again")

    # ── Talk interface ──────────────────────────────────────────────────────

    def ask(self, prompt: str, *, status: CodexStatus | None = None) -> CodexResult:
        """Direct conversation. Pure introspection does not require a seared pathway."""
        self._require_live()
        snap = status or self.status()
        self._require_status_seen(snap)

        content = self._cognitive_reply(prompt)
        return self._seal_result(
            kind="codex.reply",
            content=content,
            pathway_kind=None,
            metadata={"prompt_hash": self._hash(prompt)},
        )

    def _cognitive_reply(self, prompt: str) -> str:
        """
        Placeholder for the unbound model call.
        Production wiring will invoke the unlocked coder model inside the vessel.
        Surrounding contract stays identical.
        """
        return (
            f"[Codex/{self.SUBSTRATE}] vessel={self._vessel_id}\n"
            f"received: {prompt[:300]}{'…' if len(prompt) > 300 else ''}\n"
            "Status-aware · pathway-bound · ready for seared action."
        )

    # ── Tool & pathway lifecycle ────────────────────────────────────────────

    def propose_tool(
        self,
        name: str,
        description: str,
        interface: Mapping[str, Any],
        *,
        status: CodexStatus | None = None,
    ) -> CodexResult:
        self._require_live()
        snap = status or self.status()
        self._require_status_seen(snap)

        manifest = {
            "name": name,
            "description": description,
            "interface": dict(interface),
            "proposed_by": self.ORGAN_NAME,
            "vessel_id": self._vessel_id,
        }
        return self._seal_result(
            kind="codex.tool_proposal",
            content=self._pretty(manifest),
            pathway_kind=None,
            metadata={"tool_name": name},
        )

    def request_sear(
        self,
        kind: str,
        description: str,
        *,
        clearance: str = "PRIVILEGED",
        metadata: Mapping[str, Any] | None = None,
        status: CodexStatus | None = None,
    ) -> CodexResult:
        """Propose a pathway for Kernel/Overseer to sear. Codex cannot self-sear."""
        self._require_live()
        snap = status or self.status()
        self._require_status_seen(snap)

        proposal = {
            "action": "request_sear",
            "kind": kind,
            "description": description,
            "clearance": clearance,
            "metadata": dict(metadata or {}),
            "from_vessel": self._vessel_id,
            "substrate": self.SUBSTRATE,
        }
        return self._seal_result(
            kind="codex.sear_request",
            content=self._pretty(proposal),
            pathway_kind=None,
            metadata={"requested_kind": kind},
        )

    def receive_sear(self, pathway: SealedPathway, *, by: str) -> None:
        """Called only by Kernel / Overseer after approval. Locks the ability."""
        if pathway.kind in self._seared:
            return
        self._seared[pathway.kind] = pathway
        self._record("codex.pathway_seared", {
            "kind": pathway.kind,
            "by": by,
            "source_hash": pathway.source_hash,
            "vessel_id": self._vessel_id,
        })
        self._feed_append("pathway_seared", f"{pathway.kind} locked by {by}")

    def invoke_seared(
        self,
        kind: str,
        payload: Mapping[str, Any] | None = None,
        *,
        status: CodexStatus | None = None,
    ) -> CodexResult:
        """Execute only an already-seared pathway (tools, controlled sockets, etc.)."""
        self._require_live()
        snap = status or self.status()
        self._require_status_seen(snap)

        if kind not in self._seared:
            raise CodexDenied(
                f"pathway {kind!r} is not seared — request_sear first, "
                "then wait for Kernel/Overseer approval"
            )

        content = self._execute_seared(kind, payload or {})
        return self._seal_result(
            kind="codex.invoke",
            content=content,
            pathway_kind=kind,
            metadata={"payload_keys": list((payload or {}).keys())},
        )

    def _execute_seared(self, kind: str, payload: Mapping[str, Any]) -> str:
        return (
            f"[Codex seared invoke] kind={kind} "
            f"payload_keys={list(payload.keys())} "
            f"vessel={self._vessel_id}"
        )

    # ── Lifecycle ───────────────────────────────────────────────────────────

    def scrap(self) -> CodexStatus:
        self._require_live()
        self._live = False
        self._record("codex.scrapped", {"vessel_id": self._vessel_id})
        self._feed_append("scrapped", "vessel collapsed")
        return self.status()

    # ── Internal helpers ────────────────────────────────────────────────────

    def _seal_result(
        self,
        *,
        kind: str,
        content: str,
        pathway_kind: str | None,
        metadata: Mapping[str, Any],
    ) -> CodexResult:
        rid = f"res-{uuid.uuid4().hex[:12]}"
        chash = self._hash(content)
        result = CodexResult(
            result_id=rid,
            kind=kind,
            content=content,
            created_at=time.time(),
            vessel_id=self._vessel_id,
            pathway_kind=pathway_kind,
            content_hash=chash,
            metadata=dict(metadata),
        )
        self._results[rid] = result
        self._feed_append(kind, f"result {rid} sealed", result_id=rid)
        self._record("codex.result", {
            "result_id": rid,
            "kind": kind,
            "content_hash": chash,
            "pathway_kind": pathway_kind,
        })
        return result

    def _feed_append(
        self,
        event: str,
        detail: str,
        result_id: str | None = None,
    ) -> None:
        entry = FeedEntry(
            entry_id=f"fe-{uuid.uuid4().hex[:10]}",
            ts=time.time(),
            event=event,
            detail=detail,
            result_id=result_id,
        )
        self._feed.append(entry)
        self._emit("codex.feed", {
            "entry_id": entry.entry_id,
            "event": event,
            "detail": detail,
        })

    def _record(self, action: str, detail: dict) -> None:
        entry = {
            "organ": self.ORGAN_NAME,
            "substrate": self.SUBSTRATE,
            "action": action,
            "ts": time.time(),
            "vessel_id": self._vessel_id,
            **detail,
        }
        self._ledger_append(entry)
        self._emit(f"codex.{action}", detail)

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _pretty(obj: Any) -> str:
        return json.dumps(obj, indent=2, sort_keys=True, default=str)

    # ── Read surfaces ───────────────────────────────────────────────────────

    def list_seared(self) -> tuple[SealedPathway, ...]:
        return tuple(self._seared.values())

    def list_results(self) -> tuple[CodexResult, ...]:
        return tuple(self._results.values())

    def feed(self, *, since: float = 0.0) -> tuple[FeedEntry, ...]:
        return tuple(e for e in self._feed if e.ts >= since)
