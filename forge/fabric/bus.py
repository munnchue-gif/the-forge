"""
Forge-NG — SubstanceBus: asymmetric event fabric.

THE TELEPATHY PROPERTY (Eugene's vision, made physical)
──────────────────────────────────────────────────────────────────────────────
When the substance splices itself into deaf sections, each section gets its own
private channel. Sections CANNOT hear each other — that is the isolation.

But the substance is one material, so the Overseer woven through all of it can
still hear every section at once. The asymmetry is the whole trick:

    section  →  can publish only to its own channel
    section  →  cannot subscribe to a sibling's channel   (deaf to neighbours)
    Overseer →  taps EVERY channel read-only              (omnipresent listener)
    Overseer →  reaches INTO any section via signed command (control across gap)

A cut wire can't leak sideways; the overseer's tap is the only path that
crosses a seam, and (in overseer.py) it is gated + audited. This module is the
plumbing; the trust rules live at the gate.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any

logger = logging.getLogger("forge_ng.bus")


class SubstanceBus:
    """
    A sharded pub/sub fabric. Each 'section' is an isolated namespace.

    Regular subscribers may only listen to the section they belong to.
    A privileged tap (the Overseer) may listen across ALL sections.
    """

    def __init__(self, maxsize: int = 4096) -> None:
        # Bounded queues: a stalled subscriber or slow overseer can never
        # balloon memory. Overflow is dropped and counted, not buffered
        # forever — backpressure stays observable, not silent.
        self._maxsize = maxsize
        # section_id -> topic -> list[Queue]  (normal, isolated subscribers)
        self._channels: dict[str, dict[str, list[asyncio.Queue]]] = defaultdict(
            lambda: defaultdict(list)
        )
        # Overseer taps: list of queues that receive EVERY event, tagged with
        # its origin section. Read-only firehose — taps never publish here.
        self._taps: list[asyncio.Queue] = []
        self._sealed: set[str] = set()   # sections that exist (splice created)
        self.dropped: int = 0            # observable overflow counter

    # ── Section lifecycle (driven by SpliceCapability at the gate) ──────────

    def open_section(self, section_id: str) -> None:
        """Create a sealed section. Idempotent."""
        self._sealed.add(section_id)
        _ = self._channels[section_id]  # materialise the namespace
        logger.debug("section opened: %s", section_id)

    def close_section(self, section_id: str) -> None:
        """Dissolve a section (merge direction). Drops its channels."""
        self._sealed.discard(section_id)
        self._channels.pop(section_id, None)
        logger.debug("section closed: %s", section_id)

    def sections(self) -> list[str]:
        return sorted(self._sealed)

    # ── Section-local pub/sub (isolated — cannot cross a seam) ───────────────

    def subscribe(self, section_id: str, topic: str) -> asyncio.Queue:
        """
        Subscribe within ONE section only. A caller physically cannot pass a
        section_id it wasn't given, and there is no API to subscribe to '*'
        for normal callers — deafness is structural, not policy.
        """
        if section_id not in self._sealed:
            raise KeyError(f"no such section: {section_id!r}")
        q: asyncio.Queue = asyncio.Queue(maxsize=self._maxsize)
        self._channels[section_id][topic].append(q)
        return q

    def publish(self, section_id: str, topic: str, event: dict[str, Any]) -> None:
        """
        Publish inside one section. Delivered to that section's subscribers
        AND mirrored to every Overseer tap (tagged with origin). Never
        delivered to any OTHER section — that is the seam.
        """
        if section_id not in self._sealed:
            raise KeyError(f"no such section: {section_id!r}")

        # 1. section-local delivery (copy-on-write snapshot)
        for q in list(self._channels[section_id].get(topic, ())):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                self.dropped += 1
                logger.warning("section %s topic %s queue full; dropped", section_id, topic)

        # 2. overseer firehose — every tap sees everything, tagged
        if self._taps:
            tapped = {"_section": section_id, "_topic": topic, **event}
            for tap in list(self._taps):
                try:
                    tap.put_nowait(tapped)
                except asyncio.QueueFull:
                    self.dropped += 1
                    logger.warning("overseer tap queue full; event dropped")

    # ── Overseer-only omnipresent tap ───────────────────────────────────────

    def open_tap(self) -> asyncio.Queue:
        """
        Register an omnipresent read-only tap. Receives EVERY event from EVERY
        section, each tagged with _section / _topic. This is the only construct
        that crosses seams, and only the Overseer is handed one.
        """
        q: asyncio.Queue = asyncio.Queue(maxsize=self._maxsize)
        self._taps.append(q)
        return q

    def close_tap(self, q: asyncio.Queue) -> None:
        try:
            self._taps.remove(q)
        except ValueError:
            pass
