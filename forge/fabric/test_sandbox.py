"""
Proof of the Concoctinator: a sealed arena where the fabric concocts and strips
freely, catches what would fail, and promotes only clean concoctions to live.
"""

from __future__ import annotations

from fabric.gate import FabricGate
from fabric.wrap import WrapStore
from fabric.types import Finding, make_finding
from fabric.sandbox import Concoctinator


def test_arena_is_isolated_from_live():
    """The sandbox owns its own substance instance — a different gate/bus/store
    than any live fabric. Isolation IS the freedom."""
    live_gate = FabricGate(b"live-secret-000000000000000000000")
    box = Concoctinator()
    assert box.arena["gate"] is not live_gate       # separate doors
    assert box.arena["store"].shelf_size() == 0      # its own empty shelf


def test_concoct_trusting_the_declared_method():
    """Trust the method: shape comes from the intent's own declaration."""
    box = Concoctinator()
    c = box.concoct(
        intent={"presets": {"role": "mixer"}, "tool_binds": ["read", "splice"]},
        model_id="m", snips=["a", "b"],
    )
    assert c.wrap is not None
    assert dict(c.wrap.presets)["role"] == "mixer"
    # two splices + one conform recorded
    assert sum(1 for s in c.steps if s.action == "splice") == 2
    assert any(s.action == "conform" for s in c.steps)


def test_concoct_with_npu_brain_shaper():
    """Trust the brain: a shaper proposes the shape instead of the tool."""
    box = Concoctinator()

    def brain_shaper(intent):
        # brain ignores what the tool asked and proposes a safe shape
        return {"role": "brain-proposed"}, ["read"]

    c = box.concoct(intent={"presets": {"role": "SUSPICIOUS"}},
                    model_id="m", shaper=brain_shaper)
    assert dict(c.wrap.presets)["role"] == "brain-proposed"
    conform = next(s for s in c.steps if s.action == "conform")
    assert conform.detail["shape_origin"] == "npu_brain"


def test_strip_keeps_the_material():
    """The recycler: strip the suit, keep the vectors for remixing."""
    box = Concoctinator()
    c = box.concoct(intent={"presets": {"r": "x"}}, model_id="m",
                    vectors=b"raw-material")
    stripped = box.strip(c.concoction_id, keep_vectors=True)
    assert stripped.vectors == b"raw-material"       # material handed back
    assert any(s.action == "strip" for s in stripped.steps)


def test_strip_without_keeping_discards_material():
    box = Concoctinator()
    c = box.concoct(intent={"presets": {"r": "x"}}, model_id="m",
                    vectors=b"disposable")
    stripped = box.strip(c.concoction_id, keep_vectors=False)
    assert stripped.vectors == b""


def test_clean_concoction_is_promotable():
    """A well-behaved concoction passes is_clean and can be promoted."""
    box = Concoctinator()
    c = box.concoct(intent={"presets": {"role": "ok"}}, model_id="m",
                    snips=["a"], vectors=b"v")
    assert c.is_clean


def test_dirty_concoction_blocked_from_promotion():
    """A concoction the brain flagged critical is NOT clean and cannot promote —
    the arena catches it before it ever reaches the live gate."""
    box = Concoctinator()
    c = box.concoct(intent={"presets": {"role": "risky"}}, model_id="m")

    def critic(concoction):
        return [make_finding(
            id=concoction.concoction_id,
            organ="sandbox",
            severity="critical",
            title="danger",
            detail="do not ship",
        )]

    box.judge(c.concoction_id, critic)
    assert not c.is_clean

    live_gate = FabricGate(b"live-secret-000000000000000000000")
    live_store = WrapStore()
    ok, reason = box.promote(c.concoction_id, live_gate, live_store)
    assert not ok and "not clean" in reason
    assert live_store.shelf_size() == 0              # nothing leaked to live


def test_clean_concoction_promotes_to_live_gate():
    """The on-ramp: a clean concoction replays its exact shape against a REAL
    strict gate and lands in the live store."""
    box = Concoctinator()
    c = box.concoct(intent={"presets": {"role": "shippable"},
                            "tool_binds": ["read"]},
                    model_id="planner", vectors=b"good")
    assert c.is_clean

    live_gate = FabricGate(b"live-secret-000000000000000000000")
    live_store = WrapStore()
    ok, reason = box.promote(c.concoction_id, live_gate, live_store)
    assert ok, reason
    assert live_store.shelf_size() == 1              # it went live


def test_arena_experiments_never_touch_live_store():
    """Unlimited: many concoctions in the arena, live store stays empty until an
    explicit promote."""
    box = Concoctinator()
    for i in range(20):
        box.concoct(intent={"presets": {"i": str(i)}}, model_id=f"m{i}")
    assert len(box.list_concoctions()) == 20
    # arena store filled; a fresh live store is still pristine
    assert WrapStore().shelf_size() == 0
