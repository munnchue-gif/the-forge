"""Tests for macaroon-style capability attenuation (coupler prerequisite)."""

import time
from hashlib import sha256

from fabric.caveat import (
    AttenuatedGrant, Context, caveat_policy,
    expires_in, only_tenant, only_section, op_in, read_only,
)
from fabric.gate import FabricGate
from fabric.capabilities import SpliceCapability, EgressCapability


ROOT = sha256(b"root").digest()


def _ctx(**kw):
    base = dict(now=1000.0, tenant_id="default", section="", op_kind="")
    base.update(kw)
    return Context(**base)


def test_grant_satisfied_when_all_caveats_pass():
    g = (AttenuatedGrant.over("tok", ROOT)
         .add(only_tenant("default"))
         .add(only_section("cap-a")))
    assert g.check(_ctx(section="cap-a")) is None


def test_grant_fails_on_wrong_section():
    g = AttenuatedGrant.over("tok", ROOT).add(only_section("cap-a"))
    assert g.check(_ctx(section="cap-b")) is not None


def test_expiry_caveat():
    g = AttenuatedGrant.over("tok", ROOT).add(expires_in(60, issued_at=1000.0))
    assert g.check(_ctx(now=1030.0)) is None      # within ttl
    assert g.check(_ctx(now=1100.0)) is not None  # past ttl


def test_read_only_blocks_writes():
    g = AttenuatedGrant.over("tok", ROOT).add(read_only())
    assert g.check(_ctx(op_kind="fabric.observe")) is None
    assert g.check(_ctx(op_kind="net.egress")) is not None
    assert g.check(_ctx(op_kind="fabric.splice")) is not None


def test_op_allowlist():
    g = AttenuatedGrant.over("tok", ROOT).add(op_in("a", "b"))
    assert g.check(_ctx(op_kind="a")) is None
    assert g.check(_ctx(op_kind="c")) is not None


def test_chain_verifies_and_detects_tampering():
    g = (AttenuatedGrant.over("tok", ROOT)
         .add(only_tenant("default"))
         .add(read_only()))
    assert g.verify_chain(ROOT) is True
    # Attacker drops a caveat to widen the right → proof no longer matches.
    g.labels.pop()
    assert g.verify_chain(ROOT) is False


def test_you_can_only_attenuate_never_widen():
    """There is no remove(); adding a caveat only ever narrows, and the chain
    binds the exact set."""
    g = AttenuatedGrant.over("tok", ROOT).add(only_section("cap-a"))
    proof_1 = g.proof
    g.add(read_only())
    assert g.proof != proof_1                  # chain advanced
    assert not hasattr(g, "remove")            # no widening API


def test_policy_denies_write_through_the_gate_end_to_end():
    """A remote limb holds a read-only grant. Through the real gate, a splice
    (write) is DENIED even though the signature is valid."""
    gate = FabricGate(sha256(b"k").digest())
    cap = SpliceCapability(region_id="cap-a", mode="split", sections=1, deaf=True)
    signed = gate.sign(cap)

    grant = AttenuatedGrant.over(signed.token, ROOT).add(read_only())
    registry = {signed.token: grant}

    def context_of(s, tenant):
        return Context(now=time.time(), tenant_id=tenant, section="cap-a",
                       op_kind=s.kind)   # s.kind e.g. "fabric.splice"

    gate.add_policy(caveat_policy(lambda t: registry.get(t), ROOT, context_of))
    decision = gate.authorize(signed)
    assert decision.allowed is False           # read-only caveat blocked the write


def test_policy_allows_when_no_grant_registered():
    gate = FabricGate(sha256(b"k").digest())
    cap = SpliceCapability(region_id="cap-a", mode="split", sections=1, deaf=True)
    signed = gate.sign(cap)
    gate.add_policy(caveat_policy(lambda t: None, ROOT,
                                  lambda s, tn: Context(now=time.time(),
                                                        tenant_id=tn)))
    assert gate.authorize(signed).allowed is True   # unattenuated → base rules
