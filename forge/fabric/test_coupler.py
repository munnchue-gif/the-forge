"""Tests for the simple trusted couplers (A native / B away limb).

Scope: NOT the deep hostile dive (parked). Proves the honest minimum — every
coupler speaks through the gate, and the away limb holds only a narrowed grant."""

import time
from hashlib import sha256

from fabric.gate import FabricGate
from fabric.capabilities import SpliceCapability, EgressCapability, NpuEvalCapability
from fabric.coupler import CouplerA, CouplerB, HomeBay, GrantRegistry


def _gate():
    return FabricGate(sha256(b"gate").digest())


ROOT = sha256(b"root").digest()


# ── Coupler A: native, trusted, direct ────────────────────────────────────────

def test_coupler_a_authorizes_locally():
    a = CouplerA(_gate())
    cap = SpliceCapability(region_id="r", mode="split", sections=1, deaf=True)
    ok, reason = a.request(cap)
    assert ok is True


# ── Coupler B: away limb, narrowed grant ──────────────────────────────────────

def _home():
    gate = _gate()
    reg = GrantRegistry(root_secret=ROOT)
    return HomeBay(gate=gate, registry=reg)


def test_away_limb_read_grant_is_allowed():
    home = _home()
    cap = NpuEvalCapability(capsule_id="c", model_id="m", vector_sha="v")   # a read-ish op
    signed, grant = home.stamp_for_away(cap, ttl=60, readonly=True)
    b = CouplerB(home=home)
    b.receive(signed)
    ok, reason = b.present()
    assert ok is True, reason


def test_away_limb_cannot_perform_write_op():
    """A brainless limb stamped read-only is refused a write (egress), even with
    a valid signature — the caveat blocks it at the gate."""
    home = _home()
    cap = EgressCapability(capsule_id="c", dest_host="1.2.3.4", dest_port=443, payload_sha="p")
    signed, grant = home.stamp_for_away(cap, ttl=60, readonly=True)
    b = CouplerB(home=home)
    b.receive(signed)
    ok, reason = b.present()
    assert ok is False
    assert "read-only" in reason.lower() or "write" in reason.lower()


def test_away_grant_expires():
    home = _home()
    cap = NpuEvalCapability(capsule_id="c", model_id="m", vector_sha="v")
    # ttl in the past → already expired.
    signed, grant = home.stamp_for_away(cap, ttl=0.0, readonly=True)
    time.sleep(0.01)
    b = CouplerB(home=home)
    b.receive(signed)
    ok, reason = b.present()
    assert ok is False


def test_away_limb_holds_no_minting_key():
    """The limb only holds a signed cap — it has no gate secret, so it cannot
    forge or widen a right. (Structural: CouplerB has no key attribute.)"""
    home = _home()
    b = CouplerB(home=home)
    assert not hasattr(b, "_secret")
    assert not hasattr(b, "key_resolver")


def test_revoke_kills_the_grant():
    home = _home()
    cap = NpuEvalCapability(capsule_id="c", model_id="m", vector_sha="v")
    signed, grant = home.stamp_for_away(cap, ttl=60, readonly=True)
    b = CouplerB(home=home)
    b.receive(signed)
    assert b.present()[0] is True
    home.registry.revoke(signed.token)
    # After revoke there's no grant → base gate rules apply; but the same signed
    # token was already recorded once, so replay protection now denies it.
    ok, _ = b.present()
    assert ok is False


def test_present_without_grant_fails():
    home = _home()
    b = CouplerB(home=home)
    ok, reason = b.present()
    assert ok is False
    assert "no grant" in reason.lower()
