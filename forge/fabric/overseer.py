"""
Forge-NG — Overseer: the omnipresent, split-into-roles watcher.

Eugene's vision, in system terms:
  "an overseer that is omnipresent within it and split into different models…
   even though it's disconnected, it can still communicate telepathically and
   execute control codes and security measures, and if something changes it
   can adapt and change with it."

The Overseer is woven through the whole substance via a SubstanceBus tap
(hears every deaf section at once) and is itself SPLIT into two roles — exactly
your A/B watcher pair:

    WATCHER  (observe)  — consumes the firehose, builds a live picture,
                          detects change/drift/anomaly. Never acts.
    COMMANDER (act)     — the ONLY thing that reaches back INTO a sealed
                          section, and it may do so only by minting a signed
                          Capability through the FabricGate. Every reach-in is
                          replay-proof and audited. No silent control, ever.

Separation of the two roles is itself a safety property: the thing that watches
cannot act, and the thing that acts cannot watch on its own — it acts only on
the watcher's findings, and only through the gate.

The NPU-resident learning model (the continuity that holds catch files /
vectors / meta and never gets flattened on reclaim) is modelled here as a
pluggable `evaluator` hook. Today it can be any callable; when real NPU silicon
is wired, the same hook binds to it — the architecture doesn't change.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Protocol, Optional, Union, List

from fabric.bus import SubstanceBus
from fabric.gate import FabricGate, GateDecision
from fabric.capabilities import SpliceCapability
from fabric.bind.openvino_seat import OpenVinoSeat
from fabric.bind.ollama_capsule import OllamaCapsule

logger = logging.getLogger("forge_ng.overseer")

# An evaluator judges a batch of observed events and returns findings.
# This is where the NPU learning model plugs in later. It MUST be pure w.r.t.
# side effects — it observes and judges; it never acts. (The Commander acts.)
Evaluator = Callable[[list[dict[str, Any]]], list["Finding"]]

class JudgeSeat(Protocol):
    """Common interface for both local and cloud inference seats."""
    def judge(self, observations: list[dict[str, Any]]) -> list[Finding]: ...
    def health(self) -> bool: ...

@dataclass(frozen=True, slots=True)
class Finding:
    """Something the Watcher noticed. Advisory only — carries no authority."""
    section_id: str
    kind: str                 # e.g. "drift", "anomaly", "loop", "ok"
    detail: str
    severity: int = 0         # 0=info .. 3=critical

@dataclass
class OverseerStats:
    events_observed: int = 0
    findings_raised: int = 0
    commands_issued: int = 0
    commands_denied: int = 0
    openvino_judgments: int = 0
    ollama_judgments: int = 0
    fallback_judgments: int = 0
    seat_failures: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "events_observed": self.events_observed,
            "findings_raised": self.findings_raised,
            "commands_issued": self.commands_issued,
            "commands_denied": self.commands_denied,
            "openvino_judgments": self.openvino_judgments,
            "ollama_judgments": self.ollama_judgments,
            "fallback_judgments": self.fallback_judgments,
            "seat_failures": self.seat_failures,
        }

class SeatManager:
    """Manages dynamic routing between available inference seats."""

    def __init__(self, seats: List[JudgeSeat]):
        self.seats = seats
        self.current_seat = None
        self._select_healthy_seat()

    def _select_healthy_seat(self) -> bool:
        """Find and select the first healthy seat."""
        for seat in self.seats:
            if seat.health():
                self.current_seat = seat
                logger.info(f"Selected seat: {seat.__class__.__name__}")
                return True
        logger.warning("No healthy seats available")
        return False

    def judge(self, observations: list[dict[str, Any]]) -> list[Finding]:
        """Route judgment to the current healthy seat, with automatic failover."""
        if not self.current_seat or not self.current_seat.health():
            if not self._select_healthy_seat():
                logger.warning("No healthy seats available - using fallback")
                return []

        try:
            findings = self.current_seat.judge(observations)
            return findings
        except Exception as e:
            logger.exception(f"Seat {self.current_seat.__class__.__name__} failed")
            if not self._select_healthy_seat():
                logger.warning("No healthy seats available after failure")
            return []

class Watcher:
    """
    Observe-only role. Holds the omnipresent tap, batches events, and runs the
    evaluator (NPU model, later) to produce Findings. Cannot act.
    """

    def __init__(
        self,
        bus: SubstanceBus,
        evaluator: Union[Evaluator, JudgeSeat, SeatManager, None] = None,
        batch_size: int = 32,
    ) -> None:
        self._bus = bus
        self._tap = bus.open_tap()
        self._evaluator = evaluator or (lambda batch: [])
        self._batch_size = batch_size
        self._buffer: list[dict[str, Any]] = []
        self.stats = OverseerStats()

    def observe_pending(self) -> list[dict[str, Any]]:
        """Drain whatever the tap has seen so far (non-blocking)."""
        drained: list[dict[str, Any]] = []
        while not self._tap.empty():
            drained.append(self._tap.get_nowait())
        self.stats.events_observed += len(drained)
        self._buffer.extend(drained)
        return drained

    def evaluate(self) -> list[Finding]:
        """Run the evaluator over the buffered observations, then clear."""
        if not self._buffer:
            return []

        try:
            if isinstance(self._evaluator, SeatManager):
                findings = self._evaluator.judge(self._buffer)
                # Update metrics based on which seat was used
                if isinstance(self._evaluator.current_seat, OpenVinoSeat):
                    self.stats.openvino_judgments += 1
                elif isinstance(self._evaluator.current_seat, OllamaCapsule):
                    self.stats.ollama_judgments += 1
                else:
                    self.stats.fallback_judgments += 1
            elif hasattr(self._evaluator, 'judge'):
                findings = self._evaluator.judge(self._buffer)
                self.stats.fallback_judgments += 1
            else:
                findings = list(self._evaluator(self._buffer))
                self.stats.fallback_judgments += 1

            self.stats.findings_raised += len(findings)
            self._buffer.clear()
            return findings
        except Exception as e:
            logger.exception("Evaluator failed; no findings this tick")
            self.stats.seat_failures += 1
            return []

    def close(self) -> None:
        self._bus.close_tap(self._tap)

class Commander:
    """
    Act-only role. The ONLY path that reaches into a sealed section. It cannot
    observe on its own — it acts on Findings handed to it, and every action is
    a signed Capability through the gate. Denials are counted, never bypassed.
    """

    def __init__(self, bus: SubstanceBus, gate: FabricGate,
                 stats: OverseerStats) -> None:
        self._bus = bus
        self._gate = gate
        self.stats = stats

    def reach_in(self, cap, *, control_event: dict[str, Any],
                 tenant_id: str = "default") -> GateDecision:
        """
        Reach into a sealed section with a control command. The command only
        lands if the gate authorizes the Capability. This is 'execute control
        codes across the gap' — real, but never silent.
        """
        signed = self._gate.sign(cap, tenant_id=tenant_id)
        decision = self._gate.authorize(signed, tenant_id=tenant_id)
        if not decision.allowed:
            self.stats.commands_denied += 1
            logger.warning("commander reach-in DENIED: %s", decision.reason)
            return decision

        # Authorized: deliver the control event into the target section.
        section = getattr(cap, "region_id", None) or getattr(cap, "capsule_id", "")
        if section in self._bus.sections():
            self._bus.publish(section, "overseer.control",
                              {"audit_id": decision.audit_id, **control_event})
        self.stats.commands_issued += 1
        logger.info("commander reach-in ALLOWED audit=%s -> %s",
                    decision.audit_id, section)
        return decision

class Overseer:
    """
    The whole omnipresent watcher: one Watcher (observe) + one Commander (act),
    sharing stats, woven through the SubstanceBus, acting only via the gate.
    """

    def __init__(
        self,
        bus: SubstanceBus,
        gate: FabricGate,
        evaluator: Union[Evaluator, JudgeSeat, SeatManager, None] = None,
    ) -> None:
        self._bus = bus
        self._gate = gate

        # Initialize SeatManager if multiple seats are provided
        if isinstance(evaluator, list):
            self.seat_manager = SeatManager(evaluator)
            self.watcher = Watcher(bus, self.seat_manager)
        else:
            self.watcher = Watcher(bus, evaluator)

        self.commander = Commander(bus, gate, self.watcher.stats)
        # Rolling read-only history of findings, for the App /feed drain-by-cursor.
        self._feed_log: list[dict[str, Any]] = []

    @property
    def stats(self) -> OverseerStats:
        return self.watcher.stats

    def split_region(self, region_id: str, sections: int,
                     *, tenant_id: str = "default") -> GateDecision:
        """
        Authorize + physically perform a substance split: gate-sign a
        SpliceCapability, and only if allowed, open the deaf sections on the bus.
        Isolation is created by the same action that authorizes it.
        """
        cap = SpliceCapability(region_id=region_id, mode="split",
                               sections=sections, deaf=True)
        signed = self._gate.sign(cap, tenant_id=tenant_id)
        decision = self._gate.authorize(signed, tenant_id=tenant_id)
        if decision.allowed:
            for i in range(sections):
                self._bus.open_section(f"{region_id}.s{i}")
        return decision

    def tick(self) -> list[Finding]:
        """One observation cycle: drain the tap, evaluate, return findings."""
        self.watcher.observe_pending()
        findings = self.watcher.evaluate()
        for f in findings:
            self._feed_log.append(f.as_dict() if hasattr(f, "as_dict") else {
                "section_id": getattr(f, "section_id", None),
                "kind": getattr(f, "kind", None),
                "detail": getattr(f, "detail", None),
                "severity": getattr(f, "severity", None),
            })
        return findings

    def drain_findings(self, cursor: int = 0) -> list[dict[str, Any]]:
        """Read-only pull of findings recorded since `cursor` (an index into the
        rolling feed log). The App's /feed calls this each poll. Never mutates."""
        if cursor < 0:
            cursor = 0
        return self._feed_log[cursor:]

    def section_status(self) -> list[dict[str, Any]]:
        """Current bus sections + basic status for the App's live map."""
        return [{"section_id": sid, "deaf": True} for sid in self._bus.sections()]

    def close(self) -> None:
        self.watcher.close()
