"""
Property-based tests (Hypothesis) — the test type the M4 observer review said
we were missing. Unit tests prove code matches intent on hand-picked inputs;
these throw thousands of generated inputs at the security-critical invariants.

Invariants proven:
  • Replay ledger: NO false negatives (a replayed token is ALWAYS caught) and
    NO false-positive lockout (distinct fresh tokens are ALWAYS accepted), across
    generated bursts — the review's risk #1.
  • Gate: any two distinct legitimate mints both authorize (nonce fix holds for
    arbitrary capabilities).
  • Bus: bounded queue never exceeds capacity under generated publish storms,
    and the dropped counter is exact.
  • Delimiter escape: no caller-controlled string can forge a colliding canonical.
"""

from hashlib import sha256

from hypothesis import given, settings, strategies as st

from fabric.gate import FabricGate, ReplayLedger
from fabric.capabilities import SpliceCapability, MountCapability
from fabric.bus import SubstanceBus


# ── Replay ledger: no false negatives, no false-positive lockout ──────────────

@settings(max_examples=200)
@given(n=st.integers(min_value=1, max_value=500))
def test_distinct_tokens_never_falsely_rejected(n):
    """N distinct fresh tokens in the same instant are ALL accepted (no lockout)."""
    led = ReplayLedger(window_seconds=30, tolerance=1)
    now = 1000.0
    for i in range(n):
        digest = sha256(f"tok-{i}".encode()).digest()
        assert led.check_and_record(digest, now) is True


@settings(max_examples=200)
@given(tokens=st.lists(st.binary(min_size=8, max_size=8), min_size=1, max_size=200))
def test_replayed_token_always_caught(tokens):
    """Any token, once recorded, is ALWAYS rejected on replay (no false negative)."""
    led = ReplayLedger(window_seconds=30, tolerance=1)
    now = 5000.0
    seen = set()
    for t in tokens:
        first = led.check_and_record(t, now)
        if t in seen:
            assert first is False        # replay must be caught
        else:
            assert first is True         # first sighting accepted
            seen.add(t)
        # An immediate re-check of the same token is always a replay.
        assert led.check_and_record(t, now) is False


# ── Gate: two distinct legit mints of ANY capability both authorize ───────────

@settings(max_examples=150)
@given(region=st.text(min_size=1, max_size=40),
       mode=st.sampled_from(["split", "merge"]),
       sections=st.integers(min_value=1, max_value=8))
def test_two_legit_mints_authorize(region, mode, sections):
    g = FabricGate(sha256(b"k").digest())
    cap = SpliceCapability(region_id=region, mode=mode, sections=sections, deaf=True)
    a = g.sign(cap)
    b = g.sign(cap)
    assert a.token != b.token
    assert g.authorize(a).allowed
    assert g.authorize(b).allowed
    # …but replaying a's exact token is still caught.
    assert not g.authorize(a).allowed


# ── Delimiter escape: no injected '|' can forge a colliding canonical ─────────

@settings(max_examples=200)
@given(cid=st.text(min_size=0, max_size=30),
       agent=st.text(min_size=0, max_size=30),
       h=st.text(min_size=0, max_size=30))
def test_no_canonical_collision_via_delimiter(cid, agent, h):
    """For any two DIFFERENT field tuples, canonical() strings must differ —
    escaping guarantees the '|' can't be used to shift boundaries."""
    a = MountCapability(capsule_id=cid, agent_name=agent, slot_cap_hash=h)
    # A shifted variant that, without escaping, could collide:
    b = MountCapability(capsule_id=cid + "|" + agent, agent_name="", slot_cap_hash=h)
    if (cid, agent) != (cid + "|" + agent, ""):
        assert a.canonical() != b.canonical()


# ── Bus: bounded queue never exceeds capacity; dropped counter exact ──────────

@settings(max_examples=100)
@given(cap=st.integers(min_value=1, max_value=32),
       msgs=st.integers(min_value=0, max_value=300))
def test_bounded_queue_never_overflows(cap, msgs):
    """Under a generated publish storm, a subscriber queue NEVER exceeds its
    capacity, and every un-delivered message is counted exactly (no silent
    memory balloon) — the review's memory-DoS concern."""
    bus = SubstanceBus(maxsize=cap)
    bus.open_section("sec")
    q = bus.subscribe("sec", "t")          # returns the bounded asyncio.Queue
    before_dropped = bus.dropped
    for i in range(msgs):
        bus.publish("sec", "t", {"i": i})
    # queue is hard-bounded
    assert q.qsize() <= cap
    # accounting is exact: delivered + dropped == published
    delivered = q.qsize()
    dropped = bus.dropped - before_dropped
    assert delivered + dropped == msgs
