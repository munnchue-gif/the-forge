"""
Proof that the being CLOSES: body (Overseer) bonded to brain (NpuSeat) via the
VectorConduit, and every adaptation still flows through the gate.
"""

from __future__ import annotations

from fabric.bus import SubstanceBus
from fabric.gate import FabricGate, Decision
from fabric.overseer import Overseer
from fabric.types import Finding, make_finding
from fabric.conduit import VectorConduit, VectorMemory, HeuristicSeat, NpuSeat

SECRET = b"conduit-test-key-0000000000000000000"


def _rig():
    bus = SubstanceBus()
    gate = FabricGate(SECRET)
    overseer = Overseer(bus, gate)
    conduit = VectorConduit(overseer, gate)
    return bus, gate, overseer, conduit


def test_loop_closes_feed_judge_command():
    """A section drifts → brain judges drift → conduit corrects it via the
    gate. The full bond cycle in one tick."""
    bus, gate, overseer, conduit = _rig()
    overseer.split_region("cap", sections=1)

    bus.publish("cap.s0", "status", {"state": "drift", "value": 9999})
    findings = conduit.tick()

    assert any(f.title == "drift" for f in findings)
    assert conduit.stats.corrections_issued == 1     # it acted, through the gate
    assert conduit.stats.ticks == 1


def test_vectors_feed_up_into_memory():
    """Capsules carry vectors up; the conduit absorbs them into the being's
    continuity (not into any capsule)."""
    bus, gate, overseer, conduit = _rig()
    overseer.split_region("cap", sections=1)

    bus.publish("cap.s0", "emit",
                {"vector_ref": "v1", "vector_bytes": b"learned", "state": "ok"})
    conduit.tick()

    assert conduit.stats.vectors_fed == 1
    assert conduit.memory.recall("v1") == b"learned"


def test_memory_survives_capsule_reclaim():
    """The being's memory lives beside the brain — reclaiming the capsule that
    produced a vector does NOT erase it. Continuity holds."""
    bus, gate, overseer, conduit = _rig()
    overseer.split_region("cap", sections=1)
    bus.publish("cap.s0", "emit", {"vector_ref": "v9", "vector_bytes": b"keepme"})
    conduit.tick()

    # Simulate reclaiming the capsule: close its section entirely.
    bus.close_section("cap.s0")
    assert "cap.s0" not in bus.sections()
    # Memory is untouched — it was never in the capsule.
    assert conduit.memory.recall("v9") == b"keepme"


def test_real_npu_seat_swaps_in_without_touching_loop():
    """The future-proof claim: bond a different brain at runtime; the heartbeat
    is unchanged, only the judging differs."""
    bus, gate, overseer, conduit = _rig()
    overseer.split_region("cap", sections=1)

    class AlwaysCritical:                     # a stand-in 'NPU model'
        def judge(self, observations, memory):
            return [make_finding(
                id="cap.s0",
                organ="conduit",
                severity="critical",
                title="npu_flag",
                detail="brain says correct it",
            ) for _ in observations]

    conduit.bind_seat(AlwaysCritical())
    bus.publish("cap.s0", "anything", {"x": 1})
    findings = conduit.tick()

    assert findings and findings[0].title == "npu_flag"
    assert conduit.stats.corrections_issued == 1


def test_low_severity_findings_do_not_act():
    """The brain can observe without acting — only severity >= threshold turns
    into a real command. Watching != acting."""
    bus, gate, overseer, conduit = _rig()
    overseer.split_region("cap", sections=1)

    class Whisper:
        def judge(self, observations, memory):
            return [make_finding(
                id="cap.s0",
                organ="conduit",
                severity="info",
                title="note",
                detail="just noting",
            ) for _ in observations]

    conduit.bind_seat(Whisper())
    bus.publish("cap.s0", "t", {"x": 1})
    findings = conduit.tick()

    assert findings                          # it noticed
    assert conduit.stats.corrections_issued == 0   # but did not act


def test_memory_is_bounded():
    """The brain's memory can't balloon the skeleton — bounded rolling window."""
    mem = VectorMemory(capacity=10)
    for i in range(50):
        mem.absorb(f"v{i}", b"x", {"i": i})
    assert mem.size() <= 10
    assert mem.ingested == 50                # counted all, kept only capacity


def test_brain_corrections_are_signed_and_audited():
    """Every brain-triggered correction flows through the gate (signed +
    audited). Legitimate repeat corrections each carry a fresh nonce, so a
    genuinely needed correction is never silently dropped as a false replay —
    that was the M4 observer-review bug. Replay protection still applies to an
    intercepted TOKEN (proven in test_gate/test_wrap)."""
    bus, gate, overseer, conduit = _rig()
    overseer.split_region("cap", sections=1)

    from fabric.capabilities import SpliceCapability
    conduit.bind_corrector(
        lambda f: SpliceCapability(region_id="cap.s0", mode="merge",
                                   sections=1, deaf=False)
    )

    class Nag:
        def judge(self, observations, memory):
            return [make_finding(
                id="cap.s0",
                organ="conduit",
                severity="critical",
                title="drift",
                detail="again",
            )]

    conduit.bind_seat(Nag())

    bus.publish("cap.s0", "t", {"x": 1}); conduit.tick()
    bus.publish("cap.s0", "t", {"x": 2}); conduit.tick()

    # Both legitimate corrections land — the fabric fixes drift every time it
    # sees it, not just once. None silently denied as a false replay.
    assert conduit.stats.corrections_issued == 2
    assert conduit.stats.corrections_denied == 0


def test_heuristic_seat_detects_loops():
    """The out-of-the-box brain catches a section stuck repeating itself."""
    seat = HeuristicSeat(loop_threshold=5)
    obs = [{"_section": "cap.s0", "_topic": "spin"} for _ in range(6)]
    findings = seat.judge(obs, VectorMemory())
    assert any(f.title == "loop" for f in findings)


# ── BURN op — poisoned-vector purge (M4 observer review, risk #3) ─────────────

def test_burn_removes_poisoned_vector():
    from fabric.conduit import VectorMemory
    m = VectorMemory()
    m.absorb("good", b"a", {"src": "trusted"})
    m.absorb("poison", b"b", {"src": "attacker"})
    assert m.size() == 2
    assert m.burn("poison") is True
    assert m.size() == 1
    assert m.recall("poison") is None
    assert m.is_burned("poison") is True


def test_burned_ref_cannot_be_reabsorbed():
    from fabric.conduit import VectorMemory
    m = VectorMemory()
    m.absorb("x", b"a", {})
    m.burn("x")
    raised = False
    try:
        m.absorb("x", b"a2", {})
    except ValueError:
        raised = True
    assert raised is True


def test_burn_where_purges_a_lineage():
    from fabric.conduit import VectorMemory
    m = VectorMemory()
    m.absorb("v1", b"a", {"src": "bad-source"})
    m.absorb("v2", b"b", {"src": "bad-source"})
    m.absorb("v3", b"c", {"src": "good-source"})
    burned = m.burn_where(lambda meta: meta.get("src") == "bad-source")
    assert burned == 2
    assert m.size() == 1
    assert m.recall("v3") is not None
