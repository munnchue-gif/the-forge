"""
Forge-NG — Overseer: the omnipresent, split-into-roles watcher.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Protocol, Union

from fabric.types import Finding
from fabric.bus import SubstanceBus
from fabric.gate import FabricGate, GateDecision
from fabric.capabilities import SpliceCapability
from fabric.bind.openvino_seat import OpenVinoSeat
from fabric.bind.ollama_capsule import OllamaCapsule

logger = logging.getLogger("forge_ng.overseer")

Evaluator = Callable[[list[dict[str, Any]]], list[Finding]]


class JudgeSeat(Protocol):
    def judge(self, observations: list[dict[str, Any]]) -> list[Finding]: ...
    def health(self) -> bool: ...


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
    def __init__(self, seats: List[JudgeSeat]) -> None:
        self.seats = seats
        self.current_seat: Optional[JudgeSeat] = None
        self._select_healthy_seat()

    def _select_healthy_seat(self) -> bool:
        for seat in self.seats:
            try:
                if seat.health():
                    self.current_seat = seat
                    logger.info("Selected seat: %s", seat.__class__.__name__)
                    return True
            except Exception:
                continue
        logger.warning("No healthy seats available")
        return False

    def judge(self, observations: list[dict[str, Any]]) -> list[Finding]:
        if not self.current_seat or not self.current_seat.health():
            if not self._select_healthy_seat():
                logger.warning("No healthy seats available - using fallback")
                return []
        try:
            return self.current_seat.judge(observations)
        except Exception:
            logger.exception(
                "Seat %s failed - attempting failover",
                self.current_seat.__class__.__name__
            )
            if not self._select_healthy_seat():
                logger.warning("No healthy seats available after failure")
            return []


class Watcher:
    def __init__(
        self,
        bus: SubstanceBus,
        evaluator: Union[Evaluator, JudgeSeat, SeatManager, None] = None,
        batch_size: int = 32,
    ) -> None:
        self._bus = bus
        self._tap = bus.open_tap()
        self._evaluator = evaluator if evaluator is not None else (lambda batch: [])
        self._batch_size = batch_size
        self._buffer: list[dict[str, Any]] = []
        self.stats = OverseerStats()

    def observe_pending(self) -> list[dict[str, Any]]:
        drained: list[dict[str, Any]] = []
        while not self._tap.empty():
            try:
                drained.append(self._tap.get_nowait())
            except Exception:
                break
        self.stats.events_observed += len(drained)
        self._buffer.extend(drained)
        return drained

    def evaluate(self) -> list[Finding]:
        if not self._buffer:
            return []
        try:
            if isinstance(self._evaluator, SeatManager):
                findings = self._evaluator.judge(self._buffer)
                seat = self._evaluator.current_seat
                if isinstance(seat, OpenVinoSeat):
                    self.stats.openvino_judgments += 1
                elif isinstance(seat, OllamaCapsule):
                    self.stats.ollama_judgments += 1
                else:
                    self.stats.fallback_judgments += 1
            elif hasattr(self._evaluator, "judge"):
                findings = self._evaluator.judge(self._buffer)
                self.stats.fallback_judgments += 1
            else:
                findings = list(self._evaluator(self._buffer))
                self.stats.fallback_judgments += 1

            self.stats.findings_raised += len(findings)
            self._buffer.clear()
            return findings
        except Exception:
            logger.exception("Evaluator failed; no findings this tick")
            self.stats.seat_failures += 1
            self._buffer.clear()
            return []

    def close(self) -> None:
        self._bus.close_tap(self._tap)


class Commander:
    def __init__(
        self,
        bus: SubstanceBus,
        gate: FabricGate,
        stats: OverseerStats,
    ) -> None:
        self._bus = bus
        self._gate = gate
        self.stats = stats

    def reach_in(
        self,
        cap: Any,
        *,
        control_event: dict[str, Any],
        tenant_id: str = "default",
    ) -> GateDecision:
        signed = self._gate.sign(cap, tenant_id=tenant_id)
        decision = self._gate.authorize(signed, tenant_id=tenant_id)

        if not decision.allowed:
            self.stats.commands_denied += 1
            logger.warning("commander reach-in DENIED: %s", decision.reason)
            return decision

        section = getattr(cap, "region_id", None) or getattr(cap, "capsule_id", None)
        if section and section in self._bus.sections():
            self._bus.publish(
                section,
                "overseer.control",
                {"audit_id": decision.audit_id, **control_event},
            )

        self.stats.commands_issued += 1
        logger.info(
            "commander reach-in ALLOWED audit=%s -> %s",
            decision.audit_id,
            section,
        )
        return decision


class Overseer:
    def __init__(
        self,
        bus: SubstanceBus,
        gate: FabricGate,
        evaluator: Union[Evaluator, JudgeSeat, SeatManager, List[JudgeSeat], None] = None,
    ) -> None:
        self._bus = bus
        self._gate = gate

        if isinstance(evaluator, list):
            self.seat_manager: Optional[SeatManager] = SeatManager(evaluator)
            self.watcher = Watcher(bus, self.seat_manager)
        else:
            self.seat_manager = None
            self.watcher = Watcher(bus, evaluator)

        self.commander = Commander(bus, gate, self.watcher.stats)
        self._feed_log: list[dict[str, Any]] = []

    @property
    def stats(self) -> OverseerStats:
        return self.watcher.stats

    def split_region(
        self,
        region_id: str,
        sections: int,
        *,
        tenant_id: str = "default",
    ) -> GateDecision:
        cap = SpliceCapability(
            region_id=region_id,
            mode="split",
            sections=sections,
            deaf=True,
        )
        signed = self._gate.sign(cap, tenant_id=tenant_id)
        decision = self._gate.authorize(signed, tenant_id=tenant_id)
        if decision.allowed:
            for i in range(sections):
                self._bus.open_section(f"{region_id}.s{i}")
        return decision

    def tick(self) -> list[Finding]:
        self.watcher.observe_pending()
        findings = self.watcher.evaluate()
        for f in findings:
            if hasattr(f, "as_dict"):
                self._feed_log.append(f.as_dict())
            else:
                self._feed_log.append({
                    "section_id": getattr(f, "section_id", None),
                    "kind": getattr(f, "kind", None),
                    "detail": getattr(f, "detail", None),
                    "severity": getattr(f, "severity", None),
                })
        return findings

    def drain_findings(self, cursor: int = 0) -> list[dict[str, Any]]:
        if cursor < 0:
            cursor = 0
        return self._feed_log[cursor:]

    def section_status(self) -> list[dict[str, Any]]:
        return [
            {"section_id": sid, "deaf": True}
            for sid in self._bus.sections()
        ]

    def watcher_info(self) -> dict[str, Any]:
        return {
            "buffer_depth": len(self.watcher._buffer),
            "feed_log_len": len(self._feed_log),
            "stats": self.stats.as_dict(),
        }

    def close(self) -> None:
        self.watcher.close()
