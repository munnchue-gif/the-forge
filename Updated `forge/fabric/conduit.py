"""
Forge-NG — VectorConduit: the bond loop between the Forge body and the NPU brain.

WHAT THIS CLOSES (Eugene's "where's the true power" — it's bonded, not attached)
──────────────────────────────────────────────────────────────────────────────
The skeleton (gate/bus/overseer/wrap) can authorize, isolate, watch, and mold —
but it has no power of its own, on purpose. The power is a SEPARATE brain on the
NPU so it can't bias or train itself into the skeleton. This module is the
spinal cord that bonds the two into one being WITHOUT fusing them:

    FEED UP    capsules emit vectors/meta/catch-files  →  conduit collects them
    JUDGE      conduit hands the batch to the NpuSeat (the bonded brain)
    COMMAND    the brain's Findings  →  gate-signed Capabilities  →  Commander
               reaches back into the exact section that needs correcting

The brain is a pluggable seat. Today it can be any callable (a heuristic, a
local model, a mock). When real NPU silicon is wired, the SAME seat interface
binds to it — nothing above the seat changes. That is the future-proofing:
the conduit is the contract, the silicon is an implementation detail.

DESIGN CONSTRAINTS HELD
──────────────────────────────────────────────────────────────────────────────
• Modular    — the brain is a Protocol (NpuSeat); swap implementations freely.
• Thin       — the conduit holds no model weight; it moves vectors and routes
               findings. All heavy thinking lives behind the seat, off-skeleton.
• Liquid     — it flows: sections feed in continuously, findings flow out
               continuously; one tick() is one heartbeat of the being.
• Sentient   — the brain sees EVERYTHING (via the overseer tap) and adapts;
               but every adaptation it triggers is a signed, audited command.
• Unbiased   — the seat only observes and judges. It can NEVER act directly;
               action is the Commander's job, always through the gate.
• Future-proof— Level 1 (judge→correct) here; Levels 2 (memory) & 3 (shaping)
               widen this same wire without new architecture (hooks provided).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from fabric.gate import FabricGate, GateDecision
from fabric.overseer import Overseer, Finding
from fabric.capabilities import SpliceCapability

logger = logging.getLogger("forge_ng.conduit")


# ──────────────────────────────────────────────────────────────────────────────
# The NPU seat — the bonded brain's contract. Silicon plugs in HERE, nowhere else.
# ──────────────────────────────────────────────────────────────────────────────

class NpuSeat(Protocol):
    """
    The bonded brain. Separate system, unbiased, observe-and-judge only.

    A real NPU model, a local llama, or a heuristic all satisfy this. The
    conduit does not know or care which — that is the whole point of the seat.
    """

    def judge(self, observations: list[dict[str, Any]],
              memory: "VectorMemory") -> list[Finding]:
        """Look at what the body is doing (+ accumulated memory) and return
        Findings. MUST NOT act or mutate the skeleton — advisory only."""
        ...


class HeuristicSeat:
    """
    Default seat — a dependency-free brain so the being is alive out of the box
    before real silicon is bonded. Detects drift / loops from the raw stream.
    Replace with a real NpuSeat implementation; the conduit won't notice.
    """

    def __init__(self, drift_key: str = "state", drift_value: str = "drift",
                 loop_threshold: int = 5) -> None:
        self._drift_key = drift_key
        self._drift_value = drift_value
        self._loop_threshold = loop_threshold

    def judge(self, observations: list[dict[str, Any]],
              memory: "VectorMemory") -> list[Finding]:
        findings: list[Finding] = []
        counts: dict[str, int] = {}
        for e in observations:
            section = e.get("_section", "?")
            if e.get(self._drift_key) == self._drift_value:
                findings.append(Finding(section_id=section, kind="drift",
                                        detail="state diverged", severity=2))
            key = f"{section}:{e.get('_topic')}"
            counts[key] = counts.get(key, 0) + 1
        for key, n in counts.items():
            if n >= self._loop_threshold:
                sec = key.split(":", 1)[0]
                findings.append(Finding(section_id=sec, kind="loop",
                                        detail=f"{n} repeats in one tick", severity=1))
        return findings


# ──────────────────────────────────────────────────────────────────────────────
# Vector memory — the continuity the brain feeds on (Level 2 grows from here)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class VectorMemory:
    """
    The being's accumulated memory of vectors/meta/catch-files. Held HERE,
    beside the brain, NOT in any capsule — so no single capsule carries it and
    reclaiming a capsule never erases the being's memory. This is the seed of
    the "solve AI data constraints" idea: one continuity that never flattens.

    Level 1 keeps a bounded rolling window. Level 2 points this at the WrapStore
    and persistent storage — same interface, bigger shelf.
    """
    capacity: int = 100_000
    _vectors: dict[str, bytes] = field(default_factory=dict)   # ref -> bytes
    _meta: list[dict[str, Any]] = field(default_factory=list)  # rolling meta log
    _burned: set[str] = field(default_factory=set)             # tombstones
    ingested: int = 0

    def absorb(self, ref: str, vectors: bytes, meta: dict[str, Any]) -> None:
        # A burned (poisoned) ref can never be silently re-absorbed.
        if ref in self._burned:
            raise ValueError(f"refusing to absorb burned vector ref: {ref!r}")
        self._vectors[ref] = vectors
        self._meta.append({"ref": ref, "at": time.time(), **meta})
        self.ingested += 1
        # Bounded — the brain's memory can't balloon the skeleton.
        if len(self._meta) > self.capacity:
            drop = self._meta.pop(0)
            self._vectors.pop(drop["ref"], None)

    def recall(self, ref: str) -> bytes | None:
        return self._vectors.get(ref)

    def recent(self, n: int = 32) -> list[dict[str, Any]]:
        return self._meta[-n:]

    def size(self) -> int:
        return len(self._vectors)

    # ── BURN — purge poisoned vectors (M4 observer review, risk #3) ──────────
    # "Memory survives reclaim" is continuity — but it also means a POISONED
    # vector would survive too, and re-bond to the next model poured onto the
    # seat. Reclaim keeps; BURN destroys. This is the deliberate purge path.

    def burn(self, ref: str) -> bool:
        """Destroy one vector set and tombstone it so it can't be re-absorbed
        silently. Returns True if something was burned."""
        existed = ref in self._vectors
        self._vectors.pop(ref, None)
        self._meta = [m for m in self._meta if m.get("ref") != ref]
        self._burned.add(ref)
        return existed

    def burn_where(self, predicate: Callable[[dict[str, Any]], bool]) -> int:
        """Burn every vector whose meta matches a predicate — e.g. a whole
        poisoned lineage (all vectors from a compromised source). Returns the
        count burned."""
        victims = {m["ref"] for m in self._meta if predicate(m)}
        for ref in victims:
            self.burn(ref)
        return len(victims)

    def is_burned(self, ref: str) -> bool:
        return ref in self._burned


# ──────────────────────────────────────────────────────────────────────────────
# The conduit — the spinal cord
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ConduitStats:
    ticks: int = 0
    vectors_fed: int = 0
    findings_judged: int = 0
    corrections_issued: int = 0
    corrections_denied: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "ticks": self.ticks,
            "vectors_fed": self.vectors_fed,
            "findings_judged": self.findings_judged,
            "corrections_issued": self.corrections_issued,
            "corrections_denied": self.corrections_denied,
        }


class VectorConduit:
    """
    Bonds the Overseer (body's senses + hands) to the NpuSeat (bonded brain).

    One tick() is one heartbeat:
        1. FEED UP  — drain the overseer tap; absorb any carried vectors/meta
                      into VectorMemory (the continuity).
        2. JUDGE    — hand observations + memory to the seat → Findings.
        3. COMMAND  — map each actionable Finding to a gate-signed Capability
                      and have the Commander reach into the offending section.

    The seat never touches the skeleton; the conduit never thinks. Clean bond.
    """

    #: Findings of at least this severity trigger a real correction command.
    ACT_THRESHOLD = 2

    def __init__(
        self,
        overseer: Overseer,
        gate: FabricGate,
        seat: NpuSeat | None = None,
        memory: VectorMemory | None = None,
        *,
        corrector: Callable[[Finding], Any] | None = None,
        tenant_id: str = "default",
    ) -> None:
        self._overseer = overseer
        self._gate = gate
        self._seat: NpuSeat = seat or HeuristicSeat()
        self.memory = memory or VectorMemory()
        self._tenant = tenant_id
        # How a Finding becomes an action. Default: quiesce the drifting section
        # via a merge-splice. Override to grow the brain's command vocabulary
        # (Level 3) WITHOUT touching the conduit's loop.
        self._corrector = corrector or self._default_corrector
        self.stats = ConduitStats()

    # ── FEED UP ──────────────────────────────────────────────────────────────

    def _feed_up(self) -> list[dict[str, Any]]:
        observations = self._overseer.watcher.observe_pending()
        for e in observations:
            # A capsule may carry a vector payload up with its event.
            ref = e.get("vector_ref")
            if ref:
                self.memory.absorb(
                    ref=ref,
                    vectors=e.get("vector_bytes", b""),
                    meta={"section": e.get("_section"), "topic": e.get("_topic")},
                )
                self.stats.vectors_fed += 1
        return observations

    # ── COMMAND ───────────────────────────────────────────────────────────────

    def _default_corrector(self, finding: Finding) -> SpliceCapability:
        """Default corrective action: dissolve/quiesce the offending section.
        Returns a Capability; the gate decides whether it actually happens."""
        return SpliceCapability(region_id=finding.section_id, mode="merge",
                                sections=1, deaf=False)

    def _command(self, findings: list[Finding]) -> None:
        for f in findings:
            if f.severity < self.ACT_THRESHOLD:
                continue
            cap = self._corrector(f)
            decision: GateDecision = self._overseer.commander.reach_in(
                cap,
                control_event={"reason": f.kind, "detail": f.detail,
                               "severity": f.severity},
                tenant_id=self._tenant,
            )
            if decision.allowed:
                self.stats.corrections_issued += 1
            else:
                self.stats.corrections_denied += 1
                logger.warning("correction denied for %s: %s",
                               f.section_id, decision.reason)

    # ── HEARTBEAT ──────────────────────────────────────────────────────────────

    def tick(self) -> list[Finding]:
        """One full bond cycle: feed up → judge → command down."""
        self.stats.ticks += 1
        observations = self._feed_up()
        findings = self._seat.judge(observations, self.memory)
        self.stats.findings_judged += len(findings)
        self._command(findings)
        return findings

    # ── Future-proofing hooks (Levels 2 & 3 attach here, no loop changes) ─────

    def bind_seat(self, seat: NpuSeat) -> None:
        """Hot-swap the brain — bond real NPU silicon at runtime. The loop above
        is unchanged; only what does the judging differs."""
        self._seat = seat

    def bind_corrector(self, corrector: Callable[[Finding], Any]) -> None:
        """Widen the brain's command vocabulary (Level 3 shaping) without
        touching the heartbeat."""
        self._corrector = corrector
