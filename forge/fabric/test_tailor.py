"""
Tests for the Embedded Tailor — the organ that strips, drafts, fits, and hands
over shapes without ever touching the live body unproven.

Proves:
  • the Tailor drafts a sane shape from a goal (heuristic seat)
  • recycling re-pours an old suit's proven presets (nothing thrown away)
  • a clean draft fits in the arena and promotes to the LIVE store
  • the Tailor REFUSES to hand over a dirty fit (the body stays untouched)
  • the seat is hot-swappable (the NPU upgrade path) without touching the loop
  • the brain (seat) cannot act on live state directly — only via gate promote
"""

from hashlib import sha256

from fabric.gate import FabricGate
from fabric.wrap import WrapStore
from fabric.sandbox import Concoctinator
from fabric.tailor import (
    EmbeddedTailor, HeuristicTailor, TailorSeat, Draft,
)


def _live():
    """A fresh, STRICT live gate + store (production side)."""
    gate = FabricGate(sha256(b"live-secret").digest())
    store = WrapStore()
    return gate, store


def _tailor():
    return EmbeddedTailor(Concoctinator())


# ── 1. drafts a sane shape from a goal ────────────────────────────────────────

def test_draft_shape_from_goal():
    t = _tailor()
    draft = t.draft_shape("llama3", goal="a code assistant")
    assert isinstance(draft, Draft)
    assert draft.model_id == "llama3"
    # goal 'code' pulls in the code tools
    assert "shell.run" in draft.tool_binds
    assert "fs.read" in draft.tool_binds
    # always carries the conservative sealed baseline
    assert draft.presets["safety"] == "sealed"
    assert draft.reclaimed_from is None


# ── 2. recycling re-pours an old suit's proven presets ────────────────────────

def test_recycle_repours_old_shape():
    gate, store = _live()
    # Seal an old suit into the live store first.
    old_wrap, _ = store.seal(
        gate, capsule_id="old", model_id="llama3",
        presets={"temperature": "0.2", "persona": "lawyer"},
        tool_binds=["doc.read"],
    )
    t = _tailor()
    draft = t.draft_shape(
        "llama3", goal="chat helper",
        recycle_wrap_sha=old_wrap.wrap_sha, live_store=store,
    )
    # proven presets carried forward
    assert draft.presets["persona"] == "lawyer"
    assert draft.presets["temperature"] == "0.2"
    assert "doc.read" in draft.tool_binds
    assert draft.reclaimed_from == old_wrap.wrap_sha


# ── 3. a clean draft fits and promotes to the LIVE store ──────────────────────

def test_clean_draft_promotes_to_live():
    gate, store = _live()
    t = _tailor()
    assert store.shelf_size() == 0
    result = t.tailor("mistral", goal="research agent",
                      live_gate=gate, live_store=store)
    assert result.clean is True
    assert result.promoted_wrap_sha is not None
    # it actually landed on the live shelf
    assert store.shelf_size() == 1
    wrap, _ = store.repour(result.promoted_wrap_sha)
    assert wrap is not None
    assert "web.search" in wrap.tool_binds


# ── 4. Tailor refuses to hand over a dirty fit ────────────────────────────────

def test_dirty_fit_is_refused():
    """A seat that drafts a shape the arena flags dirty must NOT reach live."""
    gate, store = _live()

    class DirtySeat:
        def draft(self, model_id, *, goal, recycled):
            # A brain finding of severity 3 makes the concoction unclean.
            return Draft(model_id=model_id, presets={"safety": "sealed"},
                         tool_binds=(), reason="dirty test")

    t = EmbeddedTailor(Concoctinator(), seat=DirtySeat())
    draft = t.draft_shape("x", goal="whatever")
    fit = t.fit(draft, evaluator=lambda c: [_Finding(severity=3)])
    assert fit.clean is False
    # hand_over must raise, and the live body must stay empty
    raised = False
    try:
        t.hand_over(fit, live_gate=gate, live_store=store)
    except PermissionError:
        raised = True
    assert raised is True
    assert store.shelf_size() == 0


# ── 5. seat is hot-swappable (NPU upgrade path) ───────────────────────────────

def test_seat_hot_swap():
    t = _tailor()

    class NpuLikeSeat:
        def draft(self, model_id, *, goal, recycled):
            return Draft(model_id=model_id,
                         presets={"safety": "sealed", "npu": "arrow-lake"},
                         tool_binds=("npu.eval",), reason="npu draft")

    t.bind_seat(NpuLikeSeat())
    draft = t.draft_shape("m", goal="anything")
    assert draft.presets["npu"] == "arrow-lake"
    assert "npu.eval" in draft.tool_binds


def test_bind_rejects_non_seat():
    t = _tailor()
    raised = False
    try:
        t.bind_seat(object())
    except TypeError:
        raised = True
    assert raised is True


# ── 6. the default seat satisfies the protocol ────────────────────────────────

def test_heuristic_is_a_seat():
    assert isinstance(HeuristicTailor(), TailorSeat)


# small stand-in matching sandbox.Finding's duck shape (needs .severity)
class _Finding:
    def __init__(self, severity):
        self.severity = severity
        self.detail = "test"
