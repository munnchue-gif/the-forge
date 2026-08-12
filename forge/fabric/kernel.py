"""
forge/fabric/kernel.py — ForgeKernel: the boot sequence.

The moment the fabric stops being a pile of importable organs and becomes a
LIVING process.

WHY
───
Every organ was unit-tested in isolation, but nothing STOOD THEM UP together
in dependency order and ran a heartbeat.  That is the classic gap the original
Forge had (services that passed their own tests but were never wired into the
running server).  The Kernel closes it: one boot() that constructs the whole
body, bonds the brain, chains the audit log to the gate, and gives you a single
tick() heartbeat + a clean shutdown().

BOOT ORDER (dependency graph)
─────────────────────────────
  1. AuditLedger       — built first so it catches the very first gate event.
  2. FabricGate        — one door; emit hook wired to ledger.record so every
                         allow/deny is HMAC-chained from tick zero.
  3. SubstanceBus      — deaf-by-default nervous system.
  4. Overseer          — Watcher (omnipresent tap) + Commander (act via gate).
  5. VectorConduit     — spinal cord; bonds a Seat (brain) to the body.
  6. WrapStore         — recycling yard.
  7. Concoctinator     — isolated proving ground.
  8. EmbeddedTailor    — reshapes the fabric via the arena.
  9. BehavioralJudge   — evaluator available for arena judgments.

Nothing here fuses organs — it BONDS them.  Swap the seat, swap the
key_resolver, add policies/rules: all without touching this file's structure.

Public surface
──────────────
    ForgeKernel(secret, key_resolver?, seat?, judge?)
        .boot()              → self
        .tick()              → list[Finding]
        .shutdown()          → (ok: bool, bad: int | None)
        .health()            → dict
        .organ_names()       → list[str]

    boot_forge(secret, *, seat?, key_resolver?, judge?) → ForgeKernel
        Convenience one-liner that constructs + boots.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from fabric.ledger import AuditLedger
from fabric.gate import FabricGate
from fabric.bus import SubstanceBus
from fabric.overseer import Overseer
from fabric.types import Finding
from fabric.conduit import VectorConduit, NpuSeat, HeuristicSeat, VectorMemory
from fabric.wrap import WrapStore
from fabric.sandbox import Concoctinator
from fabric.tailor import EmbeddedTailor
from fabric.judge import BehavioralJudge
from fabric.capabilities import (
    SpawnCapability, MountCapability, EgressCapability, NpuEvalCapability,
    ConformCapability, SpliceCapability, ReclaimCapability,
)
from fabric import caveat as _caveat

logger = logging.getLogger("forge.kernel")


# ── Stats ──────────────────────────────────────────────────────────────────────

@dataclass
class KernelStats:
    booted: bool = False
    ticks: int = 0
    findings_total: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "booted": self.booted,
            "ticks": self.ticks,
            "findings_total": self.findings_total,
        }


# ── Kernel ─────────────────────────────────────────────────────────────────────

@dataclass
class ForgeKernel:
    """
    The living Forge.  Construct, then .boot(), then .tick() on a heartbeat,
    then .shutdown().  All organs are public attributes after boot so the
    bridge and couplers can reach them through the one gate.

    Parameters
    ----------
    secret       : master secret bytes — used to derive the ledger key and,
                   when key_resolver is None, the gate key as well.
                   Falls back to FORGE_SECRET env var (UTF-8 encoded) if not
                   supplied as a constructor argument.
    key_resolver : optional per-tenant key function for the Gate.
    seat         : optional NpuSeat; defaults to HeuristicSeat().
    judge        : optional BehavioralJudge; defaults to BehavioralJudge().
    """

    secret: bytes
    key_resolver: Optional[Callable[[str], bytes]] = None
    seat: Optional[NpuSeat] = None
    judge: Optional[BehavioralJudge] = None

    # populated by boot()
    ledger: Optional[AuditLedger] = field(default=None, init=False)
    gate: Optional[FabricGate] = field(default=None, init=False)
    bus: Optional[SubstanceBus] = field(default=None, init=False)
    overseer: Optional[Overseer] = field(default=None, init=False)
    conduit: Optional[VectorConduit] = field(default=None, init=False)
    wraps: Optional[WrapStore] = field(default=None, init=False)
    arena: Optional[Concoctinator] = field(default=None, init=False)
    tailor: Optional[EmbeddedTailor] = field(default=None, init=False)
    stats: KernelStats = field(default_factory=KernelStats, init=False)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _require_boot(self) -> None:
        if not self.stats.booted:
            raise RuntimeError("kernel not booted — call .boot() first")

    def organ_names(self) -> list[str]:
        return [
            name for name in (
                "ledger", "gate", "bus", "overseer",
                "conduit", "wraps", "arena", "tailor", "judge",
            )
            if getattr(self, name) is not None
        ]

    # ── BOOT ──────────────────────────────────────────────────────────────────

    def boot(self) -> "ForgeKernel":
        """
        Stand up every organ in dependency order and record the boot event to
        the audit chain.  Raises RuntimeError if called a second time.
        """
        if self.stats.booted:
            raise RuntimeError("kernel already booted")

        # 1. AuditLedger — built FIRST so it can record the first gate event.
        self.ledger = AuditLedger(self.secret)

        # 2. FabricGate — emit hook is a sync call to ledger.record so every
        #    decision is HMAC-chained immediately, without scheduling on an
        #    event loop.  Gate decisions must never block, so ledger.record()
        #    being sync (and lock-protected internally) is exactly right here.
        def _gate_emit(topic: str, payload: dict) -> None:
            try:
                self.ledger.record(topic, payload)  # type: ignore[union-attr]
            except Exception:
                # Ledger failures must never kill gate decisions (per objective).
                logger.exception("ledger.record failed during gate emit; ignoring")

        self.gate = FabricGate(
            secret=None if self.key_resolver else self.secret,
            key_resolver=self.key_resolver,
            emit=_gate_emit,
        )

        # 3. Nervous system.
        self.bus = SubstanceBus()

        # 4. Overseer — omnipresent watcher + gated commander.
        self.overseer = Overseer(self.bus, self.gate)

        # 5. Spinal cord — bond the brain.
        self.conduit = VectorConduit(
            self.overseer,
            self.gate,
            seat=self.seat or HeuristicSeat(),
            memory=VectorMemory(),
        )

        # 6. Recycling yard.
        self.wraps = WrapStore()

        # 7. Isolated proving ground — its OWN substance.
        self.arena = Concoctinator(secret=self.secret)

        # 8. Tailor — reshapes the fabric through the arena.
        self.tailor = EmbeddedTailor(self.arena)

        # 9. Behavioral judge available to callers.
        self.judge = self.judge or BehavioralJudge()

        self.stats.booted = True

        # Record the boot event as the first (or early) chained entry.
        self.ledger.record("kernel.boot", {"organs": self.organ_names()})
        logger.info("Forge kernel booted: %s", self.organ_names())
        return self

    # ── HEARTBEAT ─────────────────────────────────────────────────────────────

    def tick(self) -> list[Finding]:
        """
        One heartbeat: the conduit feeds telemetry up to the brain, the brain
        judges, and gate-signed corrections flow down.  Returns this tick's
        findings.
        """
        self._require_boot()
        findings = self.conduit.tick()
        self.stats.ticks += 1
        self.stats.findings_total += len(findings)
        return findings

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────

    def shutdown(self) -> tuple[bool, Optional[int]]:
        """
        Graceful stop.

        1. Records the shutdown event to the audit chain.
        2. Calls ledger.verify() — a tampered chain is a security event,
           surfaced here not swallowed.
        3. Closes the overseer watcher tap.
        4. Marks the kernel as not-booted.

        Returns
        -------
        (ok, bad) where ok is True if the audit chain is intact and bad is
        None on success or the first bad entry index (int) on failure.
        """
        self._require_boot()

        # Record shutdown before verifying so the entry is part of the chain
        # that gets checked.
        self.ledger.record("kernel.shutdown", {"ticks": self.stats.ticks})

        ok, bad = self.ledger.verify()

        try:
            self.overseer.watcher.close()
        except Exception:
            logger.exception("overseer close failed during shutdown")

        self.stats.booted = False
        logger.info(
            "Forge kernel shutdown. audit_intact=%s bad_index=%s", ok, bad
        )
        return ok, bad

    # ── HEALTH ────────────────────────────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """
        Snapshot of kernel vitals for the /health bridge endpoint.

        Returns a plain dict that is always safe to JSON-serialise.
        Keys guaranteed to be present:
            booted         (bool)
            ticks          (int)
            findings_total (int)
            audit_entries  (int)
            audit_head     (str | None)  — hex digest of the chain head
            bus_sections   (int)
        """
        self._require_boot()
        head = self.ledger.head()
        return {
            "booted": self.stats.booted,
            "ticks": self.stats.ticks,
            "findings_total": self.stats.findings_total,
            "audit_entries": self.ledger.size(),
            "audit_head": head.entry_hash if head else None,
            "bus_sections": len(self.bus.sections()),
        }

    # ── App-facing read accessors ──────────────────────────────────────────────

    def wrapstore_summary(self) -> list[dict[str, Any]]:
        """
        Read-only list of wraps in the recycling yard for the App /wraps view.
        Exposes fingerprints + shape, never the vectors themselves.
        """
        self._require_boot()
        out: list[dict[str, Any]] = []
        for wrap_sha, wrap in self.wraps._wraps.items():
            out.append({
                "wrap_sha": wrap_sha,
                "model_id": wrap.model_id,
                "tool_binds": list(wrap.tool_binds),
                "vector_ref": wrap.vector_ref,
                "sealed": True,
            })
        return out

    # Map an op string (contract §3) to the capability that expresses it.
    _EMPTY_SHA = "0" * 64
    _OP_CAPS: dict[str, Any] = {
        "hopper.spawn":   lambda t: SpawnCapability(
            capsule_id=t, script_sha=ForgeKernel._EMPTY_SHA,  # type: ignore[attr-defined]
            cpu_quota="50%", mem_limit="512m", network=False),
        "coupler.mount":  lambda t: MountCapability(
            capsule_id=t, agent_name="agent"),
        "net.egress":     lambda t: EgressCapability(
            destination=t, protocol="https", port=443),
        "npu.eval":       lambda t: NpuEvalCapability(
            model_id=t, input_sha=ForgeKernel._EMPTY_SHA),  # type: ignore[attr-defined]
        "fabric.conform": lambda t: ConformCapability(
            region_id=t, target_shape="default"),
        "fabric.splice":  lambda t: SpliceCapability(
            region_id=t, mode="split", sections=1, deaf=True),
        "fabric.reclaim": lambda t: ReclaimCapability(
            wrap_sha=ForgeKernel._EMPTY_SHA),  # type: ignore[attr-defined]
    }

    def gate_op(
        self,
        op: str,
        target: str = "default",
        *,
        tenant_id: str = "default",
    ) -> Any:
        """
        Sign + authorize a named op through the gate.  Used by the bridge to
        translate contract §3 op strings into GateDecisions without exposing
        Capability internals.

        Returns the GateDecision.  Callers that need to raise on deny call
        .enforce() on the result.
        """
        self._require_boot()
        factory = self._OP_CAPS.get(op)
        if factory is None:
            raise ValueError(f"unknown op: {op!r}")
        cap = factory(target)
        signed = self.gate.sign(cap, tenant_id=tenant_id)
        return self.gate.authorize(signed, tenant_id=tenant_id)


# ── Convenience entry point ────────────────────────────────────────────────────

def boot_forge(
    secret: bytes | None = None,
    *,
    seat: Optional[NpuSeat] = None,
    key_resolver: Optional[Callable[[str], bytes]] = None,
    judge: Optional[BehavioralJudge] = None,
) -> ForgeKernel:
    """
    One-line boot for the common case.

        kernel = boot_forge(sha256(b"my-secret").digest())

    If *secret* is None the function reads FORGE_SECRET from the environment
    (UTF-8 encoded).  Raises RuntimeError if no secret is available.
    """
    if secret is None:
        raw = os.environ.get("FORGE_SECRET", "")
        if not raw:
            raise RuntimeError(
                "boot_forge requires a secret or FORGE_SECRET env var"
            )
        secret = raw.encode("utf-8")

    return ForgeKernel(
        secret=secret,
        key_resolver=key_resolver,
        seat=seat,
        judge=judge,
    ).boot()
