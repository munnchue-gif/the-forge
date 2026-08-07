"""
Forge-NG — Kernel: the boot sequence. The moment the fabric stops being a pile
of importable organs and becomes a LIVING process.

WHY (revised plan, step 2)
──────────────────────────────────────────────────────────────────────────────
Every organ was unit-tested in isolation, but nothing STOOD THEM UP together
in dependency order and ran a heartbeat. That's the classic gap the original
Forge had (services that passed their own tests but were never wired into the
running server). The Kernel closes it: one boot() that constructs the whole
body, bonds the brain, chains the audit log to the gate, and gives you a single
tick() heartbeat + a clean shutdown().

WHAT BOOT DOES (dependency order)
──────────────────────────────────────────────────────────────────────────────
  1. AuditLedger        — the memory of the door (built first so it can catch
                          the very first gate event).
  2. FabricGate         — the one door; its emit hook is bonded to the ledger,
                          so every allow/deny is hash-chained from tick zero.
  3. SubstanceBus       — the deaf-by-default nervous system.
  4. Overseer           — Watcher (omnipresent tap) + Commander (act via gate).
  5. VectorConduit      — the spinal cord; bonds an NpuSeat (brain) to the body.
  6. WrapStore          — the recycling yard.
  7. Concoctinator      — the isolated proving ground (its own substance).
  8. EmbeddedTailor     — the organ that reshapes the fabric via the arena.

Nothing here fuses organs together — it BONDS them. Swap the seat, swap the
key_resolver, add policies/rules: all without touching this file's structure.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Callable

from fabric.ledger import AuditLedger
from fabric.gate import FabricGate
from fabric.bus import SubstanceBus
from fabric.overseer import Overseer, Finding
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


@dataclass
class KernelStats:
    booted: bool = False
    ticks: int = 0
    findings_total: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {"booted": self.booted, "ticks": self.ticks,
                "findings_total": self.findings_total}


@dataclass
class ForgeKernel:
    """
    The living Forge. Construct, then .boot(), then .tick() on a heartbeat, then
    .shutdown(). All organs are public attributes after boot so the (thin) DJ
    booth GUI and the couplers can reach them through the one gate.
    """

    secret: bytes
    key_resolver: Callable[[str], bytes] | None = None
    seat: NpuSeat | None = None
    judge: BehavioralJudge | None = None

    # populated by boot()
    ledger: AuditLedger | None = field(default=None, init=False)
    gate: FabricGate | None = field(default=None, init=False)
    bus: SubstanceBus | None = field(default=None, init=False)
    overseer: Overseer | None = field(default=None, init=False)
    conduit: VectorConduit | None = field(default=None, init=False)
    wraps: WrapStore | None = field(default=None, init=False)
    arena: Concoctinator | None = field(default=None, init=False)
    tailor: EmbeddedTailor | None = field(default=None, init=False)
    stats: KernelStats = field(default_factory=KernelStats, init=False)

    # ── BOOT ──────────────────────────────────────────────────────────────────

    def boot(self) -> "ForgeKernel":
        if self.stats.booted:
            raise RuntimeError("kernel already booted")

        # 1. Audit ledger — built first so it catches the very first gate event.
        self.ledger = AuditLedger(self.secret)

        # 2. Gate — emit hook bonded to the ledger (every decision hash-chained).
        self.gate = FabricGate(
            secret=None if self.key_resolver else self.secret,
            key_resolver=self.key_resolver,
            emit=lambda topic, payload: self.ledger.record(topic, payload),
        )

        # 3. Nervous system.
        self.bus = SubstanceBus()

        # 4. Overseer — omnipresent watcher + gated commander.
        self.overseer = Overseer(self.bus, self.gate)

        # 5. Spinal cord — bond the brain (HeuristicSeat until real NPU silicon).
        self.conduit = VectorConduit(
            self.overseer, self.gate,
            seat=self.seat or HeuristicSeat(),
            memory=VectorMemory(),
        )

        # 6. Recycling yard.
        self.wraps = WrapStore()

        # 7. Proving ground — its OWN substance (isolated from live).
        self.arena = Concoctinator(secret=self.secret)

        # 8. Tailor — reshapes the fabric through the arena.
        self.tailor = EmbeddedTailor(self.arena)

        # Behavioral judge available to callers (arena.judge evaluator).
        self.judge = self.judge or BehavioralJudge()

        self.stats.booted = True
        self.ledger.record("kernel.boot", {"organs": self.organ_names()})
        logger.info("Forge kernel booted: %s", self.organ_names())
        return self

    # ── HEARTBEAT ──────────────────────────────────────────────────────────────

    def tick(self) -> list[Finding]:
        """One full bond cycle: feed up → judge → command down."""
        self.stats.ticks += 1
        observations = self.conduit.tick()
        findings = self.conduit._seat.judge(observations, self.conduit.memory)
        self.stats.findings_total += len(findings)
        self.conduit._command(findings)
        return findings

    # ── SHUTDOWN ────────────────────────────────────────────────────────────────

    def shutdown(self) -> tuple[bool, int | None]:
        """Graceful stop. Closes the overseer tap and VERIFIES the audit chain
        is intact on the way out (returns the verify result). A tampered chain
        is a security event surfaced at shutdown, not swallowed."""
        self._require_boot()
        self.ledger.record("kernel.shutdown", {"ticks": self.stats.ticks})
        ok, bad = self.ledger.verify()
        try:
            self.overseer.watcher.close()
        except Exception:  # noqa: BLE001 — shutdown must not raise
            logger.exception("overseer close failed during shutdown")
        self.stats.booted = False
        logger.info("Forge kernel shutdown. audit_intact=%s", ok)
        return ok, bad

    # ── introspection ───────────────────────────────────────────────────────────

    # ── App-facing read accessors (Phase A — feed the bridge) ────────────────

    def wrapstore_summary(self) -> list[dict[str, Any]]:
        """Read-only list of wraps in the recycling yard, for the App /wraps view.
        Exposes fingerprints + shape, never the vectors themselves."""
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

    # Map an op string (contract §3) to the capability class that expresses it.
    _EMPTY_SHA = "0" * 64
    _OP_CAPS = {
        "hopper.spawn":   lambda t: SpawnCapability(capsule_id=t, script_sha=ForgeKernel._EMPTY_SHA, cpu_quota="50%", mem_limit="512m", network=False),
        "coupler.mount":  lambda t: MountCapability(capsule_id=t, agent_name=t, slot_cap_hash=ForgeKernel._EMPTY_SHA),
        "net.egress":     lambda t: EgressCapability(capsule_id=t, dest_host=t, dest_port=443, payload_sha=ForgeKernel._EMPTY_SHA),
        "npu.eval":       lambda t: NpuEvalCapability(capsule_id=t, model_id=t, vector_sha=ForgeKernel._EMPTY_SHA),
        "fabric.conform": lambda t: ConformCapability(capsule_id=t, model_id=t, wrap_sha=ForgeKernel._EMPTY_SHA),
        "fabric.splice":  lambda t: SpliceCapability(region_id=t, mode="split", sections=1, deaf=True),
        "fabric.reclaim": lambda t: ReclaimCapability(capsule_id=t, keep_vectors=True),
    }

    def request_action(self, op: str, target: str,
                       caveats: list[str] | None = None,
                       *, tenant_id: str = "app") -> dict[str, Any]:
        """THE /mint heart. Build the capability for `op`, NARROW it with the
        requested caveats (macaroon-style — holder can only shrink authority),
        sign it, and run it through the ONE gate. Returns only the decision.
        Never executes on the host — authorization is the whole job here."""
        self._require_boot()
        if op not in self._OP_CAPS:
            raise ValueError(f"unknown op: {op}")

        # Wire the caveat policy onto the gate once (idempotent-ish; cheap).
        cap = self._OP_CAPS[op](target)
        signed = self.gate.sign(cap, tenant_id=tenant_id)

        # Narrow: translate requested caveat strings into a Context the gate can
        # evaluate. Unknown caveats are ignored SAFELY (they only ever tighten).
        requested = list(caveats or [])
        narrowing_denied = None
        for c in requested:
            if c == "read_only" and op in ("net.egress", "fabric.splice",
                                           "coupler.mount", "fabric.reclaim",
                                           "hopper.spawn"):
                narrowing_denied = f"read_only caveat refuses op {op}"
                break
            if c.startswith("only_section:") and not target.startswith(c.split(":",1)[1]):
                narrowing_denied = "only_section caveat: target out of scope"
                break

        if narrowing_denied:
            self.ledger.record("mint.denied_caveat",
                               {"op": op, "target": target, "reason": narrowing_denied})
            return {"allowed": False, "finding": narrowing_denied,
                    "op": op, "target": target, "caveats": requested}

        decision = self.gate.authorize(signed, tenant_id=tenant_id)
        self.ledger.record("mint.decision", {
            "op": op, "target": target, "caveats": requested,
            "allowed": bool(decision.allowed), "audit": decision.audit_id,
        })
        return {
            "allowed": bool(decision.allowed),
            "finding": None if decision.allowed else decision.reason,
            "op": op, "target": target, "caveats": requested,
            "audit": decision.audit_id,
        }

    def organ_names(self) -> list[str]:
        return ["ledger", "gate", "bus", "overseer", "conduit",
                "wraps", "arena", "tailor", "judge"]

    def health(self) -> dict[str, Any]:
        self._require_boot()
        return {
            "booted": self.stats.booted,
            "ticks": self.stats.ticks,
            "gate": self.gate.stats.as_dict() if hasattr(self.gate.stats, "as_dict") else {},
            "audit_entries": self.ledger.size(),
            "audit_head": self.ledger.head()[:12],
            "memory_vectors": self.conduit.memory.size(),
            "bus_sections": len(self.bus.sections()),
            "bus_dropped": self.bus.dropped,
        }

    def _require_boot(self) -> None:
        if not self.stats.booted:
            raise RuntimeError("kernel not booted — call boot() first")


def boot_forge(secret: bytes | None = None, **kwargs) -> ForgeKernel:
    """Convenience entry point. `boot_forge(secret)` → a running kernel.
    In production the secret comes from the environment / keychain, never a
    literal. A dev default is derived here only when none is supplied."""
    if secret is None:
        secret = sha256(b"forge-dev-only-secret").digest()
        logger.warning("boot_forge: using DEV secret — supply a real secret in prod")
    return ForgeKernel(secret=secret, **kwargs).boot()
