"""
Proof tests for Forge-NG FabricGate.

The headline test — test_replay_survives_register_pressure — is the exact
scenario the ORIGINAL SecurityGuard fails: a replayed token whose register
slots have been evicted by later traffic. Forge-NG must still catch it.
"""

from __future__ import annotations

import hashlib

from fabric.gate import FabricGate, Decision, GateDenied
from fabric.capabilities import (
    SpawnCapability, MountCapability, EgressCapability, NpuEvalCapability,
)

SECRET = b"test-secret-key-do-not-use-in-prod"


def _spawn(i: int) -> SpawnCapability:
    return SpawnCapability(
        capsule_id=f"cap-{i}",
        script_sha=hashlib.sha256(f"script-{i}".encode()).hexdigest(),
        cpu_quota="100%", mem_limit="2G", network=False,
    )


def test_happy_path_allows():
    g = FabricGate(SECRET, window_seconds=30, tolerance=1)
    signed = g.sign(_spawn(1))
    assert g.authorize(signed).allowed


def test_tampered_signature_denied():
    g = FabricGate(SECRET)
    signed = g.sign(_spawn(1))
    bad = signed.__class__(kind=signed.kind, canonical=signed.canonical,
                           token="0" * 64, issued_at=signed.issued_at)
    assert g.authorize(bad).decision is Decision.DENY_SIGNATURE


def test_expired_denied():
    g = FabricGate(SECRET, window_seconds=30, tolerance=1)
    signed = g.sign(_spawn(1), ts=1000.0)
    d = g.authorize(signed, now=1000.0 + 10_000)
    assert d.decision is Decision.DENY_EXPIRED


def test_immediate_replay_denied():
    g = FabricGate(SECRET)
    signed = g.sign(_spawn(1))
    assert g.authorize(signed).allowed
    assert g.authorize(signed).decision is Decision.DENY_REPLAY


def test_replay_survives_register_pressure():
    """
    THE FIX. Original core: two 48-bit slots, silent eviction → a replay
    after enough traffic slips through (false negative). Forge-NG keeps an
    EXACT bounded ledger, so the replay is still caught after 100k other
    tokens pass through within the same validity window.
    """
    g = FabricGate(SECRET, window_seconds=30, tolerance=1)
    victim = g.sign(_spawn(0))
    assert g.authorize(victim).allowed          # first use: fine

    # Flood the gate with 100k *distinct* valid tokens (same time window).
    for i in range(1, 100_001):
        s = g.sign(_spawn(i))
        assert g.authorize(s).allowed

    # Now replay the victim. Original would let this through; we must not.
    assert g.authorize(victim).decision is Decision.DENY_REPLAY


def test_ledger_is_memory_bounded():
    """After the validity window fully passes, old tokens are dropped —
    memory can't grow without bound (the other half of the fix)."""
    g = FabricGate(SECRET, window_seconds=1, tolerance=1)
    for i in range(5000):
        g.authorize(g.sign(_spawn(i), ts=1000.0), now=1000.0)
    early = g.ledger_size()
    # Jump far past the validity window; a new op triggers GC of stale buckets.
    g.authorize(g.sign(_spawn(999999), ts=2000.0), now=2000.0)
    assert g.ledger_size() < early


def test_one_gate_all_capabilities():
    """Spawn, mount, egress, AND the new NPU eval all ride the same gate
    with zero new gate code — the extensibility claim, proven."""
    g = FabricGate(SECRET)
    caps = [
        _spawn(1),
        MountCapability("cap-1", "planner", "abc123"),
        EgressCapability("cap-1", "api.example.com", 443, "deadbeef"),
        NpuEvalCapability("cap-1", "qwen-npu", "f00dface"),
    ]
    for c in caps:
        assert g.authorize(g.sign(c)).allowed


def test_per_tenant_key_isolation():
    """A token signed for tenant A must not validate for tenant B —
    the multi-tenant SDK-readiness property the original lacked."""
    keys = {"A": b"key-A-secret-000000000000", "B": b"key-B-secret-000000000000"}
    g = FabricGate(key_resolver=lambda t: keys[t])
    signed_for_a = g.sign(_spawn(1), tenant_id="A")
    assert g.authorize(signed_for_a, tenant_id="A").allowed
    assert g.authorize(signed_for_a, tenant_id="B").decision is Decision.DENY_SIGNATURE


def test_policy_hook_denies():
    g = FabricGate(SECRET)
    g.add_policy(lambda s, t: "blocked host" if "evil.com" in s.canonical else None)
    bad = EgressCapability("cap-1", "evil.com", 443, "x")
    assert g.authorize(g.sign(bad)).decision is Decision.DENY_POLICY
    good = EgressCapability("cap-1", "api.example.com", 443, "x")
    assert g.authorize(g.sign(good)).allowed


def test_enforce_raises():
    g = FabricGate(SECRET)
    signed = g.sign(_spawn(1))
    g.enforce(signed)                       # first: ok
    try:
        g.enforce(signed)                   # replay: must raise
        assert False, "expected GateDenied"
    except GateDenied as e:
        assert e.decision.decision is Decision.DENY_REPLAY


# ── M4 observer-review security fixes ─────────────────────────────────────────

def test_nonce_allows_two_legit_identical_actions():
    """FIX 1 (nonce): two legitimate identical actions in the same window both
    authorize, because each mint carries a fresh nonce → different tokens."""
    from hashlib import sha256
    from fabric.capabilities import SpliceCapability
    g = FabricGate(sha256(b"k").digest())
    cap = SpliceCapability(region_id="r", mode="split", sections=1, deaf=True)
    a = g.sign(cap)
    b = g.sign(cap)
    assert a.token != b.token           # unique mints
    assert g.authorize(a).allowed
    assert g.authorize(b).allowed       # was falsely denied before the fix


def test_same_token_replay_still_blocked():
    """FIX 1 must NOT weaken replay protection: replaying the SAME token fails."""
    from hashlib import sha256
    from fabric.capabilities import SpliceCapability
    g = FabricGate(sha256(b"k").digest())
    cap = SpliceCapability(region_id="r", mode="split", sections=1, deaf=True)
    s = g.sign(cap)
    assert g.authorize(s).allowed
    assert not g.authorize(s).allowed   # exact token reuse = replay


def test_nonce_is_bound_into_hmac():
    """The nonce can't be swapped: tampering the nonce breaks the signature."""
    from hashlib import sha256
    from fabric.capabilities import SpliceCapability
    from fabric.gate import SignedCapability
    g = FabricGate(sha256(b"k").digest())
    cap = SpliceCapability(region_id="r", mode="split", sections=1, deaf=True)
    s = g.sign(cap)
    tampered = SignedCapability(kind=s.kind, canonical=s.canonical,
                                token=s.token, issued_at=s.issued_at,
                                nonce="attacker-swapped")
    assert not g.authorize(tampered).allowed   # signature mismatch


def test_delimiter_injection_cannot_forge_action():
    """FIX 2 (delimiter escape): a '|' smuggled into a caller-controlled field
    must NOT collide with a differently-structured legitimate capability."""
    from fabric.capabilities import MountCapability
    # Attacker tries to make capsule_id='a' agent_name='b' look identical to
    # capsule_id='a|b' by stuffing a delimiter.
    legit = MountCapability(capsule_id="a", agent_name="b", slot_cap_hash="h")
    attack = MountCapability(capsule_id="a|b", agent_name="", slot_cap_hash="h")
    assert legit.canonical() != attack.canonical()   # escaped → no collision
    assert "\\|" in attack.canonical()                # the '|' was escaped
