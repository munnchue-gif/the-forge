"""
Proof of the omnipresent-overseer / telepathy-across-disconnection claim.

The headline test — test_deaf_sections_but_overseer_hears_all — is the whole
vision in one assertion: two sections cannot hear each other, but the overseer
woven through the substance hears both, and can reach into one via a signed,
audited command while the other stays sealed.
"""

from __future__ import annotations

import hashlib

from fabric.bus import SubstanceBus
from fabric.gate import FabricGate, Decision
from fabric.overseer import Overseer, Finding
from fabric.capabilities import SpliceCapability

SECRET = b"overseer-test-key-00000000000000000"


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def test_sections_are_deaf_to_each_other():
    bus = SubstanceBus()
    bus.open_section("cap.s0")
    bus.open_section("cap.s1")

    q0 = bus.subscribe("cap.s0", "thought")
    # s1 subscriber must NOT receive s0's events.
    q1 = bus.subscribe("cap.s1", "thought")

    bus.publish("cap.s0", "thought", {"msg": "hello from A"})

    assert not q0.empty()          # A hears itself
    assert q1.empty()              # B is deaf to A — the seam holds


def test_cannot_subscribe_to_nonexistent_section():
    bus = SubstanceBus()
    try:
        bus.subscribe("ghost", "x")
        assert False, "expected KeyError"
    except KeyError:
        pass


def test_deaf_sections_but_overseer_hears_all():
    """THE VISION. Deaf siblings, omnipresent overseer."""
    bus = SubstanceBus()
    gate = FabricGate(SECRET)
    overseer = Overseer(bus, gate)

    # Substance splits itself into two deaf sections (gate-authorized).
    d = overseer.split_region("cap", sections=2)
    assert d.allowed
    assert bus.sections() == ["cap.s0", "cap.s1"]

    # Each section thinks its own private thoughts.
    bus.publish("cap.s0", "thought", {"who": "A", "v": 1})
    bus.publish("cap.s1", "thought", {"who": "B", "v": 2})

    # The overseer's tap heard BOTH, tagged by origin.
    seen = overseer.watcher.observe_pending()
    origins = {(e["_section"], e["who"]) for e in seen}
    assert ("cap.s0", "A") in origins
    assert ("cap.s1", "B") in origins
    assert overseer.stats.events_observed == 2


def test_overseer_reaches_into_one_section_only():
    """Control across the gap — signed, audited, and targeted."""
    bus = SubstanceBus()
    gate = FabricGate(SECRET)
    overseer = Overseer(bus, gate)
    overseer.split_region("cap", sections=2)

    # A subscriber inside s0 listening for control commands.
    ctrl0 = bus.subscribe("cap.s0", "overseer.control")
    ctrl1 = bus.subscribe("cap.s1", "overseer.control")

    # Commander reaches into s0 only.
    reach = SpliceCapability(region_id="cap.s0", mode="merge", sections=1, deaf=False)
    decision = overseer.commander.reach_in(reach, control_event={"cmd": "quiesce"})
    assert decision.allowed

    assert not ctrl0.empty()       # s0 got the control command
    assert ctrl1.empty()           # s1 untouched — reach-in is targeted
    assert overseer.stats.commands_issued == 1


def test_overseer_adapts_on_detected_change():
    """'If something changes, it can adapt' — the evaluator raises a Finding,
    and the commander acts on it via the gate. Watch cannot act; act needs a
    finding + the gate."""
    bus = SubstanceBus()
    gate = FabricGate(SECRET)

    def evaluator(batch):
        # Detect a section reporting drift.
        out = []
        for e in batch:
            if e.get("state") == "drift":
                out.append(Finding(section_id=e["_section"], kind="drift",
                                   detail="value diverged", severity=2))
        return out

    overseer = Overseer(bus, gate, evaluator=evaluator)
    overseer.split_region("cap", sections=1)

    bus.publish("cap.s0", "status", {"state": "drift", "value": 9999})

    findings = overseer.tick()
    assert len(findings) == 1 and findings[0].kind == "drift"

    # Overseer adapts: commander corrects the drifting section, through the gate.
    fix = SpliceCapability(region_id=findings[0].section_id, mode="merge",
                           sections=1, deaf=False)
    d = overseer.commander.reach_in(fix, control_event={"cmd": "recalibrate"})
    assert d.allowed
    assert overseer.stats.commands_issued == 1


def test_replayed_control_command_is_blocked():
    """Even the omnipresent overseer cannot act silently or twice — a replayed
    reach-in is denied by the gate."""
    bus = SubstanceBus()
    gate = FabricGate(SECRET)
    overseer = Overseer(bus, gate)
    overseer.split_region("cap", sections=1)

    cap = SpliceCapability(region_id="cap.s0", mode="merge", sections=1, deaf=False)
    signed = gate.sign(cap)
    assert gate.authorize(signed).allowed
    # The same signed command replayed is refused — control is always fresh.
    assert gate.authorize(signed).decision is Decision.DENY_REPLAY


def test_bus_is_memory_bounded_under_stall():
    """A stalled subscriber cannot balloon memory — overflow is dropped and
    counted, so backpressure is observable, never silent. The seamless-under-
    load property."""
    bus = SubstanceBus(maxsize=64)
    bus.open_section("cap.s0")
    q = bus.subscribe("cap.s0", "flood")   # subscriber that never drains

    for i in range(1000):
        bus.publish("cap.s0", "flood", {"i": i})

    assert q.qsize() <= 64            # hard-bounded, did not grow to 1000
    assert bus.dropped >= 936         # the rest were counted, not lost silently
